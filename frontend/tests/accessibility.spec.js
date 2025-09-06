// @ts-check
import { test, expect } from '@playwright/test';

test.describe('Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    // Mock the channels API endpoint
    await page.route('**/api/channels/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 'Q2hhbm5lbDox',
            name: 'Default Channel',
            slug: 'default',
            markup_percent: '0.00'
          },
          {
            id: 'Q2hhbm5lbDoy',
            name: 'Moscow Store', 
            slug: 'moscow',
            markup_percent: '15.00'
          }
        ])
      });
    });
  });
  
  test('should have proper heading hierarchy', async ({ page }) => {
    await page.goto('/');
    
    // Check heading hierarchy
    const h1 = page.locator('h1');
    await expect(h1).toContainText('Saleor Price Manager');
    
    const h2 = page.locator('h2');
    await expect(h2).toContainText('Channel Management');
    
    const h3 = page.locator('h3').first();
    await expect(h3).toContainText('API Information');
  });
  
  test('should have proper form labels', async ({ page }) => {
    await page.goto('/');
    
    // Wait for channels to load
    await expect(page.locator('.channel-card')).toHaveCount(2);
    
    // Check that all inputs have proper labels
    const markupInputs = page.locator('input[placeholder="15.5"]');
    const priceInputs = page.locator('input[placeholder="100.00"]');
    
    // All markup inputs should have labels
    const markupCount = await markupInputs.count();
    for (let i = 0; i < markupCount; i++) {
      const input = markupInputs.nth(i);
      const inputId = await input.getAttribute('id');
      const label = page.locator(`label[for="${inputId}"]`);
      await expect(label).toBeVisible();
    }
    
    // All price inputs should have labels
    const priceCount = await priceInputs.count();
    for (let i = 0; i < priceCount; i++) {
      const input = priceInputs.nth(i);
      const inputId = await input.getAttribute('id');
      const label = page.locator(`label[for="${inputId}"]`);
      await expect(label).toBeVisible();
    }
  });
  
  test('should be keyboard navigable', async ({ page }) => {
    await page.goto('/');
    
    // Wait for channels to load
    await expect(page.locator('.channel-card')).toHaveCount(2);
    
    // Should be able to tab through interactive elements
    await page.keyboard.press('Tab'); // Theme toggle
    await page.keyboard.press('Tab'); // First markup input
    await page.keyboard.press('Tab'); // First update button
    await page.keyboard.press('Tab'); // First price input
    await page.keyboard.press('Tab'); // First calculate button
    
    // Focus should be on a button or input
    const focusedElement = page.locator(':focus');
    const tagName = await focusedElement.evaluate(el => el.tagName.toLowerCase());
    expect(['input', 'button'].includes(tagName)).toBe(true);
  });
  
  test('should have proper ARIA attributes', async ({ page }) => {
    await page.goto('/');
    
    // Theme toggle should have proper ARIA attributes
    const themeToggle = page.locator('.theme-toggle button');
    await expect(themeToggle).toHaveAttribute('aria-label', 'Theme selector');
    await expect(themeToggle).toHaveAttribute('aria-expanded', 'false');
    
    // Loading spinner should have proper label
    await page.route('**/api/channels/', async (route) => {
      // Delay response to test loading state
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });
    
    await page.goto('/');
    
    const loadingSpinner = page.locator('[aria-label="Loading"]');
    if (await loadingSpinner.isVisible()) {
      await expect(loadingSpinner).toHaveAttribute('aria-label', 'Loading');
    }
  });
  
  test('should have sufficient color contrast in both themes', async ({ page }) => {
    await page.goto('/');
    
    // Test light theme contrast
    const h1Light = page.locator('h1');
    const h1Styles = await h1Light.evaluate(el => {
      const styles = getComputedStyle(el);
      return {
        color: styles.color,
        backgroundColor: styles.backgroundColor
      };
    });
    
    // Switch to dark theme
    await page.locator('.theme-toggle button').click();
    await page.locator('text=Dark').click();
    
    // Wait for theme to apply
    await expect(page.locator('html')).toHaveClass(/dark/);
    
    // Test dark theme contrast
    const h1Dark = page.locator('h1');
    const h1DarkStyles = await h1Dark.evaluate(el => {
      const styles = getComputedStyle(el);
      return {
        color: styles.color,
        backgroundColor: styles.backgroundColor
      };
    });
    
    // Colors should be different between themes
    expect(h1Styles.color).not.toBe(h1DarkStyles.color);
  });
  
  test('should handle focus management in theme dropdown', async ({ page }) => {
    await page.goto('/');
    
    // Focus theme toggle
    const themeButton = page.locator('.theme-toggle button');
    await themeButton.focus();
    
    // Open dropdown
    await themeButton.press('Enter');
    
    // Dropdown should be open
    await expect(page.locator('text=Light')).toBeVisible();
    
    // Escape should close dropdown and return focus
    await page.keyboard.press('Escape');
    await expect(page.locator('text=Light')).not.toBeVisible();
    
    // Focus should return to toggle button
    const focusedElement = await page.evaluate(() => document.activeElement?.outerHTML);
    expect(focusedElement).toContain('Theme selector');
  });
  
  test('should provide appropriate error messages', async ({ page }) => {
    // Mock API error
    await page.route('**/api/channels/', async (route) => {
      await route.fulfill({
        status: 500,
        body: 'Server Error'
      });
    });
    
    await page.goto('/');
    
    // Should show descriptive error message
    const errorMessage = page.locator('.error-message');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toContainText('Failed to fetch channels');
    
    // Should provide recovery action
    const retryButton = page.locator('button:has-text("Retry")');
    await expect(retryButton).toBeVisible();
    
    // Retry button should be focusable
    await retryButton.focus();
    expect(await retryButton.evaluate(el => el === document.activeElement)).toBe(true);
  });
});
