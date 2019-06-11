# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth import hashers
from stark.service.start_assembly import BootstrapModelForms
from web.models import Staff


class ResetPWDModelForm(BootstrapModelForms):
    """
    专门用来重置用户密码的modelform
    """
    password = forms.CharField(label="重置密码", widget=forms.PasswordInput)
    r_pwd = forms.CharField(label="确认重置密码", widget=forms.PasswordInput)

    class Meta:
        """进行字段的自定制"""
        model = Staff
        fields = ["password", "r_pwd"]

    def clean_r_pwd(self):
        """局部钩子校验两次密码是否一致"""
        password = self.cleaned_data["password"]
        r_pwd = self.cleaned_data["r_pwd"]
        if password != r_pwd:
            raise ValidationError("两次密码不一致")
        else:
            return password

    def clean(self):
        """对用户密码进行加密"""
        password = hashers.make_password(self.cleaned_data["password"])
        self.cleaned_data["password"] = password
        return self.cleaned_data


