import base64
import pickle
from django_redis import get_redis_connection

"""
需求：用户登录时，将cookie购物车数据合并到Redis购物车数据中。

1.合并方向：cookie购物车数据合并到Redis购物车数据中。
2.合并数据：购物车商品数据和勾选状态。
3.合并方案：
    3.1 Redis数据库中的购物车数据保留。
    3.2 如果cookie中的购物车数据在Redis数据库中已存在，将cookie购物车数据覆盖Redis购物车数据。
    3.3 如果cookie中的购物车数据在Redis数据库中不存在，将cookie购物车数据新增到Redis。
    3.4 最终购物车的勾选状态以cookie购物车勾选状态为准。
"""


def merge_cart_cookie_to_redis(request, user, response):
    """
    登录后合并cookie购物车数据到Redis
    :param request: 本次请求对象，获取cookie中的数据
    :param response: 本次响应对象，清除cookie中的数据
    :param user: 登录用户信息，获取user_id
    :return: response
    """
    # 获取cookie中的购物车数据
    cookie_cart = request.COOKIES.get('carts')
    # cookie中没有数据就响应结果
    if not cookie_cart:
        return response
    cookie_cart_dict = pickle.loads(base64.b64decode(cookie_cart.encode()))

    new_cart_dict = {}
    new_cart_selected_add = []
    new_cart_selected_remove = []
    # 同步cookie中购物车数据
    for sku_id, cookie_dict in cookie_cart_dict.items():
        new_cart_dict[sku_id] = cookie_dict['count']

        if cookie_dict['selected']:
            new_cart_selected_add.append(sku_id)
        else:
            new_cart_selected_remove.append(sku_id)

    # 将new_cart_dict写入到Redis数据库
    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()
    pl.hmset('carts_%s' % user.id, new_cart_dict)
    # 将勾选状态同步到Redis数据库
    if new_cart_selected_add:
        pl.sadd('selected_%s' % user.id, *new_cart_selected_add)
    if new_cart_selected_remove:
        pl.srem('selected_%s' % user.id, *new_cart_selected_remove)
    pl.execute()

    # 清除cookie
    response.delete_cookie('carts')

    return response
