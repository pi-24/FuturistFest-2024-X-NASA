import time
import urllib
import wave, struct, math
import numpy as np
import scipy.ndimage
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import soundfile as sf
import librosa

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

def switch_to_results_page(driver):
    """Switch to results page"""
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    driver.switch_to.window(driver.window_handles[1])

def download_image(driver):
    img_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//img[@id='img1']")))
    img_url = img_element.get_attribute("src")
    urllib.request.urlretrieve(img_url, "image.jpg")

def load_picture(file, contrast=True, highpass=False):
    img = Image.open(file)
    img = img.convert("L")
    imgArr = np.array(img)
    imgArr = np.flip(imgArr, axis=0)
    
    if contrast:
        imgArr = 1/(imgArr+10**15.2)
    else:
        imgArr = 1 - imgArr
    
    imgArr -= np.min(imgArr)
    imgArr = imgArr/np.max(imgArr)
    
    if highpass:
        removeLowValues = np.vectorize(lambda x: x if x > 0.5 else 0, otypes=[np.float64])
        imgArr = removeLowValues(imgArr)
    
    return imgArr

def gen_sound_from_image(file, output="sound.wav", duration=60.0, sampleRate=44100, min_freq=200, max_freq=2000):
    imgArr = load_picture(file)
    
    num_freqs = imgArr.shape[1]
    num_samples = int(duration * sampleRate)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    
    audio = np.zeros(num_samples)
    
    for i in range(num_freqs):
        freq = min_freq + i * (max_freq - min_freq) / num_freqs
        sine_wave = np.sin(2 * np.pi * freq * t)
        # Normalize sine wave to ensure it fits within the audio sample range
        sine_wave *= imgArr[:, i % imgArr.shape[0]].mean()
        audio += sine_wave
    
    audio = audio / np.max(np.abs(audio))  # Normalize
    
    # Apply fade-in and fade-out
    fade_in = np.linspace(0, 1, int(sampleRate * 0.5))
    fade_out = np.linspace(1, 0, int(sampleRate * 0.5))
    audio[:len(fade_in)] *= fade_in
    audio[-len(fade_out):] *= fade_out
    
    sf.write(output, audio, sampleRate)

def main():
    coords = get_user_input()
    driver = setup_driver()
    navigate_to_skyview(driver)
    input_coords(driver, coords)
    select_dataset(driver)
    submit_query(driver)
    switch_to_results_page(driver)
    time.sleep(10)
    download_image(driver)
    gen_sound_from_image("image.jpg", output="sound.wav", duration=60.0)  # Set duration to 60 seconds
    driver.quit()

if __name__ == "__main__":
    main()
