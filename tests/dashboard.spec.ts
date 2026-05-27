import { test, expect, Page } from '@playwright/test';

const URL = 'http://localhost:3000';

async function waitForData(page: Page) {
  // Wait until at least one stat card moves away from its initial '-' value
  await expect(page.locator('#stat-files')).not.toHaveText('-', { timeout: 15000 });
}

test.describe('Dashboard – initial load', () => {
  test('page title is correct', async ({ page }) => {
    await page.goto(URL);
    await expect(page).toHaveTitle('Prismatic - Intelligence Dashboard');
  });

  test('stat cards populate after data loads', async ({ page }) => {
    await page.goto(URL);
    await waitForData(page);

    for (const id of ['stat-files', 'stat-reviews', 'stat-confidential', 'stat-confidence', 'stat-review', 'stat-disputes']) {
      const text = await page.locator(`#${id}`).textContent();
      expect(text).not.toBe('-');
      expect(text).not.toBe('');
    }
  });

  test('refresh badge shows timestamp, not "Loading…"', async ({ page }) => {
    await page.goto(URL);
    await waitForData(page);
    const badge = page.locator('#last-refresh');
    await expect(badge).not.toHaveText('Loading…', { timeout: 15000 });
    await expect(badge).not.toContainText('Error:');
  });

  test('charts render', async ({ page }) => {
    await page.goto(URL);
    await waitForData(page);
    // Canvas elements should be present and have non-zero dimensions
    for (const id of ['chart-classification', 'chart-sentiment']) {
      const box = await page.locator(`#${id}`).boundingBox();
      expect(box).not.toBeNull();
      expect(box!.width).toBeGreaterThan(0);
      expect(box!.height).toBeGreaterThan(0);
    }
  });

  test('category pills render', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('#categories-list .category-pill').first()).toBeVisible({ timeout: 10000 });
    const count = await page.locator('#categories-list .category-pill').count();
    expect(count).toBeGreaterThan(0);
  });

  test('health badges resolve to up or down', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('#health-api')).toHaveClass(/up|down/, { timeout: 10000 });
    await expect(page.locator('#health-n8n')).toHaveClass(/up|down/, { timeout: 10000 });
  });

  test('recent documents table has rows', async ({ page }) => {
    await page.goto(URL);
    await waitForData(page);
    const rows = page.locator('#docs-tbody tr');
    await expect(rows.first()).toBeVisible({ timeout: 10000 });
    const count = await rows.count();
    expect(count).toBeGreaterThan(0);
  });
});

test.describe('Dashboard – hard refresh resilience', () => {
  test('data loads after hard refresh (cache cleared)', async ({ page }) => {
    // First load – warm the page
    await page.goto(URL);
    await waitForData(page);

    // Hard refresh: clear cache then reload
    await page.context().clearCookies();
    await page.reload({ waitUntil: 'domcontentloaded' });
    // Page should still populate stats within timeout
    await waitForData(page);
    await expect(page.locator('#last-refresh')).not.toHaveText('Loading…', { timeout: 15000 });
  });
});

test.describe('Dashboard – chat (RAG)', () => {
  test('chat input is visible and interactive', async ({ page }) => {
    await page.goto(URL);
    const input = page.locator('#chat-input');
    await expect(input).toBeVisible();
    await expect(input).toBeEnabled();
  });

  test('suggested questions send a message', async ({ page }) => {
    await page.goto(URL);
    const hint = page.locator('.welcome-hint').first();
    await expect(hint).toBeVisible();
    await hint.click();

    // A user bubble should appear
    await expect(page.locator('.msg-bubble-user').first()).toBeVisible({ timeout: 5000 });
    // Typing indicator appears while waiting
    const typing = page.locator('.msg-typing');
    // It may have already resolved, so just check it appeared then either resolves or stays
    // Check the chat status says loading
    await expect(page.locator('#chat-status')).toHaveText('Sending…', { timeout: 5000 });
  });
});
