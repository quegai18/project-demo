# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from stark.service.start_assembly import StarkHandler
from django.conf.urls import url
from django.utils.safestring import mark_safe
from django.shortcuts import render
from django.db.models import F
from web.forms.scorerecordform import ScoreRecordModeForm
from web.models import Student
from .base import PermissionHandler


class ScoreHandler(PermissionHandler, StarkHandler):
    """积分管理最好只进行添加，不可以修改和删除"""

    model_form_class = ScoreRecordModeForm

    list_display = [
        "student",
        "content",
        "score",
        "user",
    ]

    def display_operation(self, obj=None, is_header=None, *args, **kwargs):
        """
        这里可以写上业务逻辑来根据用户的权限高低判断需要是否需要展示页面中的修改删除按钮
        :param obj:每一行的记录对象
        :param is_header:用于判断是放在表头还是在表内
        :return:mark_safe(字符串格式的标签) 或者其他内容
        """
        if is_header:                   # 如果这是是True，就表示这是对表头进行的编辑
            return "操作"
        else:                           #这表示对行内进行编辑
            # 这里进行别名拼接，用url的别名和路由分发的名称空间这两个值进行拼接
            # 这里进行拼接的namespace来自于StarkSite中的namespace属性
            edit_name = "%s:%s" %(self.site.namespace, self.get_edit_url_name)              # 修改按钮的别名
            delete_name = "%s:%s" %(self.site.namespace, self.get_delete_url_name)          # 删除按钮的别名
            student_id = kwargs.get("student_id")
            edit_url = StarkHandler.memory_url(self.request, edit_name, **{"student_id": student_id, "pk": obj.pk},)
            delete_url = StarkHandler.memory_url(self.request, delete_name, **{"student_id": student_id, "pk": obj.pk},)
            # 这里放了编辑和修改两个按钮
            button = mark_safe("""
                <a style="color: #333333;" href="{0}">
                    <i class="fa fa-edit" aria-hidden="true"></i></a>
                |
                <a style="color: #d9534f;" href="{1}"><i
                        class="fa fa-trash-o"></i></a>
            """.format(edit_url, delete_url))
            return button

    def get_urls(self):
        patterns = [
            url("^list/(?P<student_id>\d+)/$", self.wapper(self.changelist_view), name=self.get_list_url_name),
            url("^add/(?P<student_id>\d+)/$", self.wapper(self.add_view), name=self.get_add_url_name),
            url("^edit/(?P<student_id>\d+)/(?P<pk>\d+)/$", self.wapper(self.edit_view), name=self.get_edit_url_name),
            url("^del/(?P<student_id>\d+)/(?P<pk>\d+)/$", self.wapper(self.delete_view), name=self.get_delete_url_name),
        ]
        patterns.extend(self.extra_urls())
        return patterns

    def get_queryset(self, request, *args, **kwargs):
        student_id = int(kwargs.get("student_id"))
        query_set = self.model_class.objects.filter(student_id=student_id)
        return query_set

    def get_edit_object(self, request, pk, *args, **kwargs):
        """方便扩展修改功能的数据校验"""
        student_id = kwargs.get("student_id")
        return self.model_class.objects.filter(id=pk, student_id=student_id).first()

    def delete_object(self, request, pk, *args, **kwargs):
        student_id = kwargs.get("student_id")
        return self.model_class.objects.filter(id=pk, student_id=student_id)

    def save(self, request, form, is_update, *args, **kwargs):
        student_id = kwargs.get("student_id")
        student_object = Student.objects.filter(id=student_id).first()
        if not student_object:
            return render(request, "rbac/refuse.html", {"error_msg":"违规操作：查找不到当前学员，请重新选择！"})
        if not is_update:
            form.instance.user_id = request.user.pk
            form.instance.student_id = student_id
        form.save()
        Student.objects.filter(id=student_id).update(score=F("score") + form.cleaned_data["score"])

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

    action_list = []


