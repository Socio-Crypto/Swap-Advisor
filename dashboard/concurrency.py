import threading

class ConcurrentRunner:
    def __init__(self):
        self.results = {}

    def _run_function(self, name, func, *args, **kwargs):
        result = func(*args, **kwargs)
        self.results[name] = result
    
    def run_concurrently(self, *functions):
        threads = []

        for i, func in enumerate(functions):
            name = f"func{i+1}"
            thread = threading.Thread(target=self._run_function, args=(name, func,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return self.results