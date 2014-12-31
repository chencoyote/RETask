# coding: utf-8

import threading
import Queue
import time
import sys

Qin = Queue.Queue()
Qout = Queue.Queue()
Qerr = Queue.Queue()
Pool = []
def report_error():
    Qerr.put(sys.exc_info()[:2])

def get_all_from_queue(Q):
    try:
        while 1:
            yield Q.get_nowait()
    except Queue.Empty:
        raise StopIteration

def do_work_from_queue():
    while 1:
        command, item = Qin.get()
        if command == "stop":
            break
        try:
            if command == "start":
                res = "new_" + item
            else:
                raise ValueError, "command error %s" % command
        except:
            report_error()
        else:
            Qout.put(res)

def make_and_start_thread_pool(th_num_pool=5, daemon=False):
    for i in xrange(th_num_pool):
        new_thread = threading.Thread(target=do_work_from_queue)
        new_thread.setDaemon(daemon)
        Pool.append(new_thread)
        print Pool
        new_thread.start()

def req_work(data, command="start"):
    Qin.put((command, data))

def get_res():
    return Qout.get()

def show_all_res():
    for res in get_all_from_queue(Qout):
        print "res: ----> %s" % res

def show_all_errors():
    for etype, err in get_all_from_queue(Qerr):
        print "err: ----> %s" % etype, err

def stop_and_free_thread_pool():
    for i in range(len(Pool)):
        req_work(None, "stop")
    for existing_thread in Pool:
        existing_thread.join()
    del Pool[:]

if __name__ == "__main__":
    for i in ("aaa",7,"cccc"): req_work(i)
    make_and_start_thread_pool()
    stop_and_free_thread_pool()
    show_all_res()
    show_all_errors()



