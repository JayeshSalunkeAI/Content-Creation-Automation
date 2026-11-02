import React from 'react';

// GradeOverlay — uniform vignette + grain over everything, matching the plugin's
// brand style (grade.vignette = 0, grade.grain = 0 in studio/engine/styles.js so the
// grade happens exactly once, here).
export const GradeOverlay: React.FC = () => (
  <>
    <div
      style={{
        position: 'absolute', inset: 0, pointerEvents: 'none',
        background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,.55) 100%)',
      }}
    />
    {/* TODO(P10 fine): animated seeded grain via noise canvas / noise() for texture parity */}
  </>
);
