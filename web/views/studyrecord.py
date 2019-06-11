# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from stark.service.start_assembly import StarkHandler
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.shortcuts import render
from web.models import CourseRecord
from .base import PermissionHandler


class StudyRecordHandler(PermissionHandler, StarkHandler):

    list_display = [
        "course_record",
        "student",
        StarkHandler.get_choice_text("上课记录", "record"),
    ]

    def display_operation(self, obj=None, is_header=None, *args, **kwargs):
        """
        这里可以写上业务逻辑来根据用户的权限高低判断需要是否需要展示页面中的修改删除按钮
        :param obj:每一行的记录对象
        :param is_header:用于判断是放在表头还是在表内
        :return:mark_safe(字符串格式的标签) 或者其他内容
        """
        if is_header:  # 如果这是是True，就表示这是对表头进行的编辑
            return "操作"
        else:  # 这表示对行内进行编辑
            # 这里进行别名拼接，用url的别名和路由分发的名称空间这两个值进行拼接
            # 这里进行拼接的namespace来自于StarkSite中的namespace属性
            edit_name = "%s:%s" % (self.site.namespace, self.get_edit_url_name)  # 修改按钮的别名
            delete_name = "%s:%s" % (self.site.namespace, self.get_delete_url_name)  # 删除按钮的别名
            course_record_id = kwargs.get("course_record_id")
            edit_url = StarkHandler.memory_url(self.request, edit_name, **{"course_record_id": course_record_id, "pk": obj.pk}, )
            delete_url = StarkHandler.memory_url(self.request, delete_name, **{"course_record_id": course_record_id, "pk": obj.pk}, )
            # 这里放了编辑和修改两个按钮
            button = mark_safe("""
                    <a style="color: #333333;" href="{0}">
                        <i class="fa fa-edit" aria-hidden="true"></i></a>
                    |
                    <a style="color: #d9534f;" href="{1}"><i
                            class="fa fa-trash-o"></i></a>
                """.format(edit_url, delete_url))
            return button

    def save(self, request, form, is_update, *args, **kwargs):
        course_record_id = kwargs.get("course_record_id")
        class_object = CourseRecord.objects.filter(id=course_record_id).first()
        if not class_object:
            return render(request, "rbac/refuse.html", {"error_msg": "违规操作：查找不到当前学员，请重新选择！"})
        form.save()

    def get_queryset(self, request, *args, **kwargs):
        course_record_id = int(kwargs.get("course_record_id"))
        query_set = self.model_class.objects.filter(course_record=course_record_id)
        return query_set

    def get_edit_object(self, request, pk, *args, **kwargs):
        """方便扩展修改功能的数据校验"""
        course_record_id = kwargs.get("course_record_id")
        return self.model_class.objects.filter(id=pk, course_record=course_record_id).first()

    def delete_object(self, request, pk, *args, **kwargs):
        course_record_id = kwargs.get("course_record_id")
        return self.model_class.objects.filter(id=pk, course_record=course_record_id)

    def get_urls(self):
        patterns = [
            url("^list/(?P<course_record_id>\d+)/$", self.wapper(self.changelist_view), name=self.get_list_url_name),
            url("^add/(?P<course_record_id>\d+)/$", self.wapper(self.add_view), name=self.get_add_url_name),
            url("^edit/(?P<course_record_id>\d+)/(?P<pk>\d+)/$", self.wapper(self.edit_view), name=self.get_edit_url_name),
            url("^del/(?P<course_record_id>\d+)/(?P<pk>\d+)/$", self.wapper(self.delete_view), name=self.get_delete_url_name),
        ]
        patterns.extend(self.extra_urls())
        return patterns
