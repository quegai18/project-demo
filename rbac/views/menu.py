"""菜单管理"""
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from rbac.models import *
from rbac.forms.model_form import MenuMoedelForm
from rbac.forms.model_form import SecondMenuModelForm
from rbac.forms.model_form import PermissionsModelForm
from rbac.forms.model_form import MultiAddForm
from rbac.forms.model_form import MultiUpdateForm
from rbac.service.basic_urls import *
from django.forms import formset_factory
from rbac.service import routes
from collections import OrderedDict
from django.conf import settings


def menu_list(request):
    """菜单管理列表"""
    current_menu_id = request.GET.get("mid")   # 这是用户选择的一级菜单ID
    current_second_menu_id = request.GET.get("sid")    # 这是用户选择的二级菜单ID
    if not Menu.objects.filter(id=current_menu_id).exists():
        current_menu_id = None
    if not Permission.objects.filter(id=current_second_menu_id).exists():
        current_second_menu_id = None
    if current_menu_id:
        second_menu = Permission.objects.filter(menu_id=current_menu_id)   # 通过点击的一级菜单ID来筛选出相关联的二级菜单对象
    else:
        second_menu = {}
    if current_second_menu_id:
        permissions = Permission.objects.filter(pid=current_second_menu_id)   # 通过二级菜单ID获取与二级菜单ID相关联的权限
    else:
        permissions = {}
    return render(
        request,
        "rbac/menu_list.html",
        {
            "menu_query": Menu.objects.all(),
            "current_menu_id": current_menu_id,
            "second_menu": second_menu,
            "current_second_menu_id": current_second_menu_id,
            "permissions": permissions,
        }
    )


def menu_add(request):

    """添加一级菜单"""
    if request.method == "GET":
        form = MenuMoedelForm()
        return render(request, "rbac/user_input.html", {"form": form})
    # 把form表单提交的数据传入modelform组件内
    form = MenuMoedelForm(data=request.POST)
    if form.is_valid():
        # 如何数据合法，就进行保存
        form.save()
        return redirect(memory_reverse(request, name="rbac:menu_list"))
    # 如果数据不合法，就返回错误信息
    return render(request, "rbac/user_input.html", {"form": form})


def menu_edit(request, pk):
    """
    一级菜单信息的修改
    :param request:
    :param pk: 一级菜单的ID
    :return:
    """
    obj = Menu.objects.filter(id=pk).first()
    if not obj:
        return render(request, "rbac/refuse.html", {"error_msg": "未查询到对应的菜单信息"})
    if request.method == "GET":
        # 把这个角色对象传入form组件里面，页面点开后的input输入框内会自带上这个对象的各种值
        # instance表示已有的值
        form = MenuMoedelForm(instance=obj)
        return render(request, "rbac/user_input.html", {"form": form})
    form = MenuMoedelForm(instance=obj, data=request.POST)
    if form.is_valid():
        # 如何数据合法，就进行保存
        form.save()
    return redirect(memory_reverse(request, name="rbac:menu_list"))


def menu_del(request, pk):

    """
    一级菜单信息的删除
    :param request:
    :param pk: 一级菜单的ID
    :return:
    """
    url = memory_reverse(request, name="rbac:menu_list")
    obj = Menu.objects.filter(id=pk)
    if not obj:
        return render(request, "rbac/refuse.html", {"error_msg": "未查询到对应的菜单信息"})
    if request.method == "GET":
        # delete模板中的取消按钮，没有具体指向哪个页面，就是为了其他地方也能复用，于是决定从views中灵活传送这个跳转地址
        return render(request, "rbac/delete.html", {"cancel_url": url})
    obj.delete()
    return redirect(url)


def sec_menu_add(request, menu_id):
    """
    二级菜单的添加操作
    :param request:
    :param menu_id: 当前被选中的一级菜单ID(用于设置默认值)
    :return:
    """
    """添加一级菜单"""
    menu_obj = Menu.objects.filter(id=menu_id).first()
    if request.method == "GET":
        # initial是Forms组件中用于以下拉菜单方式显示并默认选中
        form = SecondMenuModelForm(initial={"menu": menu_obj})
        return render(request, "rbac/user_input.html", {"form": form})
    # 把form表单提交的数据传入modelform组件内
    form = SecondMenuModelForm(data=request.POST)
    if form.is_valid():
        # 如何数据合法，就进行保存
        form.save()
        return redirect(memory_reverse(request, name="rbac:menu_list"))
    # 如果数据不合法，就返回错误信息
    return render(request, "rbac/user_input.html", {"form": form})


