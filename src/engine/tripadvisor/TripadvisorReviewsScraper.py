from bs4 import BeautifulSoup
from src.model.Review import Review
from src.model.Author import Author
from selenium.webdriver.common.by import By
from src.engine.tripadvisor.TripadvisorAuthorScraper import getAuthorObj
import time
from pprint import pprint  

DEFAULT_EMPTY = "--"
TAGS_TEXT_SEPARATOR = " "

def _expandReviews(chrome):
    spans = chrome.find_elements(By.TAG_NAME, 'span')
    spansMore = [span for span in spans if span.get_attribute("onclick") == "widgetEvCall('handlers.clickExpand',event,this);"]
    spansMore[0].click()

def _selectAllLanguages(chrome):  
    divs = chrome.find_elements(By.TAG_NAME, 'label')
    allLanguageButton = [div for div in divs if div.get_attribute("for") == "filters_detail_language_filterLang_ALL"]
    allLanguageButton[0].click() 

def _nextReviewPage(chrome, pageNumber):
    url = chrome.current_url
    newReviewStart = pageNumber * 15
    if pageNumber == 1:
        newUrl = url.replace("-Reviews-", "-Reviews-or"+str(newReviewStart)+"-")
    else:
        oldReviewStart = (pageNumber-1) * 15
        newUrl = url.replace("-or"+str(oldReviewStart), "-or"+str(newReviewStart))
    chrome.get(newUrl)
    time.sleep(1.5)
    if "-or"+str(newReviewStart) in chrome.current_url:
        return True
    else:
        return False     

def _getReviewTime(soup):
    try:
        titleTag = soup.find("a", {"class" : "title"})
        return titleTag.getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY 

def _getReviewRatingDate(soup):
    try:
        ratingDateTag = soup.find("span", {"class" : "ratingDate"})
        return ratingDateTag.getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY   

def _getViaMobile(soup):
    try:
        viaMobile = soup.findAll("span", {"class" : "viaMobile"})
        return len(viaMobile) > 0
    except:
        return DEFAULT_EMPTY 

def _getDateOfVisit(soup):
    try:
        dateOfVisit = soup.find("div", {"data-prwidget-name" : "reviews_stay_date_hsx"})
        return dateOfVisit.getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY  

def _getHelpfulNumber(soup):
    try:
        dateOfVisit = soup.find("span", {"class" : "numHelp"})
        hempfulNumber = dateOfVisit.getText(separator=TAGS_TEXT_SEPARATOR).strip()
        if len(hempfulNumber) > 0: 
            return hempfulNumber
        else:
            return "0"
    except:
        return "0"        

def _getStarsValue(soup):
    try:
        ratingList = soup.find("div", {"class" : "rating-list"})
        ratingValueTag = ratingList.findAll("li", {"class" :  "recommend-answer"})[0]
        ratingValueBubbleTag = ratingValueTag.find("div")
        stars = (ratingValueBubbleTag["class"])[1].split("_")[-1]
        return stars[0] + "," + stars[1]
    except:
        return DEFAULT_EMPTY   
    
def _getStarsService(soup):
    try:
        ratingList = soup.find("div", {"class" : "rating-list"})
        ratingServiceTag = ratingList.findAll("li", {"class" :  "recommend-answer"})[1]
        ratingServiceBubbleTag = ratingServiceTag.find("div")
        stars = (ratingServiceBubbleTag["class"])[1].split("_")[-1]
        return stars[0] + "," + stars[1]
    except:
        return DEFAULT_EMPTY       

def _getStarsFood(soup):
    try:
        ratingList = soup.find("div", {"class" : "rating-list"})
        ratingFoodTag = ratingList.findAll("li", {"class" :  "recommend-answer"})[2]
        ratingFoodBubbleTag = ratingFoodTag.find("div")
        stars = (ratingFoodBubbleTag["class"])[1].split("_")[-1]
        return stars[0] + "," + stars[1]
    except:
        return DEFAULT_EMPTY  

def _getReviewText(soup):
    try:
        reviewTextTag = soup.findAll("p", {"class" : "partial_entry"})[0]
        return reviewTextTag.getText(separator=TAGS_TEXT_SEPARATOR).replace('\n', '')
    except:
        return DEFAULT_EMPTY    

def _getReviewReply(soup):
    try:
        reviewReplyTag = soup.findAll("p", {"class" : "partial_entry"})[1]
        return reviewReplyTag.getText(separator=TAGS_TEXT_SEPARATOR).replace('\n', '')
    except:
        return DEFAULT_EMPTY   
    
def _getReviewReviews(soup):
    try:
        reviewerReviews = soup.find("div", {"class" : "memberBadging g10n is-shown-at-tablet"})
        return reviewerReviews.getText(separator=TAGS_TEXT_SEPARATOR).replace('\n', '')
    except:
        return DEFAULT_EMPTY      

def _getReviewAuthor(soup, chrome):
    try:
        return getAuthorObj(soup, chrome)
    except:
        return Author()                             

def _scrapeReview(reviewSoup, chrome):
    review = Review()
    review.title = _getReviewTime(reviewSoup)
    review.ratingDate = _getReviewRatingDate(reviewSoup)
    review.isViaMobile = _getViaMobile(reviewSoup)
    review.dateOfVisit = _getDateOfVisit(reviewSoup)
    review.helpful = _getHelpfulNumber(reviewSoup)
    review.starsValue = _getStarsValue(reviewSoup)
    review.starsService = _getStarsService(reviewSoup)
    review.starsFood = _getStarsFood(reviewSoup)
    review.text = _getReviewText(reviewSoup)
    review.reply = _getReviewReply(reviewSoup)
    review.reviewerReviews = _getReviewReviews(reviewSoup)
    review.setAuthor(_getReviewAuthor(reviewSoup, chrome))
    return review



def getUsersReviews(soup, chrome, restaurantId, maxReviews):
    reviewPageNumber = 0
    reviewsObjList = list()
    try:
        _selectAllLanguages(chrome)
        time.sleep(1.5)

        while len(reviewsObjList) < int(maxReviews):
            reviewPageNumber += 1
            _expandReviews(chrome)
            time.sleep(1.5)

            expandedHtml = chrome.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
            soup = BeautifulSoup(expandedHtml, 'html.parser')

            detailTag = soup.find("div", {"data-tab" : "TABS_REVIEWS"})
            reviewsListTag = detailTag.find("div", {"data-contextchoice" : "DETAIL"})
            reviews = reviewsListTag.findAll("div", {"class": "review-container"})

            for review in reviews:
                try:
                    newReview = _scrapeReview(review, chrome)
                    newReview.restaurantId = restaurantId
                    reviewsObjList.append(newReview)
                except:
                    pass
        
            if _nextReviewPage(chrome, reviewPageNumber) == False:
                break    
    except:
        pass
    return reviewsObjList