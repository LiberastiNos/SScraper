from flask import Flask, request, jsonify
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import json
import time
import random

options = uc.ChromeOptions()
options.add_argument("--user-data-dir=profile")
options.add_argument("--start-maximized")

def create_profile():
    driver = uc.Chrome(options=options)
    driver.get("https://shopee.tw")
    time.sleep(10)
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
def shopee_scraper():
    store_id = request.args.get('storeId')
    deal_id = request.args.get('dealId')

    if not store_id or not deal_id:
        return jsonify({'error': 'Missing storeId or dealId'}), 400

    product_url = f"https://shopee.tw/滿意寶寶-日本白金-極上呵護-極上の呵護-S-60片-i.{store_id}.{deal_id}"
    network_log = []
    driver.execute_cdp_cmd("Network.enable", {})

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
                body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                network_log.append({
                    "url": url,
                    "body": body['body']
                })
        except Exception as e:
            print(f"Error capturing response: {e}")

    driver.request_interceptor = None
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled": True})

    driver.get("https://shopee.tw")
    time.sleep(10)
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "header.shopee-top.shopee-top--sticky")))
    print("Page loaded")
    driver.get(product_url)
    time.sleep(15)

    # Store request urls and match with response 
    logs = driver.get_log("performance")
    for entry in logs:
        message = json.loads(entry["message"])["message"]
        if message["method"] == "Network.requestWillBeSent":
            capture_request(message["params"])
        elif message["method"] == "Network.responseReceived":
            capture_response(message["params"])

    if network_log:
        print(f"Matched response from {network_log[0]['url']}")
        return jsonify(json.loads(network_log[0]["body"]))
    elif network_log and "90309999" in network_log[0]["body"]:
        print("Check the browser, there may be a captcha, if not try again some time later.")
    else:
        return jsonify({'error': 'No matching XHR response found'}), 404

if create_profile():
    options = uc.ChromeOptions()
    options.add_argument("--user-data-dir=profile")
    options.add_argument("--start-maximized")
    options.set_capability(
        "goog:loggingPrefs", {"performance": "ALL"}
    )
    driver = uc.Chrome(options=options)
    print("You can now request.")
    app.run()
