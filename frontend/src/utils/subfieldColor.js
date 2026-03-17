// Deterministic subfield → color mapping using string hash
const PALETTE = [
  [99, 102, 241],   // indigo
  [139, 92, 246],   // violet
  [14, 165, 233],   // sky
  [20, 184, 166],   // teal
  [16, 185, 129],   // emerald
  [245, 158, 11],   // amber
  [244, 63, 94],    // rose
  [249, 115, 22],   // orange
  [236, 72, 153],   // pink
  [6, 182, 212],    // cyan
  [132, 204, 22],   // lime
  [168, 85, 247],   // fuchsia
]

function hash(str) {
  let h = 0
  for (let i = 0; i < str.length; i++) {
    h = (Math.imul(31, h) + str.charCodeAt(i)) | 0
  }
  return Math.abs(h)
}

/** Returns { color, bg } CSS color strings for a given subfield label. */
export function subfieldStyle(subfield) {
  if (!subfield) return { color: 'rgb(148,163,184)', bg: 'rgba(148,163,184,0.15)' }
  const [r, g, b] = PALETTE[hash(subfield) % PALETTE.length]
  return { color: `rgb(${r},${g},${b})`, bg: `rgba(${r},${g},${b},0.13)` }
}
