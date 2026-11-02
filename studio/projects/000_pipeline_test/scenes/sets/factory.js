// sets/factory.js — THE MACHINE: recurring set-piece character.
// factory(): machine room interior (interiorWarm dusk outside, warm practicals)
// rooftop(): dusk exterior wide for the end beat
import { E, V, mood, layer, blurLayer, backdrop, rr, seg, circle, ring, linGrad, glow, alpha, shade } from '/engine/core.js';
import * as FX from '/engine/fx2d.js';

export const factoryGround = () => E.H * V(0.8, 0.68);

// the MACHINE — flat vector silhouette with a live screen, blinking indicator, paper feed
export function machine(g, t, x, y, s, M, o = {}) {
  g.save();
  g.translate(x, y);
  g.scale(s, s);
  const bodyW = 460, bodyH = 380;
  // feed drawer at the bottom: a sheet slides out on a slow loop
  const feed = (t * 0.28) % 1;
  const sheetY = -26 - 46 * (feed < 0.75 ? ease(feed / 0.75) : 1 - ease((feed - 0.75) / 0.25) * 0.15);
  g.fillStyle = shade(M.floor, -0.35);
  rr(g, -70, -96, 140, 96, 12); g.fill();
  g.fillStyle = shade(M.practical, 0.06);
  rr(g, -48, sheetY, 96, 60, 6); g.fill();
  // body
  g.fillStyle = shade(M.wall, -0.5);
  rr(g, -bodyW / 2, -bodyH - 90, bodyW, bodyH, 26); g.fill();
  g.fillStyle = shade(M.wall, -0.28);
  rr(g, -bodyW / 2, -bodyH - 90, bodyW, 34, 16); g.fill();       // top face
  // screen: two running waveforms
  const sx = -bodyW / 2 + 54, sy = -bodyH + 6, sw = bodyW - 108, sh = 168;
  FX.screen(g, { x: sx, y: sy, w: sw, h: sh, glowC: M.practical, a: 0.26 }, (g, px, py, pw, ph) => {
    g.strokeStyle = shade(M.practical, 0.1); g.lineWidth = 3;
    for (const row of [0.38, 0.7]) {
      g.beginPath();
      for (let i = 0; i <= 24; i++) {
        const fx = px + 10 + (i / 24) * (pw - 20);
        const fy = py + ph * row + Math.sin(i * 0.9 + t * (row < 0.5 ? 5 : 3.2)) * 10;
        if (i === 0) g.moveTo(fx, fy); else g.lineTo(fx, fy);
      }
      g.stroke();
    }
  });
  // blinking indicator + rim-ward edge highlight
  const on = (t % 1.4) < 0.85;
  ring(g, bodyW / 2 - 46, -bodyH - 44, 11, 4, on ? alpha(M.practical, 0.95) : alpha(M.practical, 0.25));
  if (on) glow(g, bodyW / 2 - 46, -bodyH - 44, 34, M.practical, 0.5);
  // mast + vents
  seg(g, [[0, -bodyH - 90], [0, -bodyH - 250]], 16, shade(M.wall, -0.5));
  for (const dy of [80, 130, 180]) seg(g, [[-bodyW / 2 + 40, -180 + dy], [bodyW / 2 - 40, -180 + dy]], 6, alpha(M.dark, 0.75));
  g.strokeStyle = shade(M.wall, -0.62); g.lineWidth = 4;
  g.beginPath(); g.moveTo(-bodyW / 2, -bodyH - 84); g.lineTo(-bodyW / 2, -100); g.stroke();
  g.restore();
}

const ease = (x) => x - (1 - x) * 0.35; // tiny local settle for the feed sheet (deterministic)

