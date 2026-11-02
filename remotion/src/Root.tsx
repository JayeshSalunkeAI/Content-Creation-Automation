import { Composition } from 'remotion';
import React from 'react';
import { ShortVideo, type MasterJson, type WordsFrames, EMPTY_MASTER } from './ShortVideo';

// Brand fonts (stage-1 candidates + future default). OFL via @fontsource; each import
// is only the weights the tokens layer actually uses. Fonts irrelevant to a theme are
// still fine to ship (subset files, no runtime cost beyond bundle size).
import '@fontsource/fraunces/600.css';
import '@fontsource/fraunces/800.css';
import '@fontsource/space-grotesk/500.css';
import '@fontsource/space-grotesk/700.css';
import '@fontsource/ibm-plex-mono/600.css';
import '@fontsource/ibm-plex-mono/700.css';
import '@fontsource/archivo-black/400.css';
import '@fontsource/fredoka/500.css';
import '@fontsource/fredoka/700.css';

// One composition. Size/fps/duration come from master.json via calculateMetadata,
// so S8 (plugin render) and P10 (Remotion) agree exactly.
export const RemotionRoot: React.FC = () => (
  <Composition
    id="ShortVideo"
    component={ShortVideo}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={1}
    defaultProps={{
      master: EMPTY_MASTER as MasterJson,
      words: { fps: 30, words: [] } as WordsFrames,
      debug: false,
    }}
    calculateMetadata={({ props }) => ({
      fps: props.master.fps,
      width: props.master.width,
      height: props.master.height,
      durationInFrames: props.master.durationFrames,
    })}
  />
);
