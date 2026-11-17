/** Run with Node 24: node --test examples/update-verifier.test.mjs */
import assert from 'node:assert/strict';
import test from 'node:test';
import { webcrypto } from 'node:crypto';
import {
  verifyUpdateBundle,
  MAX_PAYLOAD_BYTES,
  MAX_MANIFEST_BYTES,
} from '../assets/update-verifier.js';

// Test keys exist only in memory. No production signing key is involved.
const keys = await webcrypto.subtle.generateKey({ name: 'ECDSA', namedCurve: 'P-256' }, false, [
  'sign',
  'verify',
]);
const encoder = new TextEncoder();
const payload = encoder.encode(
  'NexaFusion educational firmware bytes. Never flash this to a device.',
);
const digest = Buffer.from(await webcrypto.subtle.digest('SHA-256', payload)).toString('hex');
const context = {
  trustedPublicKey: keys.publicKey,
  device: 'demo-board-v1',
  installedVersion: 7,
  minimumVersion: 8,
};
async function fixture(changes = {}, raw) {
  const manifest = {
    schema: 1,
    device: 'demo-board-v1',
    version: 8,
    length: payload.length,
    sha256: digest,
    ...changes,
  };
  const manifestBytes = raw ?? encoder.encode(JSON.stringify(manifest));
  const signature = new Uint8Array(
    await webcrypto.subtle.sign({ name: 'ECDSA', hash: 'SHA-256' }, keys.privateKey, manifestBytes),
  );
  return { manifestBytes, payloadBytes: payload.slice(), signature };
}
const check = (bundle, overrides = {}, crypto = webcrypto) =>
  verifyUpdateBundle(bundle, { ...context, ...overrides }, crypto);
async function refusal(bundle, reason, overrides) {
  assert.deepEqual(await check(bundle, overrides), { accepted: false, reason });
}

test('accepts an authentic update for the expected device and newer version', async () => {
  const result = await check(await fixture());
  assert.equal(result.accepted, true);
  assert.equal(result.version, 8);
  assert.equal(result.sha256, digest);
  assert.deepEqual(result.payloadBytes, payload);
});
test('rejects one altered payload bit', async () => {
  const bundle = await fixture();
  bundle.payloadBytes[0] ^= 1;
  await refusal(bundle, 'payload-mismatch');
});
test('rejects one altered manifest bit', async () => {
  const bundle = await fixture();
  bundle.manifestBytes[0] ^= 1;
  await refusal(bundle, 'invalid-signature');
});
test('rejects one altered signature bit', async () => {
  const bundle = await fixture();
  bundle.signature[0] ^= 1;
  await refusal(bundle, 'invalid-signature');
});
test('rejects a signature checked against another trusted key', async () => {
  const other = await webcrypto.subtle.generateKey({ name: 'ECDSA', namedCurve: 'P-256' }, false, [
    'sign',
    'verify',
  ]);
  await refusal(await fixture(), 'invalid-signature', { trustedPublicKey: other.publicKey });
});
test('rejects an authentic image intended for a different device', async () => {
  await refusal(await fixture({ device: 'another-board' }), 'wrong-device');
});
test('rejects reinstalling the current version', async () => {
  await refusal(await fixture({ version: 7 }), 'rollback');
});
test('rejects an older correctly signed version', async () => {
  await refusal(await fixture({ version: 6 }), 'rollback');
});
test('enforces a minimum permitted version above the installed version', async () => {
  await refusal(await fixture(), 'rollback', { minimumVersion: 9 });
});
test('rejects a signed length that does not match the payload', async () => {
  await refusal(await fixture({ length: payload.length + 1 }), 'length-mismatch');
});
test('rejects unknown signed schema versions', async () => {
  await refusal(await fixture({ schema: 2 }), 'invalid-manifest');
});
test('rejects unexpected signed fields instead of guessing their meaning', async () => {
  await refusal(await fixture({ forceInstall: true }), 'invalid-manifest');
});
test('rejects non-integer versions', async () => {
  await refusal(await fixture({ version: 8.5 }), 'invalid-manifest');
});
test('rejects malformed but authentically signed JSON', async () => {
  await refusal(await fixture({}, encoder.encode('{')), 'invalid-manifest');
});
test('rejects malformed but authentically signed UTF-8', async () => {
  await refusal(await fixture({}, new Uint8Array([255])), 'invalid-manifest');
});
test('rejects signed duplicate keys instead of depending on parser precedence', async () => {
  const bundle = await fixture();
  const duplicate = encoder.encode(
    new TextDecoder()
      .decode(bundle.manifestBytes)
      .replace('"version":8', '"version":7,"version":8'),
  );
  await refusal(await fixture({}, duplicate), 'invalid-manifest');
});
test('rejects alternate signed JSON encoding outside the defined format', async () => {
  const bundle = await fixture();
  const alternate = encoder.encode(' ' + new TextDecoder().decode(bundle.manifestBytes));
  await refusal(await fixture({}, alternate), 'invalid-manifest');
});
test('bounds the manifest before invoking cryptography', async () => {
  const bundle = await fixture();
  bundle.manifestBytes = new Uint8Array(MAX_MANIFEST_BYTES + 1);
  await refusal(bundle, 'invalid-bundle');
});
test('bounds the payload before invoking cryptography', async () => {
  const bundle = await fixture();
  bundle.payloadBytes = new Uint8Array(MAX_PAYLOAD_BYTES + 1);
  await refusal(bundle, 'invalid-bundle');
});
test('rejects truncated signatures', async () => {
  const bundle = await fixture();
  bundle.signature = bundle.signature.slice(1);
  await refusal(bundle, 'invalid-bundle');
});
test('requires trusted version state', async () => {
  await refusal(await fixture(), 'invalid-trust-context', { installedVersion: undefined });
});
test('fails closed if cryptography is unavailable', async () => {
  assert.deepEqual(await check(await fixture(), {}, {}), {
    accepted: false,
    reason: 'verification-unavailable',
  });
});
test('fails closed if the crypto provider throws', async () => {
  assert.deepEqual(
    await check(
      await fixture(),
      {},
      {
        subtle: {
          verify() {
            throw new Error('provider failed');
          },
        },
      },
    ),
    { accepted: false, reason: 'verification-error' },
  );
});
test('returns the verified snapshot even if input changes during verification', async () => {
  const bundle = await fixture();
  const mutableContext = { ...context };
  const pending = verifyUpdateBundle(bundle, mutableContext, webcrypto);
  bundle.payloadBytes.fill(0);
  bundle.manifestBytes.fill(0);
  bundle.signature.fill(0);
  mutableContext.device = 'attacker-changed';
  const result = await pending;
  assert.equal(result.accepted, true);
  assert.deepEqual(result.payloadBytes, payload);
});
