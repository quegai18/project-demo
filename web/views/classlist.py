# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from django.urls import reverse
from django.utils.safestring import mark_safe
from stark.service.start_assembly import StarkHandler
from stark.service.start_assembly import SearchOption
from stark.service.start_assembly import get_datetime_text
from stark.service.start_assembly import get_Many_to_Many_text
from web.forms.classlistform import ClasslistModelForm
from .base import PermissionHandler


class ClassListHandler(PermissionHandler, StarkHandler):

    def display_courserecord(self, obj=None, is_header=None):
        """为公共客户表新增一个查看客户跟进记录的功能"""
        if is_header:
            return "上课记录"
        # 这里进行别名拼接，用url的别名和路由分发的名称空间这两个值进行拼接
        # 这里进行拼接的namespace来自于StarkSite中的namespace属性
        nickname = "%s:%s" % (self.site.namespace, "web_courserecord_list")  # 修改按钮的别名
        url = reverse(nickname, kwargs={"class_id": obj.pk})
        button = mark_safe("""<a target='_blank' href="{0}">查看记录</a>""".format(url))
        return button

    def display_course(self, obj=None, is_header=None):
        if is_header:
            return "班级"
        return "%s(%s)期" % (obj.course, obj.semester)

    list_display = [
        StarkHandler.display_checkbox,
        "school",
        display_course,
        "price",
        "tutor",
        get_Many_to_Many_text("任课老师", "teacher"),
        get_datetime_text("开班日期", "start_date"),
        display_courserecord,
    ]

    search_group = [  # 配置进行组合搜索的字段，默认为空
        SearchOption("school", is_multi=True),  # 这是都用默认设置的展示(基本足够了)，is_choices设置该字段是否支持多选
        SearchOption("course", is_multi=True),  # 这里就是举例带条件(要求ID大于5)的去获取进行组合搜索字段的数据
    ]

    model_form_class = ClasslistModelForm
