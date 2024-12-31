from web3 import Web3
import csv
from datetime import datetime
import asyncio
import time
import pandas as pd
from moralis import evm_api


moralis_api_key = "xxxxxx"

# RPC URL
rpc_url = "https://mainnet.infura.io/v3/xxxxxx"

# 代币合约地址（可以更改为任何 ERC20 代币）
token_address = "0xcd9218d87675959ede5c9d2cf4c6790d8ae90c7b"

# 代币合约 ABI
token_abi = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_from", "type": "address"},
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "transferFrom",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_spender", "type": "address"},
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "payable": True,
        "stateMutability": "payable",
        "type": "fallback",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "owner", "type": "address"},
            {"indexed": True, "name": "spender", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"},
        ],
        "name": "Approval",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"},
        ],
        "name": "Transfer",
        "type": "event",
    },
]

# 创建 Web3 实例
w3 = Web3(Web3.HTTPProvider(rpc_url))

# 创建合约实例
contract = w3.eth.contract(
    address=Web3.to_checksum_address(token_address), abi=token_abi
)


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
        code = w3.eth.get_code(Web3.to_checksum_address(token_address), mid)

        # 如果在此区块有代码，说明合约已经被创建
        if code != b"":
            high = mid - 1  # 继续向前找
            contract_creation_block = mid  # 记录当前找到的区块
        else:
            low = mid + 1  # 如果没有代码，说明要往后找

    return contract_creation_block


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
    token_contract = w3.eth.contract(
        address=Web3.to_checksum_address(token_address), abi=token_abi
    )
    try:
        decimals = token_contract.functions.decimals().call()
    except:
        decimals = 18  # 默认精度
    balances = {addr: balance / (10**decimals) for addr, balance in balances.items()}

    print("总事件: ", total_events)

    # 将结果写入 Excel 文件
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    excel_filename = f"logs/snapshot-{timestamp}.xlsx"

    # 将字典转换为 DataFrame
    df = pd.DataFrame(list(balances.items()), columns=["wallet address", "amount"])

    # 保存为 Excel 文件
    df.to_excel(excel_filename, index=False)

    print("...完成")


async def get_address_info():
    # 读取excel
    df = pd.read_excel("logs/snapshot-2024-12-31_10-22-18.xlsx")
    # print(df)
    # 根据amount从大到小排序，取前5000地址
    df = df.sort_values(by="amount", ascending=False)
    df = df.head(2365)

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
    df.to_csv("logs/snapshot-top1000.csv", index=False)


def test():
    print("test")
    params = {
        "address": "0xf055E21E3a809747C03AfA24F4A2eA250538fbff",
        "order": "ASC",
        "chain": "eth",
    }
    result = evm_api.wallets.get_wallet_history(
        api_key=moralis_api_key,
        params=params,
    )
    print(result)


if __name__ == "__main__":
    # asyncio.run(main())
    asyncio.run(get_address_info())
    # test()
