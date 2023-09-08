from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
import scraping_module as mod
import time
import pandas as pd
import re
import numpy as np
import os

chrome_driver_path = "./webdriver/chromedriver"

# chrome_driver_path = "./chromedriver"
# Scroll a page down continuously
def scrollPage(driver: webdriver.Chrome, scroll_pause_time: float = 0.5, N = 7):
    """ Scroll a page down continuously
    :param driver: A webdriver object, already intialized to the page you want to scroll
    :type driver: webdriver.Chrome
    :param scroll_pause_time: The time to pause between each scroll, default is 0.5 seconds
    :type scroll_pause_time: float
    :param N: The number of times to scroll down, default is 7
    :type N: int
    
    :return: None
    :rtype: None"""
    

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    n = 0 
    while n < N:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(scroll_pause_time)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        n+=1

def zee_daily_extractor(df: pd.DataFrame = None) -> pd.DataFrame:
    """Extracts the latest news from Zee Business. Extracts only financial news.
    
    :param df: (Optional) A dataframe to append the extracted data to, default is None. 
               The dataframe must have the following columns: Date, Title, News, Author, Source
    :type df: pd.DataFrame
    :return: A dataframe with the extracted data
    :rtype: pd.DataFrame
    """

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    service = ChromeService(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service,options=options)
    driver.get("https://www.zeebiz.com/companies")

    # Scroll
    scrollPage(driver)

    # Wait for the page to load
    elem = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div[4]/div/div/div[2]/div/div/div[2]/div/div/div/div[6]/section/div/div/div[3]/div/div[1]/div[1]'))
    )

    
    # Get all li elements with class = "newsList" which is already ul
    ls = elem.find_elements(By.TAG_NAME, "a")
    
    
    links = []
    for i in ls:
        try:
            link = i.get_attribute("href")
            links.append(link)
        except:
            continue
    
    n = 0
    # loop through the links in the top section
    data = []
    for link in links:
        
        try:
            # Get the page
            driver.get(link)
            res = mod.zeebiz(driver)
            
            if res not in data:
                data.append(res)
                n += 1
        except:
            driver.close()
            service = ChromeService(executable_path=chrome_driver_path)
            driver = webdriver.Chrome(service=service,options=options)
            driver.set_page_load_timeout(15)
            continue

        if n > 10:
            break

    

    driver.close()
    
    ds = pd.DataFrame(data, columns=["Date", "Title", "News", "Author"])
    ds["Source"] = "Zee Business"

    # Find today's date
    today = pd.Timestamp.today().strftime("%Y-%m-%d")

    if df is None:
        df = ds
    else:
        df = pd.concat([df, ds], ignore_index=True)
    

    return ds
    

