# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.shortcuts import render, HttpResponse
from django.db import transaction
from stark.service.start_assembly import StarkHandler
from stark.service.start_assembly import get_datetime_text
from stark.service.start_assembly import get_Many_to_Many_text
from web.forms.addpubliccustomerform import PublicCustomerModelForm
from web.models import ConsultRecord
from web.models import Customer
from .base import PermissionHandler


class PunlicCustomerHandler(PermissionHandler, StarkHandler):

    def get_queryset(self, request, *args, **kwargs):
        return self.model_class.objects.filter(consultant__isnull=True)

    model_form_class = PublicCustomerModelForm

    @property
    def get_checkrecord_url_name(self):
        """获取客户跟踪记录的路由别名"""
        return self.get_url_name("checkrecord")

    def display_checkrecord(self, obj=None, is_header=None, *args, **kwargs):
        """为公共客户表新增一个查看客户跟进记录的功能"""
        if is_header:
            return "查看跟进记录"
        # 这里进行别名拼接，用url的别名和路由分发的名称空间这两个值进行拼接
        # 这里进行拼接的namespace来自于StarkSite中的namespace属性
        nickname = "%s:%s" % (self.site.namespace, self.get_checkrecord_url_name)  # 修改按钮的别名
        url = StarkHandler.memory_url(self.request, nickname, *[obj.pk])
        # 这里放了编辑和修改两个按钮
        button = mark_safe("""<a href="{0}">点击查看</a>""".format(url))
        return button

    def checkRecord_view(self, request, pk, *args, **kwargs):
        """查看跟踪记录"""
        current_customer_record_queryset = ConsultRecord.objects.filter(customer__id=pk)
        if not current_customer_record_queryset:
            return render(request, "rbac/refuse.html", {"error_msg": "当前客户跟踪记录为空"})
        return render(request, "recordview.html", {"record_list":current_customer_record_queryset})

    def extra_urls(self):
        """为查看跟踪记录功能添加一个url"""
        patterns = [
            url("^checkrecord/(?P<pk>\d+)/$", self.wapper(self.checkRecord_view), name=self.get_checkrecord_url_name),
        ]
        return patterns

    list_display = [
        StarkHandler.display_checkbox,
        "name",
        "qq",
        get_Many_to_Many_text("咨询课程", "course"),
        get_datetime_text("咨询日期", "date"),
        display_checkrecord,
    ]

    def multi_apply_to_private(self, request, *args, **kwargs):
        """用于添加一个批量添加到私人客户的选项,"""
        pk_list = request.POST.getlist("pk")                                # 通过getlist把页面传来的所有被选中的数据ID都获取到
        private_customer_count = Customer.objects.filter(id=request.user.pk, status=2).count()          # 取出当前销售员的私户数量
        if private_customer_count + len(pk_list) > Customer.MAX_PRIVATE_CUSTOMER_COUNT:
            return HttpResponse("当前未成单的客户有%s人，还可以申请的私户数量：%s" % (private_customer_count, Customer.MAX_PRIVATE_CUSTOMER_COUNT - private_customer_count))
        # 这里为了极限情况下的同时操作，需要在数据库中加锁
        flag = False
        with transaction.atomic():          # 事务
            origin_queryset = Customer.objects.filter(id__in=pk_list, status=2, consultant__isnull=True).select_for_update()    # 在数据库中加锁
            if len(origin_queryset) == len(pk_list):            # 必须要让数据库中记录的个数和前端提交来的ID个数要相等
                Customer.objects.filter(id__in=pk_list, status=2, consultant__isnull=True).update(consultant=request.user.pk)
                flag = True
        if not flag:
            return HttpResponse("选中的客户已经被人抢走啦！")

    multi_apply_to_private.text = "批量添加到我的客户"

    action_list = [multi_apply_to_private, StarkHandler.multi_delete]


