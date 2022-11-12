from decimal import Decimal
import json
from datetime import datetime

from django.views import View
from django.http import JsonResponse
from django.utils import timezone

from django_redis import get_redis_connection

from utils.views import LoginRequiredJSONMixin
from user.models import Address
from goods.models import SKU
from .models import OrderInfo, OrderGoods


class OrderSettlementView(LoginRequiredJSONMixin, View):
    """结算订单"""

    def get(self, request):
        """提供订单结算页面"""
        # 获取登录用户
        user = request.user

        # 查询当前用户的所有地址信息
        addresses = Address.objects.filter(user=user, is_deleted=False)

        # 从Redis购物车中查询出被勾选的商品信息
        redis_conn = get_redis_connection('carts')
        redis_cart = redis_conn.hgetall('carts_%s' % user.id)
        cart_selected = redis_conn.smembers('selected_%s' % user.id)
        cart = {}
        for sku_id in cart_selected:
            cart[int(sku_id)] = int(redis_cart[sku_id])

        # 查询商品信息
        sku_list = []
        # 查询商品信息
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'count': cart[sku.id],
                'price': sku.price
            })

        # 补充运费
        freight = Decimal('10.00')

        addresses_list = []
        for address in addresses:
            addresses_list.append({
                'id': address.id,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'receiver': address.receiver,
                'mobile': address.mobile
            })

        # 渲染界面
        context = {
            'addresses': addresses_list,
            'skus': sku_list,
            'freight': freight,
        }

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'context': context})


class OrderCommitView(LoginRequiredJSONMixin, View):

    def post(self, request):
        # 1 接收请求     user,address_id,pay_method
        user = request.user

        data = json.loads(request.body.decode())
        address_id = data.get('address_id')
        pay_method = data.get('pay_method')

        # 2 验证数据
        if not all([address_id, pay_method]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})

        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '参数不正确'})

        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return JsonResponse({'code': 400, 'errmsg': '参数不正确'})

        # order_id 主键（自己生成）   年月日时分秒 + 用户id（9位数字）
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S%f') + '%09d' % user.id

        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']

        #  总数量，总金额
        total_count = 0
        total_amount = Decimal('0')
        freight = Decimal('10.00')

        # 3 数据入库     生成订单（订单基本信息表和订单商品信息表）
        # 3.1 保存订单基本信息
        order_info = OrderInfo.objects.create(
            order_id=order_id,
            user=user,
            address=address,
            total_count=total_count,
            total_amount=total_amount,
            freight=freight,
            pay_method=pay_method,
            status=status
        )

        # 3.2 再保存订单商品信息
        redis_cli = get_redis_connection('carts')
        sku_id_counts = redis_cli.hgetall('carts_%s' % user.id)
        #  获取set
        selected_ids = redis_cli.smembers('selected_%s' % user.id)
        carts = {}

        #  遍历选中商品的id，
        for sku_id in selected_ids:
            carts[int(sku_id)] = int(sku_id_counts[sku_id])

        for sku_id, count in carts.items():

            sku = SKU.objects.get(id=sku_id)
            # 判断库存是否充足
            if sku.stock < count:
                return JsonResponse({'code': 400, 'errmsg': '库存不足'})
            # 如果充足，则库存减少，销量增加
            sku.stock -= count
            sku.sales += count

            # 累加总数量和总金额
            order_info.total_count += count
            order_info.total_amount += (count * sku.price)

            # 保存订单商品信息
            OrderGoods.objects.create(
                order=order_info,
                sku=sku,
                count=count,
                price=sku.price
            )

        # 更新订单的总金额和总数量
        order_info.save()

        # 4 将redis中选中的商品信息移除出去 （暂缓）
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'order_id': order_id})