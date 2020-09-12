import json
from datetime import datetime

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from tools.login_dec import login_check
from user.models import Address
from carts.views import CartsView
from django.conf import settings
from .models import *
from goods.models import SKU

# Create your views here.

newCartsView = CartsView()

class AdvanceView(View):

    def get_address(self,user_id):
        all_address = Address.objects.filter(user_profile_id=user_id,is_active=True)
        if not all_address:
            #用户还没有地址
            return []
        #需求：默认地址要显示在所有地址最前面
        address_default = []
        address_normal = []
        for addr in all_address:
            addr_dic = {
                'id':addr.id,
                'name':addr.receiver,
                'mobile':addr.receiver_mobile,
                'title':addr.tag,
                'address':addr.address
            }
            if addr.is_default == True:
                address_default.append(addr_dic)
            else:
                address_normal.append(addr_dic)
        return address_default+address_normal

    @login_check
    def get(self,request,username):
        user = request.myuser
        settlement = int(request.GET['settlement_type'])
        # 获取地址
        address_list = self.get_address(user.id)
        if settlement == 0:
            #从购物车点确认订单
            #获取购物车中　勾选上的物品信息
            skus_list=newCartsView.get_carts_list(user.id)
            selected_carts = [s for s in skus_list if s['selected']==1]
            data = {}
            data['addresses'] = address_list
            data['sku_list'] = selected_carts
            return JsonResponse({'code':200,'data':data,'base_url':settings.PIC_URL})
        else:
            #从商品详情页点立即购买进入确认订单
            pass

class OrderInfoView(View):

    @login_check
    def post(self,request,username):
        #生成用户订单
        user =request.myuser
        address_id = json.loads(request.body).get('address_id')
        try:
            address = Address.objects.get(id=address_id,is_active=True)
        except Exception as e:
            return JsonResponse({'code':10500,'errmsg':'address error'})
        #开启事务保证统一性
        with transaction.atomic():
            #初始存档点
            sid = transaction.savepoint()
            #order_id: 时间＋用户主键
            now = datetime.now()
            order_id = '%s%02d'%(now.strftime('%Y%m%d%H%M%S'), user.id)
            order = OrderInfo.objects.create(
                order_id=order_id,
                user_profile = user,
                address = address.address,
                receiver=address.receiver,
                receiver_mobile = address.receiver_mobile,
                tag = address.tag,
                total_amount = 0,
                total_count = 0,
                freight = 10,
                pay_method=1,
                status=1
            )
            #取出购物车数据
            all_carts = newCartsView.get_carts_all_data(user.id)
            #过滤出选中的商品
            carts_data = {k:v for k,v in all_carts.items() if v[1]==1}
            skus = SKU.objects.filter(id__in=carts_data.keys())
            total_count = 0
            total_amount = 0
            for sku in skus:
                carts_count = int(carts_data[sku.id][0])
                if sku.stock < carts_count:
                    #库存不够
                    #回滚
                    transaction.savepoint_rollback(sid)
                    return JsonResponse({'code':10501,'errmsg':'stock error %s'%(sku.id)})

                #修改库存&乐观锁
                old_version = sku.version
                result = SKU.objects.filter(id=sku.id,version=old_version).update(stock=sku.stock-carts_count,sales=sku.sales+carts_count,version=old_version+1)
                if result == 0:
                    #证明当前数据有变化
                    transaction.savepoint_rollback(sid)
                    return JsonResponse({'code':10502,'errmsg':'库存发生变化,稍后再试'})
                #穿件订单商品数据
                OrderGoods.objects.create(
                    order_id=order_id,
                    sku_id=sku.id,
                    count=carts_count,
                    price=sku.price
                )
                #计算总数量和总金额
                total_amount+=sku.price * carts_count
                total_count+=carts_count
            #更新订单数据
            order.total_count = total_count
            order.total_amount = total_amount
            order.save()
            #提交事务
            transaction.savepoint_commit(sid)

        #删除购物车中　勾选状态的商品

        data = {
            'saller':'dashop11',
            'total_amount':order.total_amount+order.freight,
            'order_id':order_id,
            'pay_url':''
        }

        return JsonResponse({'code':200,'data':data})