from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, NoSuchElementException, WebDriverException
import time
import sys

def get_player_data(player_name, max_retries=3, timeout=60):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    
    for attempt in range(max_retries):
        driver = webdriver.Chrome(options=chrome_options)
        try:
            print(f"Attempt {attempt + 1} of {max_retries}")
            driver.set_page_load_timeout(timeout)
            
            start_time = time.time()
            driver.get("https://www.besoccer.com/")
            print(f"Loaded homepage in {time.time() - start_time:.2f} seconds")
            
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
                print("Not enough autocomplete links found. Player might not exist.")
                return "Player not found"
            
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
            page_title = driver.title
            print(f"Page title: {page_title}")
            
            # Check if the player name is in the page title
            player_name_parts = player_name.lower().split()
            if not all(part in page_title.lower() for part in player_name_parts):
                print(f"Warning: Player name '{player_name}' not found in page title.")
                return "Player not found or mismatch in player name"
            
            # Find and click on the "Career" link
            try:
                start_time = time.time()
                career_link = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//nav[@class='head-menu']//a[contains(text(), 'Career')]"))
                )
                career_link.click()
                print(f"Clicked Career link after {time.time() - start_time:.2f} seconds")
                
                # Add a short wait
                time.sleep(5)
                
                start_time = time.time()
                WebDriverWait(driver, 10).until(EC.url_contains("/career-path/"))
                print(f"Career page loaded in {time.time() - start_time:.2f} seconds")
                
                # Get the current URL (career page URL)
                career_url = driver.current_url
                print(f"Career page URL: {career_url}")
                
                # Extract career data
                start_time = time.time()
                career_data = extract_career_data(driver)
                print(f"Extracted career data in {time.time() - start_time:.2f} seconds")
                
                return career_url, career_data
            except (TimeoutException, NoSuchElementException) as e:
                print(f"Error clicking on Career link: {str(e)}")
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

def extract_career_data(driver):
    try:
        general_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#general.container"))
        )
        print("General container found")
        print("General container HTML:")
        print(general_container.get_attribute('outerHTML')[:1000])  # Print first 1000 characters

        # Print the entire page source
        print("Full page source:")
        print(driver.page_source[:5000])  # Print first 5000 characters

    except Exception as e:
        print(f"Error extracting career data: {str(e)}")

    return {}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        player_name = " ".join(sys.argv[1:])
    else:
        player_name = input("Enter player name: ").strip()
    
    if player_name:
        result = get_player_data(player_name)
        if isinstance(result, tuple):
            career_url, career_data = result
            print(f"Final result: {career_url}")
            print("Career data:")
            for tab, data in career_data.items():
                print(f"\n{tab}:")
                for key, value in data.items():
                    print(f"  {key}: {value}")
        else:
            print(f"Final result: {result}")
    else:
        print("Error: Player name cannot be empty.")
