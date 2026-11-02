import { Config } from '@remotion/cli/config';

/**
 * Hardware GPU rendering (dGPU). Remotion 4.x defaults to 'swangle' = SwiftShader,
 * which renders 100% on CPU and leaves the NVIDIA RTX idle. 'angle' runs ANGLE over
 * Direct3D; which adapter is used is decided by Windows per-app GpuPreference:
 * chrome-headless-shell.exe is pinned to "High performance" (the RTX) by
 * pipeline/set_gpu_pref.ps1 — rerun that script after any `npm install` that
 * refreshes node_modules, or playwright browser updates. Expected nvidia-smi
 * evidence during a render: chrome-headless-shell.exe listed on GPU 0, ~300-700 MiB
 * dedicated memory in use.
 */
Config.setChromiumOpenGlRenderer('angle');
