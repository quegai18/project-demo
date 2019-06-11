# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from stark.service.start_assembly import StarkHandler
from django.utils.safestring import mark_safe
from django.urls import reverse
from stark.service.start_assembly import get_datetime_text
from stark.service.start_assembly import get_Many_to_Many_text
from web.forms.addpubliccustomerform import PrivateCustomerModelForm
from .base import PermissionHandler


class PrivateCustomerHandler(PermissionHandler, StarkHandler):

    model_form_class = PrivateCustomerModelForm

    def save(self, request, form, is_update, *args, **kwargs):
        if not is_update:
            form.instance.consultant_id = request.user.pk
        form.save()

    def display_checkrecord(self, obj=None, is_header=None, *args, **kwargs):
        """为公共客户表新增一个查看客户跟进记录的功能"""
        if is_header:
            return "跟进记录"
        # 这里进行别名拼接，用url的别名和路由分发的名称空间这两个值进行拼接
        # 这里进行拼接的namespace来自于StarkSite中的namespace属性
        nickname = "%s:%s" % (self.site.namespace, "web_consultrecord_list")  # 修改按钮的别名
        url = reverse(nickname, kwargs={"customer_id": obj.pk})
        # 这里放了编辑和修改两个按钮
        button = mark_safe("""<a target='_blank' href="{0}">点击查看</a>""".format(url))
        return button

    def display_checkpayment(self, obj=None, is_header=None, *args, **kwargs):
        """为公共客户表新增一个查看客户缴费记录的功能"""
        if is_header:
            return "缴费操作"
        # 这里进行别名拼接，用url的别名和路由分发的名称空间这两个值进行拼接
        # 这里进行拼接的namespace来自于StarkSite中的namespace属性
        nickname = "%s:%s" % (self.site.namespace, "web_paymentrecord_list")  # 修改按钮的别名
        url = reverse(nickname, kwargs={"customer_id": obj.pk})
        # 这里放了编辑和修改两个按钮
        button = mark_safe("""<a target='_blank' href="{0}">点击查看</a>""".format(url))
        return button

    list_display = [
        StarkHandler.display_checkbox,
        "name",
        "qq",
        StarkHandler.get_choice_text("客户状态", "status"),
        get_Many_to_Many_text("咨询课程", "course"),
        get_datetime_text("咨询日期", "date"),
        get_datetime_text("最后跟进日期", "last_consult_date"),
        display_checkrecord,
        display_checkpayment,
    ]

    def get_queryset(self, request, *args, **kwargs):
        """获取当前销售员私户内的客户列表"""
        return self.model_class.objects.filter(consultant=request.user.pk)

    def multi_apply_to_public(self, request, *args, **kwargs):
        """批量移除到公户,"""
        pk_list = request.POST.getlist("pk")                                # 通过getlist把页面传来的所有被选中的数据ID都获取到
        self.model_class.objects.filter(id__in=pk_list, status=2, consultant=request.user.pk).update(consultant=None)

    multi_apply_to_public.text = "批量移除到公共客户"

    action_list = [multi_apply_to_public, ]



