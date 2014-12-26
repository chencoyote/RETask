# -*- coding: utf-8 -*-

# import buildin libs
import multiprocessing
import zmq
# import tawRemo libs


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
        pass

    def __something(self):
        # 定义一些内部的功能
        pass


class Reciver(object):

    def __init__(self, opts):
        self.opts = opts

    def start(self):
        # TODO reciver启动时执行的逻辑, 建立zmq连接, zmq的Router模式
        pass

    def zmq_device(self):
        self.context = zmq.Context(self.opts['worker_threads'])
        self.uri = 'tcp://{interface}:{ret_port}'.format(**self.opts)
        self.clients = self.context.socket(zmq.ROUTER)
        if self.opts['ipv6'] is True and hasattr(zmq, 'IPV4ONLY'):
            # IPv6 sockets work for both IPv6 and IPv4 addresses
            self.clients.setsockopt(zmq.IPV4ONLY, 0)
        try:
            self.clients.setsockopt(zmq.HWM, self.opts['rep_hwm'])
        # in zmq >= 3.0, there are separate send and receive HWM settings
        except AttributeError:
            self.clients.setsockopt(zmq.SNDHWM, self.opts['rep_hwm'])
            self.clients.setsockopt(zmq.RCVHWM, self.opts['rep_hwm'])

        self.workers = self.context.socket(zmq.DEALER)
        self.w_uri = 'ipc://{0}'.format(
            os.path.join(self.opts['sock_dir'], 'workers.ipc')
        )

        log.info('Setting up the master communication server')
        self.clients.bind(self.uri)

        self.workers.bind(self.w_uri)

        while True:
            try:
                zmq.device(zmq.QUEUE, self.clients, self.workers)
            except zmq.ZMQError as exc:
                if exc.errno == errno.EINTR:
                    continue
                raise exc
    def __someting(self):
        # TODO 一些内置函数
        pass


class Worker(multiprocessing.Process):
    """
    与Reciver连接, 进行消息处理
    """
    def __init__(self, opts):
        multiprocessing.Process.__init__(self)
        self.opts = opts

    def run(self):
        # TODO worker启动执行逻辑, 连接Reciver, 根据选项启动多个线程
        pass

    def handle(self):
        # TODO 处理接收到的消息, 并且判断消息该发送到什么地方
        pass

    def worker_thread(self):
        # TODO 如果需要worker启动多个线程
        ##  此功能有待考虑暂且不做
        pass

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
        