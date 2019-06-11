from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
import re


class RbacMiddleware(MiddlewareMixin):
    """这个自定义中间件用于检验当前用户的权限url是否支持访问"""
    def process_request(self, request):
        """
        当用户请求进来的时候触发执行代码
        :param request:
        :return:
        """
        """
        - 获取用户当前请求的url
        - session中获取当前用户的权限url-list
        - 只要匹配成功就OK
        """
        current_url = request.path_info                 # 获取当前的请求路径
        # 如果在白名单内，则不用匹配，直接放行
        for vaild_url in settings.VAILD_URL_LIST:
            if re.match(vaild_url, current_url):
                return None

        permisssions_url_dict = request.session.get(settings.PERMISSION_SESSION_KEY)
        url_record = [
            {"title": "首页", "url": "/index/"},
        ]
        if not permisssions_url_dict:
            """如果session里面的值为空，则肯定是当前用户没登录呢"""
            return redirect("/rbac/login/")
        else:
            """进入到这里就开始进行url匹配"""
            for url in settings.NO_PERMISSION_LIST:  # 读取需要登录但是不需要权限的所有URL
                if re.match(url, current_url):       # 如果匹配成功了
                    request.current_url_menu = 0    # 默认选中的二级菜单ID
                    request.url_record = url_record
                    return None

            flag = False
            for item in permisssions_url_dict.values():
                # 数据库中存的权限url都没有明确的结束符号，那么如果路径后缀其他内容的话也是可以通过的，要精准控制只能手动增加结束符号
                url = r"^{0}$".format(item["url"])
                if re.match(url, current_url):
                    flag = True
                    """
                    权限匹配成功后，就需要判断当前的权限是否是一个二级菜单
                        - 如果是，那需要返回它的ID，让inclution_tag直接选中它自己这个菜单就可以
                        - 如果不是，那需要返回它的PID，让inclution_tag根据PID选中对应的菜单
                    """
                    request.current_url_menu = item["pid"] or item["id"]
                    if not item["pid"]:
                        # (用于动态导航条的显示)有pid表示这是一个非菜单的权限
                        url_record.extend([{"title": item["title"], "url": item["url"], "class":"active"}])
                    else:
                        # 如果没有则是一个菜单权限
                        url_record.extend([
                            {"title": item["ptitle"], "url": item["purl"]},
                            {"title": item["title"], "url": item["url"], "class":"active"},
                        ])
                    request.url_record = url_record
                    break
            if not flag:
                return render(request, "rbac/refuse.html")




