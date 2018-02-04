# -*- coding: utf-8 -*-
# @Time    : 17/12/26 下午6:19
# @Author  : Edward
# @Site    :
# @File    : error_taker.py
# @Software: PyCharm Community Edition

from functools import wraps
from flask import jsonify

def taker(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        try:
            ret = {'data':fun(*args, **kwargs), 'error':0}
        except Exception, e:
            ret = {'msg': str(e), 'error':1}
        return jsonify(ret)
    return wrapper