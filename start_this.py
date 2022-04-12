import logging
import time


logging.basicConfig(filename="log.txt", level=logging.INFO)


while True:
    try:
        print('Launch!')
        import bot_body
    except Exception as e:
        logging.error(f'VERY BIG PROBLEM!\n{str(e)}')
        print(f'VERY BIG PROBLEM!\n{str(e)}')
        time.sleep(10)
