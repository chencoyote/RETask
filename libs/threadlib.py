# -*- coding: utf-8 -*-

# import buildin libs
import os
import inspect
import ctypes
import threading
# import self libs


def _async_raise(tid, exctype):
    '''Raises an exception in the threads with id tid'''
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid,
                                                  ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # "if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")

class StoppableThread(threading.Thread):

    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        try:
            #while not self._stop.isSet():
            self.handle()
        except Exception:
            print "some error happen"

    def join(self):
        self.stop()

    def _get_tid(self):
        """determines this (self's) thread id

        CAREFUL : this function is executed in the context of the caller
        thread, to get the identity of the thread represented by this
        instance.
        """
        if not self.isAlive():
            raise threading.ThreadError("the thread is not active")

        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id

        # no, look for it in the _active dict
        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid

        # TODO: in python 2.6, there's a simpler way to do : self.ident

        raise AssertionError("could not determine the thread's id")


class threadPool(object):

    def __init__(self, name=None):
        self.name = name if name else self.__class__.__name__
        self._pool = {}
        self.tid = 0

    def add_thread(self, sub_thread, args=None, kwargs=None, daemonic=True):
        if args is None:
            args = []

        if kwargs is None:
            kwargs = {}

        if type(sub_thread) == type(threading.Thread) and issubclass(sub_thread, StoppableThread):
            print "is stop"
            t = sub_thread(*args, **kwargs)
        elif type(sub_thread) == type(threading.Thread):
            print "is thread"
            t = sub_thread(*args, **kwargs)
        else:
            print "is fun"
            t = threading.Thread(target=sub_thread, args=args, kwargs=kwargs)
        t.setDaemon(daemonic)
        t.start()
        try:
            self.tid = t._get_tid()
        except AssertionError:
            _t_tid = len(self._pool.keys())
            self.tid = "{0}_{1}".format(sub_thread.__class__.__name__, _t_tid)

        self._pool[self.tid] = {"thed": sub_thread,
                                "args": args,
                                "kwargs": kwargs,
                                "Thread": t}

    def get_all_tid(self):
        return self._pool.keys()

    def stop_all_process(self, retry_for_stop=3):
        if len(self._pool) > 0:
            for tid, t_map in self._pool.items():
                try:
                    t_map["Thread"].stop()
                except:
                    t_map["Thread"].join()
        else:
            return 

        t = 0
        while self._pool and t < retry_for_stop:
            for tid, t_map in self._pool.items():
                try:
                    if t_map["Thread"].stopped():
                        del self._pool[tid]
                except KeyError:
                    pass
            t += 1
        


