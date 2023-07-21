''' This module contains functions to scrape the Money Control FInancial Ratios
    and turn them into csv files. Requires a laptop/desktop system with a big enough screen
    Requires installing chromedriver. Tested on Ubuntu 22.04 and working as on Jun 9 2023
    
    A lot of this is hard coded for simplicity'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import re
import numpy as np

def getName(url:str) -> str:
    ''' Obtain the name of the stock as encoded into the money control url'''
    newURLpieces = re.split('(/)|(#)', url)
    newURLpieces = list(filter(lambda item: item is not None, newURLpieces))
    return newURLpieces[8]

def correctformat(currentPageURL:str) -> str:
    ''' Returns the URL of the page with added page number. Works only for MoneyControl Financial Ratios.
        No guarantee that the given URL exists. Use try/except statements while using'''
    # Split the string into pieces and then makes the necessary changes
    
    newURLpieces = re.split('(/)|(#)', currentPageURL)
    newURLpieces = list(filter(lambda item: item is not None, newURLpieces))
    
    newURLpieces.insert(-2,"/1")
    
    
    # Rejoin the pieces
    url = ''
    for piece in newURLpieces:
        url += piece
    
    
    return url
    
def NextPageURL(currentPageNumber:int, currentPageURL:str) -> str:
    ''' Find the URL of the next page. Works only for MoneyControl Financial Ratios.
        No guarantee that the given URL exists. Use try/except statements while using'''
    # Split the string into pieces and then makes the necessary changes
    currentPageNumber += 1
    newURLpieces = re.split('(/)|(#)', currentPageURL)
    newURLpieces = list(filter(lambda item: item is not None, newURLpieces))
    newURLpieces[-3] = f"{currentPageNumber}"
    
    # Rejoin the pieces
    url = ''
    for piece in newURLpieces:
        url += piece
    
    #print(url)
    return url


def getFinancialRatios(PageURL:str):
    ''' Scrapes off financial ratios as much as available upto 16 prior years
        firstPageURL must be an existing page.
        :returns: Dataframe of extracted data along with the ticker name'''
        
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(PageURL)
    line = driver.find_element(By.TAG_NAME, "ctag")
    ticker = line.text.split(" ")[4]

    

    # Repeatedly attempts to pull upto 4 pages of sequential data
    # On exception, assumes that the page does not exist and jumps to except block

    n_page = 1 # Page number of financial ratios to be scraped
    data=[]
    tablex = None
    try:
        while n_page <= 4:

            # Fetch the page
            if n_page >1:
                driver.get(PageURL)

            # Get the table from the html
            table =  driver.find_element(By.CLASS_NAME,'mctable1')

            rows= table.find_elements(By.TAG_NAME, "tr")

            if n_page == 1:
                for row in rows:
                    columns =row.find_elements(By.TAG_NAME,"td")
                    row_data = [column.text for column in columns]

                    if row_data[-1] ==' ':
                        row_data.pop()

                    data.append(row_data)
            else:
                i = 0
                for row in rows:
                    columns =row.find_elements(By.TAG_NAME,"td")
                    row_data = [column.text for column in columns]
                    row_data.pop(0)
                    if row_data[-1] ==' ':
                        row_data.pop()

                    data[i] = data[i] + row_data
                    i+=1

            
            tablex = pd.DataFrame.from_records(data)
            n_page +=1
            PageURL = NextPageURL(n_page - 1, PageURL)
        driver.close()
        
        
        df = tablex.transpose()
        df.columns = df.iloc[0]
        df = df.drop(df.index[0])

        
        return (df, ticker)
    except:
        driver.close()
        
        df = tablex.transpose()
        df.columns = df.iloc[0]
        df = df.drop(df.index[0])

        return (df, ticker)


def consolidatedURL(url:str)-> str:
    '''Gets consolidated and not standalone ratios'''
    newURLpieces = re.split('(/)|(#)', url)
    newURLpieces = list(filter(lambda item: item is not None, newURLpieces))

    newURLpieces[10] = 'consolidated-ratiosVI'
    #print(newURLpieces)
    
    url = ''
    for piece in newURLpieces:
        url += piece
    return url

####################---------Scrapers for specific websites!----------###################################

def CNBC(driver):

    headline = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME,"narticle-title"))
    )
    
    title = headline.text

    try: 
        action_element = driver.find_element(By.CLASS_NAME,"continue-btn")
        action = ActionChains(driver)
        action.move_to_element(action_element)
        action.perform()
        action.click(on_element = action_element)
        action.perform()
    except:
        pass

    news = driver.find_element(By.CLASS_NAME,"narticle-text")
    ls = news.find_elements(By.TAG_NAME, "div")
    ls1 = ''
    for elem in ls:
        try:
            r = elem.find_elements(By.TAG_NAME,"a")
            if len(r)!=0 :
                pass       
            else: 
                ls1 = ls1 +(elem.text)
        except:
            ls1 = ls1 + (elem.text)

    dats = driver.find_element(By.CLASS_NAME, "nauthor-name").text
    dattimez = dats[-37:-9]
    author = dats[:-37]
    
    return (dattimez,title,ls1,author)


def simply(driver):
    
    title_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,"//h1[@data-cy-id='article-title']"))
    )

    title = title_element.text
    
    news = driver.find_element(By.XPATH,"//div[@data-cy-id='page-article']")
    news_ls = news.text.split('\n')
    news_ls = news_ls[:-6]
    news_ls = news_ls[3:]
    ls = news.find_elements(By.TAG_NAME, "div")
    ls1 = ''
    for elem in ls:
        try:
            
                ls1 = ls1 +(elem.text)
        except:
            ls1 = ls1 +(elem.text)
    
    
    author = driver.find_element(By.XPATH,"//div[@class='sc-evZas iNxhpg']").text
    dattimez = driver.find_element(By.XPATH,"//span[@class='styled__PublishedDate-sc-a9o8vv-14 fDsGou']").text
    
    return (dattimez[10:],title,ls1,author)

def business_today(driver):
    
    headline = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "story-heading"))
    )


    #headline = driver.find_element(By.CLASS_NAME, "story-heading")
    title = headline.text
    news = driver.find_element(By.CLASS_NAME, "story-with-main-sec")
    ls = news.find_elements(By.TAG_NAME, "p")
    ls1 = ''
    for elem in ls[:-4]:
        try:
            r = elem.find_elements(By.TAG_NAME,"a")
            if len(r)!=0:
                pass
            else: 
                ls1 = ls1 +(elem.text)
        except:
            ls1 = ls1 +(elem.text)
            
    dats = driver.find_element(By.CLASS_NAME, "str_ftr_rhs")
    dattimez = dats.text[-25:]
    author = dats.text[11:-27]
    
    return (dattimez,title,ls1,author)
def equity_bulls(driver):

    headline = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )
    
    # headline = driver.find_element(By.TAG_NAME, "h1")
    title = headline.text
    
    news = driver.find_element(By.CLASS_NAME, "single_page_content")
    ls = news.find_elements(By.TAG_NAME, "p")
    ls1 = ''
    for elem in ls:
        try:
            r = elem.find_elements(By.TAG_NAME,"a")
            if len(r)!=0:
                pass
            else: 
                ls1 = ls1 +(elem.text)
        except:
            ls1 = ls1 +(elem.text)
    
    dats = driver.find_elements(By.TAG_NAME, "h4")
    for elem in dats:
        if elem.text.find("Posted")!=-1:
            dattimez = elem.text[12:]
            
        elif elem.text.find("Source")!=-1:
            author = elem.text
        else:
            continue
        
    return (dattimez,title,ls1,author)
def fin_express(driver):

    headline = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "wp-block-post-title"))
    )
    
    headline = driver.find_element(By.CLASS_NAME, "wp-block-post-title")
    title = headline.text
    
    news = driver.find_element(By.CLASS_NAME, "pcl-container")
    ls = news.find_elements(By.TAG_NAME, "p")
    ls1 = ''
    for elem in ls:
        try:
            r = elem.find_elements(By.TAG_NAME,"a")
            if len(r)!=0:
                pass
            else: 
                ls1 = ls1 + (elem.text)
        except:
            ls1 = ls1 +(elem.text)
    
    dats = driver.find_element(By.ID, "author-link")
    author = dats.text
    dattimez = driver.find_element(By.CLASS_NAME, "ie-network-post-meta-date").text
    
    return (dattimez,title,ls1,author)
def zeebiz(driver):
    
    
    headline = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,"//h1[@class='article-heading article-heading-biz margin-bt10px']"))
    )
    
    
    headline = driver.find_element(By.XPATH,"//h1[@class='article-heading article-heading-biz margin-bt10px']")
    title = headline.text.replace(";", ":")
    
    try: 
        action_element = driver.find_element(By.LINK_TEXT,"Read More")
        action = ActionChains(driver)
        action.move_to_element(action_element)
        action.perform()
        action.click(on_element = action_element)
        action.perform()
    except:
        pass

    news = driver.find_element(By.CLASS_NAME, "article-para")
    ls = news.find_elements(By.TAG_NAME, "p")
    ls1 = ''
    for elem in ls:
        try:
            r = elem.find_elements(By.TAG_NAME,"a")
            if len(r)!=0:
                pass
            else: 
                ls1 = ls1 + (elem.text)
        except:
            ls1 = ls1 +(elem.text)

    author = driver.find_element(By.CLASS_NAME,"writer-name").text
    dattimez = driver.find_element(By.CLASS_NAME,"date").text

    return (dattimez,title,ls1,author)
def livemint(driver):


    headline = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME,"headline"))
    )
    


    # headline = driver.find_element(By.XPATH,"//h1[@id='headline_11686020078886']")
    title = headline.text
    
    news = driver.find_element(By.CLASS_NAME, "mainArea")
    ls = news.find_elements(By.TAG_NAME, "p")
    ls1 = driver.find_element(By.CLASS_NAME, "summary").text
    for elem in ls:
        try:
            r = elem.find_elements(By.TAG_NAME,"a")
            if len(r)!=0:
                pass
            else: 
                ls1 = ls1 + (elem.text)
        except:
            ls1 = ls1 +(elem.text)
            
    author = driver.find_element(By.XPATH,"//span[@class='articleInfo author ']").text
    dattimez = driver.find_element(By.XPATH,"//span[@class='newTimeStamp']").text
    
    return (dattimez,title,ls1,author)

def moneycontrol(driver):
    

    headline = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,"//h1[@class='article_title artTitle']"))
    )
    
    
    # headline = driver.find_element(By.XPATH,"//h1[@class='article_title artTitle']")
    title = headline.text
    
    try: 
        action_element = driver.find_element(By.ID,"readmoredivarticle")
        action = ActionChains(driver)
        action.move_to_element(action_element)
        action.perform()
        action.click(on_element = action_element)
        action.perform()
    except:
        pass

    news = driver.find_element(By.CLASS_NAME, "content_wrapper")
    ls = news.find_elements(By.TAG_NAME, "p")
    ls1 = ''
    for elem in ls:
        try:
            r = elem.find_elements(By.TAG_NAME,"a")
            if len(r)!=0:
                pass
            else: 
                ls1 = ls1 + (elem.text)
        except:
            ls1 = ls1 +(elem.text)
            
    dattimez = driver.find_element(By.CLASS_NAME,"article_schedule").text
    author = driver.find_element(By.CLASS_NAME,"article_author").text
    
    return (dattimez,title,ls1,author)

def economic_times(driver):
    
    headline = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )
    
    
    # headline = driver.find_element(By.TAG_NAME, "h1")
    title = (headline.text)

    summary = driver.find_element(By.CLASS_NAME, "summary")
    
    news = driver.find_element(By.CLASS_NAME, "artText")
    ls1 = summary.text + news.text
    
    # author = driver.find_element(By.CLASS_NAME, "auth eventDone")
    try:
        author = driver.find_element(By.XPATH, "/html/body/main/div[11]/div/div/div[2]/div/div[1]/div[2]")
    except:
        author = driver.find_element(By.CLASS_NAME, "ag")
    
    author = author.text

    dattimez = driver.find_element(By.CLASS_NAME, "jsdtTime")
    dattimez = dattimez.text[14:]
    return (dattimez,title,ls1,author)


def bqprime(driver):
    

    headline = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # headline = driver.find_element(By.TAG_NAME, "h1")
    title = (headline.text)

    summary = driver.find_element(By.TAG_NAME, "h3")
    news = driver.find_element(By.CLASS_NAME, "row-section").text.replace("ADVERTISEMENT","")
    ls1 = news + summary.text
    dats = driver.find_elements(By.CLASS_NAME, "authors-module__author__MTSY9")
    author = ''
    for obj in dats:
        author +=obj.text+" "
    dattimez = driver.find_element(By.CLASS_NAME, "story-base-template-m__story-date__3YCRm")
    dattimez = dattimez.text[14:]

    return (dattimez,title,ls1,author)
def business_standard(driver):
    
    headline = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "stryhdtp"))
    )
    
    # headline = driver.find_element(By.CLASS_NAME, "stryhdtp")
    title = headline.text.replace(";",":")

    news = driver.find_element(By.CLASS_NAME, "storycontent")
    ls = news.find_elements(By.TAG_NAME, "div")
    ls1 = ''
    for elem in ls:
        
        if elem.text.find("Also Read") == -1:
            ls1 = ls1 + (elem.text)
        else:
            ls1 = ls1 + elem.text.split("Also Read")[0]
            break
        

    author = driver.find_element(By.CLASS_NAME,"story-detail")
    author1=author.find_elements(By.TAG_NAME,"a")
    author = ""
    for elem in author1:
            if elem.text.find("Follow") != -1:
                break
            author += (elem.text)
            author += " | "
            
    dattimez=driver.find_element(By.CLASS_NAME, "story-first-time").text[17:]
    
    return (dattimez,title,ls1,author)



####################################################################################################

def get_data(website:str,driver:webdriver.Chrome) -> tuple:
    """ Returns a 4-tuple of date, title, news content and author from the given website.
    :param website: The website from which the data is to be extracted.
    :param driver: The webdriver object.
    :return: A 4-tuple of date, title, news content and author.
    :rtype: tuple"""
    driver.get(website)

    

    # Stop loading the page after 10 seconds
    driver.set_page_load_timeout(10)
    try:
        data = ''
        if(website.find('cnbctv18')!=-1):
            data = CNBC(driver)

        elif(website.find('simplywall')!=-1):
            data = simply(driver)
            
        elif(website.find('businesstoday')!=-1):
            data = business_today(driver)

        elif(website.find('equitybulls')!=-1):
            data = equity_bulls(driver)

        elif(website.find('financialexpress')!=-1):
            data = fin_express(driver)

        elif(website.find('zeebiz')!=-1):
            data = zeebiz(driver)

        elif(website.find('livemint')!=-1):
            data = livemint(driver)        
            
        elif(website.find('moneycontrol')!=-1):
            data = moneycontrol(driver)

        elif(website.find('economictimes')!=-1):
            data = economic_times(driver)    

        elif(website.find('bqprime')!=-1):
            data = bqprime(driver)

        elif(website.find('business-standard')!=-1):
            data = business_standard(driver)
        else:
            # print(f"Error on url: {website}, news source NOT FOUND")
            data = (None,None,None,None)

    except:
        driver.execute_script("window.stop();")
        data = ''
        if(website.find('cnbctv18')!=-1):
            data = CNBC(driver)

        elif(website.find('simplywall')!=-1):
            data = simply(driver)
            
        elif(website.find('businesstoday')!=-1):
            data = business_today(driver)

        elif(website.find('equitybulls')!=-1):
            data = equity_bulls(driver)

        elif(website.find('financialexpress')!=-1):
            data = fin_express(driver)

        elif(website.find('zeebiz')!=-1):
            data = zeebiz(driver)

        elif(website.find('livemint')!=-1):
            data = livemint(driver)        
            
        elif(website.find('moneycontrol')!=-1):
            data = moneycontrol(driver)

        elif(website.find('economictimes')!=-1):
            data = economic_times(driver)    

        elif(website.find('bqprime')!=-1):
            data = bqprime(driver)

        elif(website.find('business-standard')!=-1):
            data = business_standard(driver)
        else:
            # print(f"Error on url: {website}, news source NOT FOUND")
            data = (None,None,None,None)


    return data


####################################################################################################