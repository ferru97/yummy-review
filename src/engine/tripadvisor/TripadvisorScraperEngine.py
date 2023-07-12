import re
import logging
from bs4 import BeautifulSoup
from src.engine.tripadvisor.TripadvisorBaseInfoScraper import *
from src.engine.tripadvisor.TripadvisorReviewsScraper import *
from pprint import pprint      
import time            

def scrapeTripadvisorRestaurant(chrome, restaurantName, restaurantLink, maxReviews, restaurantId, startReviewsPage, id):
    chrome.get(restaurantLink)
    time.sleep(2)
    html = chrome.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    soup = BeautifulSoup(html, 'html.parser')

    restaurant = Restaurant()
    restaurant.name = getName(soup)
    restaurant.id = id
    restaurant.link = restaurantLink
    restaurant.stars = getStars(soup)
    restaurant.reviews = getReviews(soup)
    restaurant.ranking = getRanking(soup)
    restaurant.affordability = getAffordability(soup)
    restaurant.address = getAddress(soup)
    restaurant.phone = getPhoneNumber(soup)
    restaurant.hours = getHours(soup)
    restaurant.michelinStars = getMichelinStar(soup)
    restaurant.starsFood = getServiceStars(soup, "restaurants")
    restaurant.starsService = getServiceStars(soup, "bell")
    restaurant.starsWallet = getServiceStars(soup, "wallet-fill")
    restaurant.starsAtmosphere = getServiceStars(soup, "ambience")
    restaurant.meals = getMeals(soup)
    restaurant.michelinReview = getMichelinReview(soup, chrome)
    reviews = getUsersReviews(soup, chrome, restaurantId, maxReviews, startReviewsPage)
    
    reviewsNumber = len(reviews)
    logging.info(f"\tFound {reviewsNumber} reviews for restaurant [{restaurantName}]")

    return restaurant, reviews