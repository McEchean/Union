#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/20 17:17
# @Author  : Echean
# @File    : Union_main.py
# @Software: PyCharm
import time
import requests
import logging
import json
import re
from http import cookiejar

logging.basicConfig(level=None)

Header = {
    'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Host': 'uac.10010.com',
    'Referer': 'https://uac.10010.com/portal/homeLogin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    'Upgrade-Insecure-Requests': '1',
    'X-Requested-With': 'XMLHttpRequest'
}

session = requests.session()
session.headers = Header.copy()
session.cookies = cookiejar.LWPCookieJar('cookies.txt')


def login(phone_num, server_pwd):
    # flag = 0
    try:
        session.cookies.load(ignore_discard=True)
        flag = 1
    except FileNotFoundError:
        flag = 0

    if flag:
        s = check_verify(phone_num)
        if s['resultCode'] == 'false' and s['ckCode'] == '2':
            send_message(phone_num)
            login_first(phone_num, server_pwd)
            check_login()
        else:
            login_first(phone_num, server_pwd, need_verify=2)
            check_login()
    else:
        check_verify(phone_num)
        send_message(phone_num)
        login_first(phone_num, server_pwd)
        check_login()


def check_verify(phone_num):
    check_url = 'https://uac.10010.com/portal/Service/CheckNeedVerify?' \
                'callback=jQuery17200957458793685022_{0}&' \
                'userName={1}&pwdType=01&_={2}'.format(int(time.time() * 1000),
                                                       phone_num,
                                                       int(time.time() * 1000))
    needVerify = session.get(url=check_url, headers=session.headers)
    logging.info('needVerify: %s' % needVerify.status_code)
    s = eval(re.match(r'^.*?({.*?}).*$', needVerify.text).group(1))
    return s


def send_message(phone_num):
    send_message_url = 'https://uac.10010.com/portal/Service/SendCkMSG?' \
                       'callback=jQuery172036837534689129425_{0}&' \
                       'req_time={1}&mobile={2}&_={3}'.format(int(time.time() * 1000),
                                                              int(time.time() * 1000),
                                                              phone_num,
                                                              int(time.time() * 1000))
    resp_msg = session.get(url=send_message_url, headers=session.headers)
    logging.info('resp_msg: %s' % resp_msg.text)


def login_first(phone_num, server_password, need_verify=1):
    if need_verify == 1:
        VerifyCode = input('请输入验证码：')
        get_url = 'https://uac.10010.com/portal/Service/MallLogin?' \
                  'callback=jQuery17207043599656300588_{0}&' \
                  'req_time={1}0&' \
                  'redirectURL=http%3A%2F%2Fwww.10010.com%2Fnet5%2F&' \
                  'userName={2}&' \
                  'password={3}&' \
                  'pwdType=01&' \
                  'productType=01&' \
                  'redirectType=03&' \
                  'rememberMe=1&' \
                  'verifyCKCode={4}&' \
                  '_={5}'.format(int(time.time() * 1000),
                                 int(time.time() * 1000),
                                 phone_num,
                                 server_password,
                                 VerifyCode,
                                 int(time.time() * 1000))
        login_resp = session.get(get_url, headers=session.headers)
        logging.info('login_resp: %s' % login_resp.status_code)
    elif need_verify == 2:
        get_url = 'https://uac.10010.com/portal/Service/MallLogin?' \
                  'callback=jQuery17207043599656300588_{0}&' \
                  'req_time={1}0&' \
                  'redirectURL=http%3A%2F%2Fwww.10010.com%2Fnet5%2F&' \
                  'userName={2}&' \
                  'password={3}&' \
                  'pwdType=01&' \
                  'productType=01&' \
                  'redirectType=03&' \
                  'rememberMe=1&' \
                  '_={4}'.format(int(time.time() * 1000),
                                 int(time.time() * 1000),
                                 phone_num,
                                 server_password,
                                 int(time.time() * 1000))
        login_resp = session.get(get_url, headers=session.headers)
        logging.info('login_resp: %s' % login_resp.status_code)


def check_login():
    check_login_common_url = 'http://www.10010.com/mall/service/common/l?_={0}'.format(int(time.time() * 1000))
    session.headers.update({
        'Host': 'www.10010.com',
        'Referer': 'http://www.10010.com/net5/036/',
    })
    check_login_common_resp = session.post(check_login_common_url, headers=session.headers)
    logging.info('check_login_common_resp: %s' % check_login_common_resp.status_code)

    user_phone_detial()

    session.headers.update({
        'Host': 'iservice.10010.com',
        'Origin': 'http://iservice.10010.com',
        'Referer': 'http://iservice.10010.com/e4/query/bill/call_dan-iframe.html?menuCode=000100030001',
    })
    check_login_url = 'http://iservice.10010.com/e3/static/check/checklogin/?_={0}'.format(int(time.time() * 1000))
    check_login_resp = session.post(check_login_url, headers=session.headers)
    logging.info('check_login_resp: %s' % check_login_resp.status_code)


