from django.shortcuts import render

# Create your views here.
from fdfs_client.client import Fdfs_client

# 1. 创建客户端
# 修改加载配置文件的路径
client=Fdfs_client('utils/fastdfs/client.conf')
#
# # 2. 上传图片
# # 图片的绝对路径
client.upload_by_filename('/home/fan/Desktop/img/c.png')