# It reads one token of word or number from stdin.
# USAGES:
#   tokens = Tokens()
#   n = tokens.int()
#   s = tokens.read()
import re
class Tokens:
    def __init__(self, splitter=' '):
        self.queue = []
        self.splitter = splitter
    def readline(self):
        while True:
            line = input()
            if line: break
        return line
    def read(self):
        if len(self.queue) > 0:
            return self.queue.pop(0)
        line = self.readline()
        self.queue = re.split('[\t ]', line)
        return self.queue.pop(0)
    def int(self):
        return int(self.read())