# coding:utf8

import time
import hashlib
from uuid import uuid1 as get_id

class Block(object):
    def __init__(self, data, pre_hash):
        # 唯一标识
        self.id = str(get_id())
        # 生成时间戳
        self.time = str(time.time())
        # 需要保存的数据，必须要可以hash
        self.data = data
        # 计算工作量证明
        self.proof = 0
        # 上一个节点的hash
        self.pre_hash = pre_hash

    # 生成hash
    def hash(self):
        message = hashlib.sha256()
        message.update(str(self.id))
        message.update(str(self.time))
        message.update(str(self.data))
        message.update(str(self.pre_hash))
        message.update(str(self.proof))

        return message.hexdigest()

    # 用于验证hash是否合法
    @staticmethod
    def is_valid(hash):
        assert isinstance(hash, basestring), u'请传入字符串'.encode('utf8')
        # 这里的规则是hash值必须以0000开头
        # 在比特币的算法中，这个规则是会变化的，貌似是每产生2016个区块调整一次
        # 如果发现平均每个区块的产生时间少于十分钟，就会增大难度，大于十分钟则减小难度
        return hash.startswith('0000')

    # 挖矿
    def mine(self):
        while not Block.is_valid(self.hash()):
            self.proof += 1

    def to_dict(self):
        ret = {
            'id': self.id,
            'time': self.time,
            'data': self.data,
            'pre_hash': self.pre_hash,
            'proof': self.proof,
            'hash': self.hash()
        }
        return ret

    # 根据数据还原区块
    @staticmethod
    def restore(data):
        block = Block(data=data['data'], pre_hash=data['pre_hash'])
        block.id = data['id']
        block.time = data['time']
        block.proof = data['proof']

        return block

if __name__ == '__main__':
    block = Block(data=u'测试', pre_hash='123123123')
    block.mine()
    print block.hash()
    block.proof += 1
    block.mine()
    print block.hash()
