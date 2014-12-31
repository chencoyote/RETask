import threadlib
import threading
import zmq
import time

reciver_url = "tcp://127.0.0.1:4055"
class test(threadlib.StoppableThread):

    def __init__(self, i):
        super(test, self).__init__()
        self.i = i

    def handle(self):
        while not self._stop.isSet():
            print "im work"
            c = zmq.Context()
            s = c.socket(zmq.REQ)
            s.connect(reciver_url)
            s.send('{"type":"msg","data":"%d"}' % self.i)
            msg = s.recv()
            print msg

pool = threadlib.threadPool(name="test")

for i in range(2):
    print "is thread? ", issubclass(test, threadlib.StoppableThread)
    pool.add_thread(test, args=[i])

print pool.get_all_tid()
time.sleep(1)
pool.stop_all_process()
print pool.get_all_tid()
#for i in pool:
#    print "befor ",i.stopped()
#    print i._get_my_tid()
#    i.stop()
#    print "after: ",i.stopped()
           
