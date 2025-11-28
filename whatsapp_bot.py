"""
WhatsApp Web Automation Bot
Professional implementation for macOS, Windows, and Linux
Supports: Chrome, Brave, Firefox, Edge
"""
import time
import platform
import os
import logging
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('WhatsAppBot')


class WhatsAppBot:
    BROWSER_PATHS = {
        'Darwin': {
            'chrome': '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            'brave': '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
            'firefox': '/Applications/Firefox.app/Contents/MacOS/firefox',
            'edge': '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
        },
        'Windows': {
            'chrome': [r'C:\Program Files\Google\Chrome\Application\chrome.exe', r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'],
            'brave': [r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe', r'C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe'],
            'firefox': [r'C:\Program Files\Mozilla Firefox\firefox.exe', r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe'],
            'edge': [r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'],
        },
        'Linux': {
            'chrome': ['/usr/bin/google-chrome', '/usr/bin/google-chrome-stable'],
            'brave': ['/usr/bin/brave-browser', '/usr/bin/brave'],
            'firefox': ['/usr/bin/firefox'],
            'edge': ['/usr/bin/microsoft-edge'],
        }
    }
    
    SELECTORS = {
        'qr_canvas': '//canvas[contains(@aria-label, "Scan")]',
        'side_panel': '//div[@id="side"]',
        'message_input': ['//div[@contenteditable="true"][@data-tab="10"]', '//div[@title="Type a message"]', '//footer//div[@contenteditable="true"]'],
        'attachment_button': ['//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[1]/div/span/button', '//footer//button[contains(@aria-label, "Attach")]', '//span[@data-icon="plus"]/..'],
        'document_option': ['//*[@id="app"]/div/div/span[6]/div/ul/div/div/div[1]/li/div', '//li[contains(@data-animate-dropdown-item, "true")][1]//div'],
        'file_input': '//input[@type="file"]',
        'caption_input': ['//*[@id="app"]/div/div/div[3]/div/div[3]/div[2]/div/span/div/div/div/div[2]/div/div[1]/div[3]/div/div/div[1]/div[1]', '//div[@contenteditable="true"][@data-tab="10"]'],
        'send_button': ['//*[@id="app"]/div/div/div[3]/div/div[3]/div[2]/div/span/div/div/div/div[2]/div/div[2]/div[2]/div/div', '//span[@data-icon="send"]/..'],
        'invalid_number': ['//*[contains(text(), "Phone number shared via url is invalid")]', '//*[contains(text(), "invalid")]'],
    }

    def __init__(self):
        self.driver = None
        self.wait = None
        self.is_headless = False
        self.browser_type = None
        self.system = platform.system()
        self.base_dir = Path(__file__).parent.absolute()
        
    def _get_browser_path(self, browser_type):
        paths = self.BROWSER_PATHS.get(self.system, {}).get(browser_type, [])
        if isinstance(paths, str):
            paths = [paths]
        for path in paths:
            if os.path.exists(path):
                return path
        return None
    
    def _find_available_browser(self, preferred=None):
        if preferred:
            path = self._get_browser_path(preferred)
            if path:
                return preferred, path
        for browser in ['chrome', 'brave', 'edge', 'firefox']:
            path = self._get_browser_path(browser)
            if path:
                return browser, path
        return None, None
    
    def _create_chrome_options(self, browser_path, headless=False):
        options = ChromeOptions()
        profile_dir = self.base_dir / 'whatsapp_profile'
        profile_dir.mkdir(exist_ok=True)
        options.add_argument(f'--user-data-dir={profile_dir}')
        options.add_argument('--profile-directory=Default')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--remote-debugging-port=9222')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        if headless:
            options.add_argument('--headless=new')
        if browser_path:
            options.binary_location = browser_path
        return options
    
    def _create_firefox_options(self, browser_path, headless=False):
        options = FirefoxOptions()
        options.add_argument('--width=1920')
        options.add_argument('--height=1080')
        if headless:
            options.add_argument('--headless')
        if browser_path:
            options.binary_location = browser_path
        return options
    
    def initialize(self, headless=False, browser=None):
        try:
            self.is_headless = headless
            browser_type, browser_path = self._find_available_browser(browser)
            if not browser_path:
                raise Exception("No supported browser found. Install Chrome, Brave, Firefox, or Edge.")
            self.browser_type = browser_type
            print(f"Using browser: {browser_path}")
            if browser_type == 'firefox':
                options = self._create_firefox_options(browser_path, headless)
                self.driver = webdriver.Firefox(options=options)
            else:
                options = self._create_chrome_options(browser_path, headless)
                self.driver = webdriver.Chrome(options=options)
                self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'})
            self.wait = WebDriverWait(self.driver, 30)
            print("Opening WhatsApp Web...")
            self.driver.get('https://web.whatsapp.com')
            print("Browser opened! Please scan QR code if needed.")
            time.sleep(3)
            return True
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            self._cleanup()
            raise
    
    def _cleanup(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        self.driver = None
        self.wait = None
    
    def _find_element(self, selectors, timeout=10):
        if isinstance(selectors, str):
            selectors = [selectors]
        for selector in selectors:
            try:
                element = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, selector)))
                if element and element.is_displayed():
                    return element
            except (TimeoutException, NoSuchElementException):
                continue
        return None
    
    def _find_element_no_wait(self, selectors):
        if isinstance(selectors, str):
            selectors = [selectors]
        for selector in selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                if element and element.is_displayed():
                    return element
            except NoSuchElementException:
                continue
        return None
    
    def is_logged_in(self):
        if not self.driver:
            return False
        try:
            try:
                qr = self.driver.find_element(By.XPATH, self.SELECTORS['qr_canvas'])
                if qr.is_displayed():
                    return False
            except NoSuchElementException:
                pass
            try:
                self.driver.find_element(By.XPATH, self.SELECTORS['side_panel'])
                return True
            except NoSuchElementException:
                pass
            return False
        except:
            return False
    
    def get_qr_code(self):
        if not self.driver:
            return None
        try:
            qr = self.driver.find_element(By.XPATH, self.SELECTORS['qr_canvas'])
            if qr and qr.is_displayed():
                return self.driver.execute_script("return arguments[0].toDataURL('image/png').substring(22);", qr)
        except:
            pass
        return None
    
    def get_qr_code_base64(self):
        if not self.driver:
            return {'status': 'not_initialized', 'qr': None, 'error': 'Bot not initialized'}
        try:
            if self.is_logged_in():
                return {'status': 'logged_in', 'qr': None, 'error': None}
            qr_base64 = self.get_qr_code()
            if qr_base64:
                return {'status': 'qr_ready', 'qr': qr_base64, 'error': None}
            return {'status': 'waiting', 'qr': None, 'error': 'QR code not yet available'}
        except Exception as e:
            return {'status': 'error', 'qr': None, 'error': str(e)}
    
    def wait_for_login(self, timeout=120):
        start = time.time()
        while time.time() - start < timeout:
            if self.is_logged_in():
                print("Logged in!")
                return True
            time.sleep(2)
        return False
    
    def _open_chat(self, phone):
        phone = ''.join(filter(str.isdigit, str(phone)))
        if not phone:
            return False, "Invalid phone number"
        self.driver.get(f'https://web.whatsapp.com/send?phone={phone}')
        time.sleep(6)
        invalid = self._find_element_no_wait(self.SELECTORS['invalid_number'])
        if invalid:
            try:
                self.driver.find_element(By.XPATH, '//div[@role="button"]').click()
            except:
                pass
            return False, "Invalid phone number"
        return True, phone
    
    def send_message(self, phone, message):
        try:
            if not self.driver:
                print("Bot not initialized")
                return False
            success, result = self._open_chat(phone)
            if not success:
                return False
            phone = result
            print(f"Sending message to {phone}...")
            box = self._find_element(self.SELECTORS['message_input'])
            if not box:
                print(f"Could not find message input for {phone}")
                return False
            box.click()
            time.sleep(0.3)
            lines = message.split('\n')
            for i, line in enumerate(lines):
                box.send_keys(line)
                if i < len(lines) - 1:
                    box.send_keys(Keys.SHIFT + Keys.ENTER)
            time.sleep(0.3)
            box.send_keys(Keys.ENTER)
            print(f"Message sent to {phone}")
            time.sleep(2)
            return True
        except Exception as e:
            print(f"Error sending to {phone}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def send_message_with_attachment(self, phone, message, file_path):
        try:
            if not self.driver:
                print("Bot not initialized")
                return False
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return False
            file_path = os.path.abspath(file_path)
            success, result = self._open_chat(phone)
            if not success:
                return False
            phone = result
            print(f"Sending attachment to {phone}...")
            attach_btn = self._find_element(self.SELECTORS['attachment_button'])
            if not attach_btn:
                print("Could not find attachment button")
                return False
            attach_btn.click()
            time.sleep(2)
            doc_btn = self._find_element_no_wait(self.SELECTORS['document_option'])
            if doc_btn:
                doc_btn.click()
                time.sleep(2)
            inputs = self.driver.find_elements(By.XPATH, self.SELECTORS['file_input'])
            if not inputs:
                print("Could not find file input")
                return False
            inputs[0].send_keys(file_path)
            print(f"File uploaded: {file_path}")
            time.sleep(4)
            if message:
                cap = self._find_element_no_wait(self.SELECTORS['caption_input'])
                if cap:
                    try:
                        cap.click()
                        time.sleep(0.3)
                        cap.send_keys(message)
                    except Exception as e:
                        print(f"Could not add caption: {e}")
            time.sleep(1)
            send_btn = self._find_element(self.SELECTORS['send_button'], timeout=5)
            if not send_btn:
                print("Could not find send button")
                return False
            send_btn.click()
            print(f"Attachment sent to {phone}")
            time.sleep(5)
            return True
        except Exception as e:
            print(f"Error sending attachment to {phone}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def send_bulk_messages(self, contacts, message, delay=5):
        results = []
        for contact in contacts:
            phone = contact.get('phone') if isinstance(contact, dict) else contact
            success = self.send_message(phone, message)
            results.append({'phone': phone, 'success': success})
            if delay > 0:
                time.sleep(delay)
        return results
    
    def close(self):
        self._cleanup()


bot = WhatsAppBot()

def get_bot():
    return bot
