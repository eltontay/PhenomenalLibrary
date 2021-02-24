class Books:
    def __init__(self, 
                 id, 
                 title,
                 isbn,
                 pageCount,
                 publishedDate,
                 thumbnailUrl,
                 shortDescription,
                 LongDescription,
                 status,
                 orders,
                 categories):
        self.id=id
        self.title=title
        self.isbn=isbn
        self.pageCount=pageCount
        self.publishedDate=publishedDate
        self.thumbnailUrl=thumbnailUrl
        self.shortDescription=shortDescription
        self.LongDescription=LongDescription
        self.status=status
        self.orders=orders
        self.categories=categories