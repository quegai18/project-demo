from django.conf.urls import url
from rbac.views import role
from rbac.views import user
from rbac.views import menu
from rbac.views import distribute
from rbac.views import account

app_name = "rbac"


urlpatterns = [
    # 角色管路
    url("^role/list/$", role.role_list, name="role_list"),
    url("^role/add/$", role.role_add, name="role_add"),
    url("^role/edit/(?P<pk>\d+)/$", role.role_edit, name="role_edit"),
    url("^role/del/(?P<pk>\d+)/$", role.role_del, name="role_del"),
    # 用户管理
    # url("^user/list/$", user.user_list, name="user_list"),
    # url("^user/add/$", user.user_add, name="user_add"),
    # url("^user/edit/(?P<pk>\d+)/$", user.user_edit, name="user_edit"),
    # url("^user/del/(?P<pk>\d+)/$", user.user_del, name="user_del"),
    # url("^user/reset/(?P<pk>\d+)/$", user.user_reset, name="user_reset"),
    # 一级菜单管理
    url("^menu/list/$", menu.menu_list, name="menu_list"),
    url("^menu/add/$", menu.menu_add, name="menu_add"),
    url("^menu/edit/(?P<pk>\d+)/$", menu.menu_edit, name="menu_edit"),
    url("^menu/del/(?P<pk>\d+)/$", menu.menu_del, name="menu_del"),
    # 二级菜单管理
    url("^second/menu/add/(?P<menu_id>\d+)/$", menu.sec_menu_add, name="sec_menu_add"),
    url("^second/menu/edit/(?P<pk>\d+)/$", menu.sec_menu_edit, name="sec_menu_edit"),
    url("^second/menu/del/(?P<pk>\d+)/$", menu.sec_menu_del, name="sec_menu_del"),
    # 三级菜单管理
    url("^permissions/menu/add/(?P<sid>\d+)/$", menu.permissions_add, name="permissions_add"),
    url("^permissions/menu/edit/(?P<pk>\d+)/$", menu.permissions_edit, name="permissions_edit"),
    url("^permissions/menu/del/(?P<pk>\d+)/$", menu.permissions_del, name="permissions_del"),
    # 批量权限操作
    url("^multi/permissions/$", menu.multi_permissions_list, name="multi_permissions_list"),
    url("^multi/permissions/add/$", menu.multi_permissions_add, name="multi_permissions_add"),
    url("^multi/permissions/edit/$", menu.multi_permissions_edit, name="multi_permissions_edit"),
    url("^multi/permissions/del/(?P<pk>\d+)/$", menu.multi_permissions_del, name="multi_permissions_del"),
    # 权限分配
    url("^distribute/permissions/$", distribute.distribute_permissions, name="distribute_permissions"),

]