def sec_menu_edit(request, pk):
    """
    :param request:
    :param pk: 当前要编辑的二级菜单ID
    :return:
    """
    obj = Permission.objects.filter(id=pk).first()
    if not obj:
        return render(request, "rbac/refuse.html")
    if request.method == "GET":
        # 把这个角色对象传入form组件里面，页面点开后的input输入框内会自带上这个对象的各种值
        # instance表示已有的值
        form = SecondMenuModelForm(instance=obj)
        return render(request, "rbac/user_input.html", {"form": form})
    form = SecondMenuModelForm(instance=obj, data=request.POST)
    if form.is_valid():
        # 如何数据合法，就进行保存
        form.save()
    return redirect(memory_reverse(request, name="rbac:menu_list"))


def sec_menu_del(request, pk):
    """
    二级菜单信息的删除
    :param request:
    :param pk: 二级菜单的ID
    :return:
    """
    url = memory_reverse(request, name="rbac:menu_list")
    obj = Permission.objects.filter(id=pk)
    if not obj:
        return render(request, "rbac/refuse.html")
    if request.method == "GET":
        # delete模板中的取消按钮，没有具体指向哪个页面，就是为了其他地方也能复用，于是决定从views中灵活传送这个跳转地址
        return render(request, "rbac/delete.html", {"cancel_url": url})
    obj.delete()
    return redirect(url)


def permissions_add(request, sid):
    """
    增加权限url
    :param request:
    :param sid: 相关联的二级菜单ID
    :return:
    """
    if request.method == "GET":
        # initial用于表示Forms组件的默认值
        form = PermissionsModelForm()
        return render(request, "rbac/user_input.html", {"form": form})
    # 把form表单提交的数据传入modelform组件内
    form = PermissionsModelForm(data=request.POST)
    if form.is_valid():
        permission_obj = Permission.objects.filter(id=sid).first()
        if not permission_obj:
            return render(request, "rbac/refuse.html")
        # 在创建权限url时没有让用户选择关联的二级菜单，默认认为就与用户点击选中的二级菜单相关联
        # form.instance.pid就是给form对象添加pid的默认值
        form.instance.pid = permission_obj
        # 如何数据合法，就进行保存
        form.save()
        return redirect(memory_reverse(request, name="rbac:menu_list"))
    # 如果数据不合法，就返回错误信息
    return render(request, "rbac/user_input.html", {"form": form})


def permissions_edit(request, pk):
    """
    :param request:
    :param pk: 当前要编辑的权限ID
    :return:
    """
    obj = Permission.objects.filter(id=pk).first()
    if not obj:
        return render(request, "rbac/refuse.html")
    if request.method == "GET":
        # 把这个角色对象传入form组件里面，页面点开后的input输入框内会自带上这个对象的各种值
        # instance表示已有的值
        form = PermissionsModelForm(instance=obj)
        return render(request, "rbac/user_input.html", {"form": form})
    form = PermissionsModelForm(instance=obj, data=request.POST)
    if form.is_valid():
        # 如何数据合法，就进行保存
        form.save()
    return redirect(memory_reverse(request, name="rbac:menu_list"))


def permissions_del(request, pk):
    """
    二级菜单信息的删除
    :param request:
    :param pk: 权限ID
    :return:
    """
    url = memory_reverse(request, name="rbac:menu_list")
    obj = Permission.objects.filter(id=pk)
    if not obj:
        return render(request, "rbac/refuse.html")
    if request.method == "GET":
        # delete模板中的取消按钮，没有具体指向哪个页面，就是为了其他地方也能复用，于是决定从views中灵活传送这个跳转地址
        return render(request, "rbac/delete.html", {"cancel_url": url})
    obj.delete()
    return redirect(url)


