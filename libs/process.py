# -*- coding: utf-8 -*-

# import buildin libs
import os
import time
import signal
import multiprocessing
# import self libs


def proc_is_running(pid):
    """
    show the process is running or not
    """
    try:
        os.kill(pid, signal.SIGHUP)
        return True
    except OSError:
        return False

def set_pidfile(pidfile, user):
    """
    write a pidfile
    """
    pdir = os.path.dirname(pidfile)
    if not os.path.isdir(pidr) and pdir:
        os.makedirs(pdir)
    try:
        with open(pidfile, "w+") as f:
            f.write(str(os.getpid()))
    except IOError:
        pass
    # 目前没有必要写该文件的用户权限,暂时留空
    # 需要时再添加
    pass

def clean_proc(proc, wait_for_kill=10):
    """
    使multiprocessing的进程全部正常退出.
    """
    if not proc:
        return
    try:
        waited = 0
        while proc.is_alive():
            proc.terminate()
            waited += 1
            time.sleep(0.1)
            if proc.is_alive() and (waited >= wait_for_kill):
                print "Can not stop with terminate, and kill -9 to use"
                os.kill(proc.pid, signal.SIGKILL)
    except Exception, e:
        raise e

class ProcessManager(object):
    """
    多进程管理的class
    """

    def __init__(self, PM_name=None, wait_for_kill=5):
        self._process_map = {}
        
        self.name = PM_name
        if self.name == None:
            self.name = self.__class__.__name__

        self.wait_for_kill = wait_for_kill

        self._PM_pid = os.getpid()
        self._sigterm_handler = signal.getsignal(signal.SIGTERM)

    def add_process(self, sub_process, args=None, kwargs=None):
        """
        添加一个进程到_process_map中进行管理, key为该进程运行时候的的pid
        """
        if args is None:
            args = []

        if kwargs is None:
            kwargs = {}

        if type(sub_process) == type(multiprocessing.Process) and issubclass(sub_process, multiprocessing.Process):
            p = sub_process(*args, **kwargs)
        else:
            p = multiprocessing.Process(target=sub_process, args=args, kwargs=kwargs)
        p.start()

        self._process_map[p.pid] = {'proc': sub_process,
                                    'args': args,
                                    'kwargs': kwargs,
                                    'Process': p}

    def restart_process(self, pid):
        """
        重启某一个进程, 挂起之后,重新添加, 然后删除
        """
        self._process_map[pid]['Process'].join(1)

        self.add_process(self._process_map[pid]['proc'],
                         self._process_map[pid]['args'],
                         self._process_map[pid]['kwargs'])

        del self._process_map[pid]

    def run(self):
        """
        Load and start all available api modules
        """
        # make sure to kill the subprocesses if the parent is killed
        signal.signal(signal.SIGTERM, self.kill_children)

        while True:
            try:
                # in case someone died while we were waiting...
                self.check_children()

                pid, exit_status = os.wait()
                if pid not in self._process_map:
                    print ('Process of pid {0} died, not a known'
                               ' process, will not restart').format(pid)
                    continue
                self.restart_process(pid)
            # OSError is raised if a signal handler is called (SIGTERM) during os.wait
            except OSError:
                break

    def check_children(self):
        '''
        Check the children once
        '''
        for pid, mapping in self._process_map.iteritems():
            if not mapping['Process'].is_alive():
                self.restart_process(pid)

    def kill_children(self, *args):
        '''
        Kill all of the children
        '''
        # check that this is the correct process, children inherit this
        # handler, if we are in a child lets just run the original handler
        if os.getpid() != self._PM_pid:
            if callable(self._sigterm_handler):
                return self._sigterm_handler(*args)
            elif self._sigterm_handler is not None:
                return signal.default_int_handler(signal.SIGTERM)(*args)
            else:
                return

        for pid, p_map in self._process_map.items():
            p_map['Process'].terminate()

        end_time = time.time() + self.wait_for_kill  # when to die

        while self._process_map and time.time() < end_time:
            for pid, p_map in self._process_map.items():
                p_map['Process'].join(0)

                # This is a race condition if a signal was passed to all children
                try:
                    del self._process_map[pid]
                except KeyError:
                    pass
        # if anyone is done after
        for pid in self._process_map:
            try:
                os.kill(signal.SIGKILL, pid)
            # in case the process has since decided to die, os.kill returns OSError
            except OSError:
                pass
   