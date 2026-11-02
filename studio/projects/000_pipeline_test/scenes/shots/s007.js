// shots/s007.js — EDIT LAYER: the EDITOR builds captions on the monitor; HERO watches over the shoulder (blurred).
import { E, V, S, registerShot, layer, blurLayer, ease, prog, wordTime, lerp, seg, circle, glow, alpha, shade, text, measure, FONTS, talkAmount } from '/engine/core.js';
import { drawFigure, POSES, posesAt, breathe } from '/engine/rig2d.js';
import * as FX from '/engine/fx2d.js';
import * as UI from '/engine/ui2d.js';
import { factory } from '../sets/factory.js';
import { HERO, EDITOR } from '../cast.js';

registerShot('s007', { draw(g, t, info) {
  const cam = { z: 1.04 + 0.05 * ease.inOut(t / info.dur), x: 10 + 16 * ease.inOut(t / info.dur) };
  const { GY, CX, M } = factory(g, t, cam, {});
  const ui = S().ui;
  const g0 = info.shot.start;

  // desk for the console (right of the machine, under the window)
  const dx = CX + V(150, 190), dw = V(740, 660), dh = V(430, 380);
  layer(g, cam, 0.9, (g) => {
    FX.counter(g, { x: dx - dw / 2, y: GY - 40, w: dw, h: 120, color: M.wall, top: shade(M.wall, 0.2), doors: 3 });
  });

  // monitor with the caption assembly: three caption groups build in as the line is spoken
  const sw = V(430, 380), sh = V(260, 232), sx = dx - sw / 2, sy = GY - 40 - dh + 30;
  const tF = (wordTime('final', g0) ?? g0 + 2.6) - g0;
  layer(g, cam, 1, (g) => {
    FX.screen(g, { x: sx, y: sy, w: sw, h: sh, glowC: M.practical, a: 0.3 }, (g, px, py, pw, ph) => {
      const groups = [['THE', 'EDITING', 'ENGINE'], ['ADDS', 'CAPTIONS', 'OVERLAYS'], ['AND', 'THE', 'FINAL', 'MIX']];
      const size = V(32, 25), rh = V(64, 54);
      groups.forEach((row, k) => {
        const a = ease.out(prog(t, (k + 1) * 0.55, (k + 1) * 0.55 + 0.35));
        if (a <= 0) return;
        const hi = k === groups.length - 1 && t > tF;
        const ws = row.map(s => ({ s, w: measure(g, s, size, FONTS.ui, 900) }));
        const total = ws.reduce((x, o) => x + o.w, 0) + size * 0.4 * (row.length - 1);
        let x = px + pw / 2 - total / 2;
        ws.forEach(({ s, w }) => {
          text(g, s, x + w / 2, py + rh * 0.9 + k * rh, { size, color: hi ? ui.gold : ui.cream, font: FONTS.ui, weight: 900, alpha: a, align: 'center' });
          x += w + size * 0.4;
        });
      });
      // scrub bar + playhead cycling in the monitor
      seg(g, [[px + 18, py + ph - 16], [px + pw - 18, py + ph - 16]], 3, alpha(ui.blueprint, 0.5));
      const phd = (t * 0.35) % 1;
      circle(g, lerp(px + 18, px + pw - 18, phd), py + ph - 16, 5, alpha(ui.gold, 0.9));
    });
  });

  // the EDITOR speaks the line into existance
  layer(g, cam, 1, (g) => {
    drawFigure(g, {
      x: dx + V(310, 270), y: GY, s: V(1.42, 1.3), facing: -1, outfit: EDITOR,
      pose: breathe(posesAt(t, [[0, POSES.talk], [1.15, POSES.explain], [2.6, POSES.point]]), t),
      expr: 'neutral', talk: talkAmount(g0 + t) * 0.8, blink: (t % 3.7) > 3.54,
      rim: { color: M.practical, dir: [-0.5, -0.4] },
    });
    FX.pool(g, sx + sw / 2, GY + 10, V(360, 330), V(46, 42), M.practical, 0.18);
  });

  // HERO over the shoulder: big blurred foreground silhouette on the left edge
  blurLayer(g, 8, (g) => {
    drawFigure(g, { x: CX - V(560, 430), y: E.H * V(1.16, 1.1), s: V(3.0, 2.6), facing: 1, outfit: HERO, pose: POSES.stand, alpha: 0.5, dim: true, shadow: false, rim: false });
  }, cam, 1.4);

  const tF2 = (wordTime('final', g0) ?? g0 + 2.6) - g0;
  UI.badge(g, { str: 'MIX', a: ease.out(prog(t, tF2 + 0.05, tF2 + 0.4)) });
  FX.dust(g, t, { count: 22 });
} });
