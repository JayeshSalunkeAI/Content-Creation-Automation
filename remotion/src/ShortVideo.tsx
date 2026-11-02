import React from 'react';
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, staticFile } from 'remotion';
import { GradeOverlay } from './components/GradeOverlay';
import { Captions } from './components/captions/Captions';
import { RenderOverlay } from './components/registry';
import { getSegmentComponent } from './components/registry';
import { getTheme, BrandProvider } from './brand/theme';

// Schema doclint: these types mirror schemas/master.schema.json (ch.master/1).
export interface SegmentProps {
  id: string;
  type: 'plugin' | 'remotion';
  startFrame: number;
  endFrame: number;
  line?: string;
  transitionIn?: { type: string; frames: number };
  plugin?: { clip: string; clipOffsetFrames: number; shotIds: string[] };
  remotion?: { component: string; props: Record<string, unknown>; assets?: string[]; hideCaptions?: boolean };
}
export interface MasterJson {
  schema: 'ch.master/1';
  id: string;
  title: string;
  fps: number;
  width: number;
  height: number;
  durationFrames: number;
  mode: 'A' | 'B';
  voice: { file: string; voiceId: string; speed: number };
  words: { pluginFile: string; framesFile: string };
  segments: SegmentProps[];
  overlays?: Array<{ id: string; kind: string; startFrame: number; endFrame: number; props?: Record<string, unknown> }>;
  captions?: { enabled: boolean; style?: string; maxWords?: number; safe?: { top: number; bottom: number; side: number } };
  audio: { mixFile: string; loudnessTarget: number };
}
export interface WordsFrames {
  fps: number;
  words: Array<{ i: number; text: string; startFrame: number; endFrame: number; segmentId: string }>;
}

// Placeholder so `remotion studio` loads before props exist; real renders always pass real props.
export const EMPTY_MASTER: MasterJson = {
  schema: 'ch.master/1', id: 'empty', title: 'Empty', fps: 30, width: 1080, height: 1920,
  durationFrames: 1, mode: 'A',
  voice: { file: '', voiceId: '', speed: 1 },
  words: { pluginFile: '', framesFile: '' },
  segments: [],
  audio: { mixFile: '', loudnessTarget: -14 },
};
interface Props { master: MasterJson; words: WordsFrames; debug: boolean; brandTheme?: string }

export const ShortVideo: React.FC<Props> = ({ master, words, debug, brandTheme }) => {
  // Brand tokens drive background + every Remotion-owned surface. 'dusk' = legacy
  // reference; 'press' / 'utility' / 'candy' are the ch-brand stage-1 candidates.
  const t = getTheme(brandTheme);
  return (
    <BrandProvider value={t}>
      <AbsoluteFill style={{ background: t.bg }}>
        {/* L1 — plugin picture, muted; offsets keep the clip in sync with master time */}
        {master.segments.filter((s) => s.type === 'plugin').length > 0 && null}
        {master.segments.map((seg) =>
          seg.type === 'plugin' && seg.plugin ? (
            <Sequence key={seg.id} from={seg.startFrame} durationInFrames={seg.endFrame - seg.startFrame}>
              <OffthreadVideo
                src={staticFile(seg.plugin.clip)}
                startFrom={seg.plugin.clipOffsetFrames}
                muted
              />
            </Sequence>
          ) : null,
        )}
        {/* L2 — Remotion-owned segments with brand transitions (components come from the registry) */}
        {master.segments.map((seg) =>
          seg.type === 'remotion' ? <SegmentHost key={seg.id} seg={seg} /> : null,
        )}
        {/* uniform vignette + grain over plugin AND remotion picture */}
        <GradeOverlay />
        {/* L3 — overlays in order hookText -> lowerThird -> logoBug -> sourceTag -> progressBar -> endCard */}
        {(master.overlays ?? []).map((o) => <RenderOverlay key={o.id} overlay={o} />)}
        {/* L4 — brand captions from the script's own words, timed by the single alignment run */}
        {master.captions?.enabled ? <Captions words={words} cfg={master.captions} master={master} /> : null}
        {/* L5 — QA-only safe-zone guides */}
        {debug ? (
          <AbsoluteFill style={{ pointerEvents: 'none', border: '2px dashed rgba(0,255,255,.5)' }}>
            {(() => {
              const s = master.captions?.safe ?? { top: 150, bottom: 250, side: 60 };
              return (
                <>
                  <div style={{ position: 'absolute', inset: `${s.top}px 0 ${s.bottom}px ${s.side}px`, border: '2px dashed rgba(255,0,128,.6)' }} />
                  <div style={{ position: 'absolute', left: 20, top: s.top, fontSize: 28, color: '#ff0088' }}>SAFE</div>
                </>
              );
            })()}
          </AbsoluteFill>
        ) : null}
        {/* the ONLY audio element */}
        {master.audio.mixFile ? <Audio src={staticFile(master.audio.mixFile)} /> : null}
      </AbsoluteFill>
    </BrandProvider>
  );
};

const SegmentHost: React.FC<{ seg: SegmentProps }> = ({ seg }) => {
  const Comp = getSegmentComponent((seg.remotion?.component ?? '').trim());
  const trans = seg.transitionIn;
  return (
    <Sequence from={seg.startFrame} durationInFrames={seg.endFrame - seg.startFrame}>
      {/* TODO(P10): wrap in TransitionWrap with brand easing when transitions land */}
      <Comp props={seg.remotion?.props ?? {}} hideCaptions={seg.remotion?.hideCaptions ?? false} />
    </Sequence>
  );
};
