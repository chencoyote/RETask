# -*- coding: utf-8 -*-

import zmq
import threading
import timeit
import time
import pdb

count = 10
reciver_url = "tcp://127.0.0.1:4055"

def connect_send(i):
    print i
    c = zmq.Context()
    s = c.socket(zmq.REQ)
    
    s.connect(reciver_url)
    s.send('{"type":"msg","data":"%d"}' % i)
    msg = s.recv()
    print msg
    s.close()

def run():
#    pdb.set_trace()
    for i in xrange(1,100):
        t = threading.Thread(target=connect_send, args=[i])
        t.setDaemon(True)
        t.start()
    return
run()
#t = timeit.Timer(run)
#print t.timeit(1)


