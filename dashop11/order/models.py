from django.db import models

from goods.models import SKU
from tools.models import BaseModel
from user.models import UserProfile
# Create your models here.

#status_choices为元组
STATUS_CHOICES = (
    (1,"待付款"),
    (2,"待发货"),
    (3,"待收货"),
    (4,"订单完成"),
)

class OrderInfo(BaseModel):

    order_id = models.CharField(max_length=64,primary_key=True,verbose_name='订单号',default='')
    #和user应该是一对多，一个用户可以有多个订单
    user_profile = models.ForeignKey(UserProfile)
    total_count = models.IntegerField(verbose_name="商品总数")
    total_amount = models.DecimalField(verbose_name='商品总金额',max_digits=10,decimal_places=2)
    freight = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='运费')
    pay_method = models.SmallIntegerField(default=1,verbose_name='支付方式')

    #订单地址
    receiver = models.CharField(verbose_name='收件人',max_length=11)
    address = models.CharField(max_length=100,verbose_name='收货地址')
    receiver_mobile = models.CharField(max_length=11,verbose_name='收件人电话')
    tag = models.CharField(verbose_name='标签',max_length=10)


    status = models.SmallIntegerField(verbose_name='订单状态',choices=STATUS_CHOICES)
    #choice 选项可以将admin后台该部分变成下拉列表。

    class Meta:
        db_table = 'order_order_info'

#订单中每一件商品单独列表
class OrderGoods(BaseModel):
    order = models.ForeignKey(OrderInfo)
    sku = models.ForeignKey(SKU)
    count = models.IntegerField(default=1,verbose_name='数量')
    price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='商品折后单价')

    class Meta:
        #遇到驼峰就拆开加上应用名
        db_table = 'order_order_goods'

    def __str__(self):
        return self.sku.name