#多线程抓取
import requests
import time
import json
from multiprocessing import Queue
from mongodb import mongo_info
from concurrent.futures import ThreadPoolExecutor
#创建队列
queue_list = Queue()
#封装请求函数，相同的请求头
def handle_requsest(url,data):
    now_time = str(int(time.time()))
    headers = {
        'Cookie':'duid=66695339',
        'client':'4',
        'version':'6972.2',
        'device':'MI 9',
        'sdk':'22,5.1.1',
        'imei':'355757579416922',
        'channel':'baidu',
        'resolution':'1600*900',
        'display-resolution':'1600*900',
        'dpi':'2.0',
        'pseudo-id':'5c6cdf45fc6bce8c',
        'brand':'Xiaomi',
        'scale':'2.0',
        'timezone':'28800',
        'language':'zh',
        'cns':'2',
        'carrier':'CMCC',
        'imsi':'460071570316924',
        'User-Agent':'Mozilla/5.0 (Linux; Android 5.1.1; MI 9 Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36',
        'uuid':'1d9eb19d-a61f-4bbd-9de3-6725ffd60cce',
        'battery-level':'1.00',
        'battery-state':'3',
        'terms-accepted':'1',
        'newbie':'1',
        'reach':'1',
        'act-code':now_time,
        'act-timestamp':now_time,
        'Content-Type':'application/x-www-form-urlencoded; charset=utf-8',
        'Accept-Encoding':'gzip, deflate',
        'Connection':'Keep-Alive',
        'session-info':'MIyig0dIBEwA3WfBpazjqbkVjffH0LHA5HzxbFamodxfgzzN/ltT/fwxrebBuLL2jq/xlrsJZmUEyBJupWf5+0epXxcorGnWZin80jBJAkfz9BPAcMiUZqnbkPIYHnHU',
        'Host':'api.douguo.net',
        'Content-Length':'186',
    }
    #IP代理
    proxy = {'http:':'http://用户名:密码@代理地址:端口'}
    resp = requests.post(url=url,headers=headers,data=data)
    return resp
#菜谱分类页面
def handle_index():
    url = 'https://api.douguo.net/recipe/flatcatalogs'
    now_time = str(int(time.time()))
    data ={ 'client':4,
            '_session':'1606558379927355757579416922',
            'v':now_time,
            '_vs':'2305',
            # 'sign_ran':'484925475026d98cb9a3107ec9b5b870',
            # 'code':'64bd71134f6cd6b6'
    }

    resp = handle_requsest(url,data)
    index_response_dict = json.loads(resp.text)

    for index_item in index_response_dict['result']['cs']:
        # food_item= {}
        # food_item['b_cate'] = index_item['name']
        for item in index_item['cs']:
            # food_item['s_cate'] = item['name']
            for food in item['cs']:
                # food_item['food'] =food['name']
                food_data = {
                    'client':'4',
                    # '_session':'1606558379927355757579416922',
                    'keyword':food['name'],
                    'order':'0',
                    '_vs':'400',
                    ' type':'0',
                    'auto_play_mode':2
                }
                #放入队列内部
                queue_list.put(food_data)

def handle_food_list(data):
    print("当前处理的食材：",data['keyword'])
    url = 'https://api.douguo.net/recipe/v2/search/0/20'
    food_list_resp = handle_requsest(url,data=data)
    # print(food_list_resp.text)
    food_list = json.loads(food_list_resp.text)
    for food in food_list['result']['list']:
        food_info = {}
        food_info['shicai'] = food_list['result']['sts']
        if food['type'] == 13:
            food_info['food_name'] = food['r']['n']
            food_info['user_name'] = food['r']['an']
            food_info['food_id'] = food['r']['id']
            food_info['describe'] = food['r']['cookstory'].replace('\n','').replace(' ','')
            food_info['zuoliao_list'] = food['r']['major']
            # print(food_info)
            food_url = 'https://api.douguo.net/recipe/v2/detail/{}'.format(food_info['food_id'])
            food_data = {
                'client': '4',
                # '_session':'1606558379927355757579416922',
                'author_id':'0',
                '_vs': '2803',
                ' type': '0',
                '_ext':'{"query":{"id":'+str(food_info['food_id'])+',"kw":'+data['keyword']+',"idx":"4","arc":"2803","type":"13"}}',

            }
            food_response = handle_requsest(url=food_url,data=food_data)
            food_response_dict = json.loads(food_response.text)
            food_info['tips'] = food_response_dict['result']['recipe']['tips']
            food_info['cook_step'] = food_response_dict['result']['recipe']['cookstep']
            print('当前入库的菜谱：',food_info['food_name'])

            mongo_info.insert_data(food_info)
        else:
            continue
if __name__ == '__main__':
    handle_index()
    #实现多线程，引入线程池
    pool = ThreadPoolExecutor(max_workers=2)
    while queue_list.qsize() >0 :
        pool.submit(handle_food_list,queue_list.get())
