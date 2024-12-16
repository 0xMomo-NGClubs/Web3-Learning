Hello，大家好，我是Momo。我最近在学习以太坊相关知识，将学习过程中的一些笔记整理成文章，分享给大家。本期0x1系列是小白基础知识，希望有志同道合的朋友一起学习讨论，也请大神们多多指教。

推特：[@0xMomo](https://x.com/0xmomonifty) | 社区：[Telegram](https://t.co/JQ78TtwxeJ)

本系列所有代码和教程开源在Github:https://github.com/0xMomo-NGClubs/Web3-Learning

# 0x00 简述

这一期主要是如何进行在链上进行转账，主要涉及到以下几个方面：

1 检查钱包余额
2 获取钱包交互次数 nonce
3 获取GAS价格和GAS设置
4 构建并签名交易
5 发送交易

使用RPC节点跟私钥获取钱包余额之前我们已经讲过，这次我们使用以太坊的测试网Sepolia进行交互，没有测试ETH，这里可以使用 OKX钱包 -- 工具集 -- 领水中心 -- 领取测试的SepoliaETH
但是转账之前还是得确认一下钱包余额，是否满足转账条件，并且要考虑到GAS费用。

# 0x01 检查钱包余额

主要是检查转账的数量是否大于钱包余额

```python
# 查询ETH余额
def query_balance_eth(address, amount):
    balance = w3.eth.get_balance(address)
    if balance >= amount:
        return True
    else:
        return False
# 查询ERC20代币余额
 # erc20合约abi
    # 后面会讲到abi是什么
    erc20_abi = [
        ...
    ]
    # 获取ERC20代币合约
    address = web3.Web3.to_checksum_address(address)
    token_address = web3.Web3.to_checksum_address(token_address)
    # 创建合约对象
    token_contract = w3.eth.contract(address=token_address, abi=erc20_abi)
    # 读取代币余额
    balance = token_contract.functions.balanceOf(address).call()
    print(f"钱包地址: {address} 的ERC20代币余额: {balance}")
    if balance >= amount:
        return True
    else:
        return False
```

# 0x02 获取钱包交互次数 nonce

在区块链浏览器查询地址的时候都会有一个 nonce 字段，表示该地址已经发送的交易次数，交易次数是用来防止重放攻击的。次数根据地址的创建时间开始计算，每发送一次交易，nonce 就会加 1。
在发送交易的时候，nonce 是必须的，因为需要确保交易是按照顺序发送的，如果 nonce 不正确，交易可能会被拒绝。
当然我们也可以批量查询nonce，来查看自己的钱包地址是否被使用过，交互过。

```python
# 获取nonce
def get_nonce(address):
    address = web3.Web3.to_checksum_address(address)
    nonce = w3.eth.get_transaction_count(address)
    print(f"钱包地址: {address} 的nonce: {nonce}")
    return nonce
```

# 0x03 获取GAS价格
这里获取的GAS价格是当前的GAS价格，因为以太坊后来升级了1559版本，GAS价格是根据市场行情动态调整的，后期也会具体分享一下GAS的计算和设置，这里就用普通的GAS价格和设置。

```python
# 获取GAS价格及设置GAS价格
def get_gas_price():
    gas_price = w3.eth.gas_price
    print(f"当前GAS价格: {gas_price}")
    return gas_price
```

# 0x04 构建并签名交易，发送ETH
```python
def transfer_eth(address, amount):
    address = web3.Web3.to_checksum_address(address)
    amount = w3.to_wei(amount, "ether")
    # 检查余额是否满足转账金额条件
    if not query_balance_eth(address, amount):
        print(f"钱包地址: {address} 的余额不足, 无法转账")
        return
    # 获取nonce
    nonce = get_nonce(address)
    # 获取GAS价格
    gas_price = get_gas_price()
    # 构建交易
    tx = {
        "to": address,
        "value": amount,
        "gas": 21000,
        "gasPrice": gas_price,
        "nonce": nonce,
    }
    # 签名交易
    signed_tx = w3.eth.account.sign_transaction(tx)
    # 发送交易
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"交易哈希: {tx_hash.hex()}")
    return tx_hash.hex()
```

# 0x05 发送ERC20代币

ERC20代币的转账跟ETH的转账类似，但是需要使用到ERC20代币的合约地址和abi，这里我们使用的是ERC20代币的合约地址和abi，所以需要先获取到ERC20代币的合约地址和abi。
```python
def transfer_erc20(address, token_address, amount):
    erc20_abi = [
        {
            "constant": True,
            "inputs": [{"name": "account", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function",
        },
        {
            "constant": False,
            "inputs": [
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "payable": False,
            "stateMutability": "nonpayable",
            "type": "function",
        },
    ]
    # 获取ERC20代币合约
    address = web3.Web3.to_checksum_address(address)
    token_address = web3.Web3.to_checksum_address(token_address)
    # 创建合约对象
    token_contract = w3.eth.contract(address=token_address, abi=erc20_abi)
    # 检查余额是否满足转账金额条件
    if not query_balance_erc20(address, token_address, amount):
        print(f"钱包地址: {address} 的ERC20代币余额不足, 无法转账")
        return
    # 获取nonce
    nonce = get_nonce(address)
    # 获取GAS价格
    gas_price = get_gas_price()
    # 构建转账ERC20的交易
    tx = token_contract.functions.transfer(address, amount).build_transaction(
        {
            "gas": 21000,
            "gasPrice": gas_price,
            "nonce": nonce,
        }
    )
    # 签名交易
    signed_tx = w3.eth.account.sign_transaction(tx)
    # 发送交易
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"交易哈希: {tx_hash.hex()}")
    return tx_hash.hex()
```

# 0x06 总结

以上是对区块链钱包余额查询的讲解，本期暂不分享批量转账的方法，因为批量转账最好是用到合约，如果批量转账逐笔的话GAS消耗非常高，后期学到合约后，继续研究批量转账的方法。