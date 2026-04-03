const BASE_URL = "https://YOUR_FUNCTION_URL.lambda-url.us-east-1.on.aws/";
const LINK_SIGNING_SECRET = "REPLACE_WITH_YOUR_LINK_SIGNING_SECRET";

const notePresets = [
  "Delivery",
  "Laundry",
  "Custom",
];

const durationUnits = [
  { label: "Hours", seconds: 60 * 60 },
  { label: "Days", seconds: 24 * 60 * 60 },
  { label: "Weeks", seconds: 7 * 24 * 60 * 60 },
];

async function main() {
  const note = await chooseNote();
  if (note === null) return;

  const durationValue = await chooseDurationValue();
  if (durationValue === null) return;

  const durationUnit = await chooseDurationUnit();
  if (durationUnit === null) return;

  const ttlSeconds = durationValue * durationUnit.seconds;
  const ttlLabel = `${durationValue} ${formatUnitLabel(durationUnit.label, durationValue)}`;
  const url = await generateSignedUrl(note, ttlSeconds);

  await presentResult(url, note, ttlLabel);
}

async function chooseNote() {
  const alert = new Alert();
  alert.title = "Purpose";
  alert.message = "Choose why you are sending this door link.";

  for (const preset of notePresets) {
    alert.addAction(preset);
  }
  alert.addCancelAction("Cancel");

  const index = await alert.presentSheet();
  if (index === -1) return null;

  const selected = notePresets[index];
  if (selected !== "Custom") {
    return selected;
  }

  const custom = new Alert();
  custom.title = "Custom Purpose";
  custom.message = "Enter a short note for this link.";
  custom.addTextField("Purpose", "");
  custom.addAction("OK");
  custom.addCancelAction("Cancel");

  const result = await custom.presentAlert();
  if (result === -1) return null;

  return custom.textFieldValue(0).trim();
}

async function chooseDurationValue() {
  const alert = new Alert();
  alert.title = "Duration";
  alert.message = "Enter a whole number for how long the link should stay valid.";
  alert.addTextField("Number", "1");
  alert.addAction("Next");
  alert.addCancelAction("Cancel");

  const result = await alert.presentAlert();
  if (result === -1) return null;

  const raw = alert.textFieldValue(0).trim();

  if (!/^[1-9][0-9]*$/.test(raw)) {
    const error = new Alert();
    error.title = "Invalid Duration";
    error.message = "Please enter a whole number greater than 0.";
    error.addAction("OK");
    await error.presentAlert();
    return await chooseDurationValue();
  }

  return parseInt(raw, 10);
}

async function chooseDurationUnit() {
  const alert = new Alert();
  alert.title = "Duration Unit";
  alert.message = "Choose the time unit.";

  for (const unit of durationUnits) {
    alert.addAction(unit.label);
  }
  alert.addCancelAction("Cancel");

  const index = await alert.presentSheet();
  if (index === -1) return null;

  return durationUnits[index];
}

function formatUnitLabel(unitLabel, value) {
  const lower = unitLabel.toLowerCase();
  return value === 1 ? lower.slice(0, -1) : lower;
}

async function generateSignedUrl(note, ttlSeconds) {
  const exp = Math.floor(Date.now() / 1000) + ttlSeconds;
  const payload = `${exp}\n${note}`;
  const sig = await hmacSha256Hex(LINK_SIGNING_SECRET, payload);

  const params = [];
  params.push(`exp=${encodeURIComponent(String(exp))}`);
  params.push(`sig=${encodeURIComponent(sig)}`);
  if (note) {
    params.push(`note=${encodeURIComponent(note)}`);
  }

  return `${BASE_URL}?${params.join("&")}`;
}

async function hmacSha256Hex(secret, message) {
  const keyBytes = utf8Bytes(secret);
  const messageBytes = utf8Bytes(message);
  const digestBytes = hmacSha256Bytes(keyBytes, messageBytes);
  return bytesToHex(digestBytes);
}

function utf8Bytes(str) {
  return Array.from(Data.fromString(str).getBytes());
}

function bytesToHex(bytes) {
  return bytes.map((b) => (b & 255).toString(16).padStart(2, "0")).join("");
}

