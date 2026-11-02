import React, { createContext, useContext } from 'react';

// brand/theme.ts — THE single source of Remotion brand tokens (colours, type, surfaces).
// ch-brand stage 1: 'dusk' = legacy reference look; 'press' / 'utility' / 'candy' are the
// three candidate identities rendered side-by-side for the user to pick from.
// After the pick this file becomes generated from brand/brand.json (palette sync step).

export interface BrandTheme {
  id: string;
  label: string;
  bg: string;
  feature: string;
  accent: string;
  gold: string;
  uiFont: string;
  displayFont: string;
  monoFont: string;
  // captions
  captionColor: string;
  captionOn: string;
  captionShadow: string;
  captionWeight: number;
  captionCase: 'none' | 'uppercase';
  captionSize: number;
  // segment components
  counterText: string;
  counterGlow: string;
  counterLabel: string;
  counterTag: string;
  card: string;
  cardLine: string;
  cardText: string;
  hookColor: string;
  hookShadow: string;
  scrim: string;
  endcardText: string;
  endcardCta: string;
  metaColor: string;
  vignette: number;
  grain: number;
}

const SEGOE = "'Segoe UI', 'Nunito', sans-serif";

export const THEMES: Record<string, BrandTheme> = {
  dusk: {
    id: 'dusk', label: 'Legacy — Cinematic Dusk (reference)',
    bg: '#0b0e1a', feature: '#f4efe6', accent: '#ff6f61', gold: '#ffd47e',
    uiFont: SEGOE, displayFont: SEGOE, monoFont: SEGOE,
    captionColor: '#f4efe6', captionOn: '#ffd47e', captionShadow: '0 4px 20px rgba(0,0,0,.85)',
    captionWeight: 900, captionCase: 'none', captionSize: 64,
    counterText: '#f4efe6', counterGlow: '0 0 60px rgba(255,212,126,.35)', counterLabel: '#ffd47e', counterTag: '#9fb6d8',
    card: 'rgba(18,28,48,.94)', cardLine: 'rgba(150,180,230,.25)', cardText: '#9fb6d8',
    hookColor: '#fff', hookShadow: '0 4px 24px rgba(0,0,0,.8)',
    scrim: 'rgba(7,6,12,.7)', endcardText: '#f4efe6', endcardCta: '#ffd47e',
    metaColor: 'rgba(220,225,240,.65)',
    vignette: 0.55, grain: 0.055,
  },
  press: {
    id: 'press', label: 'PRESS RUN — paper + ink + vermillion (editorial print)',
    bg: '#f4ede3', feature: '#17150f', accent: '#e2542c', gold: '#a2701e',
    uiFont: "'Space Grotesk', 'Segoe UI', sans-serif", displayFont: "'Fraunces', 'Georgia', serif", monoFont: "'IBM Plex Mono', 'Consolas', monospace",
    captionColor: '#17150f', captionOn: '#e2542c', captionShadow: 'none',
    captionWeight: 800, captionCase: 'none', captionSize: 66,
    counterText: '#17150f', counterGlow: 'none', counterLabel: '#e2542c', counterTag: '#6b675a',
    card: 'rgba(252,246,238,.96)', cardLine: 'rgba(23,21,15,.28)', cardText: '#231f14',
    hookColor: '#17150f', hookShadow: 'none',
    scrim: 'rgba(244,237,227,.84)', endcardText: '#17150f', endcardCta: '#e2542c',
    metaColor: 'rgba(23,21,15,.55)',
    vignette: 0.18, grain: 0.1,
  },
  utility: {
    id: 'utility', label: 'UTILITY CLASS — graphite + safety yellow (industrial)',
    bg: '#16191c', feature: '#eceae2', accent: '#ffc744', gold: '#ffc744',
    uiFont: "'IBM Plex Mono', 'Consolas', monospace", displayFont: "'Archivo Black', 'Arial Black', sans-serif", monoFont: "'IBM Plex Mono', 'Consolas', monospace",
    captionColor: '#eceae2', captionOn: '#ffc744', captionShadow: '0 3px 14px rgba(0,0,0,.9)',
    captionWeight: 800, captionCase: 'uppercase', captionSize: 56,
    counterText: '#eceae2', counterGlow: '0 0 44px rgba(255,199,68,.22)', counterLabel: '#ffc744', counterTag: '#98968b',
    card: 'rgba(21,24,27,.95)', cardLine: 'rgba(214,209,199,.25)', cardText: '#dcd8cf',
    hookColor: '#eceae2', hookShadow: '0 4px 24px rgba(0,0,0,.8)',
    scrim: 'rgba(10,12,14,.8)', endcardText: '#eceae2', endcardCta: '#ffc744',
    metaColor: 'rgba(214,209,199,.6)',
    vignette: 0.5, grain: 0.09,
  },
  candy: {
    id: 'candy', label: 'CANDY POP — butter + coral + mint (flat toy world)',
    bg: '#fff4db', feature: '#2e241d', accent: '#3ec1a7', gold: '#ff5d73',
    uiFont: "'Nunito', 'Segoe UI', sans-serif", displayFont: "'Fredoka', 'Nunito', sans-serif", monoFont: "'Nunito', sans-serif",
    captionColor: '#2e241d', captionOn: '#ff5d73', captionShadow: '3px 3px 0 rgba(46,36,29,.14)',
    captionWeight: 900, captionCase: 'none', captionSize: 66,
    counterText: '#2e241d', counterGlow: 'none', counterLabel: '#ff5d73', counterTag: '#8a7666',
    card: 'rgba(255,253,248,.94)', cardLine: 'rgba(46,36,29,.2)', cardText: '#2e241d',
    hookColor: '#2e241d', hookShadow: '3px 4px 0 rgba(255,93,115,.3)',
    scrim: 'rgba(255,244,219,.82)', endcardText: '#2e241d', endcardCta: '#ff5d73',
    metaColor: 'rgba(46,36,29,.5)',
    vignette: 0.16, grain: 0.06,
  },
};

export function getTheme(id?: string | null): BrandTheme {
  // Ch-brand stage 2: 'utility' froze as the channel brand (brand/brand.json).
  return THEMES[id ?? 'utility'] ?? THEMES.utility;
}

export const BrandContext = createContext<BrandTheme>(THEMES.dusk);

export const BrandProvider: React.FC<{ value: BrandTheme; children: React.ReactNode }> = ({ value, children }) => (
  <BrandContext.Provider value={value}>{children}</BrandContext.Provider>
);

export const useBrand = (): BrandTheme => useContext(BrandContext);
