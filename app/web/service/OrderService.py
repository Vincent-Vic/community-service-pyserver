# -*- coding: utf-8 -*-
# @Time : 2022/5/4 18:35
# @Author : Vincent Vic
# @File : CategoryService.py
# @Software: PyCharm
import datetime
import json
import time

from sqlalchemy import or_

from application import db
from common.lib.APIException import APIParameterException
from common.lib.Helper import getCurrentDate, Pagination, getDateByAgo
from common.lib.constant import OrderStatus
from web.model.ServiceOrder import ServiceOrder
from web.service.CategoryService import CategoryService
from web.service.MemberService import MemberService

categoryService = CategoryService()
memberService = MemberService()


class OrderService:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            # 如果__instance还没有值，就给__instance变量赋值
            cls.__instance = object.__new__(cls)
            return cls.__instance
        else:
            # 如果__instance有值，则直接返回。
            return cls.__instance

    def getOrder(self, id):
        return ServiceOrder.query.filter_by(id=id).first()

    def getOrderInfo(self, oid):
        serviceOrder = self.getOrder(oid)
        if not serviceOrder:
            raise APIParameterException("订单不存在")
        info = dict(serviceOrder)
        print(info)
        # p_user
        p_user = memberService.getMember(serviceOrder.p_uid)
        info['p_user'] = {
            'nickname': p_user.nickname if p_user is not None else '用户已注销'
        }
        # c_user
        c_user = memberService.getMember(serviceOrder.c_uid)
        info['c_user'] = {
            'nickname': c_user.nickname if c_user is not None else '用户已注销'
        }
        return info

    def getOrderList(self, page_params):
        query = ServiceOrder.query
        # 分页处理
        page_params['total'] = query.count()

        mix_kw = page_params['mix_kw']
        # 昵称或手机号码查询
        if mix_kw != '':
            rule = or_(ServiceOrder.orderNo.ilike("%{0}%".format(mix_kw)),
                       ServiceOrder.consumer_snap_username.ilike("%{0}%".format(mix_kw)),
                       ServiceOrder.consumer_snap_tel.ilike("%{0}%".format(mix_kw)),
                       ServiceOrder.snap_title.ilike("%{0}%".format(mix_kw)))
            query = query.filter(rule)

        uid = int(page_params["uid"]) if 'uid' in page_params else -1
        openApi = True if 'api' in page_params else False
        status = int(page_params["status"])
        # 状态查询,状态大于-1 且 不是公开api可以查询 (后台)
        if status > -1 and not openApi:
            page_params['total'] = query.filter(ServiceOrder.status == status).count()
            query = query.filter(ServiceOrder.status == status)  # 状态查询
        # 状态查询,小程序查询 状态大于-1 且 会员id存在 （小程序查询自己的服务）
        elif openApi and uid > 0:
            if status > -1:
                page_params['total'] = query.filter(ServiceOrder.status == status).count()
                query = query.filter(ServiceOrder.status == status)  # 状态查询
            else:
                page_params['total'] = query.count()

            role = int(page_params['role']) == 1
            if (role):
                query = query.filter(ServiceOrder.p_uid == uid)
            else:
                query = query.filter(ServiceOrder.c_uid == uid)

        if int(page_params["nature"]) > -1:
            query = query.filter(ServiceOrder.snap_nature == int(page_params["nature"]))
        if int(page_params["category_id"]) > -1:
            query = query.filter(ServiceOrder.snap_category == int(page_params["category_id"]))

        pages = Pagination(page_params)
        serviceList = query.order_by(ServiceOrder.id.desc()).all()[pages.getOffset():pages.getLimit()]
        resp_data = {
            'list': serviceList,
            "pages": pages.getPages(),
        }
        return resp_data

    def ops(self, data):
        act = data['act']
        oid = data['id']
        serviceOrder = self.getOrder(oid)
        if not serviceOrder:
            raise APIParameterException("订单不存在")
        if act == 'remove':
            self.remove(oid)
        elif act == 'lock':
            status = -1 * serviceOrder.status
            self.updateStatus(oid, status)
        elif act == 'recover':
            self.updateStatus(oid, abs(serviceOrder.status))
        elif act == 'agree':
            self.updateStatus(oid, OrderStatus.UNPAID)
        elif act == 'pay':
            self.updateStatus(oid, OrderStatus.UNCONFIRMED)
        elif act == 'confirmed':
            self.updateStatus(oid, OrderStatus.UNRATED)
        elif act == 'rating':
            self.updateStatus(oid, OrderStatus.COMPLETED)
        elif act == 'canceled':
            self.updateStatus(oid, OrderStatus.CANCELED)
        elif act == 'deny':
            self.updateStatus(oid, OrderStatus.REFUSED)
        return serviceOrder

    def updateStatus(self, oid, status):
        db.session.query(ServiceOrder).filter_by(id=oid).update({'status': status, 'updated': getCurrentDate()})
        db.session.commit()

    def remove(self, oid):
        db.session.query(ServiceOrder).filter(ServiceOrder.id == oid).delete()
        db.session.commit()

    def edit(self, serviceOrder):
        serviceOrder.updated = getCurrentDate()
        db.session.add(serviceOrder)
        db.session.commit()

    def statusData(self, mid, role):

        data = {
            'unapproved': 0,
            'unpaid': 0,
            'unconfirmed': 0,
            'unrated': 0
        }

        if not mid:
            return data
        query = ServiceOrder.query
        if int(role) == 1:
            query = query.filter(ServiceOrder.p_uid == mid)
        else:
            query = query.filter(ServiceOrder.c_uid == mid)
        list = query.all()
        data['all'] = len(list)
        for item in list:
            # 未发布和被拒绝，取消都算
            if item.status == OrderStatus.UNAPPROVED:
                data['unapproved'] = data['unapproved'] + 1
            elif item.status == OrderStatus.UNPAID:
                data['unpaid'] = data['unpaid'] + 1
            elif item.status == OrderStatus.UNCONFIRMED:
                data['unconfirmed'] = data['unconfirmed'] + 1
            elif item.status == OrderStatus.UNRATED:
                data['unrated'] = data['unrated'] + 1

        return data

    def createOrder(self, cuid,service, address, payNum):
        order = ServiceOrder()
        now = datetime.datetime.now()
        order.orderNo = now.strftime("%d%H%M%S") + str(int(time.time()))
        order.status = OrderStatus.UNAPPROVED
        order.p_uid = service.p_uid
        order.c_uid = cuid
        order.sid = service.id
        order.pay_num = payNum
        order.price = service.price * payNum
        order.snap_title = service.title
        order.snap_category = service.category
        order.snap_price = service.price
        order.snap_nature = service.nature
        order.snap_cover_image = service.coverImage
        if service.designatedPlace == 1:
            address_obj = json.loads(address)
            order.consumer_snap_tel = address_obj['telNumber']
            order.consumer_snap_username = address_obj['userName']
            order.consumer_snap_province = address_obj['provinceName']
            order.consumer_snap_city = address_obj['cityName']
            order.consumer_snap_description = address_obj['detailInfo']
            order.consumer_snap_county = address_obj['countyName']
        order.created = getCurrentDate()
        self.edit(order)

    def toVo(self, order):
        categoryMap = categoryService.idMaps()
        item = dict();
        p_member = memberService.getMember(order.p_uid)
        if not p_member:
            item['publisher'] = {
                'id': -1,
                'avatarUrl': "",
                'nickname': "用户已经注销"
            }
        else:
            item['publisher'] = {
                'id': p_member.id,
                'avatarUrl': p_member.avatar,
                'nickname': p_member.nickname
            }
        c_member = memberService.getMember(order.c_uid)
        if not c_member:
            item['consumer'] = {
                'id': -1,
                'avatarUrl': "",
                'nickname': "用户已经注销"
            }
        else:
            item['consumer'] = {
                'id': c_member.id,
                'avatarUrl': c_member.avatar,
                'nickname': c_member.nickname
            }

        item['serviceSnap'] = {
            'nature': order.snap_nature,
            'coverImage': {
                'path': order.snap_cover_image
            },
            'price': order.snap_price,
            'title': order.snap_title,
            'category': {
                'id': order.snap_category,
                'name': categoryMap[order.snap_category]
            }
        }
        if order.consumer_snap_username:
            item['addressSnap'] = {
                'cityName': order.consumer_snap_city,
                'countyName': order.consumer_snap_county,
                'description': order.consumer_snap_description,
                'provinceName': order.consumer_snap_province,
                'telNumber': order.consumer_snap_tel,
                'userName': order.consumer_snap_username
            }
        item['created'] = order.created.strftime('%Y-%m-%d')
        item['id'] = order.id
        item['orderNo'] = order.orderNo
        item['price'] = order.price
        item['payNum'] = order.pay_num
        item['status'] = order.status
        return item

    def getVolume(self, day=30):
        q_date = getDateByAgo(day)
        list = ServiceOrder.query.filter(ServiceOrder.created >= q_date).all()
        resp_data = {
            'today-trading-amount': 0,
            '30-trading-amount': 0,
            'today-trading-volume': 0,
            '30-trading-volume': len(list),
        }
        now_date = datetime.datetime.now().strftime('%Y-%m-%d')
        for item in list:
            if OrderStatus.UNPAID < item.status < OrderStatus.CANCELED:
                resp_data['30-trading-amount'] = resp_data['30-trading-amount'] + item.price
                if item.created.strftime('%Y-%m-%d') == now_date:
                    resp_data['today-trading-amount'] = resp_data['today-trading-amount'] + item.price
            if item.created.strftime('%Y-%m-%d') == now_date:
                resp_data['today-trading-volume'] = resp_data['today-trading-volume'] + 1
        return resp_data

    def getTradingData(self, day=7):
        q_date = getDateByAgo(day)
        list = ServiceOrder.query.filter(ServiceOrder.created >= q_date).all()
        resp_data = dict()
        for item in list:
            key = item.created.strftime('%Y-%m-%d')
            if key in resp_data:
                resp_data[key] = resp_data[key] + 1
            else:
                resp_data[key] = 1

        return resp_data

    def getTradingStatusData(self, day=30):
        q_date = getDateByAgo(day)
        list = ServiceOrder.query.filter(ServiceOrder.created >= q_date).all()
        resp_data = [0, 0, 0, 0, 0, 0, 0]
        for item in list:
            resp_data[item.status] = resp_data[item.status] + 1

        return resp_data
