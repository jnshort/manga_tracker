manga_validator = {
    'validator': {
        '$jsonSchema': {
            'bsonType': 'object',
            'description': 'A manga that is being tracked by my program',
            'required': ['name', 'url', 'current_chapter', 'chapters'],
            'additionalProperties': False,
            'properties': {
                '_id': {},
                'name': {
                    'bsonType': 'string',
                    'description': 'name of the anime',
                },
                'url': {
                    'bsonType': 'string',
                    'description': 'cut off url after .com/ (or .ext/) for example https://animeheaven.me/'
                },
                'current_chapter': {
                    'bsonType': 'int',
                    'description': 'Next unread chapter'
                },
                'chapters': {
                    'bsonType': 'array',
                    'description': 'list of chapters',
                    'minItems': 0,
                    'uniqueItems': True,
                    'items': {
                        'bsonType': 'object',
                        'description': 'individual chapter of an manga',
                        'required': ['name', 'url', 'chapter_number'],
                        'additionalProperties': False,
                        'properties': {
                            'name': {
                            'bsonType': 'string',
                            'description': 'name of the manga',
                            },
                            'url': {
                                'bsonType': 'string',
                                'description': 'url of chapter'
                            },
                            'chapter_number': {
                                'bsonType': 'int',
                                'description': 'number of chapter in series'
                            },
                        }
                    }
                }
            }
        }
    }
}

