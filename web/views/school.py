# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from stark.service.start_assembly import StarkHandler
from .base import PermissionHandler


class SchoolHandler(PermissionHandler, StarkHandler):
    """用于对School表设置各种功能"""
    list_display = ["title", ]