// machine room: warm dusk, tall window with skyline, machine at depth 0.85
export function factory(g, t, cam, o = {}) {
  const M = mood(o.mood || 'interiorWarm'), GY = factoryGround(), CX = E.W / 2;
  layer(g, cam, 0.35, (g) => {
    g.fillStyle = linGrad(g, 0, -E.H, 0, GY, [M.dark, M.wall]);
    g.fillRect(-E.W, -E.H, E.W * 3, GY + E.H);
    for (const x of [-500, -40, 420, 880]) { g.fillStyle = shade(M.wall, 0.18); g.fillRect(x, GY - V(900, 1360), E.W * 0.07, 10); }
    // signature window: dusk skyline + low sun
    const wx = CX + V(150, 170), wy = GY - V(1150, 1180), ww = V(520, 520), wh = V(800, 780);
    FX.windowFrame(g, { x: wx, y: wy, w: ww, h: wh, cols: 2, frame: shade(M.wall, -0.55), bar: 12, blinds: 0 }, (g, px, py, pw, ph) => {
      g.fillStyle = linGrad(g, 0, py, 0, py + ph, M.sky);
      g.fillRect(px, py, pw, ph);
      FX.sun(g, px + pw * 0.5, py + ph * 0.78, V(52, 62), '#fff7e6', M.key, 5);
      FX.skyline(g, { x: px, y: py + ph, w: pw, maxH: ph * 0.5, color: alpha(shade(M.wall, -0.2), 0.8), windowColor: alpha(M.practical, 0.65), seed: 11 });
    });
    FX.godRays(g, wx + ww / 2, wy + wh * 0.78, { count: 12, angle: Math.PI / 2, spread: Math.PI * 0.9, len: 1500, a: 0.05, t });
  });
  layer(g, cam, 0.85, (g) => {
    machine(g, t, CX - V(210, 210), GY - 8, V(1.05, 1.0), M, o.machine || {});
    FX.pool(g, CX - V(200, 210), GY + 14, 560, 70, M.practical, 0.16);
  });
  layer(g, cam, 0.7, (g) => {
    g.fillStyle = linGrad(g, 0, GY - 20, 0, GY + 700, [shade(M.floor, 0.06), M.dark]);
    g.fillRect(-E.W, GY - 20, E.W * 3, E.H);
    FX.floorLines(g, GY - 20, GY + 700, 'rgba(0,0,0,.28)', 0.09);
  });
  return { GY, CX, M };
}

// rooftop at dusk: low skyline, big sun, railing; call with figures drawn by the shot
export function rooftop(g, t, cam, o = {}) {
  const M = mood(o.mood || 'dusk'), GY = E.H * V(0.78, 0.7), CX = E.W / 2;
  layer(g, cam, 0.15, (g) => {
    backdrop(g, M.sky);
    FX.sun(g, CX, E.H * V(0.5, 0.44), V(78, 92), '#fff3dc', M.key, 6);
    FX.godRays(g, CX, E.H * V(0.5, 0.44), { count: 15, angle: Math.PI / 2, spread: Math.PI * 1.3, len: 2100, a: 0.06, t });
  });
  layer(g, cam, 0.4, (g) => {
    FX.skyline(g, { x: -300, y: E.H * V(0.66, 0.6), w: E.W + 600, maxH: V(280, 420), color: shade(M.wall, -0.25), windowColor: alpha(M.practical, 0.8), seed: 33 });
  });
  layer(g, cam, 0.75, (g) => {
    g.fillStyle = shade(M.road, -0.4);
    g.fillRect(-E.W, E.H * V(0.66, 0.6), E.W * 3, E.H);
    // railing at ground level
    seg(g, [[-E.W, GY - 150], [E.W * 2, GY - 150]], 8, shade(M.wall, -0.5));
    for (const rx of [-400, 40, 480, 920, 1360]) seg(g, [[rx + V(0, -120), GY - 150], [rx, GY]], 7, shade(M.wall, -0.5));
    FX.pool(g, CX, GY + 6, 640, 60, M.key, 0.2);
  });
  FX.dust(g, t, { count: 26, color: '#ffd9b0', a: 0.35 });
  return { GY, CX, M };
}
