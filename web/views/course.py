# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from stark.service.start_assembly import StarkHandler
from .base import PermissionHandler


class CourseHandler(PermissionHandler, StarkHandler):
    """用于对Staff表设置各种功能"""
    list_display = ["name", ]
    search_list = ["name__contains", ]  # 为当前表配置搜索的字段，_contains表示或的意思
