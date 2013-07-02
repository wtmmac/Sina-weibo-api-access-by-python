# -*- coding: utf-8 -*-
#/usr/bin/env python

__version__ = '1.0'
__author__ = 'http://weibo.com/wtmmac'

'''
Demo for sinaweibopy
主要实现token自动生成及更新
适合于后端服务相关应用
'''

# api from:http://michaelliao.github.com/sinaweibopy/
from weibo import APIClient

import sys, os, urllib, urllib2
from http_helper import *
from retry import *
try:
    import json
except ImportError:
    import simplejson as json

# setting sys encoding to utf-8
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

# weibo api访问配置
APP_KEY = ''      # app key
APP_SECRET = ''   # app secret
CALLBACK_URL = '' # callback url 授权回调页,与OAuth2.0 授权设置的一致
USERID = ''       # 微博用户名                     
USERPASSWD = ''   # 用户密码

# token file path
save_access_token_file  = 'access_token.txt'
file_path = os.path.dirname(__file__) + os.path.sep
access_token_file_path = file_path + save_access_token_file

client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)

def make_access_token():
    '''请求access token'''
    params = urllib.urlencode({'action':'submit','withOfficalFlag':'0','ticket':'','isLoginSina':'', \
        'response_type':'code', \
        'regCallback':'', \
        'redirect_uri':CALLBACK_URL, \
        'client_id':APP_KEY, \
        'state':'', \
        'from':'', \
        'userId':USERID, \
        'passwd':USERPASSWD, \
        })

    login_url = 'https://api.weibo.com/oauth2/authorize'

    url = client.get_authorize_url()
    content = urllib2.urlopen(url)
    if content:
        headers = { 'Referer' : url }
        request = urllib2.Request(login_url, params, headers)
        opener = get_opener(False)
        urllib2.install_opener(opener)
        try:
            f = opener.open(request)
            print f.headers.headers
            return_callback_url = f.geturl()
            # print f.read()
        except urllib2.HTTPError, e:
            return_callback_url = e.geturl()
        # 取到返回的code
        code = return_callback_url.split('=')[1]
    #得到token
    token = client.request_access_token(code)
    save_access_token(token)

def save_access_token(token):
    '''将access token保存到本地'''
    f = open(access_token_file_path, 'w')
    f.write(token['access_token']+' ' + str(token['expires_in']))
    f.close()

@retry(1)
def apply_access_token():
    '''从本地读取及设置access token'''
    try:
        token = open(access_token_file_path, 'r').read().split()
        if len(token) != 2:
            make_access_token()
            return False
        # 过期验证
        access_token, expires_in = token
        try:
            client.set_access_token(access_token, expires_in)
        except StandardError, e:
            if hasattr(e, 'error'): 
                if e.error == 'expired_token':
                    # token过期重新生成
                    make_access_token()
            else:
                pass
    except:
        make_access_token()
    
    return False

if __name__ == "__main__":
    apply_access_token()

    # 以下为访问微博api的应用逻辑
    # 以接口访问状态为例
    status = client.get.account__rate_limit_status()
    print json.dumps(status)