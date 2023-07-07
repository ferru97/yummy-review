from src.model.Review import Review

class Restaurant:

    def __init__(self):
        DEFAULT_VALUE = "--"

        self.name = DEFAULT_VALUE
        self.id = DEFAULT_VALUE
        self.link = DEFAULT_VALUE
        self.stars = DEFAULT_VALUE
        self.reviews = DEFAULT_VALUE
        self.ranking = DEFAULT_VALUE
        self.affordability = DEFAULT_VALUE
        self.address = DEFAULT_VALUE
        self.phone = DEFAULT_VALUE
        self.hours = DEFAULT_VALUE
        self.starsFood = DEFAULT_VALUE
        self.starsService = DEFAULT_VALUE
        self.starsWallet = DEFAULT_VALUE
        self.starsAtmosphere = DEFAULT_VALUE
        self.meals = DEFAULT_VALUE
        self.michelinReview = DEFAULT_VALUE
        self.michelinStars = DEFAULT_VALUE
        self.numReviews = DEFAULT_VALUE
        self._reviewsText = list()

    def addReview(self, review: Review):
        self._reviewsText.append(review)

    def getReviews(self, review: Review):
        return self._reviewsText

    def getCsvRecord(self):
        data = self.__dict__
        data.pop("_reviewsText", None)
        return data         