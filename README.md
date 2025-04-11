
# Shopee Scraper

A tool to scrape Shopee Taiwan's item detail data.

There are two versions to this tool, TypeScript (Concept) and Python



## Dependencies

- Python
- Flask
- Selenium
- undetected_chromium
## Usage
```
python3 scraper.py
```
After logging in, console should show, "You can now request.".

Example:
```
GET "http://localhost:5000/shopee?storeId=<storeId>&dealId=<dealId>"
```

## FAQ

#### Does the TypeScript version work?

No, since there are no proper stealth browser alternatives in TypeScript.
What is used here (Puppeteer Stealth) is detected by Shopee, even though it passes [SannySoft](https://bot.sannysoft.com)

#### Why does the Python version require manual login, and not cookie usage?

Adding Cookie for some reason also doesnt work in Shopee, they are most likely blocking it aswell.

#### Why is this not directly requesting to and taking from the get_pc endpoint?

Requesting directly to the API get_pc endpoint results in a quick suspension of the account. Any requests after that doesnt work anymore. But taking the data from network responses of get_pc internally with a browser works even on suspension.

### What is the evading mechanism in this tool?

To be honest, not much. There are two main problems to scraping shopee:

* Random captcha challenges
* Inescapable error page

This tool prompts user to solve captcha when the current url has

"https://shopee.tw/verify/captcha?anti_bot_tracking_id"


and a restart (reload just gives you the error page again) when the current url has

"https://shopee.tw/verify/traffic/error"

then it tries to re-scrape the failed attempts (captcha or error)

I tried coming up with a captcha solver, but after realizing that the slider changes its drag on every captcha, it's definitely not going to come anytime soon.

### Can it handle high traffic?

I've designed this tool to simply be single threaded. Anything more than that would risk the fastest Captcha hammer from Shopee and maybe even a ban. So it depends what your definition of high traffic is, if its one requests every 30 seconds but continuous, solve the captchas and you should be good. 

Multiple requests at once, no.

### No proxies?

As far as I can tell, proxies, especially free ones, are unusable in this case. Most likely they will give you IP addresses from different countries. Even if its the same country, different cities. You dont want Shopee to see your account making a request from Singapore and 30 seconds later, Malaysia.

### Is this tool hosted anywhere?
Based on how this tool works, its not.

* Login needs to be manual
* Captchas need to be solved manually

Hence, user needs to interact with browser directly when needed.


