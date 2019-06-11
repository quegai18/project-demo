# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com

from stark.service.start_assembly import StarkHandler,get_Many_to_Many_text, SearchOption
from django.conf.urls import url
from django.urls import reverse
from django.utils.safestring import mark_safe
from web.forms.studentform import StudentModelForm
from .base import PermissionHandler


class StudentHandler(PermissionHandler, StarkHandler):

    model_form_class = StudentModelForm

    has_add_btn = False

    def display_checkscore(self, obj=None, is_header=None):
        """为公共客户表新增一个查看客户跟进记录的功能"""
        if is_header:
            return "学分管理"
        # 这里进行别名拼接，用url的别名和路由分发的名称空间这两个值进行拼接
        # 这里进行拼接的namespace来自于StarkSite中的namespace属性
        nickname = "%s:%s" % (self.site.namespace, "web_scorerecord_list")  # 修改按钮的别名
        url = reverse(nickname, kwargs={"student_id": obj.pk})
        button = mark_safe("""<a target='_blank' href="{0}">{1}</a>""".format(url, obj.score))
        return button

    list_display = [
        "customer",
        "qq",
        "mobile",
        get_Many_to_Many_text("已报班级", "class_list"),
        display_checkscore,
        StarkHandler.get_choice_text("学员状态", "student_status"),
    ]

    search_list = ["customer__name", "qq", "mobile"]

    search_group = [SearchOption("class_list", text_func=lambda x: "%s-%s" % (x.school.title, str(x)))]

    def get_action_list(self):
        """
        获取自定义批量操作的钩子
        :return:
        """
        return []

    def get_urls(self):
        patterns = [
            url("^list/$", self.wapper(self.changelist_view), name=self.get_list_url_name),
            url("^edit/(?P<pk>\d+)/$", self.wapper(self.edit_view), name=self.get_edit_url_name),
            url("^del/(?P<pk>\d+)/$", self.wapper(self.delete_view), name=self.get_delete_url_name),
        ]
        patterns.extend(self.extra_urls())
        return patterns



