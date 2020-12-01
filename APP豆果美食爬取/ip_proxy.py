import requests

url = 'http://ip.hahado.cn/ip'
proxy = {
    'http:':'http://用户名:密码@代理地址:端口'
}
resp = requests.get(url=url,proxies=proxy)
print(resp.text)