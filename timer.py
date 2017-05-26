
import time
import threading

class Timer(object):
    def __init__(self, seconds=60):
        self.seconds = seconds
        self.remaining = 0

    def start(self):
        thread = threading.Thread(target=Timer.__start, args=(self,))
        thread.start()

    def __start(self):
        self.remaining = self.seconds

        while self.remaining > 0:
            time.sleep(1)
            self.remaining -= 1

        self.remaining = 0
