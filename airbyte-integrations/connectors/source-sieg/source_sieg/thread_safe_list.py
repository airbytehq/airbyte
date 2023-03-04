from threading import Lock
 
class ThreadSafeList():
    def __init__(self):
        self._list = list()
        self._lock = Lock()
 
    def append(self, value):
        with self._lock:
            self._list.append(value)
 
    def get(self, index):
        with self._lock:
            return self._list[index]
 
    def length(self):
        with self._lock:
            return len(self._list)
    
    def get_list(self):
        return self._list