import logging

def getLogger(name, print_level=logging.INFO):
    logging.basicConfig(level=print_level, datefmt='%m-%d %H:%M',
                        format='[%(asctime)s] %(name)s %(levelname)s :  %(message)s')
    return logging.getLogger(name)
