from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from datetime import datetime
def run_script():
    # Your initial share information
    shares_info = {
        'PRVU': [
            {'buying_price': 154.8, 'quantity': 50, 'buy_date': '2024-02-04','name':'sandesh','target_price':155}
        ],
        'AKPL': [
            {'buying_price': 197, 'quantity': 90, 'buy_date': '2024-02-04','name':'sandesh','target_price':200}
        ],
        'MMFDB': [
            {'buying_price': 570, 'quantity': 50, 'buy_date': '2024-02-05','name':'sandesh','target_price':575},
            {'buying_price': 562, 'quantity': 175, 'buy_date': '2024-02-06','name':'pratiksha','target_price':575}
        ],
        'AHPC': [
            {'buying_price': 209, 'quantity': 50, 'buy_date': '2024-02-04','name':'sandesh','target_price':210}
        ]
    }

    driver = webdriver.Chrome()  # Ensure your driver is in PATH or specify the path

    def scrape_page():
        table = driver.find_element(By.CLASS_NAME, 'table__lg')
        ltp_data = {}
        rows = table.find_elements(By.TAG_NAME, "tr")
        header_cells = rows[0].find_elements(By.TAG_NAME, "th")
        columns = [header.text.strip() for header in header_cells]
        symbol_index = columns.index('Symbol')
        ltp_index = columns.index('LTP')

        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, "td")
            if cells:
                symbol = cells[symbol_index].text.strip()
                ltp = cells[ltp_index].text.strip().split('(')[0]
                ltp_data[symbol] = float(ltp.replace(',', ''))
        
        return ltp_data

    driver.get("https://www.nepalstock.com/today-price")
    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.CLASS_NAME, 'table__lg')))

    try:
        items_per_page_dropdown = Select(driver.find_element(By.TAG_NAME, "select"))
        items_per_page_dropdown.select_by_value("500") 
        time.sleep(30) 

        filter_button = driver.find_element(By.CSS_SELECTOR, "button.box__filter--search")
        filter_button.click()
        time.sleep(30)  
    except Exception as e:
        print(f"Could not set items per page: {e}")

    latest_prices = scrape_page()
    driver.quit()

    # Update current prices in shares_info
    for share, transactions in shares_info.items():
        for transaction in transactions:
            if share in latest_prices:
                transaction['current_price'] = latest_prices[share]
                # Check if current LTP is greater than or equal to target price
                if transaction['current_price'] >= transaction['target_price']:
                    print(f"Target reached for {share}: {transaction['current_price']} >= {transaction['target_price']}")
                    play_sound()
                else:
                    print(f"Target Price has not been reached for {share} and is:Rs.{transaction['current_price']} ")
            else:
                print(f"Current price for {share} not found.")


    def calculate_profit_loss(shares_info):
        individual_results_by_name = {}
        total_by_name = {}

        for share_name, transactions in shares_info.items():
            for transaction in transactions:
                if 'current_price' in transaction:
                    result = (transaction['current_price'] - transaction['buying_price']) * transaction['quantity']
                    name = transaction['name']
                    # Initialize name key if not exists
                    if name not in individual_results_by_name:
                        individual_results_by_name[name] = {}
                        total_by_name[name] = 0

                    total_by_name[name] += result
                    # Calculate number of days held
                    buy_date = datetime.strptime(transaction['buy_date'], '%Y-%m-%d')
                    days_held = (datetime.now() - buy_date).days
                    # Append result to individual_results_by_name
                    individual_results_by_name[name].setdefault(share_name, []).append({
                        'profit_loss': result,
                        'current_price': transaction['current_price'],
                        'days_held': days_held
                    })
                else:
                    print(f"Current price for {share_name} is missing.")

        return individual_results_by_name, total_by_name

    individual_results_by_name, total_by_name = calculate_profit_loss(shares_info)


    print("Individual Profit/Loss and Holding Duration by Name:")
    for name, shares_result in individual_results_by_name.items():
        print(f"\n{name}'s Portfolio:")
        for share, transactions in shares_result.items():
            for data in transactions:
                profit_loss = data['profit_loss']
                current_price = data['current_price']
                days_held = data['days_held']
                print(f"  {share}: {'Profit' if profit_loss > 0 else 'Loss'} Rs{abs(profit_loss)} (Current LTP: Rs{current_price}, Days Held: {days_held})")
        print(f"Total for {name}: {'Profit Rs' if total_by_name[name] > 0 else 'Loss Rs.'} {abs(total_by_name[name])}")

import schedule
import time

import winsound

def play_sound():
    frequency = 2000  # Set Frequency To 2500 Hertz
    duration = 5000   # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)

run_script()

# Schedule the script to run every 5 minutes
# schedule.every(2).minutes.do(run_script)

# print("Scheduler started.")

# # Run the scheduler in an infinite loop
# while True:
#     schedule.run_pending()
#     time.sleep(1)
