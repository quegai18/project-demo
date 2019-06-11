from django import template
from django.conf import settings
from collections import OrderedDict
from rbac.service import basic_urls

register = template.Library()


"""
这是一级菜单时使用的
@register.inclusion_tag("static_menu.html")
def static_menu_func(request):
    一级菜单的inclution_tag功能
    current_url = request.path_info
    return {"menu_list": request.session.get(settings.MENU_SESSION_KEY), "current_url": current_url}
"""


@register.inclusion_tag("rbac/mulit_menu.html")
def mulit_menu_func(request):
    """二级菜单"""
    menu_dict = request.session.get(settings.MENU_SESSION_KEY)
    # 对字典的key进行排序，让它能做到一个有序字段
    key_list = sorted(menu_dict)
    # 创造一个空的有序字典
    ordered_dict = OrderedDict()
    # 按照key遍历字典，给每个val中加入一个键值对class=hide,默认隐藏2级菜单
    for key in key_list:
        val = menu_dict[key]
        val["class"] = "hide"
        for per in val["children"]:
            # 如果当前路径与遍历的2级权限列表相同，就给它加一个active的样式
            if per[0]["id"] == request.current_url_menu:
                per[0]["class"] = "active"
                val["class"] = ""
        ordered_dict[key] = val
    return {"menu_dict": ordered_dict}


@register.inclusion_tag("rbac/nav_menu.html")
def nav_menu_func(request):
    """动态导航条"""
    return {"nav_list": request.url_record}


@register.filter
def has_permissions(request, name):
    """复用过滤功能，判断一些按钮用户是否有权限去操作"""
    # 引用一个filter功能，最多两个参数，传参方法：{% if 参数一|has_permissions:"参数二" %}，参数二只能是字符串形式
    if name in request.session[settings.PERMISSION_SESSION_KEY]:
        return True


@register.simple_tag
def memory_url(request, name, *args, **kwargs):
    """
    用于保存原路径的GET数据，以便在新路径跳转回原路径时能携带上原路径的GET数据
    :param request: 用于获取request.GET中的数据
    :param name: url别名，用于反向生成url
    :param args: 要看自己写的url中是否有其他参数传入，例如{"pk":1}
    :param kwargs:
    :return:
    """
    return basic_urls.memory_url(request, name, *args, **kwargs)
