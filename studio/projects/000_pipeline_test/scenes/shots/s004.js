// shots/s004.js — VOICE: giant close-up of the HERO mid-line; sound rings pop on 'voice' / 'now'.
import { E, V, registerShot, layer, blurLayer, ease, wordTime, clamp, circle, ring, linGrad, glow, alpha, shade, talkAmount, mood } from '/engine/core.js';
import { bigFace } from '/engine/rig2d.js';
import * as FX from '/engine/fx2d.js';
import { HERO } from '../cast.js';

registerShot('s004', { draw(g, t, info) {
  const cam = { z: 1.06 + 0.05 * ease.inOut(t / info.dur), y: 8 * Math.sin(t * 0.5) };
  const g0 = info.shot.start;
  const M = mood('interiorWarm');

  // low-key backdrop + one warm spot high behind the head
  layer(g, cam, 0.2, (g) => {
    g.fillStyle = linGrad(g, 0, 0, 0, E.H, [shade(M.dark, 0.35), M.dark]);
    g.fillRect(-E.W, -E.H, E.W * 3, E.H * 3);
    glow(g, E.W * 0.6, E.H * 0.32, E.H * 0.5, M.key, 0.14);
    FX.lensStreak(g, E.W / 2, E.H * V(0.2, 0.18), E.W * 0.8, M.key, 0.1, 2);
  });
  // defocused bokeh of the window world behind
  blurLayer(g, 12, (g) => {
    ring(g, E.W * V(0.15, 0.16), E.H * V(0.3, 0.26), V(64, 80), V(14, 16), 'rgba(255,205,140,.3)');
    ring(g, E.W * V(0.86, 0.88), E.H * V(0.24, 0.22), V(104, 110), V(20, 22), 'rgba(255,205,140,.22)');
    circle(g, E.W * V(0.78, 0.8), E.H * V(0.33, 0.3), V(40, 46), 'rgba(255,220,170,.12)');
  }, cam, 1.25);

  // the face — key light sits high right of frame, so the rim crescent reads on the right edge (rimSide -1)
  const r = E.H * V(0.37, 0.29);
  const cx = E.W / 2 + V(30, -20) + 16 * Math.sin(t * 0.4);
  const cy = E.H * V(0.47, 0.46) + 10 * Math.cos(t * 0.33);
  layer(g, cam, 1, (g) => {
    glow(g, cx, cy + r * 0.2, r * 1.9, M.practical, 0.1);
    bigFace(g, cx, cy, r, {
      outfit: HERO, expr: 'smile',
      talk: talkAmount(g0 + t), blink: (t % 3.3) > 3.16, look: [0.05, -0.04],
      rimColor: M.rim, rimSide: 1, tilt: -0.05 + 0.03 * Math.sin(t * 0.8),
    });
  });

  // sound rings out of the mouth on 'voice' and again on 'now'
  const tVoice = (wordTime('voice', g0) ?? g0 + 1.5) - g0;
  const tNow = (wordTime('now', g0) ?? g0 + 3.6) - g0;
  const ringsOut = (tB) => {
    if (t < tB) return;
    layer(g, cam, 1, (g) => {
      const x = cx + r * 0.05, y = cy + r * 0.42;
      for (let k = 0; k < 3; k++) {
        const ph = (t - tB - k * 0.26) / 1.15;
        if (ph <= 0 || ph >= 1) continue;
        ring(g, x, y, r * (0.34 + 0.85 * ph), 2.5 + 2.5 * (1 - ph), alpha(M.key, 0.45 * (1 - ph)));
      }
    });
  };
  ringsOut(tVoice); ringsOut(tNow);

  FX.dust(g, t, { count: 20, color: '#ffd9b0', a: 0.28, speed: 10 });
} });
