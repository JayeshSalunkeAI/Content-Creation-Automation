import React from 'react';
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig, Sequence } from 'remotion';
import type { SegmentProps } from '../ShortVideo';
import { useBrand } from '../brand/theme';

// registry.ts — segment components the storyboard may use.
// brand/components.md is generated from this list, declaring what exists (R-rule:
// validate.py rejects master.json referencing anything not registered here).

type SegmentComp = React.FC<{ props: Record<string, unknown>; hideCaptions: boolean }>;

export interface RegistryEntry {
  component: SegmentComp;
  description: string;
  minFrames: number;
  maxFrames: number;
  hidesCaptions: boolean;
}

const StatCounter: SegmentComp = ({ props }) => {
  const frame = useCurrentFrame();
  const t = useBrand();
  const tween = props['tween'] as { from?: number; to?: number; durFrames?: number } | undefined;
  let counter = String(props['counter'] ?? '');
  if (tween) {
    const from = Number(tween.from ?? 0);
    const to = Number(tween.to ?? 0);
    const durF = Math.max(2, Number(tween.durFrames ?? 78));
    const up = interpolate(frame, [0, durF], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic) });
    counter = Math.round(from + (to - from) * up).toLocaleString('en-US');
  }
  const pop = interpolate(frame, [0, 10], [0.86, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.back(1.6)) as unknown as (x: number) => number });
  const label = String(props['label'] ?? '');
  const tag = String(props['tag'] ?? '');
  return (
    <AbsoluteFillBlock>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: t.counterText, fontFamily: t.displayFont, transform: `scale(${pop})` }}>
        <div style={{ fontSize: 230, fontWeight: 900, fontVariantNumeric: 'tabular-nums', letterSpacing: -6, textShadow: t.counterGlow }}>{counter}</div>
        <div style={{ fontFamily: t.uiFont, fontSize: 58, fontWeight: 800, color: t.counterLabel, marginTop: 10, letterSpacing: 4 }}>{label}</div>
        {tag ? <div style={{ fontFamily: t.monoFont, marginTop: 22, fontSize: 32, color: t.counterTag, fontWeight: 700, letterSpacing: 6 }}>{tag}</div> : null}
      </div>
    </AbsoluteFillBlock>
  );
};

const MapPanZoom: SegmentComp = ({ props }) => {
  const t = useBrand();
  return (
    <AbsoluteFillBlock>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: t.counterTag, fontFamily: t.uiFont, fontSize: 60, textAlign: 'center' as const }}>
        MapPanZoom placeholder (focus: {String(props['focus'] ?? '')})<br />TODO(P10)
      </div>
    </AbsoluteFillBlock>
  );
};

function AbsoluteFillBlock({ children }: { children: React.ReactNode }) {
  return <AbsoluteFillShadow>{children}</AbsoluteFillShadow>;
}
function AbsoluteFillShadow({ children }: { children: React.ReactNode }) {
  const t = useBrand();
  return <div style={{ position: 'absolute', inset: 0, background: t.bg }}>{children}</div>;
}

export const REGISTRY: Record<string, RegistryEntry> = {
  StatCounter: { component: StatCounter, description: 'Big number + label.', minFrames: 30, maxFrames: 300, hidesCaptions: false },
  MapPanZoom: { component: MapPanZoom, description: 'Map pan/zoom takeover (d3-geo + world-atlas later).', minFrames: 45, maxFrames: 450, hidesCaptions: false },
};

export function getSegmentComponent(name: string): SegmentComp {
  const entry = REGISTRY[name];
  if (!entry) {
    const Comp: SegmentComp = ({ props }) => (
      <AbsoluteFillBlock>
        <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ff4040', fontSize: 48 }}>
          UNKNOWN COMPONENT: {name} (props: {JSON.stringify(props).slice(0, 80)})
        </div>
      </AbsoluteFillBlock>
    );
    return Comp;
  }
  return entry.component;
}

