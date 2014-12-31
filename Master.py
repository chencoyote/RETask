# -*- coding: utf-8 -*-

# import buildin libs
import multiprocessing
import threading
import zmq
import os
import json
# import self libs
import libs.process
import config.config

class Master(object):
    """
    Master进程为tawRemo的主服务进程, 启动该服务同时启动其3个子进程.
    1. Receiver  子进程
    2. Worker    子进程
    3. Publisher 子进程
    """
    def __init__(self, opts):
        # TODO 初始化一些公共变量 以及配置文件
        self.opts = opts
        pass


    def start(self):
        # TODO 加载所有要启动的子进程, 并启动
        reciver = Reciver(self.opts)
        reciver.start()
        pass

    def __something(self):
        # 定义一些内部的功能
        pass


class Reciver(object):

    def __init__(self, opts):
        self.opts = opts
        self.worker_thread = []

    def start(self):
        # TODO reciver启动时执行的逻辑, 建立zmq连接, zmq的Router模式
        self.process_manager = libs.process.ProcessManager(PM_name='MasterManager')
        #for ind in range(int(self.opts['worker_threads'])):
            # 用进程或者线程的方式启动worker
            #self.process_manager.add_process(Worker, args=[self.opts])
        # 启动消息接收的核心服务
        print "start reciver zmq"
        self.process_manager.add_process(self.reciver_zmq)
        print "start worker thread"
        self.load_worker(self.opts["worker_threads"])
        # 启动消息处理的woker线程
        # self.process_manager.add_process(self.reciver_zmq)
        # start zmq device
        self.process_manager.run()
        pass

    def reciver_zmq(self):
        """
        使用路由模式建立 reciver的接收消息端口以及和worker之间的通讯ipc
        """
        self.context = zmq.Context(self.opts['worker_threads'])
        self.listen_uri = 'tcp://{interface}:{port}'.format(**self.opts)
        self.worker_uri = 'ipc://{0}'.format(
            os.path.join(self.opts['zmq_dir'], 'workers.ipc')
        )
        self.clients = self.context.socket(zmq.ROUTER)
        if self.opts['ipv6'] is True and hasattr(zmq, 'IPV4ONLY'):
            # 判读是否使用ipv6, 否则直接使用
            self.clients.setsockopt(zmq.IPV4ONLY, 0)
        try:
            self.clients.setsockopt(zmq.HWM, self.opts['rep_hwm'])
        # 考虑兼容性问题, zmq的设置方法会有不同
        except AttributeError:
            self.clients.setsockopt(zmq.SNDHWM, self.opts['rep_hwm'])
            self.clients.setsockopt(zmq.RCVHWM, self.opts['rep_hwm'])
        self.workers = self.context.socket(zmq.DEALER)
        self.clients.bind(self.listen_uri)
        self.workers.bind(self.worker_uri)
        while True:
            try:
                zmq.device(zmq.QUEUE, self.clients, self.workers)
            except zmq.ZMQError as exc:
                if exc.errno == errno.EINTR:
                    continue
                raise exc
            except KeyboardInterrupt:
                self.__del__()

    def load_worker(self, worker_num):
        if isinstance(worker_num, int):
            for n in range(worker_num):
                print "start worker %d" % n
                w = Worker(self.opts)
                w.setDaemon(True)
                w.start()
                self.worker_thread.append(w)

    def stop_worker(self):
        for wt in self.worker_thread:
            print "stop worker thread"
            wt.join()

    def destroy(self):
        print self.worker_thread
        if hasattr(self, 'clients') and self.clients.closed is False:
            self.clients.setsockopt(zmq.LINGER, 1)
            self.clients.close()
        if hasattr(self, 'workers') and self.workers.closed is False:
            self.workers.setsockopt(zmq.LINGER, 1)
            self.workers.close()
        if hasattr(self, 'context') and self.context.closed is False:
            self.context.term()
        # Also stop the workers
        self.stop_worker()
        self.process_manager.kill_children()


    def __del__(self):
        self.destroy()


