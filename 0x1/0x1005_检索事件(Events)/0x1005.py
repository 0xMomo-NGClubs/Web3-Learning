import web3

# 连接到以太坊主网
w3 = web3.Web3(web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_PROJECT_ID"))

# ERC20代币的Transfer事件ABI
erc20_transfer_abi = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"},
        ],
        "name": "Transfer",
        "type": "event",
    }
]


# 1.获取Transfer事件
def get_transfer_events(token_address, from_block, to_block):
    # 创建合约对象
    token_address = web3.Web3.to_checksum_address(token_address)
    contract = w3.eth.contract(address=token_address, abi=erc20_transfer_abi)

    # 创建事件过滤器
    transfer_filter = contract.events.Transfer.create_filter(
        fromBlock=from_block, toBlock=to_block
    )

    # 获取事件
    events = transfer_filter.get_all_entries()

    # 打印事件信息
    for event in events:
        print(f"从: {event.args['from']}")
        print(f"到: {event.args['to']}")
        print(f"数量: {event.args['value']}")
        print(f"交易哈希: {event.transactionHash.hex()}")
        print("------------------------")

    return events


# 2.按地址筛选Transfer事件
def get_address_transfers(token_address, target_address, from_block, to_block):
    # 创建合约对象
    token_address = web3.Web3.to_checksum_address(token_address)
    target_address = web3.Web3.to_checksum_address(target_address)
    contract = w3.eth.contract(address=token_address, abi=erc20_transfer_abi)

    # 创建过滤器，筛选from地址
    transfer_filter = contract.events.Transfer.create_filter(
        fromBlock=from_block,
        toBlock=to_block,
        argument_filters={"from": target_address},
    )

    events = transfer_filter.get_all_entries()

    # 打印事件信息，数量这里是以太坊无符号整数
    for event in events:
        print(f"从: {event.args['from']}")
        print(f"到: {event.args['to']}")
        print(f"数量: {event.args['value']}")
        print(f"交易哈希: {event.transactionHash.hex()}")
        print("------------------------")

    return events


# 3.获取最新的Transfer事件
def get_latest_transfers(token_address, block_count=10):
    # 获取当前区块高度
    current_block = w3.eth.block_number
    from_block = current_block - block_count

    return get_transfer_events(token_address, from_block, "latest")


# 运行示例
if __name__ == "__main__":
    # USDT合约地址（以太坊主网）
    USDT_ADDRESS = "0xdAC17F958D2ee523a2206206994597C13D831ec7"

    # 示例1：获取最近的Transfer事件
    print("获取最近的Transfer事件：")
    latest_transfers = get_latest_transfers(USDT_ADDRESS, 5)

    # 示例2：获取特定地址的转账记录
    print("\n获取特定地址的转账记录：")
    address = "0x000000"  # 示例地址
    address_transfers = get_address_transfers(
        USDT_ADDRESS, address, from_block=21513888, to_block="latest"
    )
