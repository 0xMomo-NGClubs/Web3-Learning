import web3
import pandas as pd


# 连接到以太坊主网
w3 = web3.Web3(web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_PROJECT_ID"))


# 1.查询钱包余额
def query_balance(address):

    # 查询钱包余额
    balance = w3.eth.get_balance(address)
    # 返回余额
    print(f"钱包地址: {address} 的余额: {balance}")
    return balance


# 2.从表格读取钱包地址，批量查询钱包ETH余额并保存
# 表格表头：Address, Balance
def query_balance_from_excel(file_path):
    df = pd.read_excel(file_path)
    for index, row in df.iterrows():
        # 将地址转换为checksum格式, 防止地址大小写问题
        # checksum格式通常指的是EIP55校验地址。EIP55是一种以太坊地址校验标准，用于确保地址在大小写混合的情况下能够正确识别和验证。
        address = web3.Web3.to_checksum_address(row["Address"])
        balance = query_balance(address)
        df.at[index, "Balance"] = balance
    df.to_excel("address.xlsx", index=False)


# 3.其他链上信息读取
# 读取区块高度
def read_block_height():
    block_height = w3.eth.block_number
    print(f"当前区块高度: {block_height}")
    return block_height


# 读取区块信息
def read_block_info(block_number):
    block_info = w3.eth.get_block(block_number)
    print(f"区块信息: {block_info}")
    return block_info


# 读取GAS价格（单位：wei）
def read_gas_price():
    gas_price = w3.eth.gas_price
    print(f"当前GAS价格: {gas_price}")
    return gas_price


# 4.读取ERC20代币余额
def read_erc20_balance(address, token_address):
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
    return balance


# 运行

read_erc20_balance(
    "0x3c81d667dccf480ff320e5a5eadd4acc8f3e1144",
    "0x393f1d49425d94f47b26e591a9d111df5cd61065",
)
