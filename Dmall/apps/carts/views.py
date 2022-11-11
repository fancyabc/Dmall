import json
import pickle
import base64

# Create your views here.
from django.views import View
from django.http import JsonResponse

from django_redis import get_redis_connection

from goods.models import SKU


class CartsView(View):
    """

    前端：
        我们点击添加购物车之后， 前端将 商品id ，数量 发送给后端

    后端：
        请求：         接收参数，验证参数
        业务逻辑：       根据商品id查询数据库看看商品id对不对
                      数据入库
                        登录用户入redis
                            连接redis
                            获取用户id
                            hash
                            set
                            返回响应
                        未登录用户入cookie
                            先 cookie字典
                            字典转换为bytes
                            bytes类型数据base64编码
                            设置cookie
                            返回响应
        响应：         返回JSON
        路由：     POST  /carts/
    """
    def post(self, request):
        # 1.接收数据
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        # 2.验证数据
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '查无此商品'})
        try:
            count = int(count)
        except Exception:
            count = 1

        # 3.判断用户的登录状态
        user = request.user
        if user.is_authenticated:
            # 4.登录用户保存redis
            #    4.1 连接redis
            redis_cli = get_redis_connection('carts')
            #    4.2 操作hash
            redis_cli.hset('carts_%s' % user.id, sku_id, count)  # (key, field, value)
            #    4.3 操作set
            redis_cli.sadd('selected_%s' % user.id, sku_id)  # 默认是选中
            #    4.4 返回响应
            return JsonResponse({'code': 0, 'errmsg': 'ok'})
        # 5.未登录用户保存cookie
        else:
            #    5.1 先读取cookie数据
            cookie_cart = request.COOKIES.get('carts')
            if cookie_cart:
                carts = pickle.loads(base64.b64decode(cookie_cart))
            else:
                carts = {}

            # 判断新增的商品 有没有在购物车里
            if sku_id in carts:
                origin_count = carts[sku_id]['count']
                count += origin_count

            carts[sku_id] = {
                'count': count,
                'selected': True
            }

            #    5.2 字典转换为bytes
            carts_bytes = pickle.dumps(carts)
            #    5.3 bytes类型数据base64编码
            carts_base64 = base64.b64encode(carts_bytes)

            #    5.4 设置cookie
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
            #  value的数据是 str数据
            response.set_cookie('carts', carts_base64.decode(), max_age=3600*24)
            #    5.5 返回响应
            return response


    def get(self, request):
        user = request.user
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            sku_id_counts = redis_conn.hgetall('carts_%s' % user.id)
            selected_ids = redis_conn.smembers('selected_%s' % user.id)
            carts = {}

            for sku_id, count in sku_id_counts.items():
                carts[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in selected_ids
                }

        else:
            cookie_carts = request.COOKIES.get('carts')
            if cookie_carts:
                carts = pickle.loads(base64.b64decode(cookie_carts))
            else:
                carts = {}

        sku_ids = carts.keys()
        skus = SKU.objects.filter(id__in=sku_ids)

        sku_list = []
        for sku in skus:
            sku_list.append({
                'id': sku.id,
                'price': sku.price,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'selected': carts[sku.id]['selected'],  # 选中状态
                'count': int(carts[sku.id]['count']),  # 数量 强制转换一下
                'amount': sku.price * carts[sku.id]['count']  # 总价格
            })
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'cart_skus': sku_list})


    def put(self, request):
        user = request.user

        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count=data.get('count')
        selected=data.get('selected')
        # 验证数据
        if not all([sku_id, count]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})

        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '没有此商品'})

        try:
            count = int(count)
        except Exception:
            count = 1

        if user.is_authenticated:
            redis_cli = get_redis_connection('carts')
            redis_cli.hset('carts_%s' % user.id, sku_id, count)
            if selected:
                redis_cli.sadd('selected_%s' % user.id, sku_id)
            else:
                redis_cli.srem('selected_%s' % user.id, sku_id)

            return JsonResponse({'code': 0, 'errmsg': 'ok',
                                 'cart_sku': {'count': count, 'selected': selected}})
        else:
            cookie_cart = request.COOKIES.get('carts')
            if cookie_cart:
                carts = pickle.loads(base64.b64decode(cookie_cart))
            else:
                carts = {}

        if sku_id in carts:
            carts[sku_id] = {
                'count': count,
                'selected': selected
            }

        new_carts = base64.b64encode(pickle.dumps(carts))

        response = JsonResponse({'code': 0, 'errmsg': 'ok',
                                 'cart_sku': {'count': count, 'selected': selected}})
        response.set_cookie('carts', new_carts.decode(), max_age=24*3600)

        return response

    def delete(self, request):

        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        try:
            SKU.objects.get(pk=sku_id)  # pk primary key
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '没有此商品'})

        user = request.user
        if user.is_authenticated:

            # 4.登录用户操作redis
            redis_cli = get_redis_connection('carts')
            redis_cli.hdel('carts_%s' % user.id, sku_id)
            redis_cli.srem('selected_%s' % user.id, sku_id)

            return JsonResponse({'code': 0, 'errmsg': 'ok'})

        else:
            # 未登录用户操作cookie
            cookie_cart = request.COOKIES.get('carts')
            #     判断数据是否存在
            if cookie_cart is not None:
                #     存在则解码
                carts = pickle.loads(base64.b64decode(cookie_cart))
            else:
                #     不存在则初始化字典
                carts = {}
            #     删除数据 {}
            del carts[sku_id]
            #     我们需要对字典数据进行编码和base64的处理
            new_carts = base64.b64encode(pickle.dumps(carts))
            #     设置cookie
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
            response.set_cookie('carts', new_carts.decode(), max_age=24*3600)

            return response
