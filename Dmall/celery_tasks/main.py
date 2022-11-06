
# 0. 为celery的运行 设置Django的环境
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dmall.settings')

# 1. 创建celery实例
# 参数1： main 设置脚本路径就可以了。 脚本路径是唯一的
app = Celery('celery_tasks')

# 2. 设置broker
# 我们通过加载配置文件来设置broker
app.config_from_object('celery_tasks.config')

# 3.需要celery 自动检测指定包的任务
# autodiscover_tasks 参数是列表
# 列表中的元素是 tasks的路径
app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])
