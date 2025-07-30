import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    // Wait for the dev server to be ready
    await page.goto('/', { waitUntil: 'networkidle' });
  });

  test('should show error for network issues', async ({ page }) => {
    // Start intercepting network requests
    await page.route('**/api/auth/login', async (route) => {
      await route.abort('failed');
    });
    
    // Fill in the password
    await page.fill('input[type="password"]', 'airfare');
    
    // Click the login button
    await page.click('button:has-text("Login")');
    
    // Wait for error message
    const errorMessage = await page.waitForSelector('text=Network error occurred');
    expect(await errorMessage.isVisible()).toBeTruthy();
  });

  test('should show loading state during login', async ({ page }) => {
    // Add delay to see loading state
    await page.route('**/api/auth/login', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.fulfill({ 
        status: 200,
        body: JSON.stringify({ token: 'test-token' })
      });
    });
    
    // Fill in the password
    await page.fill('input[type="password"]', 'airfare');
    
    // Click the login button
    await page.click('button:has-text("Login")');
    
    // Check loading state
    const loadingButton = await page.waitForSelector('button:has-text("Logging in...")');
    expect(await loadingButton.isDisabled()).toBeTruthy();
  });

  test('should handle invalid password', async ({ page }) => {
    // Mock error response
    await page.route('**/api/auth/login', async (route) => {
      await route.fulfill({ 
        status: 401,
        body: JSON.stringify({ error: { message: 'Invalid password' } })
      });
    });
    
    // Fill in wrong password
    await page.fill('input[type="password"]', 'wrongpassword');
    
    // Click the login button
    await page.click('button:has-text("Login")');
    
    // Wait for error message
    const errorMessage = await page.waitForSelector('text=Invalid password');
    expect(await errorMessage.isVisible()).toBeTruthy();
  });

  test('should log in successfully and redirect', async ({ page }) => {
    // Mock successful response
    await page.route('**/api/auth/login', async (route) => {
      await route.fulfill({ 
        status: 200,
        body: JSON.stringify({ token: 'test-token' })
      });
    });
    
    // Fill in correct password
    await page.fill('input[type="password"]', 'airfare');
    
    // Click the login button
    await page.click('button:has-text("Login")');
    
    // Wait for navigation
    await page.waitForURL('**/reference-clients');
    expect(page.url()).toContain('/reference-clients');
  });

  test('should make actual API request', async ({ page }) => {
    // Fill in password
    await page.fill('input[type="password"]', 'airfare');
    
    // Start recording network
    const [response] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/api/auth/login')),
      page.click('button:has-text("Login")')
    ]);

    // Log response for debugging
    console.log('Response status:', response.status());
    console.log('Response headers:', await response.allHeaders());
    try {
      console.log('Response body:', await response.json());
    } catch (e) {
      console.log('Failed to parse response body:', await response.text());
    }

    // Check network request
    expect(response.request().method()).toBe('POST');
    expect(response.request().postData()).toBe(JSON.stringify({ password: 'airfare' }));
  });
});