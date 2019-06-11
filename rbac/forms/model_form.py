from django import forms
from rbac import models
from django.core.exceptions import ValidationError
from rbac.static.rbac import icon
from django.conf import settings
from django.utils.module_loading import import_string

"""
目录
    BootstrapModelForms：用于统一定制每个forms组件的html样式
    RoleMoedelForm：利用modelform来控制表，可以读可以新增"
    UserModelForm：利用modelform来控制表，可以读可以新增
    UpdateUserModelForm：专门用来重置用户信息的modelform
    ResetPWDModelForm：专门用来重置用户密码的modelform
    MenuMoedelForm：一级菜单新增功能的forms组件
    PermissionsModelForm：权限菜单的form组件
    SecondMenuModelForm：二级菜单的form组件
"""
UserModelClass = import_string(settings.RBAC_USER_MODEL_CLASS)


class BootstrapModelForms(forms.ModelForm):
    """
    用于统一定制每个forms组件的html样式
    """
    def __init__(self, *args, **kwargs):
        super(BootstrapModelForms, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "icon": continue
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs["style"] = "width: 300px;"


class RoleMoedelForm(BootstrapModelForms):
    """利用modelform来控制表，可以读可以新增"""

    class Meta:
        """进行字段的自定制"""
        model = models.Role
        fields = ["title", ]


class UserModelForm(BootstrapModelForms):
    """
    利用modelform来控制表，可以读可以新增
    """
    r_pwd = forms.CharField(label="确认密码")

    class Meta:
        """进行字段的自定制"""
        model = UserModelClass
        fields = ["username", "password", "email", "r_pwd"]

    def clean_username(self):
        """局部钩子校验用户名是否存在"""
        username = self.cleaned_data["username"]
        if UserModelClass.objects.filter(username=username):
            raise ValidationError("用户名已被注册")
        else:
            return username

    def clean_r_pwd(self):
        """局部钩子校验两次密码是否一致"""
        password = self.cleaned_data["password"]
        r_pwd = self.cleaned_data["r_pwd"]
        if password != r_pwd:
            raise ValidationError("两次密码不一致")
        else:
            return r_pwd


class UpdateUserModelForm(BootstrapModelForms):
    """
    专门用来重置用户信息的modelform
    """

    class Meta:
        """进行字段的自定制"""
        model = UserModelClass
        fields = ["username", "email"]


class ResetPWDModelForm(BootstrapModelForms):
    """
    专门用来重置用户密码的modelform
    """
    password = forms.CharField(label="重置密码")
    r_pwd = forms.CharField(label="确认重置密码")

    class Meta:
        """进行字段的自定制"""
        model = UserModelClass
        fields = ["password", "r_pwd"]

    def clean_r_pwd(self):
        """局部钩子校验两次密码是否一致"""
        password = self.cleaned_data["password"]
        r_pwd = self.cleaned_data["r_pwd"]
        if password != r_pwd:
            raise ValidationError("两次密码不一致")
        else:
            return password


class MenuMoedelForm(BootstrapModelForms):
    """
    一级菜单新增功能的forms组件
    """

    class Meta:
        """进行字段的自定制"""
        model = models.Menu
        fields = ["title", "icon"]
        widgets = {
            "icon": forms.RadioSelect(
                choices=icon.icon_list,
                attrs={
                    "class": "clearfix"
                }
            )
        }


class PermissionsModelForm(BootstrapModelForms):
    """权限菜单的form组件"""

    class Meta:
        model = models.Permission
        fields = ["title", "url", "name"]


class SecondMenuModelForm(BootstrapModelForms):
    """
        二级菜单的form组件
    """

    class Meta:
        model = models.Permission
        exclude = ["pid"]
        widgets = {
            "icon": forms.RadioSelect(
                choices=icon.icon_list,
                attrs={
                    "class": "clearfix"
                }
            )
        }


class MultiAddForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    url = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    menu_id = forms.ChoiceField(
        choices=[(None, "-----")],
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False
    )
    pid_id = forms.ChoiceField(
        choices=[(None, "-----")],
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["menu_id"].choices += models.Menu.objects.values_list("id", "title")
        self.fields["pid_id"].choices += models.Permission.objects.filter(pid__isnull=True).exclude(menu__isnull=True)\
            .values_list("id", "title")


class MultiUpdateForm(forms.Form):
    id = forms.IntegerField(
        # 给ID这个字段设置为隐藏，因为只是用它来做索引，不做其他用处
        widget=forms.HiddenInput(),
    )
    title = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    url = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    menu_id = forms.ChoiceField(
        choices=[(None, "-----")],
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False
    )
    pid_id = forms.ChoiceField(
        choices=[(None, "-----")],
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["menu_id"].choices += models.Menu.objects.values_list("id", "title")
        self.fields["pid_id"].choices += models.Permission.objects.filter(pid__isnull=True).exclude(menu__isnull=True)\
            .values_list("id", "title")








