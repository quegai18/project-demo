from django.shortcuts import render
from django.shortcuts import HttpResponse
from rbac.models import *
from django.conf import settings
from django.utils.module_loading import import_string


def distribute_permissions(request):
    """
    用于展示权限分配页面
    :param request:
    :return:
    """
    # 初始化各类数据
    user_has_permissions = []
    role_has_permissions = []
    user_has_roles = []
    user_has_permissions_dict = {}
    menu_dict = {}
    secmenu_dict = {}
    UserModelClass = import_string(settings.RBAC_USER_MODEL_CLASS)                                   # 根据字符串自动查找所在路径的类
    user_list = UserModelClass.objects.all()
    role_list = Role.objects.all()

    # 获取所有的菜单信息，并做成字典格式，遍历起来比列表更快
    menu_list = Menu.objects.values("id", "title")                                                          # 所有一级菜单的ID和标题
    for item in menu_list:
        item["children"] = []
        menu_dict[item["id"]] = item

    secmenu_list = Permission.objects.filter(menu__isnull=False).values("id", "title", "menu_id")           # 所有二级菜单(menu字段不为空的就是)
    for item in secmenu_list:
        item["children"] = []
        secmenu_dict[item["id"]] = item
        menu_dict[item["menu_id"]]["children"].append(item)

    permission_list = Permission.objects.filter(menu__isnull=True).values("id", "title", "pid")             # 所有三级菜单(menu字段为空的就是)
    for item in permission_list:
        pid = item["pid"]
        if not pid:
            continue
        secmenu_dict[pid]["children"].append(item)
    """
    数据结构:
    [
        {
            id: 1,
            title: 一级菜单,
            children: [
                {
                    id: 12,
                    title: 二级菜单
                    children:[
                        {
                            id: 23
                            title:三级菜单
                        }
                    ]        
                },
            ],
        },
    ]
    """

    # 获取当前用户拥有的所有权限（如果选中了角色，应该优先显示当前角色所拥有的权限，而不是当前用户）
    user_id = request.GET.get("user")
    role_id = request.GET.get("role")
    user_obj = UserModelClass.objects.filter(id=user_id).first()
    role_obj = Role.objects.filter(id=role_id).first()
    if not user_obj:
        user_id = None
    if user_id:
        user_has_roles = user_obj.role.all()
    user_has_roles_dict = {item.id: None for item in user_has_roles}
    if role_obj:                    # 如果当前选择了角色
        user_has_permissions = role_obj.permission.all()
        user_has_permissions_dict = {item.id: None for item in user_has_permissions}
    elif user_obj:                  # 如果当前选择了角色
        user_has_permissions = user_obj.role.filter(permission__isnull=False).values("id", "permission").distinct()
        user_has_permissions_dict = {item["permission"]: None for item in user_has_permissions}

    # 获取当前角色拥有的所有权限
    if not role_obj:
        role_id = None
    if role_id:
        role_has_permissions = role_obj.permission.all()
    role_has_permissions_dict = {item.id: None for item in role_has_permissions}

    # 处理修改角色的请求
    if request.method == "POST" and request.POST.get("type") == "role":
        role_id_list = request.POST.getlist("roles")
        # 用户和角色是多对多的关系，需要把获取来的数据添加到第三张表中
        if not user_obj:
            # 能走到这里肯定是在客户端页面自己写了个提交按钮来进行提交的
            return HttpResponse("请选择用户，不要捣乱！")
        user_obj.role.set(role_id_list)

    # 处理修改权限的请求
    if request.method == "POST" and request.POST.get("type") == "permission":
        permission_id_list = request.POST.getlist("permissions")
        # 权限和角色是多对多的关系
        if not role_obj:
            return HttpResponse("请选择角色，不要捣乱！")
        role_obj.permission.set(permission_id_list)

    return render(
        request,
        "rbac/distribute.html",
        {
            "user_list": user_list,
            "role_list": role_list,
            "menu_list": menu_list,
            "user_id": user_id,
            "role_id": role_id,
            "user_has_roles_dict": user_has_roles_dict,
            "user_has_permissions_dict": user_has_permissions_dict,
            "role_has_permissions_dict": role_has_permissions_dict,
        }
    )
