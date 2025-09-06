import { test, expect } from '@playwright/test';

test.describe('Accessibility Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('.channel-card', { timeout: 10000 });
  });

  test('has proper heading structure', async ({ page }) => {
    // Check main heading (h1)
    const h1 = page.locator('h1');
    await expect(h1).toBeVisible();
    await expect(h1).toContainText('🚀 Saleor Price Manager');
    
    // Check section headings (h2)
    const h2 = page.locator('h2');
    await expect(h2).toBeVisible();
    await expect(h2).toContainText('📊 Channel Management');
    
    // Check subsection headings (h3) for each channel
    const h3Elements = page.locator('h3');
    const h3Count = await h3Elements.count();
    expect(h3Count).toBeGreaterThanOrEqual(3); // At least 3 demo channels
  });

  test('form inputs have proper labels and attributes', async ({ page }) => {
    const firstChannel = page.locator('.channel-card').first();
    
    // Check markup input accessibility
    const markupInput = firstChannel.locator('input[type="number"]').first();
    await expect(markupInput).toHaveAttribute('step', '0.1');
    await expect(markupInput).toHaveAttribute('min', '0');
    await expect(markupInput).toHaveAttribute('max', '100');
    
    // Check that labels are present
    await expect(firstChannel.locator('label:has-text("Update Markup")')).toBeVisible();
    await expect(firstChannel.locator('label:has-text("Test Price Calculation")')).toBeVisible();
  });

  test('buttons have accessible text and roles', async ({ page }) => {
    const firstChannel = page.locator('.channel-card').first();
    
    // Check update button
    const updateButton = firstChannel.locator('button').first();
    await expect(updateButton).toContainText('💾 Update');
    await expect(updateButton).toHaveAttribute('type', 'button');
    
    // Check calculate button
    const calculateButton = firstChannel.locator('button').nth(1);
    await expect(calculateButton).toContainText('🧮 Calculate');
    await expect(calculateButton).toHaveAttribute('type', 'button');
  });

  test('keyboard navigation works properly', async ({ page }) => {
    // Test tab navigation through interactive elements
    await page.keyboard.press('Tab'); // Should focus first input
    
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toHaveAttribute('type', 'number');
    
    // Continue tabbing through form elements
    await page.keyboard.press('Tab'); // Should focus update button
    const secondFocused = page.locator(':focus');
    await expect(secondFocused).toContainText('💾 Update');
    
    // Test Enter key activation
    await secondFocused.press('Enter');
    // Button should be clickable with Enter key
  });

  test('links have proper attributes', async ({ page }) => {
    // Check external links have proper attributes
    const swaggerLink = page.locator('a[href="http://localhost:8000/docs"]');
    await expect(swaggerLink).toHaveAttribute('target', '_blank');
    await expect(swaggerLink).toHaveAttribute('rel', 'noopener noreferrer');
    
    const healthLink = page.locator('a[href="http://localhost:8000/health"]');
    await expect(healthLink).toHaveAttribute('target', '_blank');
    await expect(healthLink).toHaveAttribute('rel', 'noopener noreferrer');
  });

  test('error states are announced properly', async ({ page }) => {
    // Mock API failure
    await page.route('**/api/channels/', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Server error' })
      });
    });
    
    await page.reload();
    
    // Error message should be visible and descriptive
    const errorMessage = page.locator('text=Error');
    await expect(errorMessage).toBeVisible({ timeout: 10000 });
    
    // Should have helpful error description
    await expect(page.locator('text=Make sure the FastAPI backend is running'))
      .toBeVisible();
  });

  test('loading states are accessible', async ({ page }) => {
    // Mock slow API to test loading state
    await page.route('**/api/channels/', async route => {
      // Delay response to test loading state
      await new Promise(resolve => setTimeout(resolve, 1000));
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });
    
    await page.reload();
    
    // Should show loading indicator
    await expect(page.locator('text=Loading channels...')).toBeVisible();
  });

  test('responsive design works on mobile', async ({ page, browserName }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check that content is still accessible
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('.channel-card').first()).toBeVisible();
    
    // Check that form inputs are still usable
    const markupInput = page.locator('.markup-input').first();
    await expect(markupInput).toBeVisible();
    await markupInput.tap(); // Use tap instead of click on mobile
    await expect(markupInput).toBeFocused();
  });

  test('color contrast and visual elements', async ({ page }) => {
    // Check that demo badge is visible
    const demoBadge = page.locator('.demo-badge');
    await expect(demoBadge).toBeVisible();
    await expect(demoBadge).toHaveCSS('background-color', 'rgb(255, 107, 53)');
    await expect(demoBadge).toHaveCSS('color', 'rgb(255, 255, 255)');
    
    // Check button styles
    const updateButton = page.locator('.update-btn').first();
    await expect(updateButton).toHaveCSS('background-color', 'rgb(0, 112, 243)');
    await expect(updateButton).toHaveCSS('color', 'rgb(255, 255, 255)');
  });
});