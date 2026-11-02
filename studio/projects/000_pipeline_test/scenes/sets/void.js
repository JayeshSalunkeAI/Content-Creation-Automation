// sets/void.js — blueprint/diagram stage: dark vertical gradient + optional blueprint grid.
import { E, V, mood, layer, linGrad, shade, alpha } from '/engine/core.js';
import * as UI from '/engine/ui2d.js';

// o.grid (default true) turns on the blueprint grid + returns its stroke colour.
// o.fog adds faint drifting fog bands so frames are never flat.
export function voidStage(g, t, cam, o = {}) {
  const M = mood(o.mood || 'void');
  layer(g, cam, 0.2, (g) => {
    g.fillStyle = linGrad(g, 0, -E.H, 0, E.H * 1.2, [M.dark, shade(M.wall, 0.15)]);
    g.fillRect(-E.W, -E.H, E.W * 3, E.H * 3);
  });
  let grid = null;
  if (o.grid !== false) {
    layer(g, cam, 0.25, (g) => {
      g.globalAlpha = 0.55;
      UI.blueprint(g);
      g.globalAlpha = 1;
      grid = UI.bpStroke();
    });
  }
  if (o.fog) {
    layer(g, cam, 0.3, (g) => {
      const y = E.H * 0.42 + Math.sin(t * 0.24) * E.H * 0.05;
      g.fillStyle = alpha(M.fog, 0.05);
      g.fillRect(-E.W, y, E.W * 3, E.H * 0.3);
    });
  }
  return { M, grid, CX: E.W / 2, CY: E.H / 2 };
}
