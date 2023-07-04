import re
from bs4 import BeautifulSoup
from src.model.Restaurant import Restaurant
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

DEFAULT_EMPTY = "--"
TAGS_TEXT_SEPARATOR = " "

def getName(soup):
    try:
        detailTag = soup.find("div", {"data-test-target" : "restaurant-detail-info"})
        nameTag = detailTag.find("h1", {"data-test-target" : "top-info-header"})
        return nameTag.getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY

def getStars(soup):
    try:
        detailTag = soup.find("div", {"data-test-target" : "restaurant-detail-info"})
        reviewsTag = detailTag.find("a", {"href" : "#REVIEWS"})
        svgBubbles = reviewsTag.find("svg")
        bubbleNumberStr = svgBubbles["aria-label"].split(" ")
        bubbleNumber = [s for s in bubbleNumberStr if s[0].isdigit()]
        return bubbleNumber[0]
    except:
        return DEFAULT_EMPTY 

def getReviews(soup):
    try:
        detailTag = soup.find("div", {"data-test-target" : "restaurant-detail-info"})
        reviewsTag = detailTag.find("a", {"href" : "#REVIEWS"})
        reviewsSpanTag = reviewsTag.find("span")
        return (reviewsSpanTag.text.split(" "))[0]
    except:
        return DEFAULT_EMPTY    

def getRanking(soup):
    try:
        detailTag = soup.find("div", {"data-test-target" : "restaurant-detail-info"})
        rankingTag = detailTag.find("span", {"class" : "DsyBj cNFrA"})
        return rankingTag.getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY  

def getAffordability(soup):
    try:
        detailTag = soup.find("div", {"data-test-target" : "restaurant-detail-info"})
        affordabilityTag = detailTag.find("span", {"class" : "DsyBj DxyfE"})
        return affordabilityTag.getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY  

def getAddress(soup):
    try:
        detailTag = soup.find("div", {"data-test-target" : "restaurant-detail-info"})
        secondaryInfoTag = detailTag.findAll("div", {"class" : "vQlTa H3"})[1]
        spans = secondaryInfoTag.findAll("span", recursive=False)
        return spans[0].getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY 

def getPhoneNumber(soup):
    try:
        detailTag = soup.find("div", {"data-test-target" : "restaurant-detail-info"})
        secondaryInfoTag = detailTag.findAll("div", {"class" : "vQlTa H3"})[1]
        spans = secondaryInfoTag.findAll("span", recursive=False)
        return spans[1].getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY   
    
def getMichelinStar(soup):
    try:
        detailTag = soup.find("div", {"data-test-target" : "restaurant-detail-info"})
        images = detailTag.findAll("img")
        for img in images:
            src = img["src"]
            if "-Stars.svg" in src:
                return ((src.split("/"))[-1]).split("-")[0]
        return DEFAULT_EMPTY
    except:
        return DEFAULT_EMPTY  

def getServiceStars(soup, serviceType):
    try:
        detailTag = soup.find("div", {"data-tab" : "TABS_OVERVIEW"})
        columnsDivTag = detailTag.find("div", {"class" : "ui_columns"})
        reviewDiv = columnsDivTag.findAll("div", recursive=False)[0]
        starsDivs = reviewDiv.findAll("div", {"class" : "DzMcu"})
        for starsDiv in starsDivs:
            spansInfo = starsDiv.findAll("span")
            if serviceType in (spansInfo[0])["class"]:
                ratingSpan = (spansInfo[2]).find("span")
                stars = (ratingSpan["class"])[1].split("_")[-1]
                return stars[0]+"."+stars[1]
        return DEFAULT_EMPTY
    except:
        return DEFAULT_EMPTY 

def getMeals(soup):
    try:
        detailTag = soup.find("div", {"data-tab" : "TABS_OVERVIEW"})
        columnsDivTag = detailTag.find("div", {"class" : "ui_columns"})
        regexClass = re.compile('xLvvm ui_column.*')
        reviewDiv = columnsDivTag.findAll("div", {"class" : regexClass})[1]
        mealsDiv = reviewDiv.findAll("div", {"class" : "SrqKb"})
        return mealsDiv[1].getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY   

def getMichelinReview(soup, chrome):
    if len(chrome.window_handles) < 2:
        chrome.execute_script("window.open('');")

    reviewText = DEFAULT_EMPTY
    try:
        detailTag = soup.find("div", {"data-tab" : "TABS_OVERVIEW"})
        columnsDivTag = detailTag.find("div", {"class" : "ui_columns"})
        reviewDiv = columnsDivTag.findAll("div")[0]
        aTags = reviewDiv.findAll("a")
        for link in aTags:
            href = link["href"]
            if "guide.michelin" in href: 
                chrome.switch_to.window(chrome.window_handles[1])
                chrome.get(href)
                html = chrome.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
                michelinSoup = BeautifulSoup(html, 'html.parser')
                review = michelinSoup.find("div", {"class" : "restaurant-details__description--text"})
                reviewText = review.getText(separator=TAGS_TEXT_SEPARATOR).strip()
    except:
        pass
    chrome.switch_to.window(chrome.window_handles[0])
    return reviewText  

def getHours(soup):
    # TODO since is dynamic
    return "TODO"  