function hmacSha256Bytes(keyBytes, messageBytes) {
  const blockSize = 64;
  let key = keyBytes.slice();

  if (key.length > blockSize) {
    key = sha256Bytes(key);
  }

  while (key.length < blockSize) {
    key.push(0);
  }

  const oKeyPad = [];
  const iKeyPad = [];
  for (let i = 0; i < blockSize; i++) {
    oKeyPad.push(key[i] ^ 0x5c);
    iKeyPad.push(key[i] ^ 0x36);
  }

  const innerHash = sha256Bytes(iKeyPad.concat(messageBytes));
  return sha256Bytes(oKeyPad.concat(innerHash));
}

function sha256Bytes(messageBytes) {
  const k = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
    0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
    0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
    0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
    0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
    0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
  ];

  const h = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
  ];

  const bytes = messageBytes.slice();
  const bitLength = bytes.length * 8;

  bytes.push(0x80);
  while ((bytes.length % 64) !== 56) {
    bytes.push(0);
  }

  const highBits = Math.floor(bitLength / 0x100000000);
  const lowBits = bitLength >>> 0;

  bytes.push((highBits >>> 24) & 255);
  bytes.push((highBits >>> 16) & 255);
  bytes.push((highBits >>> 8) & 255);
  bytes.push(highBits & 255);
  bytes.push((lowBits >>> 24) & 255);
  bytes.push((lowBits >>> 16) & 255);
  bytes.push((lowBits >>> 8) & 255);
  bytes.push(lowBits & 255);

  const w = new Array(64);

  for (let offset = 0; offset < bytes.length; offset += 64) {
    for (let i = 0; i < 16; i++) {
      const j = offset + i * 4;
      w[i] = (
        ((bytes[j] << 24) | (bytes[j + 1] << 16) | (bytes[j + 2] << 8) | bytes[j + 3])
      ) >>> 0;
    }

    for (let i = 16; i < 64; i++) {
      const s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >>> 3);
      const s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >>> 10);
      w[i] = add32(w[i - 16], s0, w[i - 7], s1);
    }

    let a = h[0];
    let b = h[1];
    let c = h[2];
    let d = h[3];
    let e = h[4];
    let f = h[5];
    let g = h[6];
    let hh = h[7];

    for (let i = 0; i < 64; i++) {
      const s1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25);
      const ch = (e & f) ^ (~e & g);
      const temp1 = add32(hh, s1, ch, k[i], w[i]);
      const s0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22);
      const maj = (a & b) ^ (a & c) ^ (b & c);
      const temp2 = add32(s0, maj);

      hh = g;
      g = f;
      f = e;
      e = add32(d, temp1);
      d = c;
      c = b;
      b = a;
      a = add32(temp1, temp2);
    }

    h[0] = add32(h[0], a);
    h[1] = add32(h[1], b);
    h[2] = add32(h[2], c);
    h[3] = add32(h[3], d);
    h[4] = add32(h[4], e);
    h[5] = add32(h[5], f);
    h[6] = add32(h[6], g);
    h[7] = add32(h[7], hh);
  }

  const out = [];
  for (const word of h) {
    out.push((word >>> 24) & 255);
    out.push((word >>> 16) & 255);
    out.push((word >>> 8) & 255);
    out.push(word & 255);
  }

  return out;
}

function rotr(value, amount) {
  return (value >>> amount) | (value << (32 - amount));
}

function add32() {
  let result = 0;
  for (let i = 0; i < arguments.length; i++) {
    result = (result + arguments[i]) >>> 0;
  }
  return result;
}

async function presentResult(url, note, ttlLabel) {
  Pasteboard.copyString(url);

  const alert = new Alert();
  alert.title = "Link Ready";
  alert.message =
    `Purpose: ${note || "None"}\n` +
    `Expires in: ${ttlLabel}\n\n` +
    `The link has been copied to your clipboard.`;

  alert.addAction("Share");
  alert.addAction("Copy Again");
  alert.addCancelAction("Done");

  const choice = await alert.presentAlert();

  if (choice === 0) {
    const share = new ShareSheet();
    share.addItem(url);
    await share.present();
  } else if (choice === 1) {
    Pasteboard.copyString(url);
  }
}

await main();
