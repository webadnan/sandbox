# It reads one token of word or number from stdin.
class Tokens:
    def __init__(self, splitter=' '):
        self.queue = []
        self.splitter = splitter
    def read(self):
        if len(self.queue) > 0:
            return self.queue.pop(0)
        while True:
            line = input()
            if not line: continue
            self.queue = line.split(self.splitter)
            if len(self.queue) == 0: continue
            return self.queue.pop(0)
    def int(self):
        return int(self.read())