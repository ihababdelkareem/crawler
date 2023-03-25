import threading
import time

def handler(letter: str) -> None:
    for _ in range(10000):
        print(letter)

a = threading.Thread(target=handler, args=('a',))
b = threading.Thread(target=handler, args=('b',))
a.start()
b.start()
a.join()
b.join()
