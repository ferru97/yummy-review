from bs4 import BeautifulSoup
from src.model.Review import Review
from src.model.Author import Author
from selenium.webdriver.common.by import By
from src.engine.tripadvisor.TripadvisorAuthorScraper import getAuthorObj
import time
import logging

DEFAULT_EMPTY = "--"
TAGS_TEXT_SEPARATOR = " "

def _expandReviews(chrome, retry=True):
    try:
        spans = chrome.find_elements(By.TAG_NAME, 'span')
        spansMore = [span for span in spans if span.get_attribute("onclick") == "widgetEvCall('handlers.clickExpand',event,this);"]
        if len(spansMore) > 0:
            spansMore[0].click()
    except Exception as e:
        logging.error("Expand reviews exception, refreshing page...")
        if retry:
            chrome.refresh()
            time.sleep(2)
            _expandReviews(chrome, False)
        else:
            raise e      

def _selectAllLanguages(chrome):  
    divs = chrome.find_elements(By.TAG_NAME, 'label')
    allLanguageButton = [div for div in divs if div.get_attribute("for") == "filters_detail_language_filterLang_ALL"]
    if len(allLanguageButton) > 0:
        allLanguageButton[0].click() 

def _nextReviewPage(chrome, retry=True):
    try:
        oldUrl = chrome.current_url
        chrome.execute_script("document.getElementsByClassName('nav next ui_button primary')[0].click()")
        newUrl = chrome.current_url
        time.sleep(0.5)
        chrome.get(chrome.current_url)
        time.sleep(1)
        return oldUrl == newUrl
    except Exception as e:
        logging.error("Next page exception, refreshing page...")
        logging.error(e)
        if retry:
            chrome.refresh()
            time.sleep(2)
            _nextReviewPage(chrome, False)
        else:
            raise e

def _goToReviewPage(chrome, pageNum):
    while pageNum != 0:
        chrome.execute_script(f"document.querySelector(\"a[class='nav next ui_button primary']\").click()")
        time.sleep(0.7)
        pageNum -= 1


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
        reviewerReviews = soup.find("div", {"class" : "reviewerBadge badge"})
        if reviewerReviews is not None:
            return reviewerReviews.getText(separator=TAGS_TEXT_SEPARATOR).replace('\n', '')
        else:
            reviewerReviews = soup.find("span", {"class" : "badgetext"})
            return reviewerReviews.getText(separator=TAGS_TEXT_SEPARATOR).replace('\n', '')
    except:
        return DEFAULT_EMPTY      

def _getReviewAuthor(soup, chrome):
    try:
        return getAuthorObj(soup, chrome)
    except:
        return Author()                             

def _scrapeReview(reviewSoup, chrome, pageNumber):
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
    review.page = pageNumber
    return review



def getUsersReviews(soup, chrome, restaurantId, maxReviews, startReviewsPage):
    reviewPageNumber = int(startReviewsPage)
    logging.info(f"\tStart scraping reviews from page [{startReviewsPage}]")
    reviewsObjList = list()
    isLastPage = False
    try:
        _selectAllLanguages(chrome)
        time.sleep(1)

        if int(startReviewsPage):
            _goToReviewPage(chrome, startReviewsPage)
            time.sleep(1)

        while len(reviewsObjList) < int(maxReviews):
            reviewPageNumber += 1
            _expandReviews(chrome)
            time.sleep(1)

            expandedHtml = chrome.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
            soup = BeautifulSoup(expandedHtml, 'html.parser')

            detailTag = soup.find("div", {"data-tab" : "TABS_REVIEWS"})
            reviewsListTag = detailTag.find("div", {"data-contextchoice" : "DETAIL"})
            reviews = reviewsListTag.findAll("div", {"class": "review-container"})

            for review in reviews:
                try:
                    newReview = _scrapeReview(review, chrome, reviewPageNumber)
                    newReview.restaurantId = restaurantId
                    reviewsObjList.append(newReview)
                except:
                    pass
        
            if isLastPage:
                break
            else:
                isLastPage = _nextReviewPage(chrome)
    except:
        pass
    return reviewsObjList
