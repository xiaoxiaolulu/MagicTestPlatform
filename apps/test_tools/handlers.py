import base64

import requests

# client_id 为官网获取的AK， client_secret 为官网获取的SK

host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=fDowQhVGrfyof0oFlNAowVTY&client_secret=YegBNDm1gHoXwyEBwxOsNr8WoFMzqmVS'
token_response = requests.get(host)
print(token_response.json().get('access_token'))

request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general"
f = open(r'C:\Users\Null\Pictures\Saved Pictures\TIM截图20191118144631.png', 'rb')
img = base64.b64encode(f.read())
print(img)

params = {"image": img}
access_token = token_response.json().get('access_token')
request_url = request_url + "?access_token=" + access_token
headers = {'content-type': 'application/x-www-form-urlencoded'}
response = requests.post(request_url, data=params, headers=headers)
if response:
    print (response.json())