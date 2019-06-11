# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from django.conf.urls import url
from django.shortcuts import render
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from stark.service.start_assembly import StarkHandler
from stark.service.start_assembly import SearchOption
from web.forms.staffeditform import StaffEditModelForm
from web.forms.staffaddform import StaffAddModelForm
from web.forms.resetform import ResetPWDModelForm
from .base import PermissionHandler


class StaffHandler(PermissionHandler, StarkHandler):
    """用于对Staff表设置各种功能"""

    def display_reset(self, obj=None, is_header=None):
        """为员工表多加一列，用于重置密码"""
        if is_header:
            return "重置密码"
        # 这里进行别名拼接，用url的别名和路由分发的名称空间这两个值进行拼接
        # 这里进行拼接的namespace来自于StarkSite中的namespace属性
        reset_name = "%s:%s" % (self.site.namespace, self.get_reset_url_name)  # 修改按钮的别名
        reset_url = StarkHandler.memory_url(self.request, reset_name, *[obj.pk])
        # 这里放了编辑和修改两个按钮
        button = mark_safe("""<a style="font-size: 16px;" href="{0}"><i class="fa fa-gears" aria-hidden="true"></i></a>""".format(reset_url))
        return button

    list_display = [
        StarkHandler.display_checkbox,
        "name",
        StarkHandler.get_choice_text("性别", "gender"),
        "age",
        "phone",
        "email",
        "depart",
        display_reset,
    ]

    def get_model_form(self, add_or_edit, request, *args, **kwargs):
        if add_or_edit == "add":
            return StaffAddModelForm
        elif add_or_edit == "edit":
            return StaffEditModelForm

    @property
    def get_reset_url_name(self):
        """获取重置密码的路由别名"""
        return self.get_url_name("reset")

    def reset_view(self, request, pk, *args, **kwargs):
        """重置密码操作"""
        current_obj = self.model_class.objects.filter(id=pk).first()  # 获取当前要重置密码的用户对象
        if not current_obj:
            return render(request, "rbac/refuse.html")
        if request.method == "GET":
            form = ResetPWDModelForm()     # 把这个角色对象传入form组件里面，页面点开后的input输入框内会自带上这个对象的各种值
            return render(request, "stark/change.html", {"form": form})
        form = ResetPWDModelForm(instance=current_obj, data=request.POST)
        if form.is_valid():             # 如果数据合法，就进行保存
            self.save(form, is_update=False)
            name = "%s:%s" % (self.site.namespace, self.get_list_url_name)
            return redirect(StarkHandler.memory_reverse(self.request, name))  # 跳转会列表页面
        return render(request, 'stark/change.html', {'form': form})

    def extra_urls(self):
        """
        这里可以为当前表设定需要增加的url
        注意：加URL的同时要在这里写好视图函数 def test_view(self, request):pass
        """
        patterns = [
            url("^reset/(?P<pk>\d+)/$", self.wapper(self.reset_view), name=self.get_reset_url_name),
        ]
        return patterns

    search_group = [  # 配置进行组合搜索的字段，默认为空
        SearchOption("gender"),  # 这是都用默认设置的展示(基本足够了)，is_choices设置该字段是否支持多选
        SearchOption("depart", is_multi=True),
    ]

    search_list = ["name__contains", "username__contains", "phone__contains", ]  # 为当前表配置搜索的字段，_contains表示或的意思