def bqprime_daily_extractor(df: pd.DataFrame = None) -> pd.DataFrame:
    """Extracts the latest news from BQ Prime. Extracts only financial news.
    :param df: (Optional) A dataframe to append the extracted data to, default is None.
                The dataframe must have the following columns: Date, Title, News, Author, Source
    :type df: pd.DataFrame
    :return: A dataframe with the extracted data appended to the input dataframe
    :rtype: pd.DataFrame
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    service = ChromeService(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service,options=options)
    driver.get("https://www.bqprime.com/markets")

    # Wait for 2 seconds
    driver.implicitly_wait(5)

    #Scroll 
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Scroll until you see the market news section
    scrollPage(driver, N=7)
    



    # Wait for the page to load
    elem = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, 'more-from-markets'))
    )

    ls = elem.find_elements(By.TAG_NAME, "a")
    # # get element by xpath
    # elem = driver.find_element
    
    # for element in ls, get the href
    data = []
    for element in ls:
        try:
            href = element.get_attribute("href")
            driver.get(href)
            data.append(mod.bqprime(driver))
        except StaleElementReferenceException:
            continue
        

    driver.close()
    
    ds = pd.DataFrame(data, columns=["Date", "Title", "News", "Author"])
    ds["Source"] = "BQ Prime"

    # Find today's date
    today = pd.Timestamp.today().strftime("%Y-%m-%d")

    if df is None:
        df = ds
    else:
        df = pd.concat([df, ds], ignore_index=True)
    
    
    # # Save the dataframe to a csv file
    # df.to_csv(f"fin_exp-{today}.csv", index=False)
    return ds
    

def business_standard_daily_extractor(df : pd.DataFrame = None) -> pd.DataFrame:
    """Extracts the latest news from Business Standard. Extracts only financial news.
    :param df: (Optional) A dataframe to append the extracted data to, default is None.
                The dataframe must have the following columns: Date, Title, News, Author, Source
    :type df: pd.DataFrame
    :return: A dataframe with the extracted data appended to the input dataframe
    :rtype: pd.DataFrame
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    service = ChromeService(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service,options=options)
    driver.get("https://www.business-standard.com/markets/news")
    driver.set_page_load_timeout(15)

    # Scroll
    scrollPage(driver)

    # Wait for the page to load
    elem = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div/div[6]/section/div[1]/div/div/div[1]/div[2]'))
    )

    list_of_news = elem.find_elements(By.CLASS_NAME, "cardlist")
    
    
    

    links = []
    for item in list_of_news:
        try:
            
            if item.get_attribute("innerHTML").find("Premium") == -1:
                link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
                links.append(link)
        except:
            continue
    
    data = []
    for link in links:
        
        try:
            driver.get(link)
            info = mod.business_standard(driver)
            data.append(info)
        except:
            driver.close()
            service = ChromeService(executable_path=chrome_driver_path)
            driver = webdriver.Chrome(service=service,options=options)
            driver.set_page_load_timeout(15)
            continue
        
        

    driver.close()
    
    ds = pd.DataFrame(data, columns=["Date", "Title", "News", "Author"])
    ds["Source"] = "Business Standard"

    # Find today's date
    today = pd.Timestamp.today().strftime("%Y-%m-%d")

    if df is None:
        df = ds
    else:
        df = pd.concat([df, ds], ignore_index=True)
    
    
    # # Save the dataframe to a csv file
    # df.to_csv(f"fin_exp-{today}.csv", index=False)
    return ds



def bt_daily_extractor(df: pd.DataFrame) -> pd.DataFrame:
    """Extracts the latest news from Business Today. Extracts only financial news.
    :param df: (Optional) A dataframe to append the extracted data to, default is None.
                The dataframe must have the following columns: Date, Title, News, Author, Source
    :type df: pd.DataFrame
    :return: A dataframe with the extracted data appended to the input dataframe
    :rtype: pd.DataFrame
    """

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    service = ChromeService(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service,options=options)
    driver.set_page_load_timeout(30)
    driver.get("https://www.businesstoday.in/markets/stocks")

    # # Scroll
    # scrollPage(driver)

    # Wait for the page to load
    elem = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'section-listing-LHS'))
    )

    
    # Get all li elements with class = "newsList" which is already ul
    ls = elem.find_elements(By.TAG_NAME, "a")
    
    
    links = []
    for i in ls:
        try:
            link = i.get_attribute("href")
            links.append(link)
        except:
            continue

    # loop through the links in the top section
    data = []
    n = 0
    for link in links:
        res=(None, None, None, None)
        try:
            # Get the page
            driver.get(link)
            res = mod.business_today(driver)
            if res not in data:
                
                data.append(res)
                n += 1
        except:
            driver.close()
            service = ChromeService(executable_path=chrome_driver_path)
            driver = webdriver.Chrome(service=service,options=options)
            driver.set_page_load_timeout(30)
            continue
        # print(n)
        
        if n > 10:
            # print("Enough articles found.")
            break

    # Get element by xpath
    driver.get("https://www.businesstoday.in/markets/company-stock")
    #Wait for the page to load 
    elem = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'section-listing-LHS'))
    )
    
    # elem = driver.find_element(By.ID, "section-listing-LHS")

    # Get links from the element
    ls = elem.find_elements(By.TAG_NAME, "a")
    

    # Get the links
    links = []
    for i in ls:
        try:
            link = i.get_attribute("href")
            links.append(link)
        except:
            continue
    n = 0
    
    # loop through the links in the top section
    for link in links:
        
        try:
            # Get the page
            driver.get(link)
            res = mod.business_today(driver)
            if res not in data:
                
                data.append(res)
                n += 1
        except:
            driver.close()
            service = ChromeService(executable_path=chrome_driver_path)
            driver = webdriver.Chrome(service=service,options=options)
            driver.set_page_load_timeout(30)
            continue
        
        
        # print(n)
        if n > 10:
            # print("Enough articles found.")
            break

    

    driver.close()
    
    ds = pd.DataFrame(data, columns=["Date", "Title", "News", "Author"])
    ds["Source"] = "BusinessToday"

    # Find today's date
    today = pd.Timestamp.today().strftime("%Y-%m-%d")

    if df is None:
        df = ds
    else:
        df = pd.concat([df, ds], ignore_index=True)
    
    
    # # Save the dataframe to a csv file
    # df.to_csv(f"fin_exp-{today}.csv", index=False)
    return ds
     


