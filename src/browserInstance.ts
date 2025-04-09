import puppeteer, { Browser } from 'puppeteer';

let browserInstance: Browser | null = null;

export async function getBrowser(): Promise<Browser> {
  if (!browserInstance) {
    browserInstance = await puppeteer.launch({
      headless: false,
      args: ['--start-maximized'],
      userDataDir: './profile'
    });
  }
  return browserInstance;
}
