const fs = require('fs');
const zlib = require('zlib');

const buf = fs.readFileSync(process.argv[2]);
const secShift = buf.readUInt16LE(0x1e);
const secSize = 1 << secShift;
const miniShift = buf.readUInt16LE(0x20);
const miniSize = 1 << miniShift;
const numFatSectors = buf.readUInt32LE(0x2c);
const firstDir = buf.readUInt32LE(0x30);
const miniCutoff = buf.readUInt32LE(0x38);
const firstMiniFat = buf.readUInt32LE(0x3c);
const numMiniFat = buf.readUInt32LE(0x40);
const firstDifat = buf.readUInt32LE(0x44);
const numDifat = buf.readUInt32LE(0x48);

const secOff = (id) => (id + 1) * secSize;

// DIFAT
const difat = [];
for (let i = 0; i < 109; i++) {
  const v = buf.readUInt32LE(0x4c + i * 4);
  if (v === 0xffffffff) break;
  difat.push(v);
}
let ds = firstDifat;
for (let n = 0; n < numDifat && ds !== 0xffffffff && ds !== 0xfffffffe; n++) {
  const base = secOff(ds);
  for (let i = 0; i < secSize / 4 - 1; i++) {
    const v = buf.readUInt32LE(base + i * 4);
    if (v !== 0xffffffff) difat.push(v);
  }
  ds = buf.readUInt32LE(base + secSize - 4);
}

// FAT
const fat = [];
for (const s of difat.slice(0, numFatSectors || difat.length)) {
  const base = secOff(s);
  for (let i = 0; i < secSize / 4; i++) fat.push(buf.readUInt32LE(base + i * 4));
}

function chain(start) {
  const out = [];
  let s = start;
  while (s !== 0xfffffffe && s !== 0xffffffff && s < fat.length) { out.push(s); s = fat[s]; }
  return out;
}
function readChain(start, size) {
  const parts = chain(start).map((s) => buf.slice(secOff(s), secOff(s) + secSize));
  const all = Buffer.concat(parts);
  return size ? all.slice(0, size) : all;
}

// Directory entries
const dirBuf = readChain(firstDir);
const entries = [];
for (let i = 0; i + 128 <= dirBuf.length; i += 128) {
  const nameLen = dirBuf.readUInt16LE(i + 64);
  if (!nameLen) continue;
  const name = dirBuf.slice(i, i + Math.max(0, nameLen - 2)).toString('utf16le');
  entries.push({
    name,
    type: dirBuf.readUInt8(i + 66),
    start: dirBuf.readUInt32LE(i + 116),
    size: dirBuf.readUInt32LE(i + 120),
  });
}

// mini FAT + mini stream (root entry is first)
const root = entries[0];
const miniStream = root.start !== 0xffffffff ? readChain(root.start) : Buffer.alloc(0);
const miniFat = [];
{
  const mb = firstMiniFat !== 0xfffffffe && numMiniFat ? readChain(firstMiniFat) : Buffer.alloc(0);
  for (let i = 0; i + 4 <= mb.length; i += 4) miniFat.push(mb.readUInt32LE(i));
}
function readStream(e) {
  if (e.size >= miniCutoff) return readChain(e.start, e.size);
  const parts = [];
  let s = e.start;
  while (s !== 0xfffffffe && s !== 0xffffffff && s < miniFat.length) {
    parts.push(miniStream.slice(s * miniSize, (s + 1) * miniSize));
    s = miniFat[s];
  }
  return Buffer.concat(parts).slice(0, e.size);
}

if (process.env.LIST) {
  console.log(entries.map((e) => `${e.name} type=${e.type} size=${e.size}`).join('\n'));
}

const sections = entries.filter((e) => /^Section\d+$/.test(e.name)).sort((a, b) => a.name.localeCompare(b.name));
for (const sec of sections) {
  let data = readStream(sec);
  try { data = zlib.inflateRawSync(data); } catch (err) {
    try { data = zlib.inflateSync(data); } catch (e2) { /* uncompressed */ }
  }
  // walk records
  let p = 0;
  const lines = [];
  while (p + 4 <= data.length) {
    const h = data.readUInt32LE(p);
    const tag = h & 0x3ff;
    let size = (h >> 20) & 0xfff;
    p += 4;
    if (size === 0xfff) { size = data.readUInt32LE(p); p += 4; }
    if (p + size > data.length) break;
    if (tag === 67) { // PARA_TEXT
      const raw = data.slice(p, p + size);
      let s = '';
      for (let i = 0; i + 1 < raw.length; i += 2) {
        const c = raw.readUInt16LE(i);
        if (c < 32) {
          // inline/extended controls occupy 8 chars (16 bytes) for extended set
          if ([1,2,3,11,12,14,15,16,17,18,21,22,23].includes(c)) i += 14;
          if (c === 13 || c === 10) s += '\n';
          else s += ' ';
        } else s += String.fromCharCode(c);
      }
      const t = s.replace(/\s+/g, ' ').trim();
      if (t) lines.push(t);
    }
    p += size;
  }
  console.log(`===== ${sec.name} =====`);
  console.log(lines.join('\n'));
}
