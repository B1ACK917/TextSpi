import requests


def get_proxy():
    while True:
        respond = requests.get("http://127.0.0.1:5010/get/").json()
        if respond.get("proxy") is not None:
            return respond
        else:
            continue


def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


def cnt_legal_proxy():
    a = []
    for i in range(100):
        proxy = get_proxy().get("proxy")
        if proxy not in a:
            a.append(proxy)
    print(len(a))


cnt_legal_proxy()
