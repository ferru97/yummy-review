import os
import sys
import time
import logging
import validators
import pandas as pd
import src.utils.SeleniumUtils as SeleniumUtils
from urllib.parse import urlparse
from src.engine.tripadvisor.TripadvisorScraperEngine import scrapeTripadvisorRestaurant


TOTAL_NUMER_OF_ARGUMENT = 2
INPUT_FILE_DIRECTORY = "input/"
OUTPUT_FILE_DIRECTORY = "output/"

def _loadInputFile(filename):
    inputFilePath = os.path.join(INPUT_FILE_DIRECTORY, filename)
    df = pd.read_csv(inputFilePath)
    logging.info(f'Loaded dataset with {df.size} records')
    return df

def _acceptPrivacyPolicy(restaurantsDataset, chrome):
    domains = set()
    for _, restaurant in restaurantsDataset.iterrows():
        restaurantLink = str(restaurant["TripAdvisor"])
        if validators.url(restaurantLink):
            parsedUri = urlparse(restaurantLink)
            baseUrl = '{uri.scheme}://{uri.netloc}/'.format(uri=parsedUri)
            if baseUrl not in domains:
                domains.add(baseUrl)

    for domain in domains:
        logging.info(f"Accept privacy policy for [{domain}]' and press ENTER...")
        chrome.get(domain)
        input()

def saveRestaurantData(restaurantData, reviewsData, websiteName):
    outputRestaurantDf = pd.DataFrame(restaurantData)
    outputRestaurantDf.to_csv(os.path.join(OUTPUT_FILE_DIRECTORY, f"{websiteName}_restaurants.csv"), sep='\t', quotechar='"', encoding='utf-8')

    outputRviewsDf = pd.DataFrame(reviewsData)
    outputRviewsDf.to_csv(os.path.join(OUTPUT_FILE_DIRECTORY, f"{websiteName}_restaurants_reviews.csv"), sep='\t', quotechar='"', encoding='utf-8')

    

def run(restaurantsDataset, maxReviews):
    chrome = SeleniumUtils.getSeleniumInstance()
    _acceptPrivacyPolicy(restaurantsDataset, chrome)

    logging.info("Scraping process started...")
    restaurantData = list()
    reviewsData = list()

    for index, restaurant in restaurantsDataset.iterrows():
        restaurantName =  restaurant["Restaurant Name"]
        restaurantLink = str(restaurant["TripAdvisor"])

        if validators.url(restaurantLink):
            try:
                logging.info(f"{index+1}/{restaurant.size} Scraping restaurant [{restaurantName}] from Tripadvisor...")
                restaurantObj, reviewsList = scrapeTripadvisorRestaurant(chrome, restaurantName, restaurantLink, maxReviews , index)
                restaurantData.append(restaurantObj.getCsvRecord())
                reviewsData = reviewsData + reviewsList
            except:
                logging.warning(f"{index+1}/{restaurant.size} Error while processing restaurant [{restaurantName}]!")
        if index > 1:
            break
    
    revireCsvData = [data.getCsvRecord() for data in reviewsData]
    saveRestaurantData(restaurantData, revireCsvData, "tripadvisor")
    

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
    logging.info("YUMMY SCOUT!\n")

    if len(sys.argv) < 3:
        logging.critical("Invalid arguments, must be 'main.py [input_file_name] [max_reviews]' ")
        sys.exit()

    restaurantsDataset = _loadInputFile(sys.argv[1])
    run(restaurantsDataset, sys.argv[2])