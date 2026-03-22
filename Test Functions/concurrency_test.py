from queue import Queue
import concurrent.futures
import time


class DataGetter:
    def __init__(self, q: Queue):
        self.q = q
        
    def retrieve_data(self):
        j = 0
        while True:
            self.q.put(j)
            j += 1
            time.sleep(0.7)


data_q = Queue()

def wait_for(num):
    return f'Waiting...{num}'

def display():
    i = 0
    while True:
        if data_q.empty():
            print(wait_for(i))
        else:
            print(f'Got {data_q.get()}')
        i += 1
        time.sleep(0.2)

def manager():
    gettr = DataGetter(data_q)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as exc:
        exc.submit(gettr.retrieve_data)
        exc.submit(display)

if __name__ == '__main__':
    manager()