// shots/s008.js — QC: loudness meter fills, lands on −14 LUFS, SAFE ring checks on 'zones', READY badge on 'ready'.
import { E, V, S, registerShot, layer, ease, prog, wordTime, clamp, lerp, ring, seg, circle, glow, alpha, text, FONTS } from '/engine/core.js';
import * as UI from '/engine/ui2d.js';
import * as FX from '/engine/fx2d.js';
import { voidStage } from '../sets/void.js';

registerShot('s008', { draw(g, t, info) {
  const cam = { z: 1.04 + 0.04 * ease.inOut(t / info.dur), y: -8 + 12 * ease.inOut(t / info.dur) };
  voidStage(g, t, cam, { grid: true, mood: 'void', fog: true });
  const bp = S().ui.blueprint, cream = S().ui.cream, gold = S().ui.gold;
  const g0 = info.shot.start;

  // loudness meter fills during the spoken beat (ticks light left → right over ~1.15 s)
  const mx = V(E.W * 0.15, 100), my = E.H * V(0.44, 0.42), mw = E.W - 2 * V(E.W * 0.15 + 40, 120);
  const tL = (wordTime('loudness', g0) ?? g0 + 0.35) - g0;
  const targetZone = [0.52, 0.78];
  const zx0 = mx + 20 + (mw - 40) * targetZone[0], zx1 = mx + 20 + (mw - 40) * targetZone[1];
  seg(g, [[zx0, my - V(40, 38)], [zx0, my + V(40, 38)]], 3, alpha(bp, 0.5));
  seg(g, [[zx1, my - V(40, 38)], [zx1, my + V(40, 38)]], 3, alpha(bp, 0.5));
  text(g, 'SAFE ZONES', (zx0 + zx1) / 2, my - V(64, 60), { size: V(26, 26), color: alpha(cream, 0.75), font: FONTS.ui, weight: 900, spacing: 3 });
  UI.meter(g, t, { x: mx, y: my, w: mw, ticks: 40, label: 'LOUDNESS', color: gold, start: tL, speed: 1 / 1.15 });

  // the readout lands exactly when the fill completes
  const tV = tL + 1.15;
  const pV = ease.out(prog(t, tV, tV + 0.3));
  const ry = my + V(150, 140);
  if (pV > 0) {
    UI.readout(g, { label: 'INTEGRATED', value: '-14 LUFS', x: E.W / 2, y: ry, align: 'center', a: pV });
    glow(g, mx + 20 + (mw - 40), my, V(52, 48), gold, 0.65 * pV);
  }

  // SAFE ring with a check, right of the readout, on the word 'zones'
  const tZ = (wordTime('zones', g0) ?? g0 + 1.9) - g0;
  const pZ = ease.out(prog(t, tZ, tZ + 0.45));
  if (pZ > 0) {
    const zr = V(58, 54), zc = [E.W / 2 + V(340, 300), ry];
    g.save(); g.translate(zc[0], zc[1]); g.scale(clamp(0.6 + 0.4 * pZ * 1.4), clamp(0.6 + 0.4 * pZ * 1.4));
    ring(g, 0, 0, zr, 4.5, alpha(gold, 0.95 * pZ));
    seg(g, [[-zr * 0.42, 0], [-zr * 0.1, zr * 0.32], [zr * 0.5, -zr * 0.36]], 6, alpha(gold, pZ));
    g.restore();
    text(g, 'PASS', zc[0], zc[1] + zr + V(30, 28), { size: V(26, 26), color: cream, font: FONTS.ui, weight: 900, alpha: pZ, spacing: 3 });
  }

  // READY badge on the word 'ready'
  const tR = (wordTime('ready', g0) ?? g0 + 3.0) - g0;
  UI.badge(g, { str: 'READY', a: ease.out(prog(t, tR + 0.05, tR + 0.4)) });

  FX.dust(g, t, { count: 16, color: '#cfd6ff', a: 0.24 });
} });
