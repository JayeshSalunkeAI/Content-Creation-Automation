// shots/s009.js — END: rooftop at dusk; the two builders and the machine at the railing; slow pull-out; end card dims in (Remotion).
import { E, V, registerShot, layer, blurLayer, ease, prog, clamp, lerp, rr, alpha, veil } from '/engine/core.js';
import { drawFigure, POSES, breathe } from '/engine/rig2d.js';
import * as FX from '/engine/fx2d.js';
import { rooftop, machine } from '../sets/factory.js';
import { HERO, EDITOR } from '../cast.js';

registerShot('s009', { draw(g, t, info) {
  const Q = ease.inOut(prog(t, 0, info.dur));
  const cam = { z: lerp(1.22, 1.02, Q), y: -26 * Q, r: 0.004 * Math.sin(t * 0.4) };
  const { GY, CX, M } = rooftop(g, t, cam, {});

  layer(g, cam, 1, (g) => {
    // the MACHINE with them — the factory watching its own sunset
    machine(g, t, CX + V(430, 380), GY - 6, V(0.78, 0.62), M, {});
    // the two builders
    drawFigure(g, { x: CX - V(330, 290), y: GY, s: V(1.5, 1.25), facing: 1, outfit: HERO, pose: breathe(POSES.relaxed, t, 1, 2), expr: 'smile', rim: { color: M.rim, dir: [0.55, -0.45] }, blink: (t % 3.5) > 3.38 });
    drawFigure(g, { x: CX + V(60, 50), y: GY, s: V(1.42, 1.2), facing: 1, outfit: EDITOR, pose: breathe(POSES.crossArms, t, 1, 5), expr: 'smirk', rim: { color: M.rim, dir: [0.55, -0.45] }, blink: (t % 4.1) > 3.95 });
    FX.pool(g, CX, GY + 10, V(640, 560), V(52, 46), M.key, 0.16);
  });

  // rooftop edge + parapet as blurred foreground slabs (depth)
  blurLayer(g, 10, (g) => {
    g.fillStyle = 'rgba(150,90,80,.28)';
    rr(g, -140, E.H * V(0.62, 0.58), 240, E.H * V(0.5, 0.5), 40); g.fill();
    rr(g, E.W - 120, E.H * V(0.58, 0.54), 260, E.H * V(0.55, 0.55), 40); g.fill();
    g.fillStyle = 'rgba(20,10,30,.5)';
    g.fillRect(-E.W, E.H * V(0.92, 0.88), E.W * 3, E.H);
  }, cam, 1.6);

  // the end card (Remotion) fades in over the last act — give it a quiet darkening to sit on
  const dim = prog(t, info.dur - 1.5, info.dur - 0.2);
  if (dim > 0) veil(g, '#05070f', 0.34 * dim);

  FX.dust(g, t, { count: 24, color: '#ffd9b0', a: 0.3, speed: 11 });
} });
