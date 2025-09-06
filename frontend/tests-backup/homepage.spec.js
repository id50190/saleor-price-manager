import { test, expect } from '@playwright/test';

test.describe('Saleor Price Manager Homepage', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('has correct title and header', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle('Saleor Price Manager');
    
    // Check main header
    await expect(page.locator('h1')).toContainText('🚀 Saleor Price Manager');
    
    // Check demo badge
    await expect(page.locator('.demo-badge')).toContainText('DEMO MODE');
  });

  test('displays API information section', async ({ page }) => {
    // Check API info section exists
    await expect(page.locator('.api-info')).toBeVisible();
    
    // Check API links
    const swaggerLink = page.locator('a[href="http://localhost:8000/docs"]');
    await expect(swaggerLink).toBeVisible();
    
    const healthLink = page.locator('a[href="http://localhost:8000/health"]');
    await expect(healthLink).toBeVisible();
  });

  test('loads channel management section', async ({ page }) => {
    // Wait for channels to load
    await expect(page.locator('h2')).toContainText('📊 Channel Management');
    
    // Check if channels are loaded (should have at least demo channels)
    await expect(page.locator('.channel-card')).toHaveCount(3, { timeout: 10000 });
  });

  test('displays demo channels correctly', async ({ page }) => {
    // Wait for channels to load
    await page.waitForSelector('.channel-card', { timeout: 10000 });
    
    // Check Default Channel
    const defaultChannel = page.locator('.channel-card').first();
    await expect(defaultChannel.locator('h3')).toContainText('Default Channel');
    await expect(defaultChannel).toContainText('Slug: default-channel');
    await expect(defaultChannel).toContainText('Current Markup: 0%');
    
    // Check Moscow Store
    const moscowChannel = page.locator('.channel-card').nth(1);
    await expect(moscowChannel.locator('h3')).toContainText('Moscow Store');
    await expect(moscowChannel).toContainText('Current Markup: 15%');
    
    // Check SPb Store
    const spbChannel = page.locator('.channel-card').nth(2);
    await expect(spbChannel.locator('h3')).toContainText('SPb Store');
    await expect(spbChannel).toContainText('Current Markup: 10%');
  });

  test('handles API connection error gracefully', async ({ page }) => {
    // Mock API failure by intercepting requests
    await page.route('**/api/channels/', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' })
      });
    });
    
    // Reload page to trigger API call
    await page.reload();
    
    // Should show error message
    await expect(page.locator('text=Error')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Make sure the FastAPI backend is running')).toBeVisible();
  });
});