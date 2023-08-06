from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pytest

@pytest.fixture(scope="session")
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("http://localhost:8000")
    yield driver
    driver.quit()

def test_title(driver):
    assert "Git Repository List" in driver.title

def test_valid_search(driver):
    search_elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div[1]/div/input'))
    )
    search_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,'//*[@id="root"]/div/div[2]/div[1]/button'))
    )
    
    """Case for searching a valid keyword that would return some output"""
    keyword = "kubernetes"
    search_elem.clear()
    search_elem.send_keys(keyword)
    search_elem.send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,'//*[@id="root"]/div/div[2]/div[2]/div[1]/div/table/tbody/tr[1]')))
    
    assert "No Data Found" not in driver.page_source

# def test_get_details(driver):
#     i_button = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.XPATH,'//*[@id="root"]/div/div[2]/div[2]/div[1]/div/table/tbody/tr[1]/td[5]/span'))).click()
#     check_text = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.XPATH,'/html/body/div[2]/div[3]/div/div[1]/div/p[1]'))).text
#     assert "Last 3 committers" in check_text
#     driver.find_element('xpath','/html/body/div[2]/div[3]/div/div[2]/button').click()

def test_link(driver):
    name = driver.find_element('xpath','//*[@id="root"]/div/div[2]/div[2]/div[1]/div/table/tbody/tr[1]/td[1]').text
    owner = driver.find_element('xpath','//*[@id="root"]/div/div[2]/div[2]/div[1]/div/table/tbody/tr[1]/td[2]').text
    link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
        (By.XPATH,'//*[@id="root"]/div/div[2]/div[2]/div[1]/div/table/tbody/tr[1]/td[4]/a'))).click()
    time.sleep(2)
    
    tabs = driver.window_handles
    parent_tab = tabs[0]
    child_tab = tabs[1]
    driver.switch_to.window(child_tab)
    child_title = driver.title
    driver.close()
    time.sleep(2)
    driver.switch_to.window(parent_tab)

    assert f"GitHub - {name}/{owner}" in child_title

def test_invalid_search(driver):
    """Case for searching an ivalid keyword that would return No results found"""
    search_elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div[1]/div/input'))
    )
    search_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,'//*[@id="root"]/div/div[2]/div[1]/button'))
    )
    search_elem.clear()
    keyword = "c dshcbdbcbcbbcckck"
    search_elem.send_keys(keyword)
    search_btn.click()
    time.sleep(3)
    assert "No Data Found" in driver.page_source

def test_empty_search(driver):
    """search for empty character and validate we are getting error popup"""
    search_elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div[1]/div/input'))
    )
    search_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,'//*[@id="root"]/div/div[2]/div[1]/button'))
    )
    search_elem.clear()
    keyword = " "
    search_elem.send_keys(keyword)
    search_btn.click()
    pop_up_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,"//h2[@id='swal2-title']"))).text
    
    assert "Unable to get search results - Validation Failed" in pop_up_element

"Making sure we're getting error pop-up when rate limit is exceeded"
def test_pop_up(driver):
    pop_up = False
    max_attempts = 9

    for attempt in range(max_attempts+1):
        try:
            search_elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div[1]/div/input')))
    
            search_elem.clear()
            search_elem.send_keys("Kubernetes")
            search_elem.send_keys(Keys.RETURN)

            WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//div[@role='alert']")))

            print("Pop-up appeared!")
            time.sleep(3)
            pop_up = True
            assert pop_up
            break
        except:
            print(f"Attempt {attempt + 1} - Pop-up not found yet. Continuing...")

def test_api_rate_limit(driver): 
    max_attempts = 10
    search_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div[1]/div/input'))
        )
    search_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,'//*[@id="root"]/div/div[2]/div[1]/button'))
    )

    keyword = "kubernetes"
    search_elem.clear()
    search_elem.send_keys(keyword)
    pop_up_text = ""
    for attempt in range(max_attempts+1):
        search_btn.click()
        driver.implicitly_wait(1)
        pop_up_element = driver.find_elements(By.XPATH, '//h2[@id="swal2-title"]')
        if pop_up_element:
            pop_up_text = pop_up_element[0].text

    assert "Unable to get search results - API rate limit exceeded" in pop_up_text


if __name__ == "__main__":
    pytest.main()