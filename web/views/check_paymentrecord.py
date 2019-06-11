# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from stark.service.start_assembly import StarkHandler,get_datetime_text
from django.conf.urls import url
from web.models import Student
from .base import PermissionHandler


class CheckPaymentRecordHandler(PermissionHandler, StarkHandler):

    order_list = ["confirm_status", "-id"]

    has_add_btn = False

    def multi_confirm(self, request, *args, **kwargs):
        """批量审核确认功能"""
        confirm_list = request.POST.getlist("pk")
        for pk in confirm_list:
            payment_obj = self.model_class.objects.filter(id=pk, confirm_status=1).first()                # 拿到缴费记录
            if not payment_obj:continue
            payment_obj.confirm_status = 2                                              # 缴费状态变成已确认
            payment_obj.save()

            payment_obj.customer.status = 1                                             # 变更客户表中的状态
            payment_obj.customer.save()

            customer_id = payment_obj.customer.id
            student_obj = Student.objects.filter(customer_id=customer_id).first()
            student_obj.student_status = 2                             # 变更学员表中的状态
            student_obj.save()

    multi_confirm.text = "批量审核确认"

    def multi_reject(self, request, *args, **kwargs):
        """批量审核驳回"""
        reject_list = request.POST.getlist("pk")
        self.model_class.objects.filter(id__in=reject_list, confirm_status=1).update(confirm_status=3)

    multi_reject.text = "批量审核驳回"

    list_display = [
        StarkHandler.display_checkbox,
        "customer",
        "consultant",
        StarkHandler.get_choice_text("费用类型", "pay_type"),
        "paid_fee",
        "class_list",
        get_datetime_text("申请日期","apply_date"),
        StarkHandler.get_choice_text("确认状态", "confirm_status"),
        "note",
    ]

    def get_list_display(self, request, *args, **kwargs):
        """
        开发者可以根据用户的不同在'Model'Handler类中通过复写(get_list_display)方法来控制页面上应该显示的列
        这个跟'Model'Handler类复写list_display不影响，因为get_list_display方法是根据用户不同来控制的，里面还有控制的逻辑
        :return:
        """
        value = []
        if self.list_display:
            value.extend(self.list_display)
        return value

    def get_action_list(self):
        """
        获取自定义批量操作的钩子
        :return:
        """
        return [self.multi_confirm, self.multi_reject,]

    def get_urls(self):
        patterns = [
            url("^list/$", self.wapper(self.changelist_view), name=self.get_list_url_name),
        ]
        patterns.extend(self.extra_urls())
        return patterns



