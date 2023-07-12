import os
import sys
import time
import logging
import argparse
import validators
import pandas as pd
import src.utils.SeleniumUtils as SeleniumUtils
from urllib.parse import urlparse
from src.engine.tripadvisor.TripadvisorScraperEngine import scrapeTripadvisorRestaurant


TOTAL_NUMER_OF_ARGUMENT = 2
INPUT_FILE_DIRECTORY = "input/"
OUTPUT_FILE_DIRECTORY = "output/"
TRIPADVISOR_SOURCE = "tripadvisor"
GOOGLE_SOURCE = "google"

DF_TA_START_REVIEWS_PAGE = "ta_reviews_start"
DF_RESTAURANT_NAME = "Restaurant Name"
DF_TRIPADVISOR_LINK = "TripAdvisor"
DF_PROCESSED = "Processed"
DF_ID = "ID"

def _loadInputFile(filename):
    inputFilePath = os.path.join(INPUT_FILE_DIRECTORY, filename)
    df = pd.read_csv(inputFilePath)
    if not DF_TA_START_REVIEWS_PAGE in df.columns:
        df[DF_TA_START_REVIEWS_PAGE] = 0
    if not DF_ID in df.columns:
        df.insert(0, DF_ID, range(1, 1 + len(df)))
    if not DF_PROCESSED in df.columns:
        df[DF_PROCESSED] = "N"

    df.to_csv(inputFilePath, index=False)    
    logging.info(f'Loaded dataset with {len(df.index)} records')
    return df

def _updateInputFile(filename, df):
    inputFilePath = os.path.join(INPUT_FILE_DIRECTORY, filename)
    df.to_csv(inputFilePath, index=False)   


def _acceptPrivacyPolicy(restaurantsDataset, chrome):
    domains = set()
    for _, restaurant in restaurantsDataset.iterrows():
        restaurantLink = str(restaurant[DF_TRIPADVISOR_LINK])
        if validators.url(restaurantLink):
            parsedUri = urlparse(restaurantLink)
            baseUrl = '{uri.scheme}://{uri.netloc}/'.format(uri=parsedUri)
            if baseUrl not in domains:
                domains.add(baseUrl)

    for domain in domains:
        logging.info(f"Accept privacy policy for [{domain}]' and press ENTER...")
        chrome.get(domain)
        input()

def _saveRestaurantData(restaurantData, reviewsData, websiteName):
    reviewsData = [data.getCsvRecord() for data in reviewsData]
    restaurantOutputFile = os.path.join(OUTPUT_FILE_DIRECTORY, f"{websiteName}_restaurants.csv")
    reviewsOutputFile = os.path.join(OUTPUT_FILE_DIRECTORY, f"{websiteName}_restaurants_reviews.csv")
    
    withHeaderRestaurant = os.path.exists(restaurantOutputFile) == False
    outputRestaurantDf = pd.DataFrame(restaurantData)
    outputRestaurantDf.to_csv(restaurantOutputFile, sep='\t', quotechar='"', encoding='utf-8', mode='a', header=withHeaderRestaurant)

    withHeaderReview = os.path.exists(reviewsOutputFile) == False
    outputRviewsDf = pd.DataFrame(reviewsData)
    outputRviewsDf.to_csv(reviewsOutputFile, sep='\t', quotechar='"', encoding='utf-8', mode='a', header=withHeaderReview)  

    

def run(filename, maxReviews, source):
    restaurantsDataset = _loadInputFile(filename)
    datasetSize = len(restaurantsDataset.index)
    chrome = SeleniumUtils.getSeleniumInstanceFirefox()
    _acceptPrivacyPolicy(restaurantsDataset, chrome)

    logging.info("Scraping process started...")
    restaurantData = list()
    reviewsData = list()

    for index, restaurant in restaurantsDataset.iterrows():
        restaurantName =  restaurant[DF_RESTAURANT_NAME]
        restaurantLink = str(restaurant[DF_TRIPADVISOR_LINK])
        startPage = restaurant[DF_TA_START_REVIEWS_PAGE]

        if restaurant[DF_PROCESSED] == "Y":
            logging.info(f"{index+1}/{datasetSize} Restaurant [{restaurantName}] already processed...")
            continue

        if validators.url(restaurantLink):
            try:
                timeStart = time.time()
                logging.info(f"{index+1}/{datasetSize} Scraping restaurant [{restaurantName}] from Tripadvisor...")
                if source == TRIPADVISOR_SOURCE:
                    restaurantObj, reviewsList = scrapeTripadvisorRestaurant(chrome, restaurantName, restaurantLink, maxReviews , 
                                                                             index, startPage, restaurant[DF_ID])
                    if int(startPage) == 0:
                        restaurantData.append(restaurantObj.getCsvRecord())
                    reviewsData = reviewsData + reviewsList
                    
                    if len(reviewsList) > 0:
                        lastReviewPage = max([int(review.page) for review in reviewsList])
                    else:
                        lastReviewPage = 0    
                        
                    if lastReviewPage == 0 or lastReviewPage == int(startPage):
                        restaurantsDataset.loc[index, DF_PROCESSED] = "Y"
                    else:    
                        restaurantsDataset.loc[index, DF_TA_START_REVIEWS_PAGE] = lastReviewPage

                    timeEnd = time.time()
                    logging.info(f"\tFinished scraping restaurant [{restaurantName}] in {int(timeEnd-timeStart)} seconds")

                if len(restaurantData)%10 == 0:
                    logging.info("Saving partial results....")
                    _saveRestaurantData(restaurantData, reviewsData, "tripadvisor")
                    _updateInputFile(filename, restaurantsDataset)
                    restaurantData = list()
                    reviewsData = list()
            except Exception as e:
                logging.warning(f"{index+1}/{restaurant.size} Error while processing restaurant [{restaurantName}]! : {str(e)}")
        else:
            logging.error(f"{index+1}/{datasetSize} Invalid link for restaurant [{restaurantName}]!")
    
    _saveRestaurantData(restaurantData, reviewsData, "tripadvisor")
    _updateInputFile(filename, restaurantsDataset)
    

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
    logging.info("YUMMY SCOUT!\n")

    parser = argparse.ArgumentParser(description='YUMMY SCOUT')
    parser.add_argument('--file', required=True, help='input file name')
    parser.add_argument('--max-reviews', required=True, type=int, help='maximum number of reviews to fetch for each restaurant')
    parser.add_argument('--source', required=True, help='source to scrape from: tripadvisor or google')
    args = parser.parse_args()

    if args.source not in [TRIPADVISOR_SOURCE, GOOGLE_SOURCE]:
        logging.critical(f"Invalid source [{args.source}], choose between [{TRIPADVISOR_SOURCE}] and [{GOOGLE_SOURCE}]")
        sys.exit()

    run(args.file, args.max_reviews, args.source)