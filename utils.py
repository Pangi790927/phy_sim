import time
import numpy as np

# if you don't want to count frames per second you can choose another interval
class FpsCounter:
    def __init__(self, update_interval_sec=None):
        self.started = False
        self.update_interval = update_interval_sec if update_interval_sec else 1
        
    def start(self):
        self.last_time = time.time()
        self.curr_cnt = 0
        self.fps = 0
        self.started = True

    def update(self):
        if not self.started:
            self.start()
        self.curr_cnt += 1
        curr_time = time.time()
        if curr_time - self.last_time > self.update_interval:
            self.fps = self.curr_cnt / ((curr_time - self.last_time) /\
                    self.update_interval)
            self.last_time = curr_time
            self.curr_cnt = 0
            return True
        return False

    def get_fps(self):
        return self.fps