def cnbc_daily_extractor(df:pd.DataFrame = None) -> pd.DataFrame:
    """Extracts the latest news from CNBC. Extracts only financial news.
    :param df: (Optional) A dataframe to append the extracted data to, default is None.
                The dataframe must have the following columns: Date, Title, News, Author, Source
    :type df: pd.DataFrame
    :return: A dataframe with the extracted data appended to the input dataframe
    :rtype: pd.DataFrame
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    service = ChromeService(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service,options=options)
    driver.get("https://www.cnbctv18.com/market/")

    # Scroll
    scrollPage(driver)

    # Wait for the page to load
    elem = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'top-news-flex'))
    )

    
    # Get all li elements with class = "newsList" which is already ul
    ls = elem.find_elements(By.TAG_NAME, "a")
    
    
    links = []
    for i in ls:
        try:
            link = i.get_attribute("href")
            links.append(link)
        except:
            continue

    # loop through the links in the top section
    data = []
    for link in links:
        # Get the page
        driver.get(link)
        try:
            res = mod.CNBC(driver)
        except:
            continue
        data.append(res)


    ############################################################################################
    # Get element by xpath
    driver.get("https://www.cnbctv18.com/market/")
    elem = driver.find_element(By.ID, "article-list-1-key")

    # Get links from the element
    ls = elem.find_elements(By.TAG_NAME, "a")
    

    # Get the links
    links = []
    for i in ls:
        try:
            link = i.get_attribute("href")
            links.append(link)
        except:
            continue
    n = 0
    # loop through the links in the top section
    for link in links:
        # Get the page
        driver.get(link)
        try:
            res = mod.CNBC(driver)
        except:
            continue
        data.append(res)
        n += 1

        if n > 10:
            
            break

    

    driver.close()
    
    ds = pd.DataFrame(data, columns=["Date", "Title", "News", "Author"])
    ds["Source"] = "CNBC"

    # Find today's date
    today = pd.Timestamp.today().strftime("%Y-%m-%d")

    if df is None:
        df = ds
    else:
        df = pd.concat([df, ds], ignore_index=True)
    
    
    # # Save the dataframe to a csv file
    # df.to_csv(f"fin_exp-{today}.csv", index=False)
    return ds
    
def eqbull_daily_extractor(df: pd.DataFrame = None) -> pd.DataFrame:
    """Extracts the latest news from Equity Bulls. Extracts only financial news.
    :param df: (Optional) A dataframe to append the extracted data to, default is None.
                The dataframe must have the following columns: Date, Title, News, Author, Source
    :type df: pd.DataFrame
    :return: A dataframe with the extracted data appended to the input dataframe
    :rtype: pd.DataFrame
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    service = ChromeService(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service,options=options)
    driver.get("https://www.equitybulls.com/")

    # Scroll
    scrollPage(driver)

    # Wait for the page to load
    elem = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'single_post_content_left'))
    )

    
    # Get all li elements with class = "newsList" which is already ul
    ls = elem.find_elements(By.TAG_NAME, "li")
    
    
    links = []
    for i in ls:
        try:
            link = i.find_element(By.TAG_NAME, "a").get_attribute("href")
            links.append(link)
        except:
            continue

    # loop through the links
    data = []
    for link in links:
        # Get the page
        driver.get(link)
        try:
            res = mod.equity_bulls(driver)
        except:
            continue
        data.append(res)

    driver.close()
    
    ds = pd.DataFrame(data, columns=["Date", "Title", "News", "Author"])
    ds["Source"] = "EquityBulls"

    # Find today's date
    today = pd.Timestamp.today().strftime("%Y-%m-%d")

    if df is None:
        df = ds
    else:
        df = pd.concat([df, ds], ignore_index=True)
    
    
    # # Save the dataframe to a csv file
    # df.to_csv(f"fin_exp-{today}.csv", index=False)
    return ds


