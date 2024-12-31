Hello，大家好，我是Momo。我最近在学习以太坊相关知识，将学习过程中的一些笔记整理成文章，分享给大家。本期0x1系列是小白基础知识，希望有志同道合的朋友一起学习讨论，也请大神们多多指教。

推特：[@0xMomo](https://x.com/0xmomonifty) | 社区：[Telegram](https://t.co/JQ78TtwxeJ)

本系列所有代码和教程开源在Github:https://github.com/0xMomo-NGClubs/Web3-Learning

# 0x00 简述

在以太坊网络中，智能合约可以在执行过程中触发事件（Events），这些事件会被记录在区块链上作为日志（Logs）,后期也可以用于数据分析，比如分析Meme Top持仓，或者分析某个地址的转账记录等。本文将介绍：

1. 什么是EVM Events（事件）
2. Event的结构和特点
3. 如何使用Python检索Event以及检索ERC20代币的Transfer事件

# 0x01 什么是EVM Events（事件）

Events是以太坊智能合约中的一个重要特性，它允许合约在执行某些操作时向外界发出通知。Events主要用于：

1. 记录重要的状态变化
2. 提供交易的额外信息
3. 降低存储成本（相比直接存储在状态变量中）
4. 方便外部应用程序追踪合约活动

每个Event会生成一条日志记录，包含以下信息：
- 地址：触发事件的合约地址
- Topics：事件的签名哈希和索引参数
- Data：非索引参数的数据

# 0x02 Event的结构和特点

以ERC20代币的Transfer事件为例：
```solidity
event Transfer(address indexed from, address indexed to, uint256 value);
```

Event参数分为两类：
1. indexed（索引）参数：最多可以有3个，存储在Topics中，可以用于快速检索，from、to、value分别代表转账的from地址、to地址、转账数量
我们在区块链浏览器的事件中可以看到这些参数
![alt text](image.png)
2. 非索引参数：存储在Data字段中(数据那一栏)，不能直接用于检索

# 0x03 使用Python检索Event

首先需要准备好与区块链进行链接（之前介绍过，不在详细介绍）：

```python
from web3 import Web3
import json

# 连接到以太坊节点
w3 = Web3(Web3.HTTPProvider('你的RPC节点URL'))

# ERC20代币的ABI（这里只列出Transfer事件相关部分）
erc20_abi = [
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "name": "from",
                "type": "address"
            },
            {
                "indexed": True,
                "name": "to",
                "type": "address"
            },
            {
                "indexed": False,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Transfer",
        "type": "event"
    }
]
```

# 0x04 检索Transfer事件

Transfer是我们在区块链中最常见的事件，比如USDT的Transfer事件，我们可以检索到USDT的转账记录，包括转账的from地址、to地址、转账数量、交易哈希等。
如果需要检索其他的事件，我们需要知道合约的ABI，ABI相关知识在之前的教程中已经介绍过，小伙伴可以参照之前的教程找到合约ABI，替换Transfer事件即可。

```python
def get_transfer_events(token_address, from_block, to_block):
    # 创建合约对象
    contract = w3.eth.contract(address=token_address, abi=erc20_abi)
    
    # 创建事件过滤器来检索Transfer事件
    transfer_filter = contract.events.Transfer.create_filter(
        fromBlock=from_block,
        toBlock=to_block
    )
    
    # 获取事件
    events = transfer_filter.get_all_entries()
    
    # 循环遍历事件，打印事件信息，数量这里是以太坊无符号整数，后期小伙伴可以根据代币的精度转换为实际数量
    for event in events:
        print(f"从: {event.args.from}")
        print(f"到: {event.args.to}")
        print(f"数量: {event.args.value}")
        print(f"交易哈希: {event.transactionHash.hex()}")
        print("------------------------")
    
    return events

# 按地址筛选Transfer事件
def get_address_transfers(token_address, target_address, from_block, to_block):
    contract = w3.eth.contract(address=token_address, abi=erc20_abi)
    
    # 创建过滤器，可以筛选from或to地址
    transfer_filter = contract.events.Transfer.create_filter(
        fromBlock=from_block,
        toBlock=to_block,
        argument_filters={
            'from': target_address  # 或者使用 'to': target_address
        }
    )
    
    events = transfer_filter.get_all_entries()
    return events

# 获取最新的Transfer事件
def get_latest_transfers(token_address, block_count=10):
    current_block = w3.eth.block_number
    from_block = current_block - block_count
    
    return get_transfer_events(token_address, from_block, 'latest')
```

# 0x05 使用示例

```python
# USDT合约地址（以太坊主网）
USDT_ADDRESS = '0xdAC17F958D2ee523a2206206994597C13D831ec7'

# 检索最近的Transfer事件
latest_transfers = get_latest_transfers(USDT_ADDRESS, 5)

# 检索特定地址的转账记录
address = '0x123...'  # 要查询的地址
address_transfers = get_address_transfers(
    USDT_ADDRESS,
    address,
    from_block=21513888,
    to_block='latest'
)
```

# 0x06 总结

Event检索是区块链开发中的重要工具，通过它我们可以：
1. 追踪代币转账记录
2. 监控某些Token的持仓及变化
3. 如果自己是合约开发者，可以用于监控合约的执行情况

熟悉Event检索，后期Momo会介绍如何使用检索日志来分析Token的Top持仓，以及如何使用检索日志来分析某个地址的转账记录，对我们后期来打土狗非常有用，希望小伙伴们多多关注。
