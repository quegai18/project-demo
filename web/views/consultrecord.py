# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from stark.service.start_assembly import StarkHandler
from django.conf.urls import url
from django.shortcuts import render
from django.utils.safestring import mark_safe
from web.forms.consultrecordform import ConsultRecordModelForm
from web.models import Customer
from web.models import ConsultRecord
from .base import PermissionHandler


class ConsultrecordHandler(PermissionHandler, StarkHandler):

    change_list_template = "consultrecord.html"

    model_form_class = ConsultRecordModelForm

    def display_operation(self, obj=None, is_header=None, *args, **kwargs):
        """
        这里可以写上业务逻辑来根据用户的权限高低判断需要是否需要展示页面中的修改删除按钮
        :param obj:每一行的记录对象
        :param is_header:用于判断是放在表头还是在表内
        :return:mark_safe(字符串格式的标签) 或者其他内容
        """
        if is_header:                   # 如果这是是True，就表示这是对表头进行的编辑
            return "操作"
        else:                           #这表示对行内进行编辑
            # 这里进行别名拼接，用url的别名和路由分发的名称空间这两个值进行拼接
            # 这里进行拼接的namespace来自于StarkSite中的namespace属性
            edit_name = "%s:%s" %(self.site.namespace, self.get_edit_url_name)              # 修改按钮的别名
            delete_name = "%s:%s" %(self.site.namespace, self.get_delete_url_name)          # 删除按钮的别名
            customer_id = kwargs.get("customer_id")
            edit_url = StarkHandler.memory_url(self.request, edit_name, **{"customer_id": customer_id, "pk": obj.pk},)
            delete_url = StarkHandler.memory_url(self.request, delete_name, **{"customer_id": customer_id, "pk": obj.pk},)
            # 这里放了编辑和修改两个按钮
            button = mark_safe("""
                <a style="color: #333333;" href="{0}">
                    <i class="fa fa-edit" aria-hidden="true"></i></a>
                |
                <a style="color: #d9534f;" href="{1}"><i
                        class="fa fa-trash-o"></i></a>
            """.format(edit_url, delete_url))
            return button

    list_display = [
        "customer",
        "consultant",
        "date",
        "note",
    ]

    def get_urls(self):
        patterns = [
            url(r"^list/(?P<customer_id>\d+)/$", self.wapper(self.changelist_view), name=self.get_list_url_name),
            url(r"^add/(?P<customer_id>\d+)/$", self.wapper(self.add_view), name=self.get_add_url_name),
            url(r"^edit/(?P<customer_id>\d+)/(?P<pk>\d+)/$", self.wapper(self.edit_view), name=self.get_edit_url_name),
            url(r"^del/(?P<customer_id>\d+)/(?P<pk>\d+)/$", self.wapper(self.delete_view), name=self.get_delete_url_name),
        ]
        patterns.extend(self.extra_urls())
        return patterns

    def get_queryset(self, request, *args, **kwargs):
        customer_id = int(kwargs.get("customer_id"))
        query_set = self.model_class.objects.filter(customer=customer_id,customer__consultant_id=request.user.pk)
        return query_set

    def save(self, request, form, is_update, *args, **kwargs):
        customer_id = kwargs.get("customer_id")
        # 还要判断一下当前这个跟进记录的客户是不是在当前登录的这个销售员的私户内
        object_exists = Customer.objects.filter(id=customer_id, consultant_id=request.user.pk).exists()
        if not object_exists:
            # return render(request, "rbac/refuse.html", {"error_msg":"违规操作：这个客户还不属于你的私人客户！"})
            return render(request, "rbac/refuse.html", {"error_msg":"违规操作：这个客户还不是你的私人客户，无法添加跟进记录！"})
        if not is_update:
            form.instance.consultant_id = request.user.pk
            form.instance.customer_id = customer_id
        form.save()

    def get_edit_object(self, request, pk, *args, **kwargs):
        """方便扩展修改功能的数据校验"""
        customer_id = kwargs.get("customer_id")
        return ConsultRecord.objects.filter(id=pk, customer_id=customer_id, customer__consultant_id=request.user.pk).first()

    def delete_object(self, request, pk, *args, **kwargs):
        customer_id = kwargs.get("customer_id")
        return self.model_class.objects.filter(id=pk, customer_id=customer_id)


