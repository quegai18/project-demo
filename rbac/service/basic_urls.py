from django.urls import reverse
from django.http import QueryDict


def memory_reverse(request, name, *args, **kwargs):
    """
    这是放在视图里
    专门用来给反向解析的url携带上GET里面的数据
        例：http://127.0.0.1:8000/rbac/menu/edit/1/?_filter=mid%3D1
        - 在url中获取query_dict打包存入的数据
        - reverse反向解析生成url：/menu/list/
        - 对数据和url进行拼接
            /menu/list/?mid=1
    """
    url = reverse(name, args=args, kwargs=kwargs)  # 反向解析路径
    GET_data = request.GET.get("_filter")  # 获取原来url中的GET数据
    if GET_data:  # 如果有，进行字段拼接，返回新路径
        url = "%s?%s" % (url, GET_data)  # 把GET数据和url进行拼接
    return url


def memory_url(request, name, *args, **kwargs):
    """
    这是放在模板里
    用于保存原路径的GET数据，以便在新路径跳转回原路径时能携带上原路径的GET数据
    :param request: 用于获取request.GET中的数据
    :param name: url别名，用于反向生成url
    :param args: 要看自己写的url中是否有其他参数传入，例如{"pk":1}
    :param kwargs:
    :return:
    """
    basic_url = reverse(name, args=args, kwargs=kwargs)  # 先反向解析生成新的url
    if not request.GET:  # 当前路径中没有GET数据
        return basic_url
    GET_data = request.GET.urlencode()  # 获取GET中的所有数据
    # from django.http import QueryDict 需要引入
    query_dict = QueryDict(mutable=True)  # 实例化一个特殊的字典
    query_dict["_filter"] = GET_data  # 打包存入GET数据
    # query_dict.urlencode() 进行数据转译，防止造成"/menu/add/_filter=mid=1"这样改变结构的数据，而应该是"/menu/add/_filter=‘mid=1’"
    # 对反向解析的路径与GET数据进行拼接，做成新的url
    return "%s?%s" % (basic_url, query_dict.urlencode())
