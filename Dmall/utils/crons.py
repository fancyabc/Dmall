import time
import os

from django.template import loader

from utils.goods import get_categories
from contents.models import ContentCategory
from Dmall import settings


# 这个函数 能够帮助我们 数据库查询，渲染HTML页面，然后把渲染的HTML写入到指定文件
def generate_static_index():
    print('%s: generate_static_index_html' % time.ctime())
    # 1 数据库查询
    categories = get_categories()
    contents = {}
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')
    context = {
        'categories': categories,
        'contents': contents,
    }
    # 2. 加载渲染的模板
    index_template = loader.get_template('index.html')
    # 3. 把数据给模板
    index_html_data = index_template.render(context)
    # 4. 把渲染好的HTML，写入到指定文件
    # base_dir 的上一级
    file_path = os.path.join(os.path.dirname(settings.BASE_DIR), 'front_end_pc/index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(index_html_data)