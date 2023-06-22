import threading

class ConcurrentRunner:
    def __init__(self):
        self.results = {}

    def _run_function(self, func, *args, **kwargs):
        result = func(*args, **kwargs)
        self.results[func.__name__] = result

    def run_concurrently(self, *functions):
        threads = []

        for func in functions:
            thread = threading.Thread(target=self._run_function, args=(func,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return self.results