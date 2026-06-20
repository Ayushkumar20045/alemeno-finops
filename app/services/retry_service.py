import time


def retry_operation(func, retries=3, delay=2):

    for attempt in range(retries):

        try:
            return func()

        except Exception as e:

            if attempt == retries - 1:
                return None

            time.sleep(delay)