const { test, expect } = require('@playwright/test');
const { pathToFileURL } = require('url');
const path = require('path');

const pages = [
  'index.html',
  'cases/index.html',
  'cases/lingqi.html',
  'blog/index.html',
  'impressum.html',
  'datenschutz.html',
  'audit-beispiel.html',
  'danke.html',
  'blog/lingqi-haarausfall.html',
  'branchen/kosmetikstudios.html',
];

const expectedLinks = [
  'Referenzen',
  'Blog',
  'Premium-Audit Muster',
  'Kostenlose Potenzialanalyse',
];

function fileUrl(relativePath) {
  return pathToFileURL(path.join(process.cwd(), relativePath)).href;
}

test.use({ viewport: { width: 375, height: 667 } });

for (const relativePath of pages) {
  test(`mobile nav works on ${relativePath}`, async ({ page }) => {
    await page.addInitScript(() => {
      const originalSetTimeout = window.setTimeout;
      window.setTimeout = (callback, delay, ...args) => {
        if (String(callback).includes('audit-beispiel.pdf')) return 0;
        return originalSetTimeout(callback, delay, ...args);
      };
    });

    await page.goto(fileUrl(relativePath));

    const toggle = page.locator('.nav-toggle');
    const nav = page.locator('#primary-navigation');

    await expect(toggle, 'Hamburger button should be visible').toBeVisible();
    await expect(nav, 'Primary navigation should be closed initially').toBeHidden();

    await toggle.click();
    await expect(nav, 'Primary navigation should open after tapping hamburger').toBeVisible();
    await expect(toggle, 'aria-expanded should reflect open state').toHaveAttribute('aria-expanded', 'true');

    for (const label of expectedLinks) {
      const link = nav.getByRole('link', { name: label, exact: true });
      await expect(link, `${label} should be visible in the opened menu`).toBeVisible();
      await link.click({ trial: true });
    }

    await page.locator('body').dispatchEvent('click');
    await expect(nav, 'Primary navigation should close after outside click').toBeHidden();
    await expect(toggle, 'aria-expanded should reflect closed state').toHaveAttribute('aria-expanded', 'false');

    await toggle.click();
    await expect(nav).toBeVisible();

    const beforeUrl = page.url();
    await nav.getByRole('link', { name: 'Referenzen', exact: true }).click();

    await expect
      .poll(async () => {
        const urlChanged = page.url() !== beforeUrl;
        const menuHidden = await nav.isHidden().catch(() => true);
        return urlChanged || menuHidden;
      })
      .toBe(true);
  });
}
