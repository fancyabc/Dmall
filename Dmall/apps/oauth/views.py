from django.views import View
from django.http import JsonResponse
from QQLoginTool.QQtool import OAuthQQ

from Dmall import settings


class QQLoginURLView(View):
    def get(self, request):
        # 1. 生成 QQLoginTool 实例对象
        # client_id=None,               appid
        # client_secret=None,           appsecret
        # redirect_uri=None,            用户同意登录之后，跳转的页面
        # state=None                    不知道什么意思，随便写。等出了问题再分析问题
        qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state='xxxxx')
        # 2. 调用对象的方法生成跳转链接
        qq_login_url = qq.get_qq_url()
        # 3. 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'login_url': qq_login_url})