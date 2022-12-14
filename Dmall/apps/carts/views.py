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
            pipeline = redis_cli.pipeline()
            #    4.2 操作hash
            # redis_cli.hset('carts_%s' % user.id, sku_id, count)  # (key, field, value)
            pipeline.hincrby('carts_%s' % user.id, sku_id, count)
            #    4.3 操作set
            pipeline.sadd('selected_%s' % user.id, sku_id)  # 默认是选中
            pipeline.execute()
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
            pipeline = redis_cli.pipeline()
            pipeline.hset('carts_%s' % user.id, sku_id, count)
            if selected:
                pipeline.sadd('selected_%s' % user.id, sku_id)
            else:
                pipeline.srem('selected_%s' % user.id, sku_id)
            pipeline.execute()

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
            pipeline = redis_cli.pipeline()
            pipeline.hdel('carts_%s' % user.id, sku_id)
            pipeline.srem('selected_%s' % user.id, sku_id)
            pipeline.execute()

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


class CartsSelectAllView(View):
    """全选购物车"""

    def put(self, request):
        data = json.loads(request.body.decode())
        selected = data.get('selected', True)   # default true

        # 验证数据
        if not isinstance(selected, bool):
            return JsonResponse({'code': 400, 'errmsg': '参数selected有误'})

        user = request.user
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            cart = redis_conn.hgetall('carts_%s' % user.id)
            sku_id_list = cart.keys()
            if selected:
                # 全选
                redis_conn.sadd('selected_%s' % user.id, *sku_id_list)
            else:
                # 取消全选
                redis_conn.srem('selected_%s' % user.id, *sku_id_list)
            return JsonResponse({'code': 0, 'errmsg': '全选购物车成功'})
        else:
            cart = request.COOKIES.get('carts')
            response = JsonResponse({'code': 0, 'errmsg': '全选购物车成功'})
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
                for sku_id in cart:
                    cart[sku_id]['selected'] = selected
                cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
                response.set_cookie('carts', cookie_cart, max_age=7 * 24 * 3600)
            return response


class CartsSimpleView(View):
    """展示商品页面右上角购物车"""

    def get(self, request):
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录，查询Redis购物车
            redis_conn = get_redis_connection('carts')
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            cart_selected = redis_conn.smembers('selected_%s' % user.id)
            # 将redis中的两个数据统一格式，跟cookie中的格式一致，方便统一查询
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in cart_selected
                }
        else:
            # 用户未登录，查询cookie购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

        # 构造简单购物车JSON数据
        cart_skus = []
        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict.get(sku.id).get('count'),
                'default_image_url': sku.default_image.url
            })

        # 响应json列表数据
        return JsonResponse({'code': 0, 'errmsg': 'OK', 'cart_skus': cart_skus})
