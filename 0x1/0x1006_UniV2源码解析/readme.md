---
创建时间: 2025-01-23 09:54
更新时间: 2025-01-23 14:26
---

![Uniswap V2 源码解析.png](./img/Uniswap%20V2%20源码解析.png)

Hello，大家好，我是Momo。我最近在学习以太坊相关知识，将学习过程中的一些笔记整理成文章，分享给大家。本期0x1系列是小白基础知识，希望有志同道合的朋友一起学习讨论，也请大神们多多指教。

本系列所有代码和教程开源在Github - >【Web3-Learning】

# 0x00 前言
之前我们已经见到过 Uniswap V2原理和底层逻辑 ，感兴趣的小伙伴可以先看看之前的文章。

Uniswap V2分为两个主要部分：
- Core：包含Factory、Pair、Pair ERC20
- Periphery：包含Routers

主网合约部署地址
Factory Contract Address：0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f
V2Router02 Contract Address：0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D

其中，Core主要负责核心逻辑和单个swap的处理；Periphery则是外围服务，在所有swap的基础上构建服务。

# 0x01 Uniswap V2 Core解析

## UniswapV2Factory：交易对的创建与管理

`UniswapV2Factory`合约是Uniswap V2协议的核心组件之一，负责创建和管理所有交易对（Pair）。它提供了多个关键功能，包括`createPair`、`allPairs`和`getPair`等。

注：在区块链浏览器查询 UniswapV2Factory 合约地址即可查看合约函数信息
![Pasted%20image%2020250123110239.png](./img/Pasted%20image%2020250123110239.png)

### allPairs 与 allPairsLength

`allPairs`是一个数组，用于存储所有已创建的交易对合约地址。通过`allPairs`数组，用户可以查询到所有交易对的地址信息。


• `allPairsLength`函数

该函数返回`allPairs`数组的长度，即当前已创建的交易对总数。

```solidity
  function allPairsLength() external view returns (uint) {
      return allPairs.length;
  }
  ```

这个函数为用户提供了一个快速获取交易对数量的方法，方便开发者和用户了解当前协议中可用的交易对总数。


• `allPairs`的使用

通过索引访问`allPairs`数组，可以获取特定索引位置的交易对地址。

```solidity
  function allPairs(uint index) external view returns (address pair) {
      return allPairs[index];
  }
  ```

这个功能允许用户通过索引查询具体的交易对地址，方便在链上进行遍历或查询操作。


### getPair

`getPair`是一个映射（mapping），用于快速查询两个代币之间的交易对地址。它通过`tokenA`和`tokenB`的地址作为键，返回对应的交易对合约地址。


• `getPair`函数

```solidity
  function getPair(address tokenA, address tokenB) external view returns (address pair) {
      return getPair[tokenA][tokenB];
  }
  ```

该函数的实现基于一个二维映射，通过`tokenA`和`tokenB`的地址组合查询交易对地址。如果交易对不存在，则返回`0x0000000000000000000000000000000000000000`。


• `getPair`的创建逻辑

在`createPair`函数中，`getPair`被用来记录新创建的交易对地址。

```solidity
  getPair[token0][token1] = pair;
  getPair[token1][token0] = pair;
  ```

这样设计的好处是，无论`tokenA`和`tokenB`的顺序如何，都可以通过`getPair`快速查询到对应的交易对地址。


### createPair

`createPair`函数是`UniswapV2Factory`的核心功能之一，用于创建新的交易对。它接收两个代币地址`tokenA`和`tokenB`作为输入，返回创建的交易对合约地址。


• 创建逻辑

```solidity
  function createPair(address tokenA, address tokenB) external returns (address pair) {
      require(tokenA != tokenB, 'UniswapV2: IDENTICAL_ADDRESSES');
      (address token0, address token1) = tokenA < tokenB ? (tokenA, tokenB) : (tokenB, tokenA);
      require(token0 != address(0), 'UniswapV2: ZERO_ADDRESS');
      require(getPair[token0][token1] == address(0), 'UniswapV2: PAIR_EXISTS');

      bytes memory bytecode = type(UniswapV2Pair).creationCode;
      bytes32 salt = keccak256(abi.encodePacked(token0, token1));
      assembly {
          pair := create2(0, add(bytecode, 32), mload(bytecode), salt)
      }

      IUniswapV2Pair(pair).initialize(token0, token1);
      getPair[token0][token1] = pair;
      getPair[token1][token0] = pair;
      allPairs.push(pair);
      emit PairCreated(token0, token1, pair, allPairs.length);
  }
  ```


• 首先，函数检查`tokenA`和`tokenB`是否相同，并对它们进行排序，确保`token0`的地址小于`token1`。

• 然后，通过`create2`操作码创建新的交易对合约，并将合约地址记录在`getPair`映射和`allPairs`数组中。

• 最后，触发`PairCreated`事件，通知外部监听者新的交易对已创建。


# 0x02 Uniswap V2 Periphery解析


## UniswapV2Router02：用户交互的桥梁

`UniswapV2Router02`是用户与Core合约之间的主要交互接口，封装了Core合约的功能，为用户提供更便捷的交易和流动性管理功能。其主要功能包括：


### 流动性管理

• `addLiquidity`和`addLiquidityETH`函数允许用户添加流动性。

• `removeLiquidity`和`removeLiquidityETH`函数用于移除流动性。


### 交易功能

• `swapExactTokensForTokens`和`swapTokensForExactTokens`函数支持用户进行代币交换。

• `swapExactETHForTokens`和`swapTokensForExactETH`函数支持ETH与ERC20代币之间的交换。


### Flash Swaps支持

`UniswapV2Router02`支持Flash Swaps（闪电贷），允许用户在同一个交易中借入代币并完成一系列操作，最后归还代币。


## Libraries：工具库的功能扩展

Periphery部分还包括多个工具库，用于提供额外的功能支持：


### UniswapV2Library

• 提供交易对地址的计算函数`pairFor`。

• 提供价格计算函数`getAmountOut`和`getAmountIn`，用于计算交易的输入和输出代币数量。


### UniswapV2OracleLibrary

• 提供TWAP的计算功能，允许用户获取基于时间加权平均价格的价格数据。


# 0x03 总结

Uniswap V2通过Core和Periphery两部分实现了去中心化交易的核心功能。

`UniswapV2Factory`合约通过`createPair`、`allPairs`和`getPair`等功能，高效地管理交易对的创建和查询。

`UniswapV2Router02`则为用户提供了一个便捷的交互接口，封装了交易和流动性管理的核心逻辑。这种分层设计不仅提高了协议的灵活性，也增强了其可扩展性。

-- 不管从代码还是整体设计来看，真的是真的是太厉害了！不愧是Defi中的灵魂铸造着！