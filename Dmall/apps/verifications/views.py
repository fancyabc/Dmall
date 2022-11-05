from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

# Create your views here.
from django.views import View


class ImageCodeView(View):
    """图形验证码"""

    def get(self, request, uuid):
        """
        :param request: 请求对象
        :param uuid: 唯一标识图形验证码所属于的用户
        :return: image/jpeg
        """
        from libs.captcha.captcha import captcha
        text, image = captcha.generate_captcha()

        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('code')

        redis_cli.setex(uuid, 100, text)

        # 因为图片是二进制 我们不能返回JSON数据
        # content_type=响应体数据类型
        # content_type 的语法形式是： 大类/小类
        # content_type (MIME类型)
        # 图片： image/jpeg , image/gif, image/png
        return HttpResponse(image, content_type='image/jpeg')


class SmsCodeView(View):
    def get(self, request, mobile):
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        if not all([image_code, uuid]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})

        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('code')

        redis_image_code = redis_cli.get(uuid)  # 获取redis数据
        if redis_image_code is None:
            return JsonResponse({'code': 400, 'errmsg': '图片验证码已过期'})

        if redis_image_code.decode().lower() != image_code.lower():
            return JsonResponse({'code': 400, 'errmsg': '图片验证码错误'})

        # 生成短信验证码
        from random import randint
        sms_code = '%06d' % randint(0, 999999)
        redis_cli.setex(mobile, 300, sms_code)

        from libs.yuntongxun.sms import CCP
        CCP().send_template_sms(mobile, [sms_code, 5], 1)

        return JsonResponse({'code': 0, 'errmsg': 'ok'})
