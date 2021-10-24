import time

class FpsCounter:
    def __init__(self):
        self.started = False

    def start(self):
        self.last_time = time.time()
        self.curr_cnt = 0
        self.fps = 0
        self.started = True

    def update(self):
        if not self.started:
            self.start()
        self.curr_cnt += 1
        if time.time() - self.last_time > 1:
            self.last_time = time.time()
            self.fps = self.curr_cnt
            self.curr_cnt = 0
            return True
        return False

    def get_fps(self):
        return self.fps
