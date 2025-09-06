// @ts-check
import { test, expect } from '@playwright/test';

// Mock API responses for testing
test.describe('Channel Management', () => {
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
          },
          {
            id: 'Q2hhbm5lbDoz', 
            name: 'SPb Store',
            slug: 'spb',
            markup_percent: '12.50'
          }
        ])
      });
    });
  });
  
  test('should display channels correctly', async ({ page }) => {
    await page.goto('/');
    
    // Wait for channels to load
    await expect(page.locator('.channel-card')).toHaveCount(3);
    
    // Check if all channels are displayed
    await expect(page.locator('.channel-card').nth(0)).toContainText('Default Channel');
    await expect(page.locator('.channel-card').nth(1)).toContainText('Moscow Store');
    await expect(page.locator('.channel-card').nth(2)).toContainText('SPb Store');
    
    // Check markup percentages
    await expect(page.locator('.channel-card').nth(0)).toContainText('0.00%');
    await expect(page.locator('.channel-card').nth(1)).toContainText('15.00%');
    await expect(page.locator('.channel-card').nth(2)).toContainText('12.50%');
  });
  
  test('should handle markup update form interaction', async ({ page }) => {
    // Mock the markup update endpoint
    await page.route('**/api/channels/markup', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, markup: { channel_id: 'Q2hhbm5lbDoy', markup_percent: 20 } })
      });
    });
    
    await page.goto('/');
    
    // Wait for channels to load
    await expect(page.locator('.channel-card')).toHaveCount(3);
    
    // Find the Moscow Store channel and test markup update
    const moscowCard = page.locator('.channel-card').filter({ hasText: 'Moscow Store' });
    const markupInput = moscowCard.locator('input[placeholder="15.5"]');
    const updateButton = moscowCard.locator('button:has-text("Update")');
    
    // Enter new markup value
    await markupInput.fill('20');
    await updateButton.click();
    
    // Should show saving state
    await expect(updateButton).toContainText('Saving...');
  });
  
  test('should handle price calculation form interaction', async ({ page }) => {
    // Mock the price calculation endpoint
    await page.route('**/api/prices/calculate', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          product_id: 'demo_product',
          channel_id: 'Q2hhbm5lbDoy',
          base_price: '100.00',
          markup_percent: '15.00',
          final_price: '115.00',
          currency: 'USD'
        })
      });
    });
    
    await page.goto('/');
    
    // Wait for channels to load
    await expect(page.locator('.channel-card')).toHaveCount(3);
    
    // Find the Moscow Store channel and test price calculation
    const moscowCard = page.locator('.channel-card').filter({ hasText: 'Moscow Store' });
    const priceInput = moscowCard.locator('input[placeholder="100.00"]');
    const calculateButton = moscowCard.locator('button:has-text("Calculate")');
    
    // Enter base price
    await priceInput.fill('100');
    await calculateButton.click();
    
    // Should show calculating state
    await expect(calculateButton).toContainText('Calculating...');
    
    // Should show price calculation result
    await expect(page.locator('.bg-green-50')).toContainText('Price Calculation Result');
    await expect(page.locator('.bg-green-50')).toContainText('$100.00');
    await expect(page.locator('.bg-green-50')).toContainText('15.00%');
    await expect(page.locator('.bg-green-50')).toContainText('$115.00');
  });
  
  test('should show error when API fails', async ({ page }) => {
    // Mock API failure
    await page.route('**/api/channels/', async (route) => {
      await route.fulfill({
        status: 500,
        body: 'Server Error'
      });
    });
    
    await page.goto('/');
    
    // Should show error message
    await expect(page.locator('.error-message')).toBeVisible();
    await expect(page.locator('.error-message')).toContainText('Failed to fetch channels');
    
    // Should show retry button
    await expect(page.locator('button:has-text("Retry")')).toBeVisible();
  });
  
  test('should validate markup input values', async ({ page }) => {
    await page.goto('/');
    
    // Wait for channels to load
    await expect(page.locator('.channel-card')).toHaveCount(3);
    
    // Find the first channel and test invalid markup
    const firstCard = page.locator('.channel-card').first();
    const markupInput = firstCard.locator('input[placeholder="15.5"]');
    const updateButton = firstCard.locator('button:has-text("Update")');
    
    // Test with negative value
    await markupInput.fill('-5');
    await updateButton.click();
    
    // Should show validation error
    await expect(firstCard.locator('text=Please enter a valid markup between 0 and 1000')).toBeVisible();
    
    // Test with value over 1000
    await markupInput.fill('1001');
    await updateButton.click();
    
    // Should show validation error
    await expect(firstCard.locator('text=Please enter a valid markup between 0 and 1000')).toBeVisible();
  });
});
