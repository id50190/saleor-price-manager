import { test, expect } from '@playwright/test';

test.describe('Channel Management Features', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Wait for channels to load
    await page.waitForSelector('.channel-card', { timeout: 10000 });
  });

  test('can update markup for a channel', async ({ page }) => {
    // Find the first channel card
    const firstChannel = page.locator('.channel-card').first();
    
    // Find the markup input field
    const markupInput = firstChannel.locator('.markup-input').first();
    
    // Clear and enter new markup value
    await markupInput.clear();
    await markupInput.fill('25');
    
    // Click update button
    const updateButton = firstChannel.locator('.update-btn').first();
    
    // Mock successful API response
    await page.route('**/api/channels/markup', route => {
      expect(route.request().postDataJSON()).toMatchObject({
        channel_id: expect.any(String),
        markup_percent: 25
      });
      
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          markup: { channel_id: 'Q2hhbm5lbDox', markup_percent: '25.00' }
        })
      });
    });
    
    // Mock updated channels list
    await page.route('**/api/channels/', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 'Q2hhbm5lbDox',
            name: 'Default Channel',
            slug: 'default-channel',
            markup_percent: '25',
            metadata: [{ key: 'price_markup_percent', value: '25' }]
          },
          // ... other channels
        ])
      });
    });
    
    await updateButton.click();
    
    // Check for success message (alert)
    page.on('dialog', async dialog => {
      expect(dialog.message()).toContain('✅ Markup updated successfully!');
      await dialog.accept();
    });
  });

  test('can calculate price for a product', async ({ page }) => {
    // Find Moscow Store channel (15% markup)
    const moscowChannel = page.locator('.channel-card').nth(1);
    
    // Find price calculation input
    const priceInput = moscowChannel.locator('.markup-input').nth(1);
    
    // Enter test price
    await priceInput.clear();
    await priceInput.fill('100');
    
    // Mock price calculation API response
    await page.route('**/api/prices/calculate', route => {
      expect(route.request().postDataJSON()).toMatchObject({
        product_id: 'demo_product',
        channel_id: expect.any(String),
        base_price: 100
      });
      
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          product_id: 'demo_product',
          channel_id: 'Q2hhbm5lbDoy',
          base_price: '100.0',
          markup_percent: '15',
          final_price: '115.00',
          currency: 'USD'
        })
      });
    });
    
    // Click calculate button
    const calculateButton = moscowChannel.locator('.update-btn').nth(1);
    await calculateButton.click();
    
    // Wait for calculation result to appear
    const resultCard = page.locator('.channel-card[style*="background-color: #e8f5e8"]');
    await expect(resultCard).toBeVisible({ timeout: 5000 });
    
    // Check calculation result
    await expect(resultCard).toContainText('Base Price: $100.0');
    await expect(resultCard).toContainText('Markup: 15%');
    await expect(resultCard).toContainText('Final Price: $115.00');
  });

  test('shows retry button when API fails', async ({ page }) => {
    // Mock API failure
    await page.route('**/api/channels/', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Server error' })
      });
    });
    
    // Reload page
    await page.reload();
    
    // Should show retry button
    await expect(page.locator('button:has-text("🔄 Retry")')).toBeVisible({ timeout: 10000 });
    
    // Test retry functionality
    await page.route('**/api/channels/', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 'Q2hhbm5lbDox',
            name: 'Default Channel',
            slug: 'default-channel',
            markup_percent: '0',
            metadata: [{ key: 'price_markup_percent', value: '0' }]
          }
        ])
      });
    });
    
    await page.locator('button:has-text("🔄 Retry")').click();
    
    // Should now show channels
    await expect(page.locator('.channel-card')).toBeVisible({ timeout: 5000 });
  });

  test('validates markup input values', async ({ page }) => {
    const firstChannel = page.locator('.channel-card').first();
    const markupInput = firstChannel.locator('.markup-input').first();
    
    // Test negative value (should be constrained by input attributes)
    await markupInput.fill('-5');
    await markupInput.press('Tab'); // Trigger validation
    
    // HTML5 validation should prevent negative values
    const inputValue = await markupInput.inputValue();
    expect(parseFloat(inputValue)).toBeGreaterThanOrEqual(0);
    
    // Test very large value
    await markupInput.clear();
    await markupInput.fill('999');
    await markupInput.press('Tab');
    
    // Should be within reasonable range (defined by max attribute)
    const largeInputValue = await markupInput.inputValue();
    expect(parseFloat(largeInputValue)).toBeLessThanOrEqual(100);
  });

  test('keyboard navigation works for markup update', async ({ page }) => {
    const firstChannel = page.locator('.channel-card').first();
    const markupInput = firstChannel.locator('.markup-input').first();
    
    // Mock API response
    await page.route('**/api/channels/markup', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, markup: { markup_percent: '20.00' } })
      });
    });
    
    // Enter value and press Enter (should trigger update)
    await markupInput.clear();
    await markupInput.fill('20');
    await markupInput.press('Enter');
    
    // Should trigger API call (we already mocked it)
    // Check for success dialog
    page.on('dialog', async dialog => {
      expect(dialog.message()).toContain('✅ Markup updated successfully!');
      await dialog.accept();
    });
  });

  test('keyboard navigation works for price calculation', async ({ page }) => {
    const moscowChannel = page.locator('.channel-card').nth(1);
    const priceInput = moscowChannel.locator('.markup-input').nth(1);
    
    // Mock API response
    await page.route('**/api/prices/calculate', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          base_price: '50.0',
          markup_percent: '15',
          final_price: '57.50',
          currency: 'USD'
        })
      });
    });
    
    // Enter value and press Enter (should trigger calculation)
    await priceInput.clear();
    await priceInput.fill('50');
    await priceInput.press('Enter');
    
    // Wait for result
    await expect(page.locator('.channel-card[style*="background-color: #e8f5e8"]'))
      .toBeVisible({ timeout: 5000 });
  });
});