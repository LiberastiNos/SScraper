from flask import Flask, request, jsonify, g
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import json
import time
import random

cooldown = {}
cooldown["until"] = 0

def captcha_check(driver):
    if "https://shopee.tw/verify/captcha?anti_bot_tracking_id" in driver.current_url:
        input("Captcha detected, please solve, click on something random on the site after, then press enter here.")
        return True
    else:
        return False

def error_check(driver):
    if "https://shopee.tw/verify/traffic/error" in driver.current_url:
        print("Traffic error page, restarting.")
        driver.quit()
        return True
    else:
        return False

def create_profile():
    options = uc.ChromeOptions()
    options.add_argument("--user-data-dir=profile")
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)
    driver.get("https://shopee.tw")
    time.sleep(10)
    if captcha_check(driver):
        print("Re-execute program.")
        return False
    try:
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.CSS_SELECTOR, "header.shopee-top.shopee-top--sticky")))
        driver.quit()
        return True
    except:
        input("Please login. Click enter if you have logged in, and re-execute the program")
        driver.quit()
        return False
   
app = Flask(__name__)


@app.route('/shopee', methods=['GET'])
def shopee_scraper(store_id=None,deal_id=None,driver_error=None): 
    if driver_error:
        scraper = driver_error
    else:
        options = uc.ChromeOptions()
        options.add_argument("--user-data-dir=profile")
        options.add_argument("--start-maximized")
        options.set_capability(
            "goog:loggingPrefs", {"performance": "ALL"}
        )
        scraper = uc.Chrome(options=options)
    
    now = time.time()
    cooldown_until = cooldown["until"]
    print(now)
    print(cooldown_until)

    if now < cooldown_until:
        retry_after = int(cooldown_until - now)
        return (jsonify({'error': 'Rate limit, Try again later.', 'retry_after': retry_after}),429,
            {'Retry-After': str(retry_after)}
        )

    if store_id is None and deal_id is None:
        store_id = request.args.get('storeId')
        deal_id = request.args.get('dealId')

    if not store_id or not deal_id:
        return jsonify({'error': 'Missing storeId or dealId'}), 400

    product_url = f"https://shopee.tw/滿意寶寶-日本白金-極上呵護-極上の呵護-S-60片-i.{store_id}.{deal_id}"
    network_log = []
    scraper.execute_cdp_cmd("Network.enable", {})

    request_id_to_url = {}

    # Intercept request URLs
    def capture_request(event):
        try:
            request_id = event.get('requestId')
            url = event['request']['url']
            request_id_to_url[request_id] = url
        except:
            pass

    # Intercept and filter response
    def capture_response(event):
        try:
            request_id = event['requestId']
            url = request_id_to_url.get(request_id, "")
            if 'get_pc' in url and event['response']['status'] == 200:
                body = scraper.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                network_log.append({
                    "url": url,
                    "body": body['body']
                })
        except Exception as e:
            print(f"Error capturing response: {e}")

    scraper.request_interceptor = None
    scraper.execute_cdp_cmd("Network.enable", {})
    scraper.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled": True})

    scraper.get("https://shopee.tw")
    time.sleep(10)

    if captcha_check(scraper):
        return shopee_scraper(store_id,deal_id)

    if error_check(scraper):
        options = uc.ChromeOptions()
        options.add_argument("--user-data-dir=profile")
        options.add_argument("--start-maximized")
        options.set_capability(
            "goog:loggingPrefs", {"performance": "ALL"}
        )
        error = uc.Chrome(options=options)
        return shopee_scraper(store_id,deal_id, error)

    WebDriverWait(scraper, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "header.shopee-top.shopee-top--sticky")))
    print("Page loaded")
    scraper.get(product_url)
    time.sleep(15)

    # Store request urls and match with response 
    logs = scraper.get_log("performance")
    for entry in logs:
        message = json.loads(entry["message"])["message"]
        if message["method"] == "Network.requestWillBeSent":
            capture_request(message["params"])
        elif message["method"] == "Network.responseReceived":
            capture_response(message["params"])

    post_now = time.time()
    cooldown["until"] = post_now + 30
    if network_log:
        print(f"Matched response from {network_log[0]['url']}")
        scraper.quit()
        return jsonify(json.loads(network_log[0]["body"]))
    elif network_log and "90309999" in network_log[0]["body"]:
        scraper.quit()
        return jsonify({'error': 'Check the browser, there may be a captcha, re request.'}), 404
    else:
        scraper.quit()
        return jsonify({'error': 'No matching XHR response found'}), 404
    
if create_profile():
    print("You can now request.")
    app.run()