def et_daily_extractor(df: pd.DataFrame = None) -> pd.DataFrame:
    """Extracts the latest news from Economic Times. Extracts only financial news.
    :param df: (Optional) A dataframe to append the extracted data to, default is None.
                The dataframe must have the following columns: Date, Title, News, Author, Source
    :type df: pd.DataFrame
    :return: A dataframe with the extracted data appended to the input dataframe
    :rtype: pd.DataFrame
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    service = ChromeService(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service,options=options)
    driver.get("https://economictimes.indiatimes.com/markets")
    



    # Wait for the page to load
    elem = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'newsList'))
    )

    
    # Get all li elements with class = "newsList" which is already ul
    ls = elem.find_elements(By.TAG_NAME, "li")
    
    
    links = []
    for i in ls:
        try:
            link = i.find_element(By.TAG_NAME, "a").get_attribute("href")
            links.append(link)
        except:
            continue

    # loop through the links
    data = []
    for link in links:
        # Get the page
        driver.get(link)
        try:
            res = mod.economic_times(driver)
        except:
            continue
        data.append(res)


    driver.close()
    
    ds = pd.DataFrame(data, columns=["Date", "Title", "News", "Author"])
    ds["Source"] = "Economic Times"

    # Find today's date
    today = pd.Timestamp.today().strftime("%Y-%m-%d")

    if df is None:
        df = ds
    else:
        df = pd.concat([df, ds], ignore_index=True)
    
    
    # # Save the dataframe to a csv file
    # df.to_csv(f"fin_exp-{today}.csv", index=False)
    return ds
    

def finex_daily_extractor(df:pd.DataFrame = None) -> pd.DataFrame:
    """Extracts the latest news from Financial Express. Extracts only financial news.
    :param df: (Optional) A dataframe to append the extracted data to, default is None.
                The dataframe must have the following columns: Date, Title, News, Author, Source
    :type df: pd.DataFrame
    :return: A dataframe with the extracted data appended to the input dataframe
    :rtype: pd.DataFrame
    """
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    
    service = ChromeService(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service,options=options)
    driver.get("https://www.financialexpress.com/market/")

    # Scroll
    scrollPage(driver)

    # Wait for the page to load
    elem = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[3]/div/div[1]'))
    )

    
    # Get all li elements with class = "newsList" which is already ul
    ls = elem.find_elements(By.TAG_NAME, "a")
    
    
    links = []
    for i in ls:
        try:
            link = i.get_attribute("href")
            links.append(link)
        except:
            continue
    
    n = 0
    # loop through the links in the top section
    data = []
    for link in links:
        
        try:
            # Get the page
            driver.get(link)
            res = mod.fin_express(driver)
            
            if res not in data:
                data.append(res)
                n += 1
        except:
            driver.close()
            service = ChromeService(executable_path=chrome_driver_path)
            driver = webdriver.Chrome(service=service,options=options)
            driver.set_page_load_timeout(15)
            continue

        if n > 10:
            break

        
    driver.close()
    
    ds = pd.DataFrame(data, columns=["Date", "Title", "News", "Author"])
    ds["Source"] = "FINANCIAL EXPRESS"

    # Find today's date
    today = pd.Timestamp.today().strftime("%Y-%m-%d")

    if df is None:
        df = ds
    else:
        df = pd.concat([df, ds], ignore_index=True)
    
    
    # # Save the dataframe to a csv file
    # df.to_csv(f"fin_exp-{today}.csv", index=False)
    return ds
    
if __name__ == "__main__":
    # eqbull_daily_extractor()
    # et_daily_extractor()
    # cnbc_daily_extractor()

    # Initialize a dataframe with 5 columns
    df = pd.DataFrame(columns=["Date", "Title", "News", "Author","Source"])
    df = finex_daily_extractor(df)
    df = et_daily_extractor(df)
    df = eqbull_daily_extractor(df)
    df = cnbc_daily_extractor(df)
    df = bqprime_daily_extractor(df)
    df = zee_daily_extractor(df)
    df = business_standard_daily_extractor(df)
    df = bt_daily_extractor(df)


    # Find today's date
    today = pd.Timestamp.today().strftime("%Y-%m-%d")
    df.to_csv(f"articles-{today}.csv", index=False)