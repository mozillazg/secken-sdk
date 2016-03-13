# -*- coding: utf-8 -*-
from hashlib import sha1
from operator import itemgetter
import sys
try:
    from urllib.parse import quote_plus, urljoin
except ImportError:
    from urllib import quote_plus, urljoin

import requests

PY2 = sys.version_info[0] == 2
if PY2:
    text_type = unicode   # noqa
else:
    text_type = str


class NonOKError(Exception):
    """response 状态码不是 200 OK"""
    def __init__(self, response):
        self.response = response
        self.code = response.status_code


def wrap_response(response):
    if response.status_code != requests.codes.ok:
        raise NonOKError(response)
    return response.json()


class SeckenSDK(object):
    API_BASE = 'https://api.sdk.yangcong.com'
    response_handler = wrap_response

    def __init__(self, app_id, app_key, timeout=10):
        self.app_id = app_id
        self.app_key = app_key
        self.session = requests.Session()
        self.timeout = timeout

    def qrcode_for_auth(self, auth_type=1, action_type=None,
                        action_details=None, callback=None,
                        url='/qrcode_for_auth'):
        """获取验证二维码

        参数及返回值含义详见：
        https://www.yangcong.com/api#sdk/qrcode_for_auth
        """
        params = dict(auth_type=auth_type, action_type=action_type,
                      action_details=action_details, callback=callback)
        return self._request('get', url, params=params)

    def realtime_authorization(self, uid, auth_type=1,
                               action_type=None, action_details=None,
                               callback=None, url='/realtime_authorization'):
        """发起推送验证事件

        参数及返回值含义详见：
        https://www.yangcong.com/api#sdk/realtime_authorization
        """
        data = dict(uid=uid, auth_type=auth_type,
                    action_type=action_type, action_details=action_details,
                    callback=callback)
        return self._request('post', url, data=data)

    def query_auth_token(self, auth_token, url='/query_auth_token'):
        """复验验证结果的方法

        参数及返回值含义详见：
        https://www.yangcong.com/api#sdk/query_auth_token
        """
        params = dict(auth_token=auth_token)
        return self._request('get', url, params=params)

    def event_result(self, event_id, url='/event_result'):
        """查询验证事件的结果

        参数及返回值含义详见：
        https://www.yangcong.com/api#sdk/event_result
        """
        params = dict(event_id=event_id)
        return self._request('get', url, params=params)

    def _full_url(self, url):
        return urljoin(self.API_BASE, url)

    def _request(self, method, url, params=None, data=None, **kwargs):
        request = getattr(self.session, method)
        kwargs.setdefault('timeout', self.timeout)
        url = self._full_url(url)

        # 用于签名的数据
        payload = {}
        if data:
            data.setdefault('app_id', self.app_id)
            payload = data
        elif params:
            params.setdefault('app_id', self.app_id)
            payload = params
        # 签名
        signature = gen_signature(self.app_key, **payload)
        payload['signature'] = signature

        response = request(url, params=params, data=data, **kwargs)
        if self.response_handler is not None:
            response = self.__class__.response_handler(response)
        return response


def gen_signature(app_key, **params):
    """生成签名"""
    # 按字典顺排序
    sorted_params = sorted(params.items(), key=itemgetter(0))
    # 拼接字符串
    raw_data = ''.join(
        '{0}={1}'.format(k, quote_plus(to_bytes(v)))
        for k, v in sorted_params
        if v is not None
    )
    raw_data += app_key
    return sha1(to_bytes(raw_data)).hexdigest()


def to_bytes(obj, encoding='utf-8'):
    return text_type(obj).encode(encoding)
