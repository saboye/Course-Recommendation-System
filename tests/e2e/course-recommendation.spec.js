// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Course Recommendation System E2E Tests', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('Scenario 1: Page Load & Initial UI State', async ({ page }) => {
    // Verify title and brand
    await expect(page).toHaveTitle(/Course Recommendation System/);
    await expect(page.locator('.brand-title')).toBeVisible();

    // Verify hero section elements
    await expect(page.locator('.hero-title')).toHaveText('Discover Your Next Learning Adventure');
    await expect(page.locator('[data-testid="topic-chips"]')).toBeVisible();

    // Verify search form controls
    const keywordInput = page.locator('[data-testid="keyword-input"]');
    await expect(keywordInput).toBeVisible();
    await expect(keywordInput).toHaveValue('');

    const courseSelect = page.locator('[data-testid="course-select"]');
    await expect(courseSelect).toBeVisible();

    const submitBtn = page.locator('[data-testid="submit-btn"]');
    await expect(submitBtn).toBeVisible();

    const clearBtn = page.locator('[data-testid="clear-btn"]');
    await expect(clearBtn).toBeVisible();

    // Verify empty state is initially displayed, recommendations hidden
    await expect(page.locator('[data-testid="empty-state"]')).toBeVisible();
    await expect(page.locator('[data-testid="recommendations-section"]')).toBeHidden();
  });

  test('Scenario 2: Keyword Search Autocomplete Flow', async ({ page }) => {
    const keywordInput = page.locator('[data-testid="keyword-input"]');
    const courseSelect = page.locator('[data-testid="course-select"]');
    const countBadge = page.locator('[data-testid="course-count-badge"]');

    // Type keyword 'Python'
    const coursesResponsePromise = page.waitForResponse(
      (res) => res.url().includes('/courses') && res.status() === 200
    );
    await keywordInput.fill('Python');

    // Wait for API response
    await coursesResponsePromise;

    // Verify count badge and dropdown options
    await expect(countBadge).toBeVisible();
    await expect(countBadge).toContainText(/courses? found/);

    const options = courseSelect.locator('option');
    const optionsCount = await options.count();
    expect(optionsCount).toBeGreaterThan(1);

    // Verify at least one option mentions Python
    const secondOptionText = await options.nth(1).innerText();
    expect(secondOptionText.toLowerCase()).toContain('python');
  });

  test('Scenario 3: Popular Topic Chips Filter Flow', async ({ page }) => {
    const keywordInput = page.locator('[data-testid="keyword-input"]');
    const courseSelect = page.locator('[data-testid="course-select"]');

    // Click on 'Data Science' topic chip
    const dsChip = page.locator('.topic-chip[data-topic="Data Science"]');
    await expect(dsChip).toBeVisible();

    const coursesResponsePromise = page.waitForResponse(
      (res) => res.url().includes('/courses') && res.status() === 200
    );
    await dsChip.click();

    // Verify keyword input is populated with chip text
    await expect(keywordInput).toHaveValue('Data Science');

    // Wait for courses to populate
    await coursesResponsePromise;
    const options = courseSelect.locator('option');
    const optionsCount = await options.count();
    expect(optionsCount).toBeGreaterThan(1);
  });

  test('Scenario 4: Recommendation Generation Flow', async ({ page }) => {
    const keywordInput = page.locator('[data-testid="keyword-input"]');
    const courseSelect = page.locator('[data-testid="course-select"]');
    const submitBtn = page.locator('[data-testid="submit-btn"]');
    const recSection = page.locator('[data-testid="recommendations-section"]');

    // Search for courses
    const coursesResponsePromise = page.waitForResponse(
      (res) => res.url().includes('/courses') && res.status() === 200
    );
    await keywordInput.fill('Python');
    await coursesResponsePromise;

    // Select the first real course (index 1, as index 0 is the placeholder)
    const options = courseSelect.locator('option');
    const courseToSelect = await options.nth(1).getAttribute('value');
    expect(courseToSelect).toBeTruthy();
    await courseSelect.selectOption({ index: 1 });

    // Submit recommendation request
    const recResponsePromise = page.waitForResponse(
      (res) => res.url().includes('/recommend') && res.status() === 200
    );
    await submitBtn.click();
    await recResponsePromise;

    // Verify recommendations section is visible and empty state hidden
    await expect(recSection).toBeVisible();
    await expect(page.locator('[data-testid="empty-state"]')).toBeHidden();

    // Verify 5 recommendation cards rendered
    const recCards = page.locator('[data-testid="rec-card"]');
    await expect(recCards).toHaveCount(5);

    // Verify structure of first recommendation card
    const firstCard = recCards.first();
    await expect(firstCard.locator('.rec-title')).toBeVisible();
    await expect(firstCard.locator('.rec-university')).toBeVisible();
    await expect(firstCard.locator('.badge-rating')).toBeVisible();
    await expect(firstCard.locator('[data-testid="course-link"]')).toHaveAttribute('href', /^https?:\/\//);
  });

  test('Scenario 5: Custom Recommendation Count Selection', async ({ page }) => {
    const keywordInput = page.locator('[data-testid="keyword-input"]');
    const courseSelect = page.locator('[data-testid="course-select"]');
    const numRecsSelect = page.locator('#num-recs');
    const submitBtn = page.locator('[data-testid="submit-btn"]');

    // Search for courses
    const coursesResponsePromise = page.waitForResponse(
      (res) => res.url().includes('/courses') && res.status() === 200
    );
    await keywordInput.fill('Python');
    await coursesResponsePromise;

    // Select course and change count to 3
    await courseSelect.selectOption({ index: 1 });
    await numRecsSelect.selectOption('3');

    // Submit
    const recResponsePromise = page.waitForResponse(
      (res) => res.url().includes('/recommend') && res.status() === 200
    );
    await submitBtn.click();
    await recResponsePromise;

    // Verify exactly 3 cards
    const recCards = page.locator('[data-testid="rec-card"]');
    await expect(recCards).toHaveCount(3);
  });

  test('Scenario 6: Form Reset & Clear Flow', async ({ page }) => {
    const keywordInput = page.locator('[data-testid="keyword-input"]');
    const courseSelect = page.locator('[data-testid="course-select"]');
    const submitBtn = page.locator('[data-testid="submit-btn"]');
    const clearBtn = page.locator('[data-testid="clear-btn"]');
    const recSection = page.locator('[data-testid="recommendations-section"]');
    const emptyState = page.locator('[data-testid="empty-state"]');

    // First generate recommendations
    const coursesResponsePromise = page.waitForResponse(
      (res) => res.url().includes('/courses') && res.status() === 200
    );
    await keywordInput.fill('Python');
    await coursesResponsePromise;

    await courseSelect.selectOption({ index: 1 });

    const recResponsePromise = page.waitForResponse(
      (res) => res.url().includes('/recommend') && res.status() === 200
    );
    await submitBtn.click();
    await recResponsePromise;

    await expect(recSection).toBeVisible();

    // Now click clear button
    await clearBtn.click();

    // Verify inputs and state reset
    await expect(keywordInput).toHaveValue('');
    await expect(courseSelect.locator('option')).toHaveCount(1);
    await expect(recSection).toBeHidden();
    await expect(emptyState).toBeVisible();
  });

  test('Scenario 7: Validation Error on Empty Selection', async ({ page }) => {
    const submitBtn = page.locator('[data-testid="submit-btn"]');
    const alertBanner = page.locator('[data-testid="alert-banner"]');

    // Submit without selecting anything
    await submitBtn.click();

    // Verify alert banner is displayed
    await expect(alertBanner).toBeVisible();
    await expect(alertBanner).toContainText('Please choose a reference course');
  });

  test('Scenario 8: Responsive Layout on Mobile Viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });

    // Ensure elements are styled and visible without breaking
    await expect(page.locator('.brand-title')).toBeVisible();
    await expect(page.locator('[data-testid="keyword-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="submit-btn"]')).toBeVisible();
    await expect(page.locator('[data-testid="clear-btn"]')).toBeVisible();
  });

});
