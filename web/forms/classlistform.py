# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from rbac.forms.widgets.datetime_picker import DateTimeInput
from stark.service.start_assembly import BootstrapModelForms
from web.models import ClassList


class ClasslistModelForm(BootstrapModelForms):
    class Meta:
        model = ClassList
        fields = "__all__"
        widgets = {
            # 这两个表示日期的字段使用了我自定义的时间插件(基于bootstrap)，其他地方的字段如果也想这样显示只要像下面这样写就OK
            "start_date":DateTimeInput,
            "graduate_date": DateTimeInput,
        }

