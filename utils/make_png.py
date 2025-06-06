from queue import Queue
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def generate_png(download_url:str, out_file:str, download_status_queue: Queue[int]):
    options = Options()
    options.add_argument('--headless')  # 可选：无头模式
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    while True:
        try:
            download_status_queue.put(1)
            browser = webdriver.Chrome(options=options)
            download_status_queue.put(2)
            download_status_queue.put(3)
            browser.get(download_url)
            browser.implicitly_wait(10)
            js_height = "return document.body.clientHeight"
            k=1
            height = browser.execute_script(js_height)
            while True:
                if k * 500 < height:
                    browser.execute_script(f"window.scrollTo(0, {k * 500});")
                    time.sleep(0.5)
                    height = browser.execute_script(js_height)
                    k += 1
                else:
                    break
            download_status_queue.put(5)
            time.sleep(1)
            download_status_queue.put(7)
            width = 1920#browser.execute_script("return Math.max(document.body.parentNode.scrollWidth, document.body.scrollWidth, document.body.offsetWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth, document.body.clientWidth, document.documentElement.clientWidth);")
            height = browser.execute_script("return Math.max(document.body.parentNode.scrollHeight, document.body.scrollHeight, document.body.offsetHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight);")
            print(f'width: {width}, height: {height}')
            browser.set_window_size(width + 100, height + 100)  # 设置窗口大小
            browser.save_screenshot(out_file)
            download_status_queue.put(8)
            browser.quit()
            
            download_status_queue.put(9)
            download_status_queue.put(10)
            break
        except Exception as e:
            time.sleep(0.1)

def open_printer(url: str):
    options = Options()
    options.add_argument('--headless')  # 可选：无头模式
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Chrome(options=options)
    browser.get(url)
    browser.implicitly_wait(10)
    # js_height = "return document.body.clientHeight"
    # k=1
    # height = browser.execute_script(js_height)
    # while True:
    #     if k * 500 < height:
    #         browser.execute_script(f"window.scrollTo(0, {k * 500});")
    #         time.sleep(0.5)
    #         height = browser.execute_script(js_height)
    #         k += 1
    #     else:
    #         break
    # time.sleep(1)
    # width = 1920
    # height = browser.execute_script("return Math.max(document.body.parentNode.scrollHeight, document.body.scrollHeight, document.body.offsetHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight);")
    # print(f'width: {width}, height: {height}')
    # browser.set_window_size(width + 100, height + 100)  # 设置窗口大小
    browser.execute_script("window.print();")
    time.sleep(2)
    browser.quit()
