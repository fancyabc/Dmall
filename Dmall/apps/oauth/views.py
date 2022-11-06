import json

from django.views import View
from django.http import JsonResponse
from django.contrib.auth import login
from QQLoginTool.QQtool import OAuthQQ

from Dmall import settings
from .models import OAuthQQUser
from user.models import User


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

    def post(self, request):
        """用户绑定到openid"""

        # 1. 接收请求
        data = json.loads(request.body.decode())
        # 2. 获取请求参数  openid
        mobile = data.get('mobile')
        password = data.get('password')
        sms_code = data.get('sms_code')
        openid = data.get('access_token')

        # 需要对数据进行验证（省略）

        if openid is None:
            return JsonResponse({'code': 400, 'errmsg': '参数缺失'})

        # 3. 根据手机号进行用户信息的查询
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 手机号不存在
            # 查询到用户手机号没有注册。我们就创建一个user信息。然后再绑定
            user = User.objects.create_user(username=mobile, mobile=mobile, password=password)

        else:
            # 手机号存在
            # 4. 查询到用户手机号已经注册了。判断密码是否正确。密码正确就可以直接保存（绑定） 用户和openid信息
            if not user.check_password(password):
                return JsonResponse({'code': 400, 'errmsg': '账号或密码错误'})

        OAuthQQUser.objects.create(user=user, openid=openid)

        # 6. 完成状态保持
        login(request, user)
        # 7. 返回响应
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})

        response.set_cookie('username', user.username)

        return response
