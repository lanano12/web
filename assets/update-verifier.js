/**
 * Educational signed-update admission check. Uses Web Crypto, not custom crypto.
 * The caller supplies a trusted public CryptoKey and trusted device/version state.
 * This does not implement a bootloader, protected counters, key rotation or flashing.
 */
export const MAX_PAYLOAD_BYTES = 1024 * 1024;
export const MAX_MANIFEST_BYTES = 1024;

const reject = (reason) => ({ accepted: false, reason });
const integer = (value) => Number.isSafeInteger(value) && value >= 0;
const bytes = (value, max) =>
  value instanceof Uint8Array && value.length > 0 && value.length <= max;

export async function verifyUpdateBundle(bundle, context, cryptography = globalThis.crypto) {
  if (!cryptography?.subtle) return reject('verification-unavailable');
  if (
    !context ||
    !integer(context.installedVersion) ||
    !integer(context.minimumVersion) ||
    typeof context.device !== 'string' ||
    !/^[A-Za-z0-9._-]{1,64}$/.test(context.device) ||
    context.trustedPublicKey?.type !== 'public' ||
    context.trustedPublicKey.algorithm?.name !== 'ECDSA' ||
    context.trustedPublicKey.algorithm?.namedCurve !== 'P-256' ||
    !context.trustedPublicKey.usages?.includes('verify')
  ) {
    return reject('invalid-trust-context');
  }
  if (
    !bundle ||
    !bytes(bundle.manifestBytes, MAX_MANIFEST_BYTES) ||
    !bytes(bundle.payloadBytes, MAX_PAYLOAD_BYTES) ||
    !bytes(bundle.signature, 64) ||
    bundle.signature.length !== 64
  ) {
    return reject('invalid-bundle');
  }
  // Snapshot before the first await: callers cannot replace bytes/state mid-check.
  const manifestBytes = bundle.manifestBytes.slice();
  const payloadBytes = bundle.payloadBytes.slice();
  const signature = bundle.signature.slice();
  const { trustedPublicKey, device, installedVersion, minimumVersion } = context;
  try {
    const authentic = await cryptography.subtle.verify(
      { name: 'ECDSA', hash: 'SHA-256' },
      trustedPublicKey,
      signature,
      manifestBytes,
    );
    if (!authentic) return reject('invalid-signature');
    let manifest, manifestText;
    try {
      manifestText = new TextDecoder('utf-8', { fatal: true }).decode(manifestBytes);
      manifest = JSON.parse(manifestText);
    } catch {
      return reject('invalid-manifest');
    }
    if (
      !manifest ||
      Array.isArray(manifest) ||
      Object.keys(manifest).sort().join(',') !== 'device,length,schema,sha256,version' ||
      manifest.schema !== 1 ||
      typeof manifest.device !== 'string' ||
      !/^[A-Za-z0-9._-]{1,64}$/.test(manifest.device) ||
      !integer(manifest.version) ||
      !integer(manifest.length) ||
      typeof manifest.sha256 !== 'string' ||
      !/^[a-f0-9]{64}$/.test(manifest.sha256)
    )
      return reject('invalid-manifest');
    // A defined encoding prevents duplicate-key / alternate-parser ambiguity.
    const canonical = JSON.stringify({
      schema: manifest.schema,
      device: manifest.device,
      version: manifest.version,
      length: manifest.length,
      sha256: manifest.sha256,
    });
    if (manifestText !== canonical) return reject('invalid-manifest');
    if (manifest.device !== device) return reject('wrong-device');
    if (manifest.version <= installedVersion || manifest.version < minimumVersion)
      return reject('rollback');
    if (manifest.length !== payloadBytes.length) return reject('length-mismatch');
    const digest = new Uint8Array(await cryptography.subtle.digest('SHA-256', payloadBytes));
    const sha256 = Array.from(digest, (byte) => byte.toString(16).padStart(2, '0')).join('');
    if (sha256 !== manifest.sha256) return reject('payload-mismatch');
    // An installer must consume this verified snapshot, not the caller's input buffer.
    return { accepted: true, version: manifest.version, sha256, payloadBytes };
  } catch {
    return reject('verification-error');
  }
}
