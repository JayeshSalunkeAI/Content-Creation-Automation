import React from 'react';
import { useCurrentFrame, interpolate, spring, useVideoConfig } from 'remotion';
import type { MasterJson, WordsFrames } from '../../ShortVideo';
import { useBrand } from '../../brand/theme';

// Captions — script spelling, Whisper timing (words.frames.json written by pipeline/align.py).
// MVP: 3-word phrases, active word highlighted. Full measured/line-breaking version in P10.

interface Cfg { enabled?: boolean; maxWords?: number; safe?: { top: number; bottom: number; side: number } }

function groupWords(words: NonNullable<WordsFrames['words']>, maxWords: number) {
  const phrases: Array<{ start: number; end: number; words: NonNullable<WordsFrames['words']> }> = [];
  let cur: NonNullable<WordsFrames['words']> = [];
  const flush = () => {
    if (cur.length) {
      phrases.push({ start: cur[0].startFrame, end: cur[cur.length - 1].endFrame, words: cur });
      cur = [];
    }
  };
  for (const w of words) {
    const prev = cur[cur.length - 1];
    const bigGap = prev ? w.startFrame - prev.endFrame > 8 : false;
    const punctuation = /[.!?,;:]$/.test(w.text);
    cur.push(w);
    if (cur.length >= maxWords || punctuation || bigGap) flush();
  }
  flush();
  return phrases;
}

export const Captions: React.FC<{ words: WordsFrames; cfg: Cfg; master: MasterJson }> = ({ words, cfg, master }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = useBrand();
  const maxWords = cfg.maxWords ?? 3;
  const phrases = groupWords(words.words, maxWords);
  const active = phrases.find((p) => frame >= p.start && frame < p.end);
  if (!active) return null;
  // push below layers up while a lowerThird is active (MVP: reserve fixed offset)
  const y = (master.captions?.safe?.bottom ? master.height - master.captions.safe.bottom - 40 : 1500);
  const scale = spring({ frame: frame - active.start, fps, config: { damping: 18, stiffness: 260 } });
  return (
    <div
      style={{
        position: 'absolute', left: 0, right: 0, top: y - 90,
        display: 'flex', justifyContent: 'center', gap: 24, transform: `scale(${0.92 + 0.08 * scale})`,
        fontFamily: t.uiFont, fontSize: t.captionSize, fontWeight: t.captionWeight,
        textTransform: t.captionCase === 'uppercase' ? 'uppercase' : 'none',
        textShadow: t.captionShadow, color: t.captionColor,
      }}
    >
      {active.words.map((w) => {
        const on = frame >= w.startFrame && frame < w.endFrame;
        return (
          <span key={w.i} style={{ color: on ? t.captionOn : undefined, transform: on ? 'scale(1.06)' : undefined, transition: 'none' }}>
            {w.text}
          </span>
        );
      })}
    </div>
  );
};
