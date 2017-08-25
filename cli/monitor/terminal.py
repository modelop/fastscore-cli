
import sys

class Terminal(object):
    
    def __init__(self, max_width=80):
        self._max_width = max_width
        self._lines = []
        self._cursor = 0
        self._limit = 0

    @property
    def max_width(self):
        return self._max_width

    def insert(self, key, text, before=None):
        at = len(self._lines) if before == None else self.key_to_index(before)
        if self._cursor >= self._limit: # ==
            self.move_to(self._limit)
            print # a space for a new line
            self._cursor += 1
            self._limit += 1
        self._lines.insert(at, (key,text))
        for i in range(at, len(self._lines)):
            self.redraw(i)
    
    def remove(self, key):
        at = self.key_to_index(key)
        self.clear(len(self._lines)-1)
        self._lines.pop(at)
        for i in range(at, len(self._lines)):
            self.redraw(i)

    def remove_by_tag(self, tag):
        keys = []
        for key,_ in self._lines:
            if isinstance(key, tuple) and key[0] == tag:
                keys.append(key)
        for key in keys:
            self.remove(key)
    
    def update(self, key, text, pos=None):
        at = self.key_to_index(key)
        if pos == None:
            self._lines[at] = (key,text)
        else:
            bkg = self._lines[at][1]
            end = pos + len(text)
            self._lines[at] = (key,bkg[:pos] + text + bkg[end:])
        self.redraw(at)

    def key_to_index(self, key):
        for i in range(len(self._lines)):
            if self._lines[i][0] == key:
                return i

    def move_up(self, n):
        sys.stdout.write(u'\u001b[%dA' % n) 
        sys.stdout.flush()
        self._cursor -= n

    def move_down(self, n):
        sys.stdout.write(u'\u001b[%dB' % n) 
        sys.stdout.flush()
        self._cursor += n

    def move_to(self, row):
        if row == self._cursor:
            return
        if row > self._cursor:
            self.move_down(row - self._cursor)
        else:
            self.move_up(self._cursor - row)

    def redraw(self, i):
        self.move_to(i)
        sys.stdout.write(" " * self._max_width)
        sys.stdout.write(u'\u001b[1000D')
        sys.stdout.write(self._lines[i][1])
        sys.stdout.write(u'\u001b[1000D')
        sys.stdout.flush()

    def clear(self, i):
        self.move_to(i)
        sys.stdout.write(" " * self._max_width)
        sys.stdout.write(u'\u001b[1000D')
        sys.stdout.flush()

