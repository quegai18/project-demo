# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com

from stark.service.start_assembly import BootstrapModelForms
from web.models import Customer


class PublicCustomerModelForm(BootstrapModelForms):
    """公共客户添加的modelform"""
    class Meta:
        model = Customer
        exclude = ["consultant"]


class PrivateCustomerModelForm(BootstrapModelForms):
    """我的客户添加的modelform"""
    class Meta:
        model = Customer
        exclude = ["consultant"]
