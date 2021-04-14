LOGGING_CONFIG = {
        'version':1,
        'handlers':{
            'fileHandler':{
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter':'myFormatter',
                'filename':'my_logger.log',
                'maxBytes': 50000000,
                'backupCount': 5,
                'encoding':'utf-8'
            }
        },
        'loggers':{
            'info':{
                'handlers':['fileHandler'],
                'level':'INFO',
            },
            'debug':{
                'handlers':['fileHandler'],
                'level':'DEBUG',
            }
        },
        'formatters':{
            'myFormatter':{
                'format':'%(asctime)s, %(levelname)s, %(message)s'
            }
        }
    }
