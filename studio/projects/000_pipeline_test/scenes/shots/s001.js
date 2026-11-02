// shots/s001.js — HOOK: the machine runs on its own, hero walks in, title card pops.
import { E, V, S, registerShot, layer, blurLayer, ease, wordTime, clamp, lerp, rr, alpha, text, FONTS } from '/engine/core.js';
import { drawFigure, POSES, breathe, walkPose } from '/engine/rig2d.js';
import * as FX from '/engine/fx2d.js';
import { factory } from '../sets/factory.js';
import { HERO } from '../cast.js';

const TF = FONTS.title || FONTS.ui;

registerShot('s001', { draw(g, t, info) {
  const cam = { z: 1.05 + 0.05 * ease.inOut(t / info.dur), y: -14 * t };
  const { GY, CX, M } = factory(g, t, cam, {});

  const g0 = info.shot.start;
  const arrive = clamp(t / 1.8);
  const hx = CX + lerp(V(470, 420), V(10, -10), ease.out(arrive));
  const walking = arrive < 0.999;
  layer(g, cam, 1, (g) => {
    drawFigure(g, {
      x: hx, y: GY, s: V(1.5, 1.45), facing: -1, outfit: HERO,
      pose: walking ? walkPose(t * 2 * Math.PI * 0.9) : breathe(POSES.stand, t, 1, 7),
      expr: walking ? 'neutral' : 'thinking',
      blink: (t % 3.1) > 3.0, rim: { color: M.rim, dir: [0.4, -1] },
    });
  });

  // soft foreground slabs (depth cue)
  blurLayer(g, 11, (g) => {
    g.fillStyle = 'rgba(200,150,120,.45)';
    rr(g, -50, E.H * V(0.6, 0.54), 150, E.H * V(0.55, 0.6), 30); g.fill();
    g.fillStyle = 'rgba(90,110,180,.4)';
    rr(g, E.W - 110, E.H * V(0.55, 0.48), 160, E.H * V(0.62, 0.68), 30); g.fill();
  }, cam, 1.7);

  // title card pops on the word "built"
  const tIn = clamp(((wordTime('built', g0) ?? g0 + 0.5) - g0) / 0.35);
  const scale = 0.7 + 0.3 * ease.outBack(tIn);
  const yCard = E.H * V(0.28, 0.3);
  const lines = ['THIS VIDEO', 'BUILT ITSELF'];
  for (let i = 0; i < lines.length; i++) {
    g.save();
    g.translate(E.W / 2, yCard + i * V(112, 122));
    g.scale(scale, scale);
    g.globalAlpha = clamp(tIn * 1.3);
    text(g, lines[i], 0, 0, { size: V(96, 100), color: S().feature, font: TF, weight: 900, align: 'center', spacing: 4, glow: 20, glowColor: alpha(M.key, 0.5) });
    g.restore();
  }
  g.globalAlpha = 1;
  FX.dust(g, t, { count: 34 });
} });
