// @ts-check
const { defineConfig, devices } = require("@playwright/test");

/**
 * Playwright configuration for Course Recommendation System E2E testing.
 * @see https://playwright.dev/docs/test-configuration
 */
module.exports = defineConfig({
  testDir: "./tests/e2e",
  timeout: 30000,
  expect: {
    timeout: 5000,
  },
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: "http://127.0.0.1:5000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        headless: true,
        screenshot: "on",
        video: "on",
      },
    },
  ],
  webServer: {
    command: "venv\\Scripts\\python app.py",
    url: "http://127.0.0.1:5000/api/health",
    reuseExistingServer: true,
    timeout: 30000,
  },
});
