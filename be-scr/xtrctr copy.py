from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, NoSuchElementException, WebDriverException
import time
import sys

def get_player_data(player_name, max_retries=3):
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Commenting out headless mode
    
    for attempt in range(max_retries):
        driver = webdriver.Chrome(options=chrome_options)
        try:
            driver.get("https://www.besoccer.com/")
            print(f"Attempt {attempt + 1} of {max_retries}")
            
            try:
                accept_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[mode='primary'][size='large']"))
                )
                accept_button.click()
                print("Cookie consent accepted")
            except (TimeoutException, NoSuchElementException):
                print("Cookie consent popup not found or not clickable")
            
            search_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "search_input"))
            )
            print("Search input found")
            
            search_input.clear()
            search_input.send_keys(player_name)
            print(f"Searched for: {player_name}")
            
            # Wait for autocomplete results to appear and be populated
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".autocomplete-box ul#autocomplete_values li"))
                )
                print("Autocomplete box appeared and populated")
            except TimeoutException:
                print("Autocomplete box did not appear or was not populated")
                continue
            
            # Find all links in the autocomplete box
            autocomplete_links = driver.find_elements(By.CSS_SELECTOR, ".autocomplete-box ul#autocomplete_values li a")
            print(f"Number of autocomplete links found: {len(autocomplete_links)}")
            
            if len(autocomplete_links) < 2:
                print("Not enough autocomplete links found. Printing page source:")
                print(driver.page_source[:1000])
                continue
            
            # Print details of the first few links
            for i, link in enumerate(autocomplete_links[:5]):
                print(f"Link {i}: Text = '{link.text}', href = '{link.get_attribute('href')}'")
            
            # Find the player link (should be the second link)
            player_link = autocomplete_links[1]
            player_url = player_link.get_attribute("href")
            print(f"Player URL: {player_url}")
            
            # Navigate to the player URL
            driver.get(player_url)
            print("Navigated to player URL")
            
            # Wait for the player page to load
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Print the title of the page
            print(f"Page title: {driver.title}")
            
            return player_url
        
        except WebDriverException as e:
            print(f"WebDriverException occurred: {str(e)}")
            if attempt == max_retries - 1:
                return "Error occurred while fetching player data"
        
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            if attempt == max_retries - 1:
                return "Error occurred while fetching player data"
        
        finally:
            driver.quit()
    
    return "Failed to fetch player data after multiple attempts"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        player_name = " ".join(sys.argv[1:])
    else:
        player_name = input("Enter player name: ").strip()
    
    if player_name:
        player_url = get_player_data(player_name)
        print(f"Final result: {player_url}")
    else:
        print("Error: Player name cannot be empty.")
