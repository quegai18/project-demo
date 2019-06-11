# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from django import forms


class DateTimeInput(forms.TextInput):
    template_name = "rbac/datetime_picker.html"

