# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com

from stark.service.start_assembly import BootstrapModelForms
from web.models import CourseRecord


class CourseRecordModelForm(BootstrapModelForms):
    class Meta:
        model = CourseRecord
        exclude = ["id", "class_object",]

