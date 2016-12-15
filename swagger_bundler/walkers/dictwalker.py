from collections import deque


class LooseDictWalker(object):
    def __init__(self, on_container=None, on_data=None):
        self.on_container = on_container
        self.on_data = on_data

    def on_found(self, d, k):
        if self.on_container is not None:
            self.on_container(d)
        if self.on_data is not None:
            self.on_data(d[k])

    def walk(self, paths, d):
        return self._walk(deque(paths), d)

    def _walk(self, paths, d):
        if hasattr(d, "keys"):
            for k in list(d.keys()):
                if len(paths) > 0 and paths[0] == k:
                    name = paths.popleft()
                    self._walk(paths, d[k])
                    if len(paths) == 0:
                        self.on_found(d, k)
                    paths.appendleft(name)
                else:
                    self._walk(paths, d[k])
            return d
        elif isinstance(d, (list, tuple)):
            for e in d:
                self._walk(paths, e)
            return d
        else:
            return d
