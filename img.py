from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

coords = input("Enter coordinates in format of 161.265, -59.685: ")
time.sleep(3)

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get("https://skyview.gsfc.nasa.gov/current/cgi/query.pl")

#Input coords
input_element = driver.find_element(By.ID, "object")
input_element.send_keys(coords)


# Find the select element with the id "IR:AKARI"
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "GammaRay")))

select_element = driver.find_element(By.ID, "GammaRay")

select = Select(select_element)
select.select_by_visible_text("Fermi 5")

# Press submit button 
submit_button = driver.find_element(By.XPATH, "//input[@value='Submit Request']")
submit_button.click()
time.sleep(10)



driver.quit()   
