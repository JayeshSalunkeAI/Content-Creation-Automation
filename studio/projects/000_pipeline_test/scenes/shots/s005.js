// shots/s005.js — STORYBOARD: master timeline blueprint; nine shot cells pop in, the Remotion seg2 cell is dashed gold.
import { E, V, S, registerShot, layer, ease, prog, wordTime, clamp, lerp, rr, seg, circle, glow, alpha, text, FONTS } from '/engine/core.js';
import * as UI from '/engine/ui2d.js';
import * as FX from '/engine/fx2d.js';
import { voidStage } from '../sets/void.js';

registerShot('s005', { draw(g, t, info) {
  const cam = { z: 1.05 + 0.04 * ease.inOut(t / info.dur), x: 18 * Math.sin(t * 0.5) };
  const st = voidStage(g, t, cam, { grid: true, mood: 'void', fog: true });
  const bp = st.grid || UI.bpStroke();
  const ui = S().ui;
  const g0 = info.shot.start;

  // spine
  const x0 = E.W * V(0.09, 0.1), x1 = E.W * V(0.91, 0.9);
  const yS = E.H * V(0.5, 0.46);
  const cells = ['s001', 's002', 's003', 's004', 's005', 'seg2', 's007', 's008', 's009'];
  const gap = (x1 - x0) / cells.length;
  const tT = (wordTime('timeline', g0) ?? g0 + 2.2) - g0;

  const pSpine = ease.out(prog(t, 0.15, 0.8));
  layer(g, cam, 1, (g) => {
    seg(g, [[x0, yS], [lerp(x0, x1, pSpine), yS]], 4, alpha(bp, 0.9));
    circle(g, x0, yS, 7, bp); circle(g, lerp(x0, x1, pSpine), yS, 7, bp);

    // cells pop one by one from the word 'storyboard'
    const tS = (wordTime('storyboard', g0) ?? g0 + 0.75) - g0;
    const cw = gap * 0.62, chh = V(150, 118);
    cells.forEach((id, i) => {
      const pC = prog(t, tS + i * 0.32 + 0.15, tS + i * 0.32 + 0.55);
      if (pC <= 0) return;
      const a = ease.outBack(pC);
      const cx2 = x0 + gap * (i + 0.5);
      const rem = id === 'seg2';
      const col = rem ? ui.gold : bp;
      g.save(); g.translate(cx2, yS); const sc = clamp(0.4 + 0.6 * a); g.scale(sc, sc);
      rr(g, -cw / 2, -chh / 2, cw, chh, 14);
      g.fillStyle = alpha(col, rem ? 0.14 : 0.07); g.fill();
      if (rem) g.setLineDash([10, 8]);
      g.strokeStyle = alpha(col, rem ? 0.95 : 0.8); g.lineWidth = rem ? 3.5 : 2.5;
      rr(g, -cw / 2, -chh / 2, cw, chh, 14); g.stroke();
      g.setLineDash([]);
      text(g, String(i + 1), 0, -chh * 0.16, { size: V(38, 32), color: rem ? ui.gold : ui.cream, font: FONTS.ui, weight: 900, glow: rem ? 12 : 0, glowColor: alpha(ui.gold, 0.6) });
      seg(g, [[-cw * 0.26, chh * 0.24], [cw * 0.26, chh * 0.24]], 4, alpha(col, 0.55));
      g.restore();
    });

    // a pulse sweeps the whole spine once the narration says "timeline"
    const pRun = prog(t, tT, tT + 1.2);
    if (pRun > 0 && pRun < 1) {
      const px = lerp(x0, x1, pRun);
      glow(g, px, yS, V(60, 55), ui.gold, 0.7);
      circle(g, px, yS, 8, alpha(ui.gold, 0.95));
    }
  });

  const aT = ease.out(prog(t, 0.3, 0.75));
  if (aT > 0) text(g, 'MASTER TIMELINE', E.W / 2, E.H * V(0.22, 0.26), { size: V(52, 54), color: ui.cream, font: FONTS.ui, weight: 900, spacing: 6, glow: 18, glowColor: alpha(bp, 0.7), alpha: aT });
  const aR = ease.out(prog(t, tT + 1.1, tT + 1.6));
  if (aR > 0) UI.readout(g, { label: 'DURATION', value: '39.13 s', x: E.W - V(150, 120), y: E.H * V(0.78, 0.8), align: 'right', a: aR });

  FX.dust(g, t, { count: 16, color: '#cfd6ff', a: 0.25 });
} });