def multi_permissions_list(request):
    """获取当前项目中的所有URL,别名,反向解析自动拼接namespace"""
    """
    project_url_dict = {
        "rbac:menu_list" : {name:menu_list, url:/rbac/menu/list/}
    }
    """
    # 实例化一个form_class的类，参数1为自定义的form表单, extra传入需要批量生成的表单数量,生成一个formset类
    formset_add_class = formset_factory(MultiAddForm, extra=0)
    formset_update_class = formset_factory(MultiUpdateForm, extra=0)
    post_type = request.GET.get("type")                             # 看一下提交来的POST请求是什么类型
    add_forms = None                                                # 设置一个add_forms的标志位
    update_forms = None                                             # 设置一个update_forms的标志位

    if request.method == "POST" and post_type == "add":             # 如果是个POST请求并且type类型为add，就是个批量增加操作
        formset = formset_add_class(data=request.POST)              # 把POST请求带过来的数据交给forms组件来进行校验
        if formset.is_valid():                                      # 查看校验是否成功
            has_error = False                                       # 这个标志位用于查看下面遍历的所有数据是否全都合法，全都合法再批量入数据库
            obj_list = []                                           # 处于SQL性能考虑，在这里创建一个合法row的列表，用于下面的for循环结束后统一添加
            post_data = formset.cleaned_data                        # 先缓存一下cleaned_data，以便判断是否存在unique唯一索引报错
            for index in range(0, formset.total_form_count()):      # 利用post_data和cleaned_data数据索引一致的特点，对整体数据进行遍历
                row_dict = post_data[index]                         # 获取当前索引位置的数据
                try:
                    new_obj = Permission(**row_dict)                # 先尝试用row_dict
                    new_obj.validate_unique()                       # 判断是否是联合唯一索引
                    obj_list.append(new_obj)
                except Exception as e:
                    formset.errors[index].update(e)
                    add_forms = formset                             # 把add_forms替换为带有错误信息的formset
                    has_error = True
            if not has_error:
                                                                    # 遍历结束后，一次性批量增加所有合法row, batch_size参数用于设置每次批量增加的数量
                Permission.objects.bulk_create(obj_list, batch_size=10)
        else:
            # 如果验证失败，错误信息和刚提交的数据都存在这个if条件的formset中，所以要把原来页面的add_forms替换成校验后的formset
            add_forms = formset

    if request.method == "POST" and post_type == "update":          # 如果是个POST请求并且type类型为add，就是个批量跟新操作
        formset = formset_update_class(data=request.POST)           # 把POST请求带过来的数据交给forms组件来进行校验
        if formset.is_valid():                                      # 查看校验是否成功
            has_error = False                                       # 这个标志位用于查看下面遍历的所有数据是否全都合法，全都合法再批量入数据库
            post_data = formset.cleaned_data                        # 先缓存一下cleaned_data，以便判断是否存在unique唯一索引报错
            for index in range(0, formset.total_form_count()):      # 利用post_data和cleaned_data数据索引一致的特点，对整体数据进行遍历
                row_dict = post_data[index]                         # 获取当前索引位置的数据
                permissions_id = row_dict.pop("id")                 # 获取当前row的ID，顺便删除ID字段，因为修改内容不需要改ID
                try:
                    row_obj = Permission.objects.get(id=permissions_id)  # 通过ID获取数据库中原有的这个row对象
                    for k, v in row_dict.items():                   # 遍历row_dict中的每个键值对
                        setattr(row_obj, k, v)                      # 通过setattr反射，来把每个键值对设置成row_obj的属性和值
                    row_obj.validate_unique()                       # 检测字段唯一性
                    row_obj.save()                                  # 保存row
                except Exception as e:
                    formset.errors[index].update(e)
                    update_forms = formset
        else:                                                       # 验证不成功的情况
            update_forms = formset                                  # 替换formset以便显示错误信息

    project_url_dict = routes.get_all_url_dict()                    # 获取项目中的所有URL
    route_name_set = set(project_url_dict.keys())                   # 并建立一个集合

    # 获取数据库中的所有URL
    database_url_queryset = Permission.objects.all().values("id", "title", "name", "url", "menu_id", "pid_id")
    database_url_dict = OrderedDict()

    permission_name_set = set()                                     # 建立一个数据库中的所有URL的集合
    for row in database_url_queryset:                               # 遍历数据库索取来的URL的queryset集合
        database_url_dict[row["name"]] = row                        # 往字典内存放数据 {name:{URL的各个字段+记录}}
        permission_name_set.add(row["name"])                        # 往集合内插入URL的别名

    # 遍历一下项目和数据库两个URL集合，看一下有没有name是一样的，但是url不一致的情况，如果有这种情况，给挑出来
    for name, row_dict in database_url_dict.items():                # 遍历数据库中的所有url别名和url_dict
        route_dict = project_url_dict.get(name)                     # 获取项目中别名相同的url_dict
        if not route_dict:                                          # 如果项目中不存在这个url_dict, 那就属于需要更新的内容，直接跳过
            continue
        else:                                                       # 进入这里就表示项目和数据库中都有这个url_dict
            if row_dict["url"] != route_dict["url"]:                # 如果这两个url内容一致，就拉倒不管他,如果不一致
                row_dict["url"] = "项目路由和数据库中不一致，请检查"  # 直接写上提示语，就没必要展示URL了

    if not add_forms:                                               # 查看add_forms标志位是否被赋值
        add_name_list = route_name_set - permission_name_set        # 如果项目里面有，数据库里面没有，就需要进行添加
        add_forms = formset_add_class(                              # 通过initial参数来控制生成的form数量
            # 遍历数据库中所有的URL，通过别名判断查找出需要增加的URL字典
            initial=[row_dict for name, row_dict in project_url_dict.items() if name in add_name_list])

    del_name_list = permission_name_set - route_name_set            # 如果项目里面没有，数据库里面有，就需要进行删除
    # 遍历数据库中所有的URL，通过别名判断查找出需要删除的URL字典
    del_rows = [row_dict for name, row_dict in database_url_dict.items() if name in del_name_list]

    if not update_forms:                                            # 查看update_forms标志位是否被赋值
        update_name_list = permission_name_set & route_name_set     # 取数据库和项目两个集合的并集，以备修改
        # 遍历数据库中所有的URL，通过别名判断查找出需要修改的URL字典
        update_forms = formset_update_class(
            initial=[row_dict for name, row_dict in database_url_dict.items() if name in update_name_list])

    return render(request, "rbac/multi_permissions.html", {
        "add_forms": add_forms, "del_rows": del_rows, "update_forms": update_forms})


