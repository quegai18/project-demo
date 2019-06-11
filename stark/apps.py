from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules
"""
此处设置了项目启动前的自动发现功能，在路由分发之前获取项目中所有的URL并添加到urlpatterns中
所有需要被提前获取的文件都必须统一命名为"start_assembly.py"
"""


class StarkConfig(AppConfig):
    name = 'stark'

    def ready(self):
        autodiscover_modules("stark")
