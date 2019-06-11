"""
角色管理
"""
from rbac.models import *
from django.shortcuts import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from rbac.forms.model_form import RoleMoedelForm
from rbac.service.basic_urls import memory_reverse


def role_list(request):
    """角色列表"""
    return render(request, "rbac/role_list.html", {"role_queryset": Role.objects.all()})


def role_add(request):
    """添加角色"""
    if request.method == "GET":
        form = RoleMoedelForm()
        return render(request, "rbac/user_input.html", {"form": form})
    # 把form表单提交的数据传入modelform组件内
    form = RoleMoedelForm(data=request.POST)
    if form.is_valid():
        # 如何数据合法，就进行保存
        form.save()
        return redirect(memory_reverse(request, "rbac:role_list"))
    # 如果数据不合法，就返回错误信息
    return render(request, "rbac/user_input.html", {"form": form})


def role_edit(request, pk):
    """
    修改角色信息
    :param request:
    :param pid: 要修改的角色ID
    :return:
    """
    obj = Role.objects.filter(id=pk).first()
    if not obj:
        return render(request, "rbac/refuse.html")
    if request.method == "GET":
        # 把这个角色对象传入form组件里面，页面点开后的input输入框内会自带上这个对象的各种值
        form = RoleMoedelForm(instance=obj)
        return render(request, "rbac/user_input.html", {"form": form})
    form = RoleMoedelForm( instance=obj, data=request.POST)
    if form.is_valid():
        # 如何数据合法，就进行保存
        form.save()
        return redirect(memory_reverse(request, "rbac:role_list"))
    return redirect(memory_reverse(request, "rbac:role_list"))


def role_del(request, pk):
    """删除角色信息"""
    cancel_url = memory_reverse(request, "rbac:role_list")
    obj = Role.objects.filter(id=pk)
    if not obj:
        return render(request, "rbac/refuse.html")
    if request.method == "GET":
        # delete模板中的取消按钮，没有具体指向哪个页面，就是为了其他地方也能复用，于是决定从views中灵活传送这个跳转地址
        return render(request, "rbac/delete.html", {"cancel_url": cancel_url})
    obj.delete()
    return redirect(cancel_url)
