/**
 * Inspectable ECDSA P-256 / SHA-256 verification example.
 * This public test fixture demonstrates authenticity of sample bytes only.
 * It is not firmware, secure boot, key provisioning, rollback enforcement or
 * a device implementation. No signing private key is shipped or retained.
 * Everything runs locally with the browser's Web Crypto API.
 */
const PUBLIC_KEY = {
  kty: 'EC',
  x: '2P6_VrbQbm8GGlTRl1VxqoOQR8D9hOljEqrpYqd1wXY',
  y: 'w5YFHDMMc52goSxzJJqHp7QBJwmRg38iP1rypki3aZk',
  crv: 'P-256',
};
const PAYLOAD =
  'NEXAFUSION SIGNED PAYLOAD EXAMPLE\nboard=demo-001\nversion=7\nmessage=engineering close to the hardware\n';
const SIGNATURE =
  'OJnefu//PFXKbLLhKnpQxPoV3eI/BD5ZCOsP+7Gysi3aIwDPI3H2cG0pCwcM8BN6lMJGnblfl699yL7PhHPIYA==';
let keyPromise;

export async function verifyBootExample(tampered = false) {
  if (!globalThis.crypto?.subtle) return { supported: false };
  const bytes = new TextEncoder().encode(PAYLOAD);
  // Flip one bit in the sample message, retaining its original signature.
  if (tampered) bytes[bytes.length - 2] ^= 1;
  const signature = Uint8Array.from(atob(SIGNATURE), (character) => character.charCodeAt(0));
  keyPromise ??= crypto.subtle.importKey(
    'jwk',
    PUBLIC_KEY,
    { name: 'ECDSA', namedCurve: 'P-256' },
    false,
    ['verify'],
  );
  const [valid, digest] = await Promise.all([
    crypto.subtle.verify({ name: 'ECDSA', hash: 'SHA-256' }, await keyPromise, signature, bytes),
    crypto.subtle.digest('SHA-256', bytes),
  ]);
  return {
    supported: true,
    valid,
    byteLength: bytes.byteLength,
    digest: Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, '0')).join(
      '',
    ),
  };
}
