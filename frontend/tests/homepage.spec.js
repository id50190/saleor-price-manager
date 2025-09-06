// @ts-check
import { test, expect } from '@playwright/test';

// Get backend URL from environment
const APPLICATION_HOST = process.env.APPLICATION_HOST || '127.0.0.1';
const APPLICATION_PORT = process.env.APPLICATION_PORT || '8000';
const BACKEND_URL = `http://${APPLICATION_HOST}:${APPLICATION_PORT}`;

test.describe('Homepage', () => {
  test('should load the homepage', async ({ page }) => {
    await page.goto('/');
    
    // Check if page title is correct
    await expect(page).toHaveTitle('Saleor Price Manager');
    
    // Check main heading
    await expect(page.locator('h1')).toContainText('Saleor Price Manager');
    
    // Check demo badge
    await expect(page.locator('.demo-badge')).toContainText('DEMO MODE');
    
    // Check API info section
    await expect(page.locator('.api-info')).toBeVisible();
    await expect(page.locator('.api-info h3')).toContainText('API Information');
    
    // Check if backend links are present in API info section
    await expect(page.locator(`.api-info a[href="${BACKEND_URL}/docs"]`)).toBeVisible();
    await expect(page.locator(`.api-info a[href="${BACKEND_URL}/health"]`)).toBeVisible();
  });
  
  test('should show channel management section', async ({ page }) => {
    await page.goto('/');
    
    // Wait for the channel management section to be visible
    await expect(page.locator('h2')).toContainText('Channel Management');
    
    // Should either show loading, error, or channels
    const isLoadingVisible = await page.locator('[aria-label="Loading"]').isVisible();
    const isErrorVisible = await page.locator('.error-message').isVisible();
    const areChannelsVisible = await page.locator('.channel-card').count() > 0;
    
    expect(isLoadingVisible || isErrorVisible || areChannelsVisible).toBe(true);
  });
  
  test('should be responsive on mobile', async ({ page, isMobile }) => {
    if (isMobile) {
      await page.goto('/');
      
      // Check that the page is still usable on mobile
      await expect(page.locator('h1')).toBeVisible();
      await expect(page.locator('.demo-badge')).toBeVisible();
      
      // Check that the container is properly responsive
      const containerWidth = await page.locator('.container').boundingBox();
      expect(containerWidth?.width).toBeLessThanOrEqual(400); // Should fit on mobile screens
    }
  });
});
