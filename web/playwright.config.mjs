import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './e2e', fullyParallel: false, workers: 1,
  use: { baseURL: 'http://127.0.0.1:4173', headless: true, viewport: {width:1440,height:1050}, launchOptions: { executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe' } },
  webServer: { command: 'python -m http.server 4173 --bind 127.0.0.1 --directory out', url: 'http://127.0.0.1:4173', reuseExistingServer: true },
  reporter: 'list',
});
