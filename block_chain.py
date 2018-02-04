# coding:utf8

import requests
from flask import Flask, request

from block import Block
from taker import taker

app = Flask('block_chain')
app.config['JSON_AS_ASCII'] = False

# 当前服务的链
chain = []
# 待插入的数据
queued_data = []

# 区块链集合，其他区块链地址
chain_set = set()

# 添加创世区块
block = Block(data='None', pre_hash='None')
block.mine()
chain.append(block)

@app.route('/add_queued_data')
@taker
def add_data():
    global queued_data
    data = request.args.get('data')
    assert data, u'请传入数据'.encode('utf8')

    queued_data.append(data)
    return u'添加成功'.encode('utf8')

# 挖矿
# 一般来说一个区块可以记录很多数据，类似于比特币一个区块能存储1M的数据。
# 如果平均一个交易的大小为250B，那么比特币每个区块只能记录 1024 * 1024 / 250 = 4194个交易。
# 又因为比特币大概十分钟产生一个区块，所以平均一秒能够处理7笔交易。
# 多余的交易会根据交易费用进行排队。
# 这里的例子是每次只挖最新的一条数据
@app.route('/mine')
@taker
def add_block():
    global queued_data
    # data = request.args.get('data')
    # assert data, u'请传入数据'.encode('utf8')

    pre_hash = chain[-1].hash()
    block = Block(data=queued_data.pop(), pre_hash=pre_hash)
    block.mine()

    chain.append(block)
    return u'创建成功'.encode('utf8')

# 验证区块链的有效性
def valid_chain(chain):
    last_block = chain[0]
    current_index = 1

    # 遍历区块并检测合法性
    while current_index < len(chain):
        block = chain[current_index]

        # 检测当前区块的pre_hash是否合法
        if block.pre_hash != last_block.hash():
            return False

        last_block = block
        current_index += 1

    return True

# 获取所有节点的区块数据，并校验
@app.route('/sync_chain')
@taker
def sync_chain():
    global chain
    for node in chain_set:
        node_data = requests.get('http://%s/chain'%node).json()['data']
        currect_chain = map(lambda x: Block.restore(x), node_data)
        # 如果新的链比现在的长并且合法的花，就替换成最新的链
        chain = currect_chain if len(chain) < len(currect_chain) and valid_chain(currect_chain) else chain

    return u'当前节点同步完成'.encode('utf8')

# 返回区块
@app.route('/chain')
@taker
def return_chain():
    ret = []
    for block in chain:
        ret.append(block.to_dict())

    return ret

@app.route('/regist_node')
@taker
def regest_node():
    node_url = request.args.get('url', '')

    # TODO:验证url合法性

    # 添加区块链节点
    chain_set.add(node_url)

    return u'节点注册成功'.encode('utf8')

if __name__ == '__main__':
    app.run(debug=True)