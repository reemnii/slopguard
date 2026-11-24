import { scanDemo } from './scanner.mjs';
// Keep the UI independent of transport. A future live adapter must explicitly
// declare live mode and implement scan(inputs, { signal }). No endpoint is assumed.
const demoAdapter = { mode: 'demo', async scan(inputs, {signal} = {}) { if (signal?.aborted) throw new DOMException('Aborted', 'AbortError'); return scanDemo(inputs); } };
export const scannerApi = demoAdapter;
