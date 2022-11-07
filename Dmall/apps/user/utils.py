from datetime import datetime, timedelta
from authlib.jose import jwt
from Dmall import settings


# 加密
def generic_email_verify_token(user_id):
    header = {'typ': 'jwt', 'alg': 'HS256'}
    key = settings.SECRET_KEY
    data = {
        'user_id': user_id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(seconds=3600*24),
    }
#    data['exp'] = data['iat'] + timedelta(seconds=3600*24)
    token = jwt.encode(header=header, payload=data, key=key)

    return token.decode()    # 将bytes类型的数据转换为 str


def check_verify_token(token):
    key = settings.SECRET_KEY
    try:
        data = jwt.decode(token, key)
        data.validate()  # 检测token
    except Exception:
        return None
    return data.get('user_id')
