from django.views import View
from django.http import JsonResponse
from QQLoginTool.QQtool import OAuthQQ

from Dmall import settings


# 生成用户绑定链接
class QQLoginURLView(View):
    def get(self, request):
        # next表示从哪个页面进入到的登录页面，将来登录成功后，就自动回到那个页面
        next = request.GET.get('next')
        # 1. 生成 QQLoginTool 实例对象
        # client_id=None,               appid
        # client_secret=None,           appsecret
        # redirect_uri=None,            用户同意登录之后，跳转的页面
        # state=None                    不知道什么意思，随便写。等出了问题再分析问题
        qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)
        # 2. 调用对象的方法生成跳转链接
        qq_login_url = qq.get_qq_url()
        # 3. 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'login_url': qq_login_url})


#  获取code，通过code换取token，再通过token换取openid
class OauthQQView(View):
    """用户扫码登录的回调处理"""
    def get(self, request):
        # 1. 获取code
        code = request.GET.get('code')
        if code is None:
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})
        # 2. 通过code换取token
        qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                     client_secret=settings.QQ_CLIENT_SECRET,
                     redirect_uri=settings.QQ_REDIRECT_URI,
                     state='xxxxx')
        # '5D52C8BAB528D363DBCD3FC0CEDA0BA7'
        token = qq.get_access_token(code)
        # 3. 再通过token换取openid
        # 'CBCF1AA40E417CD73880666C3D6FA1D6'
        openid = qq.get_open_id(token)

        # 4. 根据openid进行查询判断
        try:    # 查看是否有 openid 对应的用户
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 5. 如果没有绑定过，则需要绑定
            response = JsonResponse({'code': 400, 'access_token': openid})
            return response
        else:
            # 6. 如果绑定过，则直接登录
            # 6.1 设置session
            login(request, qquser.user)
            # 6.2 设置cookie
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})

            response.set_cookie('username', qquser.user.username)

            return response
