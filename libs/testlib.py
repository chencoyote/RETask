import threadlib
import threading
import zmq
import time

reciver_url = "tcp://127.0.0.1:4055"
class test(threadlib.StoppableThread):

    def __init__(self, i):
        super(test, self).__init__()
        self.i = i
        #print self.i

    def handle(self):
        timeis = 0
        while not self._stop.isSet():
            print "im work on time %d" % timeis
            timeis += 1
            c = zmq.Context()
            s = c.socket(zmq.REQ)
        #s.connect(reciver_url)
        #s.send('{"type":"msg","data":"%d"}' % self.i)
        #msg = s.recv()
#            print getattr(self,"i")

pool = threadlib.threadPool(name="test")

for i in range(2):
    print "is thread? ", issubclass(test, threadlib.StoppableThread)
    pool.add_thread(test, args=[i])

print "1",pool.get_all_tid()
time.sleep(0.1)
pool.stop_all_process()
#for i in pool:
#    print "befor ",i.stopped()
#    print i._get_my_tid()
#    i.stop()
#    print "after: ",i.stopped()
           