class Worker(threading.Thread):
    """
    与Reciver连接, 进行消息处理, WORKER线程
    """
    def __init__(self, opts, timeout=3):
        threading.Thread.__init__(self)
        self.opts = opts
        self.stop_signal = threading.Event()
        self.timeout = timeout


    def run(self):
        # TODO worker启动执行逻辑, 连接Reciver, 根据选项启动多个线程
        context = zmq.Context(1)
        socket = context.socket(zmq.REP)
        w_uri = 'ipc://{0}'.format(
            os.path.join(self.opts['sock_dir'], 'workers.ipc')
            )
        try:
            socket.connect(w_uri)
            while not self.stop_signal.isSet():
                try:
                    package = socket.recv()
                    payload = self._handle(package)
                    socket.send(payload)
                # don't catch keyboard interrupts, just re-raise them
                except KeyboardInterrupt:
                    raise
                # catch all other exceptions, so we don't go defunct
                except Exception as exc:
                    # Properly handle EINTR from SIGUSR1
                    if isinstance(exc, zmq.ZMQError) and exc.errno == errno.EINTR:
                        continue
                    # lets just redo the socket (since we won't know what state its in).
                    # This protects against a single minion doing a send but not
                    # recv and thereby causing an MWorker process to go defunct
                    del socket
                    socket = context.socket(zmq.REP)
                    socket.connect(w_uri)

        # Changes here create a zeromq condition, check with thatch45 before
        # making any zeromq changes
        except KeyboardInterrupt:
            socket.close()
        pass

    def join(self):
        self.stop()
        # threading.Thread.join(self, self.timeout)

    def stop(self):
        self.stop_signal.set()

    def _handle(self, package):
        # TODO 处理接收到的消息, 并且判断消息该发送到什么地方
        print package
        try:
            package = json.loads(package)
            print type(package)
            print package["type"]
            return "i recive, goto res publish to see"
        except Exception, e:
            print str(e)
            
        # if package["type"] == "msg":
        #     pass
        # elif package["type"] == "res":
        #     pass
        # elif package["type"] == "sch":
        #     pass
        # pass

    def _msg_publish(self, msg):
        # 发布消息到MsgPublisher
        pass

    def _res_publish(self, msg):
        # 发布消息到ResPublisher
        pass

    def _sch_publish(self, msg):
        # 发布消息到SchPublisher
        pass

    # def worker_thread(self):
    #     # TODO 如果需要worker启动多个线程
    #     ##  此功能有待考虑暂且不做
    #     pass

    def __someting(self):
        # TODO 一些内置函数
        pass


class MsgPublisher(multiprocessing.Process):
    """
    与Worker连接, 并且建立msgpubliser.ipc的PUB模式ZMQ
    """
    def __init__(self, opts):
        super(Publisher, self).__init__()
        self.opts = opts

    def run(self):
        # publisher的执行逻辑, 主要是建立连接和 接收\发布 消息
        pass

    def __someting(self):
        # TODO 一些内置函数
        pass


class ResPublisher(multiprocessing.Process):
    """
    与Worker连接, 并且建立respubliser.ipc的PUB模式ZMQ
    """
    def __init__(self, opts):
        super(ResPublisher, self).__init__()
        self.opts = opts

    def run(self):
        # respublisher的执行逻辑, 主要是建立连接和 接收\发布 消息
        pass

    def __someting(self):
        # TODO 一些内置函数
        pass


class SchPublisher(multiprocessing.Process):
    """
    与Worker连接, 并且建立msgpubliser.ipc的PUB模式ZMQ
    """
    def __init__(self, opts):
        super(ResPublisher, self).__init__()
        self.opts = opts

    def run(self):
        # respublisher的执行逻辑, 主要是建立连接和 接收\发布 消息
        pass

    def __someting(self):
        # TODO 一些内置函数
        pass


if __name__ == "__main__":
    opts = config.config.get_master_conf()
    m = Master(opts)
    m.start()
    pass