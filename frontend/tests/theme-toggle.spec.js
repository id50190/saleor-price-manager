// @ts-check
import { test, expect } from '@playwright/test';

test.describe('Theme System', () => {
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
          }
        ])
      });
    });
  });
  
  test('should have theme toggle button', async ({ page }) => {
    await page.goto('/');
    
    // Should have theme toggle button in top right
    const themeToggle = page.locator('.theme-toggle');
    await expect(themeToggle).toBeVisible();
    
    // Should show current theme (default is system)
    await expect(themeToggle.locator('button')).toContainText('System');
  });
  
  test('should switch between themes', async ({ page }) => {
    await page.goto('/');
    
    const themeButton = page.locator('.theme-toggle button');
    
    // Click to open dropdown
    await themeButton.click();
    
    // Should show theme options
    await expect(page.locator('text=Light')).toBeVisible();
    await expect(page.locator('text=Dark')).toBeVisible();
    await expect(page.locator('text=System')).toBeVisible();
    
    // Switch to dark theme
    await page.locator('text=Dark').click();
    
    // Should apply dark class to html element
    const htmlElement = page.locator('html');
    await expect(htmlElement).toHaveClass(/dark/);
    
    // Theme button should show Dark
    await expect(themeButton).toContainText('Dark');
  });
  
  test('should apply dark theme styling', async ({ page }) => {
    await page.goto('/');
    
    // Switch to dark theme
    await page.locator('.theme-toggle button').click();
    await page.locator('text=Dark').click();
    
    // Wait for theme to be applied
    await expect(page.locator('html')).toHaveClass(/dark/);
    
    // Check that body has dark background
    const body = page.locator('body');
    await expect(body).toHaveClass(/dark:bg-gray-900/);
    
    // Check that cards have dark styling
    const container = page.locator('div').first();
    await expect(container).toHaveClass(/dark:bg-gray-900/);
  });
  
  test('should persist theme choice', async ({ page }) => {
    await page.goto('/');
    
    // Switch to light theme
    await page.locator('.theme-toggle button').click();
    await page.locator('text=Light').click();
    
    // Reload page
    await page.reload();
    
    // Theme should still be light
    await expect(page.locator('.theme-toggle button')).toContainText('Light');
    
    // HTML should not have dark class
    const htmlElement = page.locator('html');
    await expect(htmlElement).not.toHaveClass(/dark/);
  });
  
  test('should respect system preference', async ({ page, colorScheme }) => {
    if (colorScheme === 'dark') {
      await page.goto('/');
      
      // With system theme, should apply dark mode
      const htmlElement = page.locator('html');
      await expect(htmlElement).toHaveClass(/dark/);
      
      // Theme button should show System
      await expect(page.locator('.theme-toggle button')).toContainText('System');
    }
  });
  
  test('should close dropdown when clicking outside', async ({ page }) => {
    await page.goto('/');
    
    // Open theme dropdown
    await page.locator('.theme-toggle button').click();
    await expect(page.locator('text=Light')).toBeVisible();
    
    // Click outside
    await page.locator('h1').click();
    
    // Dropdown should be closed
    await expect(page.locator('text=Light')).not.toBeVisible();
  });
  
  test('should be keyboard accessible', async ({ page }) => {
    await page.goto('/');
    
    // Focus the theme toggle button with keyboard
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab'); // May need multiple tabs to reach the button
    
    // Press Enter to open dropdown
    await page.keyboard.press('Enter');
    
    // Should show theme options
    await expect(page.locator('text=Light')).toBeVisible();
    
    // Use arrow keys to navigate and Enter to select
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('Enter');
    
    // Should close dropdown
    await expect(page.locator('text=Light')).not.toBeVisible();
  });
});
