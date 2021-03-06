# -*- coding: utf-8 -*-
# @Time : 2022/4/30 12:22
# @Author : Vincent Vic
# @File : UserController.py
# @Software: PyCharm
from flask import Blueprint, request

from application import app
from common.lib.APIException import APIParameterException, APIAuthFailed, APINotFound
from common.lib.AuthHelper import get_member_login_id
from common.lib.CommonResult import CommonResult
from common.lib.Helper import getPageParams, getOpsData
from web.service.CategoryService import CategoryService
from web.service.MemberService import MemberService
from web.service.OrderService import OrderService
from web.service.SService import SService

order_api = Blueprint('order_api', __name__)

sService = SService()
orderService = OrderService()
categoryService = CategoryService()
memberService = MemberService()

ops_power = ['agree', 'pay', 'confirmed', 'canceled', 'deny']
service_power = ['agree',  'deny']


@order_api.route("/list")
def list():
    req = request.args
    page_params = getPageParams(req, app)
    #校验权限 存在状态查询需要登入
    uid = get_member_login_id()
    if not uid:
        raise APIAuthFailed
    page_params['uid'] = uid

    page_params['api'] = True
    page_params['role'] = req.get("role", 1)
    resp_data = orderService.getOrderList(page_params)
    pages = resp_data['pages']
    resp_data['pages'] = {
        'page_size': pages['page_size'],
        'total': pages['total'],
        'is_next': pages['is_next']
    }
    list = []
    order_list = resp_data['list']

    for order in order_list:
        item = orderService.toVo(order)
        list.append(item)
    resp_data['list'] = list

    return CommonResult.successDictData("list", resp_data)


@order_api.route("/desc")
def getInfo():
    req = request.args
    id = int(req.get('id', -1))
    if id < 0:
        raise APIParameterException("参数错误")
    order = orderService.getOrder(id)
    resp_data = orderService.toVo(order)
    return CommonResult.successDictData("desc", resp_data)


@order_api.route("/status/my")
def getStatus():
    mid = get_member_login_id()
    req = request.args
    role = req.get('role', 1)
    resp_data = orderService.statusData(mid, role)
    return CommonResult.successDictData("desc", resp_data)


# cityName: "广州市"
# countyName: "海珠区"
# detailInfo: "新港中路397号"
# errMsg: "chooseAddress:ok"
# nationalCode: "510000"
# postalCode: "510000"
# provinceName: "广东省"
# telNumber: "020-81167888"
# userName: "张三"

@order_api.post("/create")
def createOrder():
    c_uid = get_member_login_id()
    if not c_uid:
        raise APIAuthFailed
    req = request.values
    address = req['address']
    serviceId = req['serviceId']
    payNum = int(req['payNum']) if 'payNum' in req else -1
    if payNum < 1:
        raise APIParameterException("支付数量异常")
    service = sService.getService(serviceId)
    if not service:
        raise APINotFound
    if service.designatedPlace == 1:
        # 需要地址，校验地址是否存在，拿微信地址，address此时为json字符串，长度低于190属于完全不符合规则
        # {"errMsg":"chooseAddress:ok","userName":"x","nationalCode":"510000","telNumber":"1",
        # "postalCode":"510000","provinceName":"广东省","cityName":"广州市","countyName":"海珠区","detailInfo":"x"}
        if not address or len(address) < 190:
            raise APIParameterException("需要地址信息")
    orderService.createOrder(c_uid, service, address, payNum)
    sales_volume = service.salesVolume + payNum
    sService.updateSalesVolume(serviceId, sales_volume)
    return CommonResult.success()

@order_api.post("/ops")
def ops():
    a_uid = get_member_login_id()
    if not a_uid:
        raise APIAuthFailed
    data = getOpsData(request.values)
    # 校验是否是自己的服务且操作是否有权限
    if data['act'] not in ops_power:
        raise APIParameterException("没有该操作")
    order = orderService.getOrder(int(data['id']))
    if data['act'] in service_power and a_uid != order.p_uid:
        raise APIParameterException("你不是服务所有人")
    elif data['act'] not in service_power and a_uid != order.c_uid:
        raise APIParameterException("你不是订单所有人")

    orderService.ops(data)
    return CommonResult.successMsg("更新成功")