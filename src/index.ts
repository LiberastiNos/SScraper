import puppeteer from 'puppeteer-extra'
import StealthPlugin from 'puppeteer-extra-plugin-stealth'
import express, { Request, Response } from 'express';
import { getBrowser } from './browserInstance';
import fs from 'fs';

const app = express();
const PORT = 3000;
puppeteer.use(StealthPlugin())
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

async function run() {
  const browser = await getBrowser();
  const page = await browser.newPage();
  // rotate UA
  const userAgents: string[] = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.2365.66',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Android 13; Mobile; rv:124.0) Gecko/124.0 Firefox/124.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) CriOS/122.0.6261.95 Mobile/15E148 Safari/604.1',
  ]

  const customUA = userAgents[Math.floor(Math.random() * userAgents.length)]
  console.log(customUA)
  // res like human
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  await page.setUserAgent(customUA);
  await page.goto('https://shopee.tw')
  // login here, manual
  // check something that indicates login was successful, should be in the homepage
  const isPresent = await page.$('header.shopee-top.shopee-top--sticky') !== null;
  if (isPresent) {
    console.log("You are logged in. API is usable.")
  }
  else {
      console.log("Log in manually. Press ENTER here when done.");
      process.stdin.resume();
      await new Promise(resolve => process.stdin.once('data', resolve));
      console.log("API now usable if you're logged in.")
  }
}

// new tab, then open link 
// a-i links dont work anymore, 滿意寶寶-日本白金-極上呵護-極上の呵護-S-60片-i, this works. 
// start getting deal id and store id, open link, get response
app.get('/shopee', async (req, res) => {
  const browser = await getBrowser();
  const { storeId, dealId } = req.query;
  if (!storeId || !dealId) {
    res.status(400).send('Missing storeId or dealId');
  }

  const url = `https://shopee.tw/滿意寶寶-日本白金-極上呵護-極上の呵護-S-60片-i.${storeId}.${dealId}`;
  const newtab = await browser.newPage();

  let responseData: any = null;

  newtab.on('response', async (response) => {
    const reqUrl = response.url();
    const resourceType = response.request().resourceType();

    if (reqUrl.includes('get_pc') && resourceType === 'xhr') {
      try {
        const json = await response.json();
        responseData = json;
        console.log(`Matched response from ${reqUrl}`, json);
      } catch (err) {
        console.error('Error parsing JSON response:', err);
      }
    }
  });

  await newtab.goto(url, { waitUntil: 'networkidle2' });

  // process XHRs
  await sleep(60000)
  await newtab.close();

  if (responseData) {
    res.json(responseData);
  } else {
    res.status(404).send('No matching XHR response found');
  }
});

run()

app.listen(PORT, () => {
    console.log(`Gateway running at http://localhost:${PORT}/shopee`);
});