# 每次发送短信URL不一样
def send_check_message(Type, post_id):
    check_map_url = 'http://iservice.10010.com/e3/static/query/checkmapExtraParam?_={0}'.format(int(time.time() * 1000))
    check_map_resp = session.post(check_map_url, data={'menuId': post_id},
                                  headers=session.headers)
    logging.info('send_check_message_resp: %s' % check_map_resp.text)

    send_check_message_urls = {
        'call_detial': 'http://iservice.10010.com/e3/static/query/sendRandomCode?_={0}&'
                       'accessURL=http://iservice.10010.com/e4/query/bill/call_dan-iframe.html?'
                       'menuCode=000100030001&menuid=000100030001'.format(int(time.time() * 1000)),
        'net_detial': 'http://iservice.10010.com/e3/static/query/sendRandomCode?_={0}&'
                      'accessURL=http://iservice.10010.com/e4/query/basic/call_flow_iframe1.html&'
                      'menuid=000100030004'.format(int(time.time() * 1000)),
        'sms_detial': 'http://iservice.10010.com/e3/static/query/sendRandomCode?_={0}&'
                      'accessURL=http://iservice.10010.com/e4/query/calls/call_sms-iframe.html?'
                      'menuCode=000100030002&menuid=000100030002'.format(int(time.time() * 1000)),
    }

    send_check_message_url = send_check_message_urls[Type]
    send_check_message_resp = session.post(send_check_message_url, data={'menuId': post_id},
                                           headers=session.headers)
    logging.info('send_check_message_resp: %s' % send_check_message_resp.status_code)


# 每次验证短信验证码的URL也不一样
def submit_check_message_num(Type, post_id):
    check_message_num_urls = {
        'call_detial': 'http://iservice.10010.com/e3/static/query/verificationSubmit?_={0}&'
                       'accessURL=http://iservice.10010.com/e4/query/bill/call_dan-iframe.html?'
                       'menuCode=000100030001&menuid=000100030001'.format(int(time.time() * 1000)),
        'net_detial': 'http://iservice.10010.com/e3/static/query/verificationSubmit?_={0}&'
                      'accessURL=http://iservice.10010.com/e4/query/basic/call_flow_iframe1.html&'
                      'menuid=000100030004'.format(int(time.time() * 1000)),
        'sms_detial': 'http://iservice.10010.com/e3/static/query/verificationSubmit?_={0}&'
                      'accessURL=http://iservice.10010.com/e4/query/calls/call_sms-iframe.html?'
                      'menuCode=000100030002&menuid=000100030002'.format(int(time.time() * 1000)),
    }
    code = input('二重验证短信已发送，请查收！输入:')
    check_message_num_url = check_message_num_urls[Type]
    check_message_num_resp = session.post(check_message_num_url, data={'inputcode': code, 'menuId': post_id})
    logging.info('check_message_num_resp: %s' % check_message_num_resp.status_code)


def user_phone_detial():  # 待确认是否需要请求
    user_phone_detial_url = 'http://iservice.10010.com/e4/query/bill/call_dan-iframe.html?' \
                            'menuCode=000100030001'
    user_phone_detial_resp = session.get(user_phone_detial_url, headers=session.headers)
    logging.info('user_phone_detial_resp: %s' % user_phone_detial_resp.status_code)


def detial(Type, begindate, enddate, data_num):
    detial_urls = {
        'call_detial': 'http://iservice.10010.com/e3/static/query/callDetail?_={0}&'
                       'accessURL=http://iservice.10010.com/e4/query/bill/call_dan-iframe.html?'
                       'menuCode=000100030001&menuid=000100030001'.format(int(time.time() * 1000)),
        'net_detial': 'http://iservice.10010.com/e3/static/query/callFlow?_={0}&'
                      'accessURL=http://iservice.10010.com/e4/query/basic/call_flow_iframe1.html&'
                      'menuid=000100030004'.format(int(time.time() * 1000)),
        'sms_detial': 'http://iservice.10010.com/e3/static/query/sms?_=1504098130310&'
                      'accessURL=http://iservice.10010.com/e4/query/calls/call_sms-iframe.html?'
                      'menuCode=000100030002&menuid=000100030002'.format(int(time.time() * 1000)),
        'free_detial': 'http://iservice.10010.com/e3/static/query/accountBalance/search?_={0}&'
                       'accessURL=http://iservice.10010.com/e4/skip.html?menuCode=000100010002&'
                       'menuCode=000100010002'.format(int(time.time() * 1000)),
    }

    datas = {
        'other': {'pageNo': '1', 'pageSize': data_num, 'beginDate': begindate, 'endDate': enddate},
        'sms_data': {'pageNo': '1', 'pageSize': data_num, 'begindate': begindate, 'enddate': enddate},
    }

    detial_url = detial_urls[Type]
    if Type == 'sms_detial':
        session.headers.update({
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Upgrade-Insecure-Requests': '',
            'Referer': 'http://iservice.10010.com/e4/query/calls/call_sms-iframe.html?menuCode=000100030002',
        })
        Data = datas['sms_data']
    else:
        Data = datas['other']

    detial_resp = session.post(detial_url, headers=session.headers,
                               data=Data)
    logging.info('call_detial_resp: %s' % detial_resp.status_code)
    print(json.loads(detial_resp.text))


def query_info():
    info_type = input('请输入要查询的信息类别(1：通话详单 2：短信详单 3：上网详单 4：话费余量)：')
    print('请输入要查询的时间段/不跨月（格式如：20180101）')
    begin_date = input('开始日期：')
    end_date = input('结束日期：')
    query_num = input('请输入要查询的条数：')
    info_types = {
        '1': ['call_detial', '000100030001'],
        '2': ['sms_detial', '000100030002'],
        '3': ['net_detial', '000100030004'],
        '4': ['free_detial'],
    }
    if int(info_type) < 4:
        send_check_message(*info_types[info_type])
        submit_check_message_num(*info_types[info_type])
        detial(info_types[info_type][0], begin_date, end_date, query_num)
    else:
        check_login()
        detial('free_detial', begin_date, end_date, query_num)


phone_num = input('请输入手机号：')
server_pwd = input('请输入服务密码：')
login(phone_num, server_pwd)
s = 'y'
while s.lower() == 'y':
    query_info()
    s = input('是否还需要查询（y/n）：').strip()
session.cookies.save()
