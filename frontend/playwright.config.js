import { defineConfig, devices } from '@playwright/test';

// Get configuration from environment variables
const APPLICATION_HOST = process.env.APPLICATION_HOST || '127.0.0.1';
const APPLICATION_PORT_FRONTEND = process.env.APPLICATION_PORT_FRONTEND || '3000';
const APPLICATION_PORT = process.env.APPLICATION_PORT || '8000';

// Use consistent host configuration
const FRONTEND_URL = `http://${APPLICATION_HOST}:${APPLICATION_PORT_FRONTEND}`;
const BACKEND_URL = `http://${APPLICATION_HOST}:${APPLICATION_PORT}`;

/**
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests',
  timeout: 30 * 1000,
  expect: {
    timeout: 5000
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    actionTimeout: 0,
    baseURL: FRONTEND_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox', 
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    }
  ],
  webServer: {
    command: `npm run dev -- --port ${APPLICATION_PORT_FRONTEND} --host ${APPLICATION_HOST}`,
    port: parseInt(APPLICATION_PORT_FRONTEND),
    reuseExistingServer: !process.env.CI
  }
});
