# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from django import forms
from stark.service.start_assembly import BootstrapModelForms
from web.models import PaymentRecord


class PayementRecordModelForm(BootstrapModelForms):

    class Meta:
        model = PaymentRecord
        fields = ["pay_type", "paid_fee", "class_list", "note", ]


class NewStudentPayementRecordModelForm(BootstrapModelForms):

    qq = forms.CharField(label="QQ号", max_length=32)
    mobile = forms.CharField(label="手机号", max_length=32)
    emergency_contract = forms.CharField(label="紧急联系人", max_length=32)

    class Meta:
        model = PaymentRecord
        fields = ["pay_type", "paid_fee", "class_list", "qq", "mobile", "emergency_contract", "note", ]

