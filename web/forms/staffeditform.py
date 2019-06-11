# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from web import models
from stark.service.start_assembly import BootstrapModelForms


class StaffEditModelForm(BootstrapModelForms):
    """为员工信息修改功能单独设置的modelform"""

    class Meta:
        model = models.Staff
        fields = [
            "username",
            "name",
            "gender",
            "age",
            "phone",
            "email",
            "depart",
            "role",
        ]
