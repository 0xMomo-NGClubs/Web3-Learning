import web3

# 连接到以太坊主网
w3 = web3.Web3(web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_PROJECT_ID"))


# 1.获取ERC20代币基本信息
def get_token_info(token_address):
    # ERC20基础ABI
    erc20_abi = [
        {
            "constant": True,
            "inputs": [],
            "name": "name",
            "outputs": [{"name": "", "type": "string"}],
            "type": "function",
        },
        {
            "constant": True,
            "inputs": [],
            "name": "symbol",
            "outputs": [{"name": "", "type": "string"}],
            "type": "function",
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "type": "function",
        },
    ]

    token_address = web3.Web3.to_checksum_address(token_address)
    token_contract = w3.eth.contract(address=token_address, abi=erc20_abi)

    name = token_contract.functions.name().call()
    symbol = token_contract.functions.symbol().call()
    decimals = token_contract.functions.decimals().call()

    print(f"代币名称: {name}")
    print(f"代币符号: {symbol}")
    print(f"代币精度: {decimals}")

    return {"name": name, "symbol": symbol, "decimals": decimals}


# 2.监听Transfer事件
def listen_transfer_events(contract_address):
    # Transfer事件ABI
    transfer_event_abi = [
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

    contract_address = web3.Web3.to_checksum_address(contract_address)
    contract = w3.eth.contract(address=contract_address, abi=transfer_event_abi)

    # 获取Transfer事件
    transfer_filter = contract.events.Transfer.create_filter(fromBlock="latest")

    print(f"开始监听合约 {contract_address} 的Transfer事件...")
    while True:
        for event in transfer_filter.get_new_entries():
            print(f"转账事件: {event}")


# 3.调用合约方法示例（以balanceOf为例）
def call_contract_method(contract_address, wallet_address):
    # 合约方法ABI
    contract_abi = [
        {
            "constant": True,
            "inputs": [{"name": "account", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function",
        }
    ]

    contract_address = web3.Web3.to_checksum_address(contract_address)
    wallet_address = web3.Web3.to_checksum_address(wallet_address)

    contract = w3.eth.contract(address=contract_address, abi=contract_abi)
    balance = contract.functions.balanceOf(wallet_address).call()

    print(f"钱包地址 {wallet_address} 在合约 {contract_address} 中的余额: {balance}")
    return balance


# 运行示例
if __name__ == "__main__":
    # USDT合约地址
    usdt_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    # 示例钱包地址
    wallet_address = "0x3c81d667dccf480ff320e5a5eadd4acc8f3e1144"

    # 获取USDT代币信息
    print("获取USDT代币信息:")
    get_token_info(usdt_address)

    # 查询钱包USDT余额
    print("\n查询钱包USDT余额:")
    call_contract_method(usdt_address, wallet_address)

    # 监听USDT转账事件
    print("\n监听USDT转账事件:")
    listen_transfer_events(usdt_address)
