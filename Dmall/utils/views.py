from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse


# LoginRequiredMixin 未登录的用户 会返回 重定向。重定向并不是JSON数据
# 我们需要是  返回JSON数据
class LoginRequiredJSONMixin(LoginRequiredMixin):
    """对handle_no_permission方法进行重写, 使其返回json格式数据"""
    def handle_no_permission(self):
        return JsonResponse({'code': 400, 'errmsg': '没有登录'})
