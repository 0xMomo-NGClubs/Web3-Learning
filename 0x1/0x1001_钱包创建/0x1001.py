import web3
import pandas as pd


# 1.用Python生成私钥钱包地址
def create_wallet():
    # 创建一个钱包
    account = web3.Account.create()

    # 获取钱包地址和私钥
    address = account.address
    private_key = account.key.hex()

    # 打印钱包地址和私钥
    print(f"钱包地址: {address}")
    print(f"私钥: {private_key}")

    # 返回钱包地址和私钥
    return address, private_key


# 2.批量生成钱包地址并导出表格
def create_wallets(num_wallets):
    wallets = []
    # 根据输入的num_wallets数量生成钱包地址
    for i in range(num_wallets):
        wallet = create_wallet()
        wallets.append(wallet)

    # 将钱包地址和私钥导出到Excel
    df = pd.DataFrame(wallets, columns=["Address", "Private Key"])
    df.to_excel("wallets.xlsx", index=False)


# 运行
create_wallets(10)
