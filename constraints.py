import pymongo

manga_constraints = [
    [('name', pymongo.ASCENDING)],
    [('url', pymongo.ASCENDING)]
]

chapter_constraints = [
    [('name', pymongo.ASCENDING), ('chapter_number', pymongo.ASCENDING)],
    [('url', pymongo.ASCENDING)]
]

