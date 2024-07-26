from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

def get_user_input():
    """Get coordinates from user"""
    return input("Enter coordinates in format of 161.265, -59.685: ")

def setup_driver():
    """Set up Chrome driver"""
    service = Service(executable_path="chromedriver.exe")
    return webdriver.Chrome(service=service)

def navigate_to_skyview(driver):
    """Navigate to SkyView website"""
    driver.get("https://skyview.gsfc.nasa.gov/current/cgi/query.pl")

def input_coords(driver, coords):
    """Input coordinates into text field"""
    input_element = driver.find_element(By.ID, "object")
    input_element.send_keys(coords)

def select_dataset(driver):
    """Select Fermi 5 dataset"""
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "GammaRay")))
    select_element = driver.find_element(By.ID, "GammaRay")
    select = Select(select_element)
    select.select_by_visible_text("Fermi 5")

def submit_query(driver):
    """Submit query"""
    submit_button = driver.find_element(By.XPATH, "//input[@value='Submit Request']")
    submit_button.click()

def download_image(driver):
    """Download image"""
    # Wait for the "quick look jpeg" link to be present on the page
    quick_look_link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'quick look jpeg')]")))

    # Click on the link
    quick_look_link.click()

    # Get the URL of the image
    image_url = driver.current_url

    # Download the image using requests
    response = requests.get(image_url)

    # Save the image to a file
    with open("image.jpg", "wb") as f:
        f.write(response.content)

def main():
    coords = get_user_input()
    driver = setup_driver()
    navigate_to_skyview(driver)
    input_coords(driver, coords)
    select_dataset(driver)
    submit_query(driver)
    time.sleep(10)
    download_image(driver)
    driver.quit()

if __name__ == "__main__":
    main()
