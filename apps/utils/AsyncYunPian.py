import json
from urllib.parse import urlencode

from tornado import httpclient


class AsyncYunPian:
    def __init__(self, api_key):
        self.api_key = api_key

    async def send_single_sms(self, code, mobile):
        http_client = httpclient.AsyncHTTPClient()
        # 发送单条短信
        url = "https://sms.yunpian.com/v2/sms/single_send.json"
        text = "【慕学生鲜】您的验证码是{}。如非本人操作，请忽略本短信".format(code)
        # postRequest = httpclient.HTTPRequest(url=url, method='POST', body=urlencode({
        #     "apikey": self.api_key,
        #     "mobile": mobile,
        #     "text": text
        # }))
        postRequest = {
			    "code":0,
			    "data":"发送成功"
			}

        res = await http_client.fetch(str(postRequest))
        print(res.body.decode('utf8'))
        return json.loads(res.body.decode('utf8'))


if __name__ == "__main__":
    from tornado import ioloop
    loop = ioloop.IOLoop.current()
    yunpian = AsyncYunPian("d6c4ddbf50ab36611d2f52041a0b949e")
    # run_sync方法可以在运行完某个协程之后停止事件循环
    from functools import partial
    new_func = partial(yunpian.send_single_sms, '1234', '15002959016')
    loop.run_sync(new_func)