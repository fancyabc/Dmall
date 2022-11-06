import json
import re

# Create your views here.

from django.views import View
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate

from utils.views import LoginRequiredJSONMixin
from .models import User
from .utils import generic_email_verify_token, check_verify_token
from celery_tasks.email.tasks import celery_send_email


class UsernameCountView(View):
    """判断用户名是否重复注册"""
    def get(self, request, username):
        """
        :param request: 请求对象
        :param username: 用户名
        :return: JSON
        """
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code': 0, 'count': count, 'errmsg': 'ok'})


class MobileCountView(View):
    """判断手机号是否重复注册"""
    def get(self, request, mobile):
        """
        :param request: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        count = User.objects.filter(mobile=mobile).count()
        return JsonResponse({'code': 0, 'count': count, 'errmsg': 'ok'})


class RegisterView(View):
    """用户注册接口"""
    def post(self, request):
        # 1. 接收请求（POST------JSON）
        body_bytes = request.body
        body_str = body_bytes.decode()
        body_dict = json.loads(body_str)

        # 2. 获取数据
        username = body_dict.get('username')
        password = body_dict.get('password')
        password2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        allow = body_dict.get('allow')
        sms_code = body_dict.get('sms_code')    # 短信验证码

        # 3. 验证数据
        #     3.1 用户名，密码，确认密码，手机号，是否同意协议 都要有
        # all([xxx,xxx,xxx])
        # all里的元素 只要是 None,False
        # all 就返回False，否则返回True
        if not all([username, password, password2, mobile, allow]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})
        #     3.2 用户名满足规则，用户名不能重复
        if not re.match('[a-zA-Z_-]{5,20}', username):
            return JsonResponse({'code': 400, 'errmsg': '用户名不满足规则'})
        #     3.3 密码满足规则
        # 判断密码是否是8-20个字符
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return JsonResponse({'code': 400, 'errmsg': 'password格式有误!'})

        #     3.4 确认密码和密码要一致
        if password != password2:
            return JsonResponse({'code': 400, 'errmsg': '两次输入不对!'})
        #     3.5 手机号满足规则，手机号也不能重复
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400, 'errmsg': 'mobile格式有误!'})
        #     3.6 需要同意协议
        if not allow:
            return JsonResponse({'code': 400, 'errmsg': 'allow格式有误!'})
        #     3.7 短信验证码

        # 4. 数据入库
        # user=User(username=username,password=password,mobile=mobile)
        # user.save()

        # User.objects.create(username=username,password=password,mobile=mobile)
        # 以上2中方式，都是可以数据入库的
        # 但是 有一个问题 密码没有加密

        # 密码加密
        user = User.objects.create_user(username=username,password=password,mobile=mobile)

        # 状态保持 -- 登录用户的状态保持
        # user 已经登录的用户信息
        login(request, user)

        # 5. 返回响应
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        # 用户名写入到cookie
        response.set_cookie('username', user.username, max_age=3600*24*7)

        return response


class LoginView(View):

    def post(self, request):
        # 1. 接收数据
        data = json.loads(request.body.decode())
        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered')
        # 2. 验证数据
        if not all([username, password]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})

        # 根据手机号查询 还是 根据用户名查询 ?
        # USERNAME_FIELD 我们可以根据 修改 User. USERNAME_FIELD 字段
        # 来影响authenticate 的查询
        # authenticate 就是根据 USERNAME_FIELD 来查询
        if re.match('1[3-9]\d{9}', username):
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'

        # 3. 验证用户名和密码是否正确
        # 方式1 我们可以通过模型根据用户名来查询
        # User.objects.get(username=username)
        # 方式2
        # authenticate 传递用户名和密码
        # 如果用户名和密码正确，则返回 User信息
        # 如果用户名和密码不正确，则返回 None
        user = authenticate(username=username, password=password)

        if user is None:
            return JsonResponse({'code': 400, 'errmsg': '账号或密码错误'})

        # 4. session
        login(request, user)
        # 5. 判断是否记住登录
        if remembered:
            # 记住登录 具体多长时间 产品说了算
            request.session.set_expiry(None)

        else:
            # 不记住登录  浏览器关闭 session过期
            request.session.set_expiry(0)

        # 6. 返回响应
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie('username', username)
        return response


class LogoutView(View):
    """退出登录"""
    def get(self, request):
        """实现退出登录逻辑"""
        logout(request)     # 删除session信息
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.delete_cookie('username')  # 删除 cookie 信息
        return response


# LoginRequiredMixin 未登录的用户 会返回 重定向。重定向并不是JSON数据
class CenterView(LoginRequiredJSONMixin, View):
    def get(self,request):
        # request.user 就是 已经登录的用户信息
        # request.user 是来源于 中间件
        # 系统会进行判断 如果我们确实是登录用户，则可以获取到 登录用户对应的 模型实例数据
        # 如果我们确实不是登录用户，则request.user = AnonymousUser()  匿名用户
        info_data = {
            'username': request.user.username,
            'email': request.user.email,
            'mobile': request.user.mobile,
            'email_active': request.user.email_active,
        }

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'info_data': info_data})


class EmailView(View):

    def put(self, request):
        # 1. 接收请求
        data = json.loads(request.body.decode())
        # 2. 获取数据
        email = data.get('email')
        # 验证数据
        if not email:
            return JsonResponse({'code': 400,
                                      'errmsg': '缺少email参数'})
        # 正则　
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return JsonResponse({'code': 400,
                                      'errmsg': '参数email有误'})

        # 3. 保存邮箱地址
        user = request.user
        # user / request.user 就是登录用户的实例对象
        # user --> User
        user.email = email
        user.save()
        # 4. 发送一封激活邮件
        # subject,      主题
        subject = '天天商城激活邮件'
        # message,      邮件内容
        message = ""

        # from_email,   发件人
        from_email = '天天商城<m_fancy_ovo@163.com>'
        # recipient_list, 收件人列表
        recipient_list = ['2310403052@qq.com']
        token = generic_email_verify_token(request.user.id)
        verify_url = "http://www.Dmail.site:8080/success_verify_email.html?token=%s"%token

        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用天天商城。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)

        celery_send_email.delay(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message
        )

        # 5. 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})
