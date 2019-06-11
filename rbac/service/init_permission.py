from django.conf import settings


def init_permission(request, current_user):
    """

    :param request: 请求体
    :param current_user: 当前用户对象（可以是request.user）
    :return:
    """
    """
    - 当前登陆用户权限的初始化：根据当前用户信息查询到用户所有的权限并放入session中
        - current_user.role.all()根据用户对象查询他所有的角色
        - .values()时就已经跨表进行到了Role表中了
        - Role表的permission字段是一个多对多的关联字段，直接获取这个字段
        - permission字段双下划线就可以跨表进行Permission表中
        - 直接获取表中的所有url，存入session中
        * .distinct()去重：是因为有人有多个角色，这多个角色获取全部的url就会有重复出现的
        * .filter(permission__isnull=False)：如果一个新角色没有分配权限，但是这个角色有对应的用户，
            如果此时这个用户要获取他自己的所有权限时，就会出现null的情况，所以要过滤出为空的情况
    """
    permission_dict = {}
    menu_dict = {}
    url_queryset = current_user.role.all().filter(permission__isnull=False) \
        .values(
        "permission__url",
        "permission__id",
        "permission__title",
        "permission__name",
        "permission__icon",
        "permission__pid",
        "permission__pid__title",
        "permission__pid__url",
        "permission__menu__id",
        "permission__menu__title",
        "permission__menu__icon",
    ).distinct()
    # 获取权限和菜单列表信息
    for item in url_queryset:
        permission_dict[item.get("permission__name")] = {
            "id": item.get("permission__id"),
            "title": item.get("permission__title"),
            "url": item.get("permission__url"),
            "pid": item.get("permission__pid"),
            "ptitle": item.get("permission__pid__title"),
            "purl": item.get("permission__pid__url"),
        }
        # 判断这个权限是否可以作为菜单
        menu_id = item.get("permission__menu__id")
        if not menu_id:
            # 如果不可以就不走下面的代码
            continue
        node = {
                   "title": item.get("permission__title"),
                   "url": item.get("permission__url"),
                   "icon": item.get("permission__icon"),
                   "id": item.get("permission__id"),
               },
        if menu_id in menu_dict:
            menu_dict[menu_id]["children"].append(node)
        else:
            menu_dict[menu_id] = {
                "title": item.get("permission__menu__title"),
                "icon": item.get("permission__menu__icon"),
                "children": [node, ],
            }
    # 加入到session中
    request.session[settings.PERMISSION_SESSION_KEY] = permission_dict
    request.session[settings.MENU_SESSION_KEY] = menu_dict
