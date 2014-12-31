# -*- coding: utf-8 -*-
'''
Load config module
'''
# import Python libs
import os

# import thrid part libs
import yaml

# import self libs
_ZMQ_SOCKS_PATH = "/dev"
MASTER_OPTS = {
    "interface": "0.0.0.0",     # reciver服务绑定的ip地址
    "port": "4055",             # reciver服务绑定的端口
    "worker_threads": 2,        # worker启动的数量
    "ipv6":False,               # 是否启动ipv6
    "zmq_dir": _ZMQ_SOCKS_PATH, # zmq的fd所在目录
    "rep_hwm": 50000,           # 发布订阅的最高消息数(高水位)
    "worker_daemon": True,     # Worker线程是否是daemon线程
    "sock_dir": _ZMQ_SOCKS_PATH,# zmq socket ipc所在的目录
}

AGENT_DEF_OPTS = {   
    "":"",
    "":""
}

def get_master_conf(conf_path=None):
    opts = MASTER_OPTS
    if conf_path:
        opts["conf_path"] = conf_path
        # TODO 加载用户配置文件
        
    return opts

