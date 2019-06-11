# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from web.models import StudyRecord
from stark.service.start_assembly import BootstrapModelForms


class StudyRecordModelForm(BootstrapModelForms):
    class Meta:
        model = StudyRecord
        fields = ["record"]





