from threading import Thread, active_count
import test_random_util

for i in range(5):
    Thread(target=test_random_util.main, args=[i]).start()