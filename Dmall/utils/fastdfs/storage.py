"""
1 你自定义的存储系统必须为 Django.core.files.storage.Storage 的一个子类:
2 Django 必须能以无参数实例化你的存储系统。我们在创建存储类的时候，不传递任何参数
    意味着所有配置都应从 django.conf.settings 配置中获取:
3 在你的存储类中，除了其他自定义的方法外，还必须实现 _open() 以及 _save() 等其他适合你的存储类的方法。
"""


from django.core.files.storage import Storage


class MyStorage(Storage):
    def _open(self, name, mode='rb'):
        """Retrieve the specified file from storage."""
        pass

    def _save(self, name, content, max_length=None):
        """用于保存文件"""
        pass

    def url(self, name):
        return "http://192.168.25.5:8888/" + name
