// shots/s002.js — RESEARCH: hero skims the paper stack by the window, SOURCES badge.
import { E, V, S, registerShot, layer, ease, prog, wordTime, clamp, rr, seg, circle, alpha, shade } from '/engine/core.js';
import { drawFigure, POSES, posesAt, breathe } from '/engine/rig2d.js';
import * as FX from '/engine/fx2d.js';
import * as UI from '/engine/ui2d.js';
import { factory } from '../sets/factory.js';
import { factoryGround } from '../sets/factory.js';
import { HERO } from '../cast.js';

registerShot('s002', { draw(g, t, info) {
  const cam = { z: 1.02 + 0.05 * ease.inOut(t / info.dur), x: -24 + 20 * ease.inOut(t / info.dur) };
  const { GY, CX, M } = factory(g, t, cam, {});
  const g0 = info.shot.start;

  layer(g, cam, 0.9, (g) => {
    // reading bench in front of the hero
    FX.counter(g, { x: CX - V(400, 380), y: GY - 46, w: V(860, 820), h: 110, color: shade(M.wall, -0.45), top: shade(M.wall, -0.2), doors: 4 });
  });

  layer(g, cam, 1, (g) => {
    drawFigure(g, {
      x: CX - V(60, 70), y: GY, s: V(1.45, 1.4), facing: 1, outfit: HERO,
      pose: breathe(posesAt(t, [[0, POSES.holdFront], [(wordTime('agent', g0) ?? g0 + 2.4) - g0, POSES.explain]]), t),
      expr: 'thinking', blink: (t % 2.9) > 2.8,
      prop: { type: 'paper' }, rim: { color: M.rim, dir: [1, -1] },
    });
  });

  // two floating paper icons pop on "research"/"sources"
  const tR = (wordTime('research', g0) ?? g0 + 0.4) - g0;
  const tS = (wordTime('sources', g0) ?? g0 + 1.2) - g0;
  const sheet = (tt, y, rot) => {
    if (tt <= 0) return;
    const a = ease.out(clamp(tt / 0.4));
    g.save();
    g.translate(CX + V(210, 235), y);
    g.rotate(rot + 0.04 * Math.sin(t)); // gentle live drift — never static
    g.globalAlpha = a;
    rr(g, -52, -70, 104, 140, 10); g.fillStyle = shade(S().feature, 0.05); g.fill();
    for (let k = 0; k < 4; k++) seg(g, [[-34, -46 + k * 26], [30, -46 + k * 26]], 5, alpha(M.dark, 0.4));
    g.globalAlpha = 1;
    g.restore();
  };
  sheet(t - tR, E.H * V(0.3, 0.3), 0.12);
  sheet(t - tS, E.H * V(0.42, 0.4), -0.1);

  UI.badge(g, { str: 'SOURCES', a: ease.out(prog(t, tS + 0.1, tS + 0.5)), size: V(44, 48) });
  FX.dust(g, t, { count: 26 });
} });
