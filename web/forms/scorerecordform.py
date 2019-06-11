# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from stark.service.start_assembly import BootstrapModelForms
from web.models import ScoreRecord


class ScoreRecordModeForm(BootstrapModelForms):
    class Meta:
        model = ScoreRecord
        exclude = ["student", "user"]

