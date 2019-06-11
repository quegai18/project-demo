# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from django.conf.urls import url
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.urls import reverse
from stark.service.start_assembly import StarkHandler
from web.models import ClassList
from web.models import CourseRecord
from web.models import StudyRecord
from web.forms.courserecord import CourseRecordModelForm
from web.forms.studyform import StudyRecordModelForm
from django.forms.models import modelformset_factory
from .base import PermissionHandler


class CourseRecordHandler(PermissionHandler, StarkHandler):

    model_form_class = CourseRecordModelForm

    def display_courserecord(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return "考勤记录"
        # 这里进行别名拼接，用url的别名和路由分发的名称空间这两个值进行拼接
        # 这里进行拼接的namespace来自于StarkSite中的namespace属性
        nickname = "%s:%s" % (self.site.namespace, "web_studyrecord_list")  # 修改按钮的别名
        url = reverse(nickname, kwargs={"course_record_id": obj.pk})
        button = mark_safe("""<a target='_blank' href="{0}">查看记录</a>""".format(url))
        return button

    def display_attendance(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return "批量操作考勤"
        # 这里进行别名拼接，用url的别名和路由分发的名称空间这两个值进行拼接
        # 这里进行拼接的namespace来自于StarkSite中的namespace属性
        nickname = "%s:%s" % (self.site.namespace, self.get_url_name("attendance"))  # 修改按钮的别名
        url = reverse(nickname, kwargs={"courserecord_id": obj.pk})
        button = mark_safe("""<a target='_blank' href="{0}">点击查看</a>""".format(url))
        return button

    list_display = [
        StarkHandler.display_checkbox,
        "class_object",
        "day_num",
        "teacher",
        "date",
        display_courserecord,
        display_attendance,
    ]

    def attendance_view(self, request, courserecord_id, *args, **kwargs):
        """批量操作考勤记录"""
        studyrecord_object_list = StudyRecord.objects.filter(course_record_id=courserecord_id)
        study_model_formset = modelformset_factory(StudyRecord, form=StudyRecordModelForm, extra=0)
        if request.method == "POST":
            formset = study_model_formset(queryset=studyrecord_object_list, data=request.POST)
            if formset.is_valid():
                formset.save()
                return render(request, "attendance.html", {"formset": formset})
        formset = study_model_formset(queryset=studyrecord_object_list)
        return render(request, "attendance.html", {"formset":formset})

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
            class_id = kwargs.get("class_id")
            edit_url = StarkHandler.memory_url(self.request, edit_name, **{"class_id": class_id, "pk": obj.pk},)
            delete_url = StarkHandler.memory_url(self.request, delete_name, **{"class_id": class_id, "pk": obj.pk},)
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
        class_id = kwargs.get("class_id")
        class_object = ClassList.objects.filter(id=class_id).first()
        if not class_object:
            return render(request, "rbac/refuse.html", {"error_msg": "违规操作：查找不到当前学员，请重新选择！"})
        if not is_update:
            form.instance.class_object_id = class_id
        form.save()

    def get_queryset(self, request, *args, **kwargs):
        class_id = int(kwargs.get("class_id"))
        query_set = self.model_class.objects.filter(class_object=class_id)
        return query_set

    def get_edit_object(self, request, pk, *args, **kwargs):
        """方便扩展修改功能的数据校验"""
        class_id = kwargs.get("class_id")
        return self.model_class.objects.filter(id=pk, class_object=class_id).first()

    def delete_object(self, request, pk, *args, **kwargs):
        class_id = kwargs.get("class_id")
        return self.model_class.objects.filter(id=pk, class_object=class_id)

    def get_urls(self):
        patterns = [
            url("^list/(?P<class_id>\d+)/$", self.wapper(self.changelist_view), name=self.get_list_url_name),
            url("^add/(?P<class_id>\d+)/$", self.wapper(self.add_view), name=self.get_add_url_name),
            url("^edit/(?P<class_id>\d+)/(?P<pk>\d+)/$", self.wapper(self.edit_view), name=self.get_edit_url_name),
            url("^del/(?P<class_id>\d+)/(?P<pk>\d+)/$", self.wapper(self.delete_view), name=self.get_delete_url_name),
            url("^attendance/(?P<courserecord_id>\d+)/$", self.wapper(self.attendance_view), name=self.get_url_name("attendance")),
        ]
        patterns.extend(self.extra_urls())
        return patterns

    def multi_init(self, request, *args, **kwargs):
        """批量初始化学员考勤数据"""
        course_record_list = request.POST.getlist("pk")
        class_id = kwargs.get("class_id")

        class_obj = ClassList.objects.filter(id=class_id).first()
        if not class_obj:
            return render(request, "rbac/refuse.html", {"error_msg":"班级不存在，请重新选择！"})
        current_class_student_obj_list = class_obj.student_set.all()
        for course_record_id in course_record_list:         # 遍历选中的所有课程节次
            courserecord_obj = CourseRecord.objects.filter(id=course_record_id, class_object_id=class_obj).first()
            if not courserecord_obj: continue           # 判断当前的上课记录是否合法
            is_existence = StudyRecord.objects.filter(course_record=courserecord_obj).exists()  # 查看当前课程记录是否已经有了考勤记录
            if is_existence:continue
            # for student_obj in current_class_student_obj_list:
            #     StudyRecord.objects.create(student_id=student_obj.id, course_record_id=course_record_id)
            # 下面两行和上面这个for循环效果一样，batch_size用于设置一次性提交多少个，然后循环的进行提交，直到全部
            current_class_student_list = [StudyRecord(student_id=student_obj.id, course_record_id=course_record_id) for student_obj in current_class_student_obj_list]
            StudyRecord.objects.bulk_create(current_class_student_list, batch_size=50)

    multi_init.text = "批量初始化考勤"

    action_list = [multi_init,]


