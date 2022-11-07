from datetime import datetime, timedelta
from authlib.jose import jwt
from Dmall import settings

"""
问题:
    从itsdangerous（2.1.2）中调用TimedJSONWebSignatureSerializer时发现报错：cannot import name 'TimedJSONWebSignatureSerializer' from 'itsdangerous'
    跳转到代码中确实没有找到TimedJSONWebSignatureSerializer类。

解决思路:
    查看itsdangerous文档，发现该库在2.0.0版本之后就将TimedJSONWebSignatureSerializer类弃用了，
    引导用户使用直接支持JWS/JWT的库，如 authlib。

    所以，现在要么:
        1 使用2.0.0版本之前的itsdangerous库，继续使用该类，
        2 要么换用authlib库来生成token。( my choice )
"""


# 加密
def generate_openid(openid):
    header = {'typ': 'jwt', 'alg': 'HS256'}
    key = settings.SECRET_KEY
    data = {
        'openid': openid,
        'iat': datetime.utcnow(),
    }
    data['exp'] = data['iat'] + timedelta(seconds=3600)
    access_token = jwt.encode(header=header, payload=data, key=key)

    return access_token.decode()    # 将bytes类型的数据转换为 str


def check_access_token(token):
    key = settings.SECRET_KEY
    try:
        data = jwt.decode(token, key)
        data.validate()  # 检测token
    except Exception:
        return None
    return data.get('openid')
