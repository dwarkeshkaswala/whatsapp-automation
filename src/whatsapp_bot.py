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
from selenium.webdriver.common.action_chains import ActionChains

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
    
    # XPath profiles for different OS/Browser combinations
    # Each profile has selectors that work for that specific environment
    XPATH_PROFILES = {
        # macOS Brave Browser (original/default)
        'darwin_brave': {
            'attachment_button': [
                '//footer//button[contains(@aria-label, "Attach")]',
                '//span[@data-icon="plus"]/..',
                '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[1]/div/span/button'
            ],
            'document_input': '//*[@id="app"]/div/div/span[6]/div/ul/div/div/div[1]/li/div/input',
            'photo_input': '//*[@id="app"]/div/div/span[6]/div/ul/div/div/div[2]/li/div/input',
            'audio_input': '//*[@id="app"]/div/div/span[6]/div/ul/div/div/div[4]/li/div/input',
            'send_button': [
                '//span[@data-icon="send"]/..',
                '//*[@id="app"]/div/div/div[3]/div/div[3]/div[2]/div/span/div/div/div/div[2]/div/div[2]/div[2]/div/div'
            ],
        },
        # Windows Chrome Browser
        'windows_chrome': {
            'attachment_button': [
                '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[1]/div/span/button',
                '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[1]/div/span/button/div/div/div[1]/span',
                '//footer//button[contains(@aria-label, "Attach")]',
                '//span[@data-icon="plus"]/..'
            ],
            'document_input': '//*[@id="app"]/div/div/span[6]/div/ul/div/div/div[1]/li/div/input',
            'photo_input': '//*[@id="app"]/div/div/span[6]/div/ul/div/div/div[2]/li/div/input',
            'audio_input': '//*[@id="app"]/div/div/span[6]/div/ul/div/div/div[4]/li/div/input',
            'send_button': [
                '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[4]/div/span/button',
                '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[4]/div/span/button/div/div/div[1]/span',
                '//span[@data-icon="send"]/..'
            ],
        },
        # Default fallback (tries all known selectors)
        'default': {
            'attachment_button': [
                '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[1]/div/span/button',
                '//footer//button[contains(@aria-label, "Attach")]',
                '//span[@data-icon="plus"]/..',
                '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[1]/div/span/button/div/div/div[1]/span'
            ],
            'document_input': '//*[@id="app"]/div/div/span[6]/div/ul/div/div/div[1]/li/div/input',
            'photo_input': '//*[@id="app"]/div/div/span[6]/div/ul/div/div/div[2]/li/div/input',
            'audio_input': '//*[@id="app"]/div/div/span[6]/div/ul/div/div/div[4]/li/div/input',
            'send_button': [
                '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[4]/div/span/button',
                '//span[@data-icon="send"]/..',
                '//*[@id="app"]/div/div/div[3]/div/div[3]/div[2]/div/span/div/div/div/div[2]/div/div[2]/div[2]/div/div'
            ],
        },
    }
    
    # Common selectors that work across all platforms
    SELECTORS = {
        'qr_canvas': '//canvas[contains(@aria-label, "Scan")]',
        'side_panel': '//div[@id="side"]',
        'message_input': ['//div[@contenteditable="true"][@data-tab="10"]', '//div[@title="Type a message"]', '//footer//div[@contenteditable="true"]'],
        'file_input': '//input[@type="file"]',
        'caption_input': ['//*[@id="app"]/div/div/div[3]/div/div[3]/div[2]/div/span/div/div/div/div[2]/div/div[1]/div[3]/div/div/div[1]/div[1]', '//div[@contenteditable="true"][@data-tab="10"]'],
        'invalid_number': ['//*[contains(text(), "Phone number shared via url is invalid")]', '//*[contains(text(), "invalid")]'],
    }

    def __init__(self):
        self.driver = None
        self.wait = None
        self.is_headless = False
        self.browser_type = None
        self.system = platform.system()
        self.xpath_profile = None  # Will be set during initialize
        # base_dir is the project root (parent of src/)
        self.base_dir = Path(__file__).parent.parent.absolute()
    
    def _get_xpath_profile_key(self):
        """Determine which XPath profile to use based on OS and browser"""
        os_name = self.system.lower()
        browser = (self.browser_type or 'chrome').lower()
        
        # Try specific OS + browser combination
        profile_key = f"{os_name}_{browser}"
        if profile_key in self.XPATH_PROFILES:
            return profile_key
        
        # Try OS with chrome as default
        profile_key = f"{os_name}_chrome"
        if profile_key in self.XPATH_PROFILES:
            return profile_key
        
        # Fallback to default
        return 'default'
    
    def _get_selector(self, selector_name):
        """Get selector(s) for a given name, using profile-specific or common selectors"""
        # First check profile-specific selectors
        if self.xpath_profile and selector_name in self.XPATH_PROFILES.get(self.xpath_profile, {}):
            return self.XPATH_PROFILES[self.xpath_profile][selector_name]
        
        # Then check default profile
        if selector_name in self.XPATH_PROFILES.get('default', {}):
            return self.XPATH_PROFILES['default'][selector_name]
        
        # Finally check common selectors
        if selector_name in self.SELECTORS:
            return self.SELECTORS[selector_name]
        
        return None
        
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
            
            # Set XPath profile based on OS and browser
            self.xpath_profile = self._get_xpath_profile_key()
            print(f"Using browser: {browser_path}")
            print(f"XPath profile: {self.xpath_profile}")
            
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
    
    def send_message_with_attachment(self, phone, message, file_path, file_type='document'):
        """
        Send a message with an attachment.
        file_type: 'image', 'document', 'audio', 'video' (image/video use photo option, others use document)
        """
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
            print(f"Sending attachment ({file_type}) to {phone}...")
            
            # Click attachment button to open menu
            attach_btn = self._find_element(self._get_selector('attachment_button'))
            if not attach_btn:
                print("Could not find attachment button")
                return False
            attach_btn.click()
            time.sleep(1)
            
            # Select correct input based on file type
            if file_type in ['image', 'video']:
                input_xpath = self._get_selector('photo_input')
                input_name = 'photo/video'
            elif file_type == 'audio':
                input_xpath = self._get_selector('audio_input')
                input_name = 'audio'
            else:
                input_xpath = self._get_selector('document_input')
                input_name = 'document'
            
            # Find and use the file input directly
            try:
                file_input = self.driver.find_element(By.XPATH, input_xpath)
                file_input.send_keys(file_path)
                print(f"File sent to {input_name} input: {file_path}")
            except Exception as e:
                print(f"Could not find {input_name} input: {e}")
                # Fallback to generic file input
                inputs = self.driver.find_elements(By.XPATH, self._get_selector('file_input'))
                if not inputs:
                    print("Could not find any file input")
                    return False
                inputs[0].send_keys(file_path)
                print(f"File sent via fallback input: {file_path}")
            
            time.sleep(4)
            
            # Add caption if provided
            if message:
                caption_added = False
                
                # Primary caption XPath (from user)
                caption_xpath = '//*[@id="app"]/div/div/div[3]/div/div[3]/div[2]/div/span/div/div/div/div[2]/div/div[1]/div[3]/div/div/div/div[1]/div[1]/p'
                
                try:
                    # Wait for caption input to be present
                    cap = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, caption_xpath))
                    )
                    # Click on the paragraph element
                    cap.click()
                    time.sleep(0.3)
                    # Type the message
                    cap.send_keys(message)
                    caption_added = True
                    print("Caption added successfully")
                except Exception as e:
                    print(f"Primary caption method failed: {e}")
                    
                    # Fallback: Try clicking parent div and typing
                    try:
                        parent_xpath = '//*[@id="app"]/div/div/div[3]/div/div[3]/div[2]/div/span/div/div/div/div[2]/div/div[1]/div[3]/div/div/div/div[1]/div[1]'
                        parent = self.driver.find_element(By.XPATH, parent_xpath)
                        parent.click()
                        time.sleep(0.3)
                        actions = ActionChains(self.driver)
                        actions.send_keys(message).perform()
                        caption_added = True
                        print("Caption added via parent element")
                    except Exception as e2:
                        print(f"Parent element method failed: {e2}")
                
                if not caption_added:
                    print("Warning: Could not add caption, sending without caption")
            
            time.sleep(1)
            send_btn = self._find_element(self._get_selector('send_button'), timeout=5)
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
