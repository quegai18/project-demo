# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
"""权限粒度控制到按钮的校验"""
from django.conf import settings
from django.utils.safestring import mark_safe
from stark.service.start_assembly import StarkHandler


class PermissionHandler(object):

    def get_add_btn(self, request, *args, **kwargs):
        if self.has_add_btn:
            # 别名需要手动拼接namespace:name
            name = "%s:%s" % (self.site.namespace, self.get_add_url_name)
            add_url = StarkHandler.memory_url(self.request, name, *args, **kwargs)
            # 看看用户是否有添加数据的权限，有权限再显示按钮
            permisssions_url_dict = request.session.get(settings.PERMISSION_SESSION_KEY)
            if self.get_add_url_name not in permisssions_url_dict:
                return None
            add_btn = mark_safe("""
            <a class="btn btn-default" class="margin-right:20px;" href="%s">
                <i class="fa fa-plus-square" aria-hidden="true"></i> 添加数据
            </a>
            """ %(add_url))
            return add_btn
        return None

    def get_list_display(self, request, *args, **kwargs):
        value = []
        permisssions_url_dict = request.session.get(settings.PERMISSION_SESSION_KEY)
        if self.list_display:
            value.extend(self.list_display)
            if self.get_edit_url_name in permisssions_url_dict and self.get_delete_url_name in permisssions_url_dict:
                value.append(type(self).display_operation)
        return value





