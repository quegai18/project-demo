from collections import OrderedDict
from django.utils.module_loading import import_string
from django.urls import URLPattern
from django.urls import URLResolver
from django.conf import settings
import re


def check_exclude(url):
    """
    针对已经获取到的所有的url进行检查，除去不相关的，只留下跟权限有关的
    :param dict:
    :return:
    """
    exclude_url = settings.EXCLUDE_URL
    for key in exclude_url:
        if re.match(key, url):
            return True


def recursion_urls(pre_namespace, pre_url, urlpatterns, url_ordered_dict):
    """
    用于递归获取所有的url
    :param pre_namespace: 路由分发的namespace的前缀，用于拼接反向解析的name
    :param pre_url: url的前缀，用于拼接url
    :param urlpatterns: 递归的路由关系列表
    :param url_ordered_dict: 用于保存递归中获取的所有路由
    :return:
    """
    for item in urlpatterns:
        if isinstance(item, URLPattern):   # 如果成立就是一个非路由分发，将路由添加到字典中
            if not item.name:              # 如果这个路由没有name就直接跳过
                continue
            if pre_namespace:              # 如果这个路由别名有前缀，就进行字符串拼接，拼接出可以直接反解的路由别名
                name = "%s:%s" % (pre_namespace, item.name)
            else:
                name = item.name           # 如果没有前缀，就直接等于别名
            url = pre_url + str(item.pattern)
            url = url.replace("^", "").replace("$", "")
            if check_exclude(url):    # 如果跟权限没关系的，就给他排除，如果有关系就存进字典
                continue
            else:
                url_ordered_dict[name] = {"name": name, "url": url}
        elif isinstance(item, URLResolver):       # 这是一个路由分发，需要继续递归往下找
            if pre_namespace:              # 如果这个路由分发还有前缀，接着要看自己有没有前缀，有就需要进行手动拼接，没有就用之前的前缀
                if item.namespace:
                    namespace = "%s:%s" % (pre_namespace, item.namespace)
                else:
                    namespace = item.namespace
            else:
                if item.namespace:     # 这表示父级有namespace
                    namespace = item.namespace
                else:                  # 如果父级也没有，自己也没有，就用自己的name就行了
                    namespace = None
            recursion_urls(namespace, pre_url + str(item.pattern), item.url_patterns, url_ordered_dict)


def get_all_url_dict():
    """
    获取当前项目中的所有URL,别名,反向解析自动拼接namespace
    url_ordered_dict = {
        "rbac:menu_list":{
            name:"rbac:menu_list",
            url:"/rbac/menu_list/",
        }
    }
    这个功能要求必须给url设置别名，不然就没法用
    :return:
    """
    url_ordered_dict = OrderedDict()
    # settings.ROOT_URLCONF 是Django配置的根路由的路径
    md = import_string(settings.ROOT_URLCONF)         # 根据字符串形式导入模块
    recursion_urls(pre_namespace=None, pre_url="/", urlpatterns=md.urlpatterns, url_ordered_dict=url_ordered_dict)
    return url_ordered_dict
