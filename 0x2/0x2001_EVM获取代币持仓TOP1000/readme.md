Hello，大家好，我是Momo。我最近在学习以太坊相关知识，将学习过程中的一些笔记整理成文章，分享给大家。本期0x2系列是根据之前学习的基础知识进行实时热点应用，希望有志同道合的朋友一起学习讨论，也请大神们多多指教。

推特：[@0xMomo](https://x.com/0xmomonifty) | 社区：[Telegram](https://t.co/JQ78TtwxeJ)

本系列所有代码和教程开源在Github:https://github.com/0xMomo-NGClubs/Web3-Learning

# 0x00 前言

本期是因为之前有个朋友来找我能否帮他获取某个Meme代币(EVM链)TOP1000地址，并且分析这些地址的持币情况。
当然市面上其实有很多工具能够来获取了，比如：dexscreener、gmgn、dune等，这些工具做的非常好，打土狗必备。
但是如何在自己的程序中获取这些数据，能够在后续自己的需求中使用，这点非常重要，所以这里就跟大家来分享一下Momo的学习过程及思路。

# 0x01 查找合约创建的区块号

在追踪某一个土狗的时候，首先得需要找到合约创建的区块号，即合约的创建时间，这样能够减少很多不必要的区块查询，节约API成本，当然有自己的节点那最好了，哈哈。
Momo这里使用的是常规的以太坊节点RPC，通过二分查找法来获取合约创建的区块号。当然也有很多第三方API可以直接获取，我们这里还是用最基础的。

```python
# 查找合约创建的区块号
def find_contract_creation_block():
    # 获取当前最新区块号作为上界
    high = w3.eth.get_block_number()
    # 从0区块开始作为下界
    low = 0
    contract_creation_block = 0

    while low <= high:
        # 计算中间区块
        mid = (low + high) // 2
        # 检查该区块时合约地址是否存在代码
        code = w3.eth.get_code(token_address, mid)

        # 如果在此区块有代码，说明合约已经被创建
        if code != b"":
            high = mid - 1  # 继续向前找
            contract_creation_block = mid  # 记录当前找到的区块
        else:
            low = mid + 1  # 如果没有代码，说明要往后找

    return contract_creation_block
```

# 0x02 获取区块范围内事件

Momo在 0x1005 的文章中已经跟大家分享过如何获取区块范围内的事件，有需要的小伙伴可以去看一下。
这里我们是把获取某个范围内的该Token合约的转账事件封装成一个函数，方便后续调用，并且减少一定的RPC调用频率。

```python
# 扫描一定范围的区块以获取事件
async def scan_block(from_block, to_block):
    # 获取当前最新区块号作为上界
    # 从0区块开始作为下界
    try:
        # 获取合约区块区间的事件
        batch_events = contract.events.Transfer.get_logs(
            fromBlock=from_block, toBlock=to_block
        )
        print(
            {
                "从": from_block,
                "到": to_block,
                "事件数量": len(batch_events),
            }
        )
        return batch_events
    except Exception as error:
        print("重新扫描...")
        print(error)
        return await scan_block(from_block, to_block)
```

# 0x03 主进程


那接下来我们就开始写我们的程序的主进程啦。
在主进程中,我们主要做了以下几件事:

1. 获取合约创建区块（上面我们已经封装好了）和最新区块号（直接调用w3.eth.get_block_number()）,设置每次最大扫描范围为100个区块
2. 从合约创建区块开始,到最新区块,每次扫描最大范围内的区块
3. 对每个区块范围进行:
   - 调用scan_block()获取Transfer事件（上面我们已经封装好了，即获取某个范围内的该Token合约的转账事件）
   - 统计事件总数
   - 遍历每个事件,获取转账详情(发送方、接收方、金额等)
   - 根据转账情况更新各地址余额（即从发送者减去，到接收者增加）
4. 过滤掉余额为0的地址
5. 将余额根据代币精度转换，因为在以太坊中，记录的都是代币的最小单位，我们需要根据代币精度转换为相应单位
6. 最后将结果保存到Excel文件中,文件名包含时间戳，这里我们使用pandas库来保存，pandas我们之前也分享过

这样我们就能获得某个代币所有持有者的最新余额快照。


```python
async def main():
    print("Starting...")
    start_block = find_contract_creation_block()
    end_block = w3.eth.get_block_number()  # 最新区块号
    max_range = 100  # 根据您的提供者限制进行调整

    print(
        {
            "合约创建区块": start_block,
            "最新区块": end_block,
            "最大扫描范围": max_range,
        }
    )

    balances = {}
    total_events = 0

    # 从合约创建区块开始，到最新区块，每次扫描最大范围，分批扫描，防止RPC限制
    for i in range(start_block, end_block + 1, max_range):
        from_block = i
        to_block = min(i + max_range - 1, end_block)

        # 扫描区块，获取事件
        batch_events = await scan_block(from_block, to_block)

        # 统计事件数量
        total_events += len(batch_events)
        print(batch_events)

        # 遍历事件，获取事件信息
        for event in batch_events:
            from_address = event["args"]["from"]
            to_address = event["args"]["to"]
            value = event["args"]["value"]
            event_type = event["event"]
            log_index = event["logIndex"]
            transaction_index = event["transactionIndex"]
            transaction_hash = "0x" + event["transactionHash"].hex()
            block_number = event["blockNumber"]
            block_hash = "0x" + event["blockHash"].hex()
            address = event["address"]
            print(
                "事件类型",
                event_type,
                "日志索引",
                log_index,
                "交易索引",
                transaction_index,
                "交易哈希",
                transaction_hash,
                "区块号",
                block_number,
                "区块哈希",
                block_hash,
                "合约地址",
                address,
            )

            # 根据事件，更新余额
            # 从发送者减去
            if from_address in balances:
                balances[from_address] -= value
            else:
                balances[from_address] = -value

            # 添加到接收者
            if to_address in balances:
                balances[to_address] += value
            else:
                balances[to_address] = value

    # 移除余额小于等于 0 的地址
    balances = {addr: balance for addr, balance in balances.items() if balance > 0}

    # 将余额根据代币精度转换
    token_contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
    try:
        decimals = token_contract.functions.decimals().call()
    except:
        decimals = 18  # 默认精度
    balances = {
        addr: balance / (10 ** decimals) for addr, balance in balances.items()
    }

    print("总事件: ", total_events)

    # 将结果写入 Excel 文件
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    excel_filename = f"logs/snapshot-{timestamp}.xlsx"

    # 将字典转换为 DataFrame
    df = pd.DataFrame(list(balances.items()), columns=['wallet address', 'amount'])
    
    # 保存为 Excel 文件
    df.to_excel(excel_filename, index=False)

    print("...完成")
```

# 0x04 获取TOP1000地址的其他持有代币以及是否有其他公共地址交易（附加题）

Momo的朋友说，TOP1000实在是太简单也没啥用，能否再来帮我分析一下这些钱包持有哪些代币能够让我来分析一下这些钱包的持币情况，并且这些钱包是否有其他公共地址交易，比如从一些知名的交易所转入后再来参与交易等。
这样我们后期就能够用表格简单的分析这些钱包的画像，或者在token早期的时候能够猜测是否有主力来加仓。

这里呢我们使用第三方Moralis的API来获取这些数据，因为早期自己也没有相关的地址标签库，并且扫描钱包其他持币需要大量RPC调用，心疼自己没有本地节点，Momo努力必须赚钱拿下一个EVM本地节点。


这段代码主要实现了以下功能:

1. 读取EXCEL文件中的钱包地址数据,并按持币量从大到小排序,取前1000个地址进行分析（根据自己需求调整）

2. 对每个钱包地址进行以下分析:
   - 获取该地址的交易次数(nonce)
   - 使用Moralis API获取该地址持有的ERC20代币信息:
     - 统计持有代币的数量(erc20_count)
     - 记录持有代币的符号(symbol)列表
   - 使用Moralis API获取该地址的交易历史:
     - 提取交易中的from_address_label(发送方标签)
     - 用于分析是否与知名交易所等进行过交易

3. 将分析结果保存到新的EXCEL文件中,包含:
   - 钱包地址
   - 交易次数
   - ERC20代币数量
   - 持有代币列表
   - 交易对手方标签列表

这样可以帮助分析这些钱包的:
- 活跃度(通过交易次数)
- 其他持有代币
- 交易来源(是否来自交易所等)
从而更好地理解这些钱包的行为特征。

```python
async def get_address_info():
    # 读取excel
    df = pd.read_excel("logs/snapshot-2024-12-30_16-28-16.xlsx")
    # print(df)
    # 根据amount从大到小排序，取前1000地址
    df = df.sort_values(by="amount", ascending=False)
    df = df.head(1000)

    # start_block = find_contract_creation_block()
    # end_block = w3.eth.get_block_number()  # 最新区块号
    # max_range = 100  # 根据您的提供者限制进行调整

    for address in df["wallet address"]:
        # 获取地址交易次数
        nonce = w3.eth.get_transaction_count(address)
        df.loc[df["wallet address"] == address, "nonce"] = nonce
        # 获取地址持币种类数量
        # 获取地址持有的 ERC20 代币数量
        try:
            # 使用 Moralis API 获取代币余额
            params = {
                "address": address,
                "chain": "eth",
            }
            have_token = []
            balance = evm_api.wallets.get_wallet_token_balances_price(
                api_key=moralis_api_key, params=params
            )
            erc20_count = len(balance["result"])
            for item in balance["result"]:
                # 将 balance 转换为浮点数进行比较
                token_balance = float(item["balance"])
                if token_balance > 0:
                    have_token.append(item["symbol"])
            # 获取地址持币种类数量
            df.loc[df["wallet address"] == address, "erc20_count"] = erc20_count
            # 获取地址持币种类
            df.loc[df["wallet address"] == address, "have_token"] = str(have_token)
            # 获取地址交易历史
            params = {
                "address": address,
                "order": "ASC",
                "chain": "eth",
            }
            # 获取地址交易历史
            history = evm_api.wallets.get_wallet_history(
                api_key=moralis_api_key, params=params
            )
            # 获取地址交易历史
            from_address_label = []
            for item in history["result"]:
                if item["from_address_label"] is not None:
                    from_address_label.append(item["from_address_label"])
            # 将地址标签写入excel
            df.loc[df["wallet address"] == address, "from_address_label"] = str(
                from_address_label
            )
            print(df.loc[df["wallet address"] == address])
        except Exception as error:
            print(error)
    # 保存
    df.to_excel("logs/snapshot-top1000.xlsx", index=False)
```

# 0x05 总结

通过以上代码，我们能够获取到某个代币的TOP1000地址，并且能够获取到这些地址的持币情况，以及这些地址是否有其他公共地址交易，从而更好地理解这些钱包的行为特征，能够给小伙伴带来帮助的也帮忙给Momo一键三连，谢谢！


