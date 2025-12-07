/**
 * End-to-End Tests for ChatWidget
 * Tests user interactions with the chatbot using Playwright
 */

import { test, expect, Page } from '@playwright/test';

// ====================
// Test Configuration
// ====================

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';
const API_URL = process.env.API_URL || 'http://localhost:8000/api';

test.describe('ChatWidget E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to docs page
    await page.goto(`${BASE_URL}/docs/module-01-ros2/01-introduction`);
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
  });

  // ====================
  // Test 1: Widget Visibility
  // ====================

  test('should display floating chat button on page load', async ({ page }) => {
    // Check that floating button exists
    const floatingButton = page.locator('[aria-label="Open chat"]');
    await expect(floatingButton).toBeVisible();
    
    // Verify it has the chat icon
    const chatIcon = floatingButton.locator('svg');
    await expect(chatIcon).toBeVisible();
  });

  // ====================
  // Test 2: Expand/Collapse Widget
  // ====================

  test('should expand chat window when clicking floating button', async ({ page }) => {
    // Click floating button
    await page.click('[aria-label="Open chat"]');
    
    // Verify chat window appears
    const chatWindow = page.locator('text=AI Learning Assistant');
    await expect(chatWindow).toBeVisible();
    
    // Verify message list is visible
    const messageList = page.locator('text=Welcome to the AI Learning Assistant!');
    await expect(messageList).toBeVisible();
  });

  test('should minimize chat window when clicking minimize button', async ({ page }) => {
    // Expand chat
    await page.click('[aria-label="Open chat"]');
    
    // Click minimize button
    await page.click('[aria-label="Minimize chat"]');
    
    // Verify chat window is hidden
    const chatWindow = page.locator('text=AI Learning Assistant');
    await expect(chatWindow).not.toBeVisible();
    
    // Verify floating button is visible again
    const floatingButton = page.locator('[aria-label="Open chat"]');
    await expect(floatingButton).toBeVisible();
  });

  // ====================
  // Test 3: Send Message & Receive Response
  // ====================

  test('should send a question and receive an answer', async ({ page }) => {
    // Mock API response
    await page.route(`${API_URL}/answer`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          answer: 'ROS 2 is the next generation of the Robot Operating System...',
          sources: [
            {
              chunk_id: 'chunk_123',
              text: 'ROS 2 fundamentals...',
              metadata: {
                source: 'module-01-ros2/01-introduction',
                module: 'module-01-ros2',
                chapter: 'Introduction',
              },
              score: 0.95,
            },
          ],
          metadata: {
            model: 'gpt-4',
            retrieval_time_ms: 50,
            generation_time_ms: 500,
          },
        }),
      });
    });

    // Open chat
    await page.click('[aria-label="Open chat"]');
    
    // Type question
    const textarea = page.locator('textarea[aria-label="Chat input"]');
    await textarea.fill('What is ROS 2?');
    
    // Send message
    await page.click('[aria-label="Send message"]');
    
    // Verify user message appears
    await expect(page.locator('text=What is ROS 2?')).toBeVisible();
    
    // Wait for assistant response (with timeout)
    const assistantMessage = page.locator('text=ROS 2 is the next generation');
    await expect(assistantMessage).toBeVisible({ timeout: 10000 });
    
    // Verify sources are displayed
    const sourcesButton = page.locator('text=Sources (1)');
    await expect(sourcesButton).toBeVisible();
  });

  // ====================
  // Test 4: Loading State
  // ====================

  test('should show loading indicator while waiting for response', async ({ page }) => {
    // Delay API response
    await page.route(`${API_URL}/answer`, async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 2000)); // 2s delay
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          answer: 'Test answer',
          sources: [],
          metadata: {
            model: 'gpt-4',
            retrieval_time_ms: 50,
            generation_time_ms: 500,
          },
        }),
      });
    });

    // Open chat and send message
    await page.click('[aria-label="Open chat"]');
    await page.fill('textarea[aria-label="Chat input"]', 'Test question');
    await page.click('[aria-label="Send message"]');
    
    // Verify loading indicator appears (typing dots)
    const loadingIndicator = page.locator('.typingIndicator');
    await expect(loadingIndicator).toBeVisible();
    
    // Verify loading indicator disappears after response
    await expect(loadingIndicator).not.toBeVisible({ timeout: 5000 });
  });

  // ====================
  // Test 5: Error Handling
  // ====================

  test('should display error message when API fails', async ({ page }) => {
    // Mock API error
    await page.route(`${API_URL}/answer`, async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Internal server error',
        }),
      });
    });

    // Open chat and send message
    await page.click('[aria-label="Open chat"]');
    await page.fill('textarea[aria-label="Chat input"]', 'Test question');
    await page.click('[aria-label="Send message"]');
    
    // Verify error message appears
    const errorMessage = page.locator('text=Sorry, I encountered an error');
    await expect(errorMessage).toBeVisible({ timeout: 5000 });
    
    // Verify error banner appears
    const errorBanner = page.locator('text=Failed to get response');
    await expect(errorBanner).toBeVisible();
  });

  // ====================
  // Test 6: Source Citations
  // ====================

  test('should expand and collapse source citations', async ({ page }) => {
    // Mock API response with sources
    await page.route(`${API_URL}/answer`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          answer: 'Test answer',
          sources: [
            {
              chunk_id: 'chunk_1',
              text: 'Source text 1',
              metadata: {
                source: 'module-01-ros2/01-introduction',
                module: 'module-01-ros2',
              },
              score: 0.9,
            },
            {
              chunk_id: 'chunk_2',
              text: 'Source text 2',
              metadata: {
                source: 'module-01-ros2/02-nodes-topics-services',
                module: 'module-01-ros2',
              },
              score: 0.85,
            },
          ],
          metadata: {
            model: 'gpt-4',
            retrieval_time_ms: 50,
            generation_time_ms: 500,
          },
        }),
      });
    });

    // Open chat and send message
    await page.click('[aria-label="Open chat"]');
    await page.fill('textarea[aria-label="Chat input"]', 'Test question');
    await page.click('[aria-label="Send message"]');
    
    // Wait for response
    await expect(page.locator('text=Test answer')).toBeVisible();
    
    // Click sources toggle
    await page.click('text=Sources (2)');
    
    // Verify sources list appears
    await expect(page.locator('text=Source text 1')).toBeVisible();
    await expect(page.locator('text=Source text 2')).toBeVisible();
    
    // Click again to collapse
    await page.click('text=Sources (2)');
    
    // Verify sources list is hidden
    await expect(page.locator('text=Source text 1')).not.toBeVisible();
  });

  // ====================
  // Test 7: Keyboard Interactions
  // ====================

  test('should send message on Enter key', async ({ page }) => {
    // Mock API
    await page.route(`${API_URL}/answer`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          answer: 'Test answer',
          sources: [],
          metadata: {
            model: 'gpt-4',
            retrieval_time_ms: 50,
            generation_time_ms: 500,
          },
        }),
      });
    });

    // Open chat
    await page.click('[aria-label="Open chat"]');
    
    // Type and press Enter
    const textarea = page.locator('textarea[aria-label="Chat input"]');
    await textarea.fill('Test question');
    await textarea.press('Enter');
    
    // Verify message was sent
    await expect(page.locator('text=Test question')).toBeVisible();
  });

  test('should create new line on Shift+Enter', async ({ page }) => {
    // Open chat
    await page.click('[aria-label="Open chat"]');
    
    // Type multiline message
    const textarea = page.locator('textarea[aria-label="Chat input"]');
    await textarea.fill('Line 1');
    await textarea.press('Shift+Enter');
    await textarea.type('Line 2');
    
    // Verify textarea contains newline
    const value = await textarea.inputValue();
    expect(value).toContain('\n');
  });

  // ====================
  // Test 8: Responsive Design
  // ====================

  test('should adapt to mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Open chat
    await page.click('[aria-label="Open chat"]');
    
    // Verify chat takes full screen
    const chatWindow = page.locator('h3:has-text("AI Learning Assistant")').locator('..');
    const box = await chatWindow.boundingBox();
    
    expect(box?.width).toBeGreaterThanOrEqual(375);
    expect(box?.height).toBeGreaterThanOrEqual(600);
  });

  // ====================
  // Test 9: Clear Chat History
  // ====================

  test('should persist messages during session', async ({ page }) => {
    // Mock API
    await page.route(`${API_URL}/answer`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          answer: 'Test answer',
          sources: [],
          metadata: {
            model: 'gpt-4',
            retrieval_time_ms: 50,
            generation_time_ms: 500,
          },
        }),
      });
    });

    // Send first message
    await page.click('[aria-label="Open chat"]');
    await page.fill('textarea[aria-label="Chat input"]', 'Question 1');
    await page.click('[aria-label="Send message"]');
    await expect(page.locator('text=Question 1')).toBeVisible();
    
    // Minimize and reopen
    await page.click('[aria-label="Minimize chat"]');
    await page.click('[aria-label="Open chat"]');
    
    // Verify first message is still there
    await expect(page.locator('text=Question 1')).toBeVisible();
    
    // Send second message
    await page.fill('textarea[aria-label="Chat input"]', 'Question 2');
    await page.click('[aria-label="Send message"]');
    
    // Verify both messages are visible
    await expect(page.locator('text=Question 1')).toBeVisible();
    await expect(page.locator('text=Question 2')).toBeVisible();
  });
});