def multi_permissions_add(request):
    # 先生成一个formset_class类，设置复制form组件的数量为5
    formset_class = formset_factory(PermissionsModelForm, extra=5)
    if request.method == "GET":
        # 实例化一个formset，它的数据格式为formset = [form, form, form..]
        formset = formset_class()
        return render(request, "rbac/multi_permissions.html", {"formset": formset})
    formset = formset_class(data=request.POST)
    if formset.is_valid():   # 如果输入合法
        flag = True   # 设一个标志位，用于决定页面返回什么内容
        post_row_list = formset.cleaned_data
        for index in range(0, formset.total_form_count()):
            row = post_row_list[index]
            # 如果记录为空，它是能通过is_valid()检测的，在这里进行判断，如果为空就跳过
            if not row: continue
            try:
                # 先生成记录对象
                obj = Permission(**row)
                # 查看是否有联合唯一字段的报错
                obj.validate_unique()
                # 没报错就保存
                obj.save()
            except Exception as e:
                flag = False
                formset.errors[index].update(e)
        if flag:
            return HttpResponse("OK")
        else:
            return render(request, "rbac/multi_permissions.html", {"formset": formset})
    return render(request, "rbac/multi_permissions.html", {"formset": formset})


def multi_permissions_edit(request):
    formset_class = formset_factory(PermissionsModelForm, extra=0)
    if request.method == "GET":
        permissions_obj_list = Permission.objects.all()
        formset = formset_class(initial=permissions_obj_list)
        render(request, "rbac/multi_permissions.html", {"formset": formset})
    formset = formset_class(data=request.POST)
    if formset.is_valid():  # 如果输入合法
        flag = True  # 设一个标志位，用于决定页面返回什么内容
        post_row_list = formset.cleaned_data
        for index in range(0, formset.total_form_count()):
            row = post_row_list[index]
            # 如果记录为空，它是能通过is_valid()检测的，在这里进行判断，如果为空就跳过
            if not row: continue
            try:
                # 先生成记录对象
                obj = Permission(**row)
                # 查看是否有联合唯一字段的报错
                obj.validate_unique()
                # 没报错就保存
                obj.save()
            except Exception as e:
                flag = False
                formset.errors[index].update(e)
        if flag:
            return HttpResponse("OK")
        else:
            return render(request, "rbac/multi_permissions.html", {"formset": formset})
    return render(request, "rbac/multi_permissions.html", {"formset": formset})


def multi_permissions_del(request, pk):
    """
    批量操作页面发送来的删除请求
    :param request:
    :param pk: 选中的URL的ID
    :return:
    """
    url = memory_reverse(request, name="rbac:multi_permissions_list")
    obj = Permission.objects.filter(id=pk)
    if not obj:
        return render(request, "rbac/refuse.html")
    if request.method == "GET":
        # delete模板中的取消按钮，没有具体指向哪个页面，就是为了其他地方也能复用，于是决定从views中灵活传送这个跳转地址
        return render(request, "rbac/delete.html", {"cancel_url": url})
    obj.delete()
    return redirect(url)
