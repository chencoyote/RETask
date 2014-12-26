# -*- coding: utf-8 -*-

# import buildin libs
import multiprocessing
import threading

# import tawRemo libs



class Agent(object):

    def  __init__(self, opts):
        pass

    def start(self):
        pass

    def __someting(self):
        pass


class SchAgent(multiprocessing.Process):

    def __init__(self, opts, schedule):
        self.opts = opts
        self.schedule = schedule
        pass

    def load_schedule(self):
        # load schedule
        pass

    def run(self):
        pass

class TaskAgent(threading.Thread):

    def __init__(self, opts):
        pass

    def load_task(self, task):
        pass

    def run(self):
        pass