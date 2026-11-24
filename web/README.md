# SlopGuard console

Next.js / React prototype with Tailwind CSS, Lucide icons, and a Prism-highlighted editor.

```sh
npm install
npm run dev
```

Open http://127.0.0.1:3000. `npm run build` creates the static site in `out/`.

`npm test` runs deterministic scanner checks. `npx playwright test` runs browser flows against the static build. The checked-in browser config uses Windows Chrome; set `launchOptions.executablePath` for your machine or use an installed Playwright Chromium browser.

The app opens with clearly labeled sample history. Scan results use deterministic fixtures in `lib/scanner.mjs`; unknown names are unverified. No registry, provider, or Python backend requests occur. History and workspace preferences live in browser storage; clear them through Settings. Scans are limited to 50 local records.

`lib/api.mjs` is the transport boundary. Replace the demo adapter with an explicit live adapter implementing `scan(inputs, {signal})` when connecting the existing Python scanner. Preserve unverified registry errors; replace demo labels only after a backend is connected. Keep API credentials on the server.

Experiment generation returns fixed samples based on the prompt's language keywords. The metrics are an illustrative 50-case example, not measured scanner performance.
