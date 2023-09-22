from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import yaml
from datetime import datetime

URL = 'https://smm-heaven.net/admin/updates'
ADMIN_HASH = yaml.safe_load(open('credentials.yaml'))['SMMHEAVEN']['ADMIN_HASH']
LAST_UPDATE = datetime.timestamp(datetime.strptime('2023-09-22 07:56:37', '%Y-%m-%d %H:%M:%S'))

def get_updates() -> list[(str, str, str)]:
    driver_opt = Options()
    driver_service = Service(executable_path='./geckodriver.exe')
    # driver_opt.headless = True
    driver_opt.add_argument("--window-size=800,800")
    driver_opt.page_load_strategy = 'eager'

    driver = webdriver.Firefox(options=driver_opt, service=driver_service)

    driver.get(URL)
    driver.add_cookie({'name': 'admin_hash', 'value': ADMIN_HASH})
    driver.get(URL)

    table: WebElement = WebDriverWait(driver, 15).until(
        expected_conditions.presence_of_element_located((By.TAG_NAME, 'table'))
    )

    table = table.find_element(by=By.TAG_NAME, value='tbody')
    children = table.find_elements(by=By.XPATH, value='*')
    
    updates = []
    new_time = None
    for c in children:
        elems = c.find_elements(by=By.XPATH, value='*')
        time_s = elems[2].text
        _time = datetime.strptime(time_s, '%Y-%m-%d %H:%M:%S')
        stamp = datetime.timestamp(_time)
        if new_time == None: new_time = stamp

        if stamp <= LAST_UPDATE:
            break

        service = elems[1].text
        change = elems[3].text        

        updates.append((service, change, time_s))

    LAST_UPDATE = new_time

    driver.quit()

    return updates