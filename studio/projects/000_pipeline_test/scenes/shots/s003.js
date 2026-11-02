// shots/s003.js — SCRIPT insert: cream page macro, lines type in on "Short, punchy", cursor settles on "word", TIMED badge.
import { E, V, S, registerShot, layer, blurLayer, ease, prog, wordTime, clamp, rr, seg, alpha, mood } from '/engine/core.js';
import * as FX from '/engine/fx2d.js';
import * as UI from '/engine/ui2d.js';
import { voidStage } from '../sets/void.js';

registerShot('s003', { draw(g, t, info) {
  const cam = { z: 1.03 + 0.04 * ease.inOut(t / info.dur) };
  voidStage(g, t, cam, { grid: false, mood: 'void' });
  const M = mood('void');
  const gold = S().ui.gold;
  const g0 = info.shot.start;

  // blurred desk surface as soft foreground slab (bottom of frame)
  blurLayer(g, 10, (g) => {
    g.fillStyle = 'rgba(120,110,160,.25)';
    rr(g, -80, E.H * 0.74, E.W + 160, E.H * 0.4, 40); g.fill();
  }, cam, 1.7);

  const pw = V(620, 640), ph = V(780, 660);
  const cx = E.W / 2, cy = E.H * V(0.46, 0.45);
  const tS = (wordTime('punchy', g0) ?? g0 + 1.2) - g0;   // lines start typing on "Short, punchy"
  const tW = (wordTime('word', g0) ?? g0 + tS + 1.4) - g0; // cursor settles on "word"

  layer(g, cam, 1, (g) => {
    g.save();
    g.translate(cx, cy);
    g.rotate(-0.05 + 0.008 * Math.sin(t * 0.8)); // tiny live sway — never static
    rr(g, -pw / 2 + 16, -ph / 2 + 22, pw, ph, 18); g.fillStyle = alpha(M.dark, 0.5); g.fill();
    rr(g, -pw / 2, -ph / 2, pw, ph, 18); g.fillStyle = S().feature; g.fill();
    for (let i = 0; i < 6; i++) {
      const step = tS * 0.5 / 5;
      const on = ease.out(prog(t, tS * 0.45 + i * step, tS * 0.45 + i * step + 0.3));
      const lw = (i % 2 ? 0.58 : 0.76) * pw * clamp(on);
      seg(g, [[-pw / 2 + 64, -ph / 2 + 120 + i * 92], [-pw / 2 + 64 + lw, -ph / 2 + 120 + i * 92]], 9, alpha(M.dark, 0.42));
    }
    // blinking type cursor until the word "word" lands, then it holds solid for a beat
    if (t < tW + 0.5 && (t * 2.6) % 1 < 0.55) {
      seg(g, [[-pw / 2 + 64, -ph / 2 + 128 + 5 * 92 - 14], [-pw / 2 + 64, -ph / 2 + 128 + 5 * 92 + 26]], 6, alpha(gold, 0.9));
    }
    g.restore();
  });

  UI.badge(g, { str: 'TIMED', a: ease.out(prog(t, tW + 0.05, tW + 0.45)), size: V(44, 48) });
  FX.dust(g, t, { count: 14, color: '#cfd6ff', a: 0.22 });
} });
