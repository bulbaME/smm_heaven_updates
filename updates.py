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
ADMIN_CRED = yaml.safe_load(open('credentials.yaml'))['SMMHEAVEN']['ADMIN']
LAST_UPDATE = datetime.timestamp(datetime.strptime(open('lastupdate.time').readline(), '%Y-%m-%d %H:%M:%S'))
MAX_WAIT_TIME = 10

def get_admin_hash() -> str | None:
    try:
        fr = open('admin.hash')
        s = fr.readline()
        fr.close()
        
        return s
    except BaseException:
        return None

def set_admin_hash(h: str):
    fw = open('admin.hash', 'w')
    fw.write(h)
    fw.close()

def get_driver() -> webdriver.Firefox:
    driver_opt = Options()
    driver_service = Service(executable_path='./geckodriver.exe')
    # driver_opt.headless = True
    driver_opt.add_argument("--window-size=800,800")
    driver_opt.page_load_strategy = 'eager'

    return webdriver.Firefox(options=driver_opt, service=driver_service)

def login(driver: webdriver.Firefox):
    form: WebElement = WebDriverWait(driver, MAX_WAIT_TIME).until(
        expected_conditions.presence_of_element_located((By.TAG_NAME, 'form'))
    )
    
    inputs = form.find_elements(by=By.TAG_NAME, value='input')

    inputs = list(filter(lambda x: x.is_displayed(), inputs))

    inputs[0].send_keys(ADMIN_CRED['LOGIN'])
    inputs[1].send_keys(ADMIN_CRED['PSW'])

    form.submit()

def enter_passcode(driver: webdriver.Firefox, passcode) -> bool:
    form = driver.find_element(by=By.TAG_NAME, value='form')
    inputs = form.find_elements(by=By.TAG_NAME, value='input')

    inputs = list(filter(lambda x: x.is_displayed(), inputs))

    inputs[0].send_keys(passcode)
    form.submit()

    try:
        WebDriverWait(driver, MAX_WAIT_TIME).until(
            expected_conditions.presence_of_element_located((By.TAG_NAME, 'table'))
        )
    except BaseException:
        return False
    
    h = driver.get_cookie('admin_hash')['value']

    set_admin_hash(h)

    return True

def get_updates() -> list[(str, str, str)]:
    driver = get_driver()

    driver.get(URL)
    driver.add_cookie({'name': 'admin_hash', 'value': get_admin_hash()})
    driver.get(URL)

    table = None
    try:
        table: WebElement = WebDriverWait(driver, MAX_WAIT_TIME).until(
            expected_conditions.presence_of_element_located((By.TAG_NAME, 'table'))
        )
    except BaseException:
        pass

    if table == None:
        driver.quit()
        return None

    table = table.find_element(by=By.TAG_NAME, value='tbody')
    children = table.find_elements(by=By.XPATH, value='*')
    
    updates = []
    new_time = None
    new_time_s = None
    for c in children:
        elems = c.find_elements(by=By.XPATH, value='*')
        time_s = elems[2].text
        _time = datetime.strptime(time_s, '%Y-%m-%d %H:%M:%S')
        stamp = datetime.timestamp(_time)
        if new_time == None: new_time = stamp
        if new_time_s == None: new_time_s = stamp

        if stamp <= LAST_UPDATE:
            break

        service = elems[1].text
        change = elems[3].text        

        updates.append((service, change, time_s))

    LAST_UPDATE = new_time
    fw = open('lastupdate.time', 'w')
    fw.write(new_time_s)
    fw.close()

    driver.quit()

    return updates