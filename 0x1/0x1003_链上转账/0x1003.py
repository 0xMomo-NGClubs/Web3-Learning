import web3


# 连接到以太坊主网
w3 = web3.Web3(web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_PROJECT_ID"))


# 1.查询钱包是否满足转账金额条件
# 查询ETH余额
def query_balance_eth(address, amount):
    address = web3.Web3.to_checksum_address(address)
    balance = w3.eth.get_balance(address)
    if balance >= amount:
        return True
    else:
        return False


# 查询ERC20代币余额
def query_balance_erc20(address, token_address, amount):
    # erc20合约abi
    # 后面会讲到abi是什么
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
    # 读取代币余额
    balance = token_contract.functions.balanceOf(address).call()
    print(f"钱包地址: {address} 的ERC20代币余额: {balance}")
    if balance >= amount:
        return True
    else:
        return False


# 2.获取钱包交互次数 nonce
def get_nonce(address):
    address = web3.Web3.to_checksum_address(address)
    nonce = w3.eth.get_transaction_count(address)
    print(f"钱包地址: {address} 的nonce: {nonce}")
    return nonce


# 3.获取GAS价格及设置GAS价格
def get_gas_price():
    gas_price = w3.eth.gas_price
    print(f"当前GAS价格: {gas_price}")
    return gas_price


# 4.转账ETH
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


# 5.转账ERC20代币
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
