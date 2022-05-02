# -*- coding: utf-8 -*-
# @Time : 2022/5/2 10:08
# @Author : Vincent Vic
# @File : Helper.py
# @Software: PyCharm
# 统一渲染方法
import datetime

from flask import render_template, g
import math

from common.lib.Utils import ObjToJson

'''
自定义分页类
'''


class Pagination:

    def __init__(self, params):
        self.ret = {
            "is_prev": 1,
            "is_next": 1,
            "from": 0,
            "end": 0,
            "current": 0,
            "total_pages": 0,
            "page": 0,
            "page_size": 0,
            "total": 0,
        }
        total = int(params['total'])
        page_size = int(params['page_size'])
        page = int(params['page'])
        display = int(params['display'])
        total_pages = int(math.ceil(total / page_size))
        total_pages = total_pages if total_pages > 0 else 1
        if page <= 1:
            self.ret['is_prev'] = 0

        if page >= total_pages:
            self.ret['is_next'] = 0

        self.ret['page'] = page
        semi = int(math.ceil(display / 2))

        if page - semi > 0:
            self.ret['from'] = page - semi
        else:
            self.ret['from'] = 1

        if page + semi <= total_pages:
            self.ret['end'] = page + semi
        else:
            self.ret['end'] = total_pages

        self.ret['current'] = page
        self.ret['total_pages'] = total_pages
        self.ret['page_size'] = page_size
        self.ret['total'] = total
        self.ret['range'] = range(self.ret['from'], self.ret['end'] + 1)

    def getOffset(self):
        return (self.ret['page'] - 1) * self.ret['page_size']

    def getLimit(self):
        return self.ret['page'] * self.ret['page_size']

    def getPages(self):
        return self.ret


def ops_render(template, context={}):
    if 'current_user' in g:
        context['current_user'] = g.current_user
    return render_template(template, **context)


def getCurrentDate(format="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.now().strftime(format)
