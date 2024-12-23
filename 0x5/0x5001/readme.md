
Hello，大家好，我是Momo。最近在整理一些撸毛相关的知识写成笔记，把一些自己认为有价值的东西分享给大家，希望有志同道合的朋友一起学习讨论，也请大神们多多指教。

推特：[@0xMomo](https://x.com/0xmomonifty) | 社区：[Telegram](https://t.co/JQ78TtwxeJ)

0x5 系列是对目前热点项目的学习、使用、总结分享。结合自己的白话文让大家更加简单快捷的了解项目并参与其中，所以一下内容分享均为自己的理解认知，如有问题与错误请谅解并与我联系及时更正！

本系列所有代码和教程也会开源在Github:https://github.com/0xMomo-NGClubs/Web3-Learning

## 0x00 前言

最近 粒子网络（particle.network）的 UniversalX 热度非常高，整体使用体验也非常的丝滑，比市面上其他的钱包来相比可以做到不用过多的去感受每条链之间的隔阂，并且现在除了转账之外可以直接兑换各链的Token，也可以资产跨链打Meme，无须顾虑Gas Token。

之前很多小伙伴也在交互粒子网络的测试网，每天都在进行签到，现在 UniversalX 上线了也可以进行交互一下，Momo猜测接下来大概率会进行空投。

现在UniversalX(后文简称UX)也有很多玩法，比如最近与Chain.fm一起的 「全链冲浪季」[UniversalX <> [Chain.fm](http://chain.fm/) 全链冲浪季](https://particlenetwork.notion.site/UniversalX-Chain-fm-1604e92032ab804b8371f1d7e5b2bf25) 可以直接在频道推送的点击 UX 的图标进行兑换购买。现在也支持在 UX 的账户中点击 Red Packet 创建红包发送到TG，X等社交软件中来给用户抽取红包。

## 0x01 链抽象

Particle Network 其实很早就开始建设自己的技术堆栈，从 钱包抽象 => 账户抽象 => 链抽象，
那么这里Momo简单概括一下每一层的理解：

钱包抽象：用户能够创建与他们的 Web2 社交账户链接的智能合约钱包，减少用户需要对Web3钱包的专业知识学习。
账户抽象：通过 ERC-4337 智能账户利用账户抽象，解锁无气交易和会话密钥等特性，以增强其 dApps 的用户体验。在这一块大家可以联想到目前热门钱包内的 **无私钥** 智能合约账户（AA账户）。
链抽象：在现在多链时代的今天，链抽象可以做到一种无需手动处理与多个链交互的过程的用户体验。
![Pasted image 20241223163507.png](Pasted%20image%2020241223163507.png)
而且为了实现跨所有链的交互统一，和用户提供单一余额和账户状态，Particle Network采用单独一条L1来负责外部链交易执行和确认（调度）。
![Pasted image 20241223164047.png](Pasted%20image%2020241223164047.png)

## 0x02 相关资料

[Introduction - Particle Network docs](https://developers.particle.network/landing/introduction)
[意图与链抽象 101 | 登链社区 | 区块链技术社区](https://learnblockchain.cn/article/9199)
[Site Unreachable](https://zhuanlan.zhihu.com/p/653920859)


## 0x03 使用体验和背后逻辑

1. 可以点击 [UniversalX](https://universalx.app/user/x/0xmomonifty?inviteCode=4PJCAF) 访问等登录界面（可以用我的邀请码4PJCAF），这里不仅能够使用常见的Web3钱包插件登录，也可以使用Web2相关社交账号登陆，无须无需存储私钥、安装额外工具。丝滑~
这里主要是因为Particle Network实现了模块化智能 Waas（钱包即服务）依赖于 MPC-TSS 来保护用户的私钥，同时实现非托管社交登录。使得交互的用户无须对Web3专业知识有所了解，也有助于相关门户提高转化率和加快用户注册速度。丝滑~
![Pasted image 20241223165835.png](Pasted%20image%2020241223165835.png)
	
2. 登录后 UX 就会创建Universal Account 通用账户，我们可以点击 Receive 对自己的账户进行转入 UX 支持的区块链网络的代币Token 也可以点击 Send 发送相关Token到自己的Web3钱包货交易所，在这里你所有链的资产都会汇聚到这里，无须考虑代币在哪个链上。当然也可以直接用法币购买。丝滑~
这里是因为UX会在众多支持的链上（EVM、SVM等）都会部署创建一个智能账户，但你无需考虑的这些。
![Pasted image 20241223170124.png](Pasted%20image%2020241223170124.png)
![Pasted image 20241223170401.png](Pasted%20image%2020241223170401.png)

4. 点击 Trade 即可进行代币兑换，我们可以使用所有支持的网络中的 5 种主要代币的组合来购买代币，也可以将Token兑换成目前支持的5 种主要代币，过程中不用考虑所在的区块链网络和Gas费用。丝滑~
在这里 UX 会对用户的交易意图通过Particle Network L1进行统一结算，并在相关链上使用智能合约账户（AA）进行兑换后进行跨链，过程对用户来说相当无感。并且得力于抽象账户，允许用户使用任何代币支付燃气费用。
![Pasted image 20241223172549.png](Pasted%20image%2020241223172549.png)

5. 结合以上 UX 的优点，目前我们还可以点击 More -- Red Packet 来创建红包发送到社交平台进行抽奖，并且可以在Chain.fm中点击图标直接进行代币交换，体验也是相当丝滑~
![Pasted image 20241223172933.png](Pasted%20image%2020241223172933.png)

## 0x04 总结

以上是Momo对UniversalX & 粒子网络学习和使用体验分享，UniversalX使用主流钱包或者传统社交账号来登录，并且会帮你在各个区块链网络创建好智能合约账户，通过自己的L1网络进行统一结算，让用户可以统一管理自己的资产和无感跨链、主链GAS来进行交易。