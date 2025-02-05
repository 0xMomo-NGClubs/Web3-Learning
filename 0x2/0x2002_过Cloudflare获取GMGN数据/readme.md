---
创建时间: 2025-02-05 09:48
更新时间: 2025-02-05 15:03
tags:
  - noCaptcha
---

![[提升/区块链/推特/推文/0x2/0x2002/&附件/你的段落文字.png]](./img/你的段落文字.png)
Hello，大家好，我是Momo。我最近在学习以太坊相关知识，将学习过程中的一些笔记整理成文章，分享给大家。本期0x2系列是根据之前学习的基础知识进行实时热点应用，希望有志同道合的朋友一起学习讨论，也请大神们多多指教。

本系列所有代码和教程开源在Github - >【Web3-Learning】

# 0x00 前言

Momo最近在进行枯坐，一边盯链上，一边学习打狗的知识，其中GMGN是最常用的，但是人眼还是快不过机器，所以Momo开始研究如何获取 GMGN 、Dexscreener 的数据来进行程序筛选。

然而，Cloudflare的反爬机制如同一道坚不可摧的城墙，Momo研究了好久，最后在 @ 的热情帮助下，使用了 #noCaptcha 进行验证码挑战。

Momo这里还是选择自己最擅长的Python来给大家演示分享。

# 0x01 GMGN API 获取

Pump发射的新币数量非常多，金狗就隐藏在其中，我们就从获取GMGN“即将打满”来举例。

1. 来到 GMGN 的 Solana网站的即将打满，开启 审查-开发者工具-网络 来查看请求情况。

![[Pasted image 20250205100737.png]](./img/Pasted%20image%2020250205100737.png)

2. 我们这里看到请求的URL为 `https://gmgn.ai/defi/quotation/v1/rank/sol/pump/1h`

3. 复制整段URL来访问即跳出CF盾

![[Pasted image 20250205101042.png]](./img/Pasted%20image%2020250205101042.png)
4. 手动过CF盾就可以看到接口的JSON数据啦
![[Pasted image 20250205101136.png]]
# 0x02 准备代理IP

频繁请求GMGN我们得准备多个IP，防止IP被拉黑，而且调用 noCaptcha 服务获取浏览器指纹也会用到，这里我们就用之前介绍过Momo常用的几个

IP代理：
[webshare](https://www.webshare.io/?referral_code=y8bssfgni4o1)
这家我经常用，25个数据中心IP大概14U/月，性价比更高
[Войти](https://panel.proxyline.net)
1.8U/IP/月，性价比也非常高

# 0x03 准备好 noCaptcha 

noCaptcha 是一家优秀的CAPTCHA 识别服务，可以轻松的绕过图像等验证码，注册联系官方TG即可获赠测试额度。

可以解决 Akamai、reCaptcha、hCaptcha、cloudflare、incapsula、aws waf、perimeterx、kasada、datadome、shape 的验证码

注册好后获取个人秘钥

# 0x03 请求 CAPTCHA 识别

有了上面3样我们开始识别CF盾获取指纹啦，GMGN请求过盾用的是cookies模式，所以用到的编程语言需要有 tls 指纹的 http 请求框架，这里Momo用 Python 的 tls_client 和 requests 。

使用 noCaptcha 的流程为：将目标网址、代理 IP 发送 POST 给 noCaptcha 创建过盾任务，等待几秒后返回 Cookies 和 浏览器 user_agent ，我们使用返回的参数即可访问到过盾后的数据。

~~~python
class NoCaptcha:
    def __init__(self, user_token: str):
        self.user_token = user_token
        self.session = requests.Session()

    def solve_cloudflare(self, website_url: str, proxy: str) -> dict:
        """
        解决 Cloudflare 验证码

        Args:
            website_url: 目标网站 URL
            proxy: 代理地址

        Returns:
            dict: API 响应结果
        """
        response = self._create_task(website_url, proxy)
        logger.info(f"NoCaptcha 任务结果: {response}")
        print(f"NoCaptcha 任务结果: {response}")
        return response

    def _create_task(self, website_url: str, proxy: str) -> dict:
        """
        创建验证码解决任务

        Args:
            website_url: 目标网站 URL
            proxy: 代理地址

        Returns:
            dict: API 响应结果
        """
        headers = {"User-Token": self.user_token, "Content-Type": "application/json"}

        data = {"href": website_url, "proxy": proxy}

        response = self.session.post(
            "http://api.nocaptcha.io/api/wanda/cloudflare/universal",
            headers=headers,
            json=data,
        )
        response_json = response.json()
        print(f"NoCaptcha 任务结果: {response_json}")

        if response_json.get("status") == 1:
            return response_json
        else:
            raise Exception(f"验证失败: {response_json.get('msg', '未知错误')}")
~~~

这里主要为了拿到 User-agent 和 Cookies ，其中 Cookies 包含 cf_clearance 和 __cf_bm。

![[Pasted image 20250205110636.png]](./img/Pasted%20image%2020250205110636.png)


# 0x04 请求 GMGN 数据

拿到指纹后，我们就可以请求 GMGN 的数据啦。
我们使用 tls_client 来请求 GMGN 的 Pump 即将打满的数据，其他接口也是一样。

1. 包装gmgn的请求
~~~python
class gmgn:
    BASE_URL = "https://gmgn.ai/defi/quotation"

    def __init__(self, ua, cookie, proxy):
        self.ua = ua
        self.cookie = cookie
        self.proxy = proxy

    def defaultRequest(self):

        client_identifier = "Chrome_" + self.ua.split("Chrome/")[1].split(".")[0]
        self.sendRequest = tls_client.Session(client_identifier=client_identifier)

        self.headers = {
            "Host": "gmgn.ai",
            "accept": "application/json, text/plain, */*",
            "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "dnt": "1",
            "priority": "u=1, i",
            "referer": "https://gmgn.ai/?chain=sol",
            "user-agent": self.ua,
            "cookie": self.cookie,
        }
~~~

2. 请求GMGN的Pump即将打满的数据(Http Get请求)
~~~python
    # 获取token信息
    def getTokensByCompletion(self) -> dict:
        """
        获取GMGN的Pump即将打满的数据
        """

        url = f"{self.BASE_URL}/v1/rank/sol/pump/1h"

        request = self.sendRequest.get(url, headers=self.headers, proxy=self.proxy)

        jsonResponse = request.json()["data"]

        return jsonResponse
~~~

3. 轻松过盾，拿到数据
![[Pasted image 20250205105721.png]](./img/Pasted%20image%2020250205105721.png)

# 0x06 总结 

这种方法不仅适用于获取 Pump 数据,也可以用于请求其他Cloudflare有反爬虫的接口。获取价格波动、交易量变化、市场深度等关键指标，在通过自己的筛选因子，助力自己成为链上小将！