// overlays — MVP implementations; refined by ch-brand.
export const OVERLAYS: Record<string, React.FC<{ props: Record<string, unknown> }>> = {
  hookText: ({ props }) => {
    const t = useBrand();
    const s = String(props['text'] ?? '');
    if (!s) return null;
    return (
      <div style={{ position: 'absolute', left: 0, right: 0, top: 170, textAlign: 'center', color: t.hookColor, fontFamily: t.displayFont, fontWeight: 900, fontSize: 84, textShadow: t.hookShadow, padding: '0 60px' }}>
        {s}
      </div>
    );
  },
  lowerThird: ({ props }) => {
    const t = useBrand();
    const s = String(props['text'] ?? '');
    if (!s) return null;
    return (
      <div style={{ position: 'absolute', left: 60, bottom: 420, background: t.card, border: `1px solid ${t.cardLine}`, borderRadius: 16, padding: '18px 34px', color: t.cardText, fontSize: 44, fontFamily: t.uiFont }}>
        {s}
      </div>
    );
  },
  progressBar: () => <div style={{ display: 'none' }} />, // TODO(P10): thin bar at top using `useCurrentFrame`
  endCard: ({ props }) => {
    const t = useBrand();
    const s = String(props['title'] ?? '');
    const fade = interpolate(useCurrentFrame(), [0, 14], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
    return (
      <div style={{ position: 'absolute', inset: 0, background: t.scrim, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', color: t.endcardText, fontFamily: t.displayFont, opacity: fade }}>
        <div style={{ fontSize: 92, fontWeight: 900, textAlign: 'center' as const, padding: '0 80px' }}>{s}</div>
        <div style={{ fontFamily: t.uiFont, marginTop: 30, fontSize: 52, color: t.endcardCta, fontWeight: 800 }}>Follow for more</div>
      </div>
    );
  },
  logoBug: () => null,
  receiptTicker: ({ props }) => {
    // BRAND SIGNATURE — "the video shows its own receipts": a live frame counter fed by
    // the render clock itself (useCurrentFrame), never a fake number baked into props.
    const t = useBrand();
    const frame = useCurrentFrame();
    const total = Number(props['totalFrames'] ?? '—');
    const fps = Number(props['fps'] ?? 30);
    return (
      <div style={{ position: 'absolute', left: 48, top: 44, display: 'flex', alignItems: 'center', gap: 16, background: t.card, border: `1px solid ${t.cardLine}`, borderRadius: 8, padding: '10px 18px', fontFamily: t.monoFont, fontWeight: 700, fontSize: 27, letterSpacing: 2, color: t.counterTag }}>
        <span style={{ color: t.accent }}>{String(frame).padStart(4, '0')}<span style={{ color: t.counterTag }}>/{total}</span></span>
        <span>{fps} FPS</span>
      </div>
    );
  },
  takeStamp: ({ props }) => {
    // Take stamp at real segment starts (shot boundaries straight out of master.json).
    const t = useBrand();
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();
    const s = String(props['text'] ?? '');
    const take = String(props['take'] ?? 1);
    const stamp = spring({ frame, fps, config: { damping: 14, stiffness: 260 } });
    const opacity = interpolate(frame, [0, 6], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
    return (
      <div style={{ position: 'absolute', right: 48, top: 44, background: t.card, border: `2px solid ${t.gold}`, borderRadius: 8, padding: '12px 22px', fontFamily: t.monoFont, fontWeight: 700, fontSize: 30, letterSpacing: 4, color: t.gold, opacity, transform: `scale(${Math.min(stamp, 1.08)})` }}>
        {s} <span style={{ color: t.counterTag }}>· TAKE {take}</span>
      </div>
    );
  },
  qcSeal: ({ props }) => {
    // QC seal on the endcard: the production data that only a real pipeline can print.
    const t = useBrand();
    const frame = useCurrentFrame();
    const s = String(props['label'] ?? 'QC PASS');
    const pop = interpolate(frame, [0, 10], [0.5, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.back(1.8)) as unknown as (x: number) => number });
    return (
      <div style={{ position: 'absolute', left: 60, bottom: 150, background: t.gold, color: '#16191c', fontFamily: t.monoFont, fontWeight: 700, fontSize: 34, letterSpacing: 3, padding: '14px 26px', borderRadius: 6, opacity: Math.min(pop, 1), transform: `scale(${pop}) rotate(-2deg)`, boxShadow: '0 6px 24px rgba(0,0,0,.35)' }}>
        {s} <span style={{ color: 'rgba(22,25,28,.55)' }}>/ QC-01</span>
      </div>
    );
  },
  sourceTag: ({ props }) => {
    const t = useBrand();
    const s = String(props['text'] ?? '');
    if (!s) return null;
    return (
      <div style={{ position: 'absolute', right: 60, bottom: 300, color: t.metaColor, fontSize: 30, fontFamily: t.monoFont }}>{s}</div>
    );
  },
};

export function RenderOverlay(overlay: { overlay: { id: string; kind: string; startFrame: number; endFrame: number; props?: Record<string, unknown> } }) {
  const { kind, startFrame, endFrame } = overlay.overlay;
  const Comp = OVERLAYS[kind] ?? (() => null);
  const more = Math.max(1, endFrame - startFrame);
  return (
    <React.Fragment key={overlay.overlay.id}>
      {startFrame >= 0 ? (
        <Sequence from={startFrame} durationInFrames={more}><Comp props={overlay.overlay.props ?? {}} /></Sequence>
      ) : (
        <Comp props={overlay.overlay.props ?? {}} />
      )}
    </React.Fragment>
  );
}
