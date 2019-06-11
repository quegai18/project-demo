# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from django import forms
from django.conf import settings
from django.contrib.auth import hashers
from django.utils.module_loading import import_string
from django.core.exceptions import ValidationError
from web import models
from stark.service.start_assembly import BootstrapModelForms


UserModelClass = import_string(settings.RBAC_USER_MODEL_CLASS)


class StaffAddModelForm(BootstrapModelForms):
    """为添加员工操作单独设置的modelform"""
    confirm_password = forms.CharField(label="确认密码", widget=forms.PasswordInput)  # 多加一个确认密码字段

    class Meta:
        model = models.Staff
        fields = [
            "username",
            "password",
            "confirm_password",
            "name",
            "gender",
            "age",
            "phone",
            "email",
            "depart",
            "role",
        ]

    def clean_username(self):
        """局部钩子校验用户名是否存在"""
        username = self.cleaned_data["username"]
        if UserModelClass.objects.filter(username=username):
            raise ValidationError("用户名已被注册")
        else:
            return username

    def clean_confirm_password(self):
        """对用户两次输入的密码进行校验"""
        password = self.cleaned_data["password"]
        confirm_password = self.cleaned_data["confirm_password"]
        if confirm_password != password:
            raise ValidationError("两次密码输入不一致")
        else:
            return confirm_password

    def clean_password(self):
        password = self.cleaned_data["password"]
        if len(password) < 4:
            raise ValidationError("密码过于简短，请重新设置")
        else:
            return password

    def clean(self):
        """对用户密码进行加密"""
        password = hashers.make_password(self.cleaned_data["password"])
        self.cleaned_data["password"] = password
        return self.cleaned_data