// hold_<id>.js — generated placeholder covering a Remotion-owned time range.
// The player must cover every frame; Remotion overlays this segment, but semi
// transparent transitions can briefly reveal the picture underneath, hence a
// plain brand-dark hold instead of MISSING frames.
import { E, registerShot } from '/engine/core.js';

registerShot('hold_seg2', {
  draw(g, t, info) {
    g.fillStyle = '#0b0e1a'; g.fillRect(0, 0, E.W, E.H);
    g.fillStyle = 'rgba(255,255,255,0.03)';
    const r = E.W * 0.02;
    g.beginPath();
    g.arc((0.5 + 0.02 * Math.sin(t * 0.5)) * E.W, E.H * 0.5, r, 0, 7);
    g.fill();
  },
});
