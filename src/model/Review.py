from src.model.Author import Author

class Review:

    def __init__(self):
        DEFAULT_VALUE = "--"

        self.restaurantId = DEFAULT_VALUE
        self.title = DEFAULT_VALUE
        self.ratingDate = DEFAULT_VALUE
        self.reviewerReviews = DEFAULT_VALUE
        self.dateOfVisit = DEFAULT_VALUE
        self.helpful = DEFAULT_VALUE
        self.text = DEFAULT_VALUE
        self.isViaMobile = False
        self.starsValue = DEFAULT_VALUE
        self.starsService = DEFAULT_VALUE
        self.starsFood = DEFAULT_VALUE
        self.reply = DEFAULT_VALUE
        self._author = DEFAULT_VALUE

    def setAuthor(self, reviewer: Author):
        self._author = reviewer
        

    def getCsvRecord(self):
        authorData = self._author.__dict__
        renamedAuthorData = dict()
        for key in authorData:
            renamedAuthorData["author_"+key] = authorData[key]

        reviewData = self.__dict__
        reviewData.pop("_author", None)

        return reviewData | renamedAuthorData




        