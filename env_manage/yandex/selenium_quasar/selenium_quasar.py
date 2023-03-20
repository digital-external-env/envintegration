import time
from typing import Union
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By


class SeleniumQuasar:
    def __init__(self, login, password):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-infobars')
        self.chrome_options.add_argument('--remote-debugging-port=9222')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.login = login
        self.password = password
        self.link = 'https://passport.yandex.ru/auth/'

    def authorization(self) -> None:
        """
        Yandex authorization
        :return: None
        """
        self.driver.get(self.link)

        mail = self.driver.find_element(By.XPATH,
                                        '/html/body/div[1]/div/div[2]/div[2]/div/div/div[2]/div[3]/div/div/div/div[1]/form/div[1]/div[1]/button').click()
        login = self.driver.find_element(By.XPATH,
                                         '/html/body/div[1]/div/div[2]/div[2]/div/div/div[2]/div[3]/div/div/div/div[1]/form/div[2]/div/div[2]/span/input')
        time.sleep(3)
        login.send_keys(self.login)
        login_enter = self.driver.find_element(By.CSS_SELECTOR, '#passp\:sign-in')
        login_enter.click()
        time.sleep(3)
        password = self.driver.find_element(By.XPATH,
                                            '/html/body/div[1]/div/div[2]/div[2]/div/div/div[2]/div[3]/div/div/div/form/div[2]/div[1]/span/input')
        password.send_keys(self.password)
        password_enter = self.driver.find_element(By.CSS_SELECTOR, '#passp\:sign-in')
        password_enter.click()
        time.sleep(3)

    def add_scenario(self, scenario_name: str,
                     smart_speaker_name: str,
                     text: Union[str, None] = None,
                     action: Union[str, None] = None) -> None:
        """
                Add scenario for yandex smart speaker
                Args:
                    scenario_name (str): name of scenario
                    smart_speaker_name (str): name of smart speaker
                    text (Union[str, None]): text for voice phrase
                    action (Union[str, None]): text fo add task
                :return: None
                """
        self.driver.get('https://yandex.ru/quasar/iot/')
        add = self.driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div/div/div[1]/button').click()
        time.sleep(2)
        scenario = self.driver.find_element(By.XPATH,
                                            '/html/body/div/div/div[7]/div/div[2]/div/div[3]/div/div[1]/div/div[2]/div[1]/div').click()
        time.sleep(1)
        add_name = self.driver.find_element(By.XPATH,
                                            '/html/body/div/div/div[1]/div/div/div/div/div[1]/div[2]/div/div[2]/div[1]/div').click()
        time.sleep(1)
        name = self.driver.find_element(By.XPATH,
                                        '/html/body/div/div/div[1]/div/div/div/div[1]/div[1]/div[3]/textarea').send_keys(
            scenario_name)
        time.sleep(1)
        save = self.driver.find_element(By.XPATH, '/html/body/div/div/div[2]/button').click()
        time.sleep(1)
        add_condition = self.driver.find_element(By.XPATH,
                                                 '/html/body/div/div/div[1]/div/div/div/div/div[2]/div[2]/div/div[2]/div/div').click()
        time.sleep(1)
        phrase = self.driver.find_element(By.XPATH,
                                          '/html/body/div/div/div[6]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/div/div').click()
        time.sleep(1)
        condition_name = self.driver.find_element(By.XPATH,
                                                  '/html/body/div/div/div[1]/div/div/div/div/div[3]/textarea').send_keys(
            scenario_name)
        time.sleep(1)
        save = self.driver.find_element(By.XPATH, '/html/body/div/div/div[2]/button').click()
        time.sleep(1)

        add_action = self.driver.find_element(By.XPATH,
                                              '/html/body/div/div/div[1]/div/div/div/div/div[3]/div[2]/div/div[2]').click()
        time.sleep(1)

        devices = self.driver.find_elements(By.CLASS_NAME, 'list-item__name')
        for device in devices:
            if smart_speaker_name in device.text:
                device.click()
                time.sleep(1)
                break

        time.sleep(1)
        if text is None and action is None:
            raise ValueError
        if text:
            read_text = self.driver.find_element(By.XPATH,
                                                 '/html/body/div/div/div/div/div/main/div/div[4]/div/div/div/div[2]/div[1]/div').click()
            time.sleep(1)
            text_ = self.driver.find_element(By.XPATH,
                                             '/html/body/div/div/div/div/div/main/div/div[3]/textarea').send_keys(text)
            time.sleep(1)
            save = self.driver.find_element(By.XPATH, '/html/body/div/div/div/div/div/footer/button').click()
            time.sleep(1)

        elif action:
            do_action = self.driver.find_element(By.XPATH,
                                                 '/html/body/div/div/div/div/div/main/div/div[2]/div/div/div/div[2]/div[1]/div').click()
            time.sleep(1)
            action_ = self.driver.find_element(By.XPATH,
                                               '/html/body/div/div/div/div/div/main/div/div[3]/textarea').send_keys(
                action)
            time.sleep(1)
            save = self.driver.find_element(By.XPATH, '/html/body/div/div/div/div/div/footer/button').click()
            time.sleep(1)

        save = self.driver.find_element(By.XPATH, '/html/body/div/div/div[5]/button').click()
        time.sleep(2)

    def run_scenario(self, scenario_name: str) -> None:
        """
                       Run scenario
                       Args:
                           scenario_name (str): name of scenario

                       :return: None
                       """
        self.driver.get('https://yandex.ru/quasar/iot/')
        self.driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div/div/div[2]/div/div/div[2]/button').click()
        time.sleep(3)
        scenarios = self.driver.find_elements(By.CLASS_NAME, 'list-item')
        for scenario in scenarios:
            name = scenario.find_element(By.CLASS_NAME, 'list-item__name')

            if scenario_name == name.text:
                scenario.find_element(By.TAG_NAME, 'path').click()
                time.sleep(1)
                break
        time.sleep(2)

    def delete_scenario(self, scenario_name: str) -> None:
        """
                              Delete scenario
                              Args:
                                  scenario_name (str): name of scenario

                              :return: None
                              """
        self.driver.get('https://yandex.ru/quasar/iot/')
        self.driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div/div/div[2]/div/div/div[2]/button').click()
        time.sleep(3)
        scenarios = self.driver.find_elements(By.CLASS_NAME, 'list-item')
        for scenario in scenarios:
            name = scenario.find_element(By.CLASS_NAME, 'list-item__name')
            if scenario_name == name.text:
                scenario.click()
                time.sleep(1)
                self.driver.find_element(By.XPATH,
                                         '/html/body/div/div/div[1]/div/div/header/div/div/div/div[2]/button').click()
                time.sleep(1)
                self.driver.find_element(By.XPATH, '/html/body/div[4]/div/div/div/div/button').click()
                time.sleep(1)
                break
        time.sleep(2)
