"""
人员管理
"""
from django.utils.module_loading import import_string
from django.conf import settings
from django.shortcuts import redirect
from django.shortcuts import render
from rbac.forms.model_form import UserModelForm
from rbac.forms.model_form import UpdateUserModelForm
from rbac.forms.model_form import ResetPWDModelForm
from rbac.service.basic_urls import memory_reverse
from django.contrib.auth import hashers

UserModelClass = import_string(settings.RBAC_USER_MODEL_CLASS)


def user_list(request):
    """用户列表"""
    return render(request, "rbac/user_list.html", {"user_queryset": UserModelClass.objects.all()})


def user_add(request):
    """添加用户"""
    if request.method == "GET":
        form = UserModelForm()
        return render(request, "rbac/user_input.html", {"form": form})
    # 把form表单提交的数据传入modelform组件内
    form = UserModelForm(data=request.POST)
    if form.is_valid():
        # 如何数据合法，就进行保存
        UserModelClass.objects.create_user(
            username=request.POST.get("username"),
            password=request.POST.get("password"),
            email=request.POST.get("email"),
        )
        return redirect(memory_reverse(request, "rbac:user_list"))
    # 如果数据不合法，就返回错误信息
    return render(request, "rbac/user_input.html", {"form": form})


def user_edit(request, pk):
    """
    修改角色信息
    :param request:
    :param pk: 要修改的角色ID
    :return:
    """
    obj = UserModelClass.objects.filter(id=pk).first()
    if not obj:
        return render(request, "rbac/refuse.html")
    if request.method == "GET":
        # 把这个角色对象传入form组件里面，页面点开后的input输入框内会自带上这个对象的各种值
        form = UpdateUserModelForm(instance=obj)
        return render(request, "rbac/user_input.html", {"form": form})
    form = UpdateUserModelForm(instance=obj, data=request.POST)
    if form.is_valid():
        # 如何数据合法，就进行保存
        form.save()
    return redirect(memory_reverse(request, "rbac:user_list"))


def user_del(request, pk):
    """删除角色信息"""
    cancel_url = memory_reverse(request, "rbac:user_list")
    obj = UserModelClass.objects.filter(id=pk)
    if not obj:
        return render(request, "rbac/refuse.html")
    if request.method == "GET":
        # delete模板中的取消按钮，没有具体指向哪个页面，就是为了其他地方也能复用，于是决定从views中灵活传送这个跳转地址
        return render(request, "rbac/delete.html", {"cancel_url": cancel_url})
    obj.delete()
    return redirect(cancel_url)


def user_reset(request, pk):
    """重置密码"""
    obj = UserModelClass.objects.filter(id=pk).first()
    if not obj:
        return render(request, "rbac/refuse.html")
    if request.method == "GET":
        # 把这个角色对象传入form组件里面，页面点开后的input输入框内会自带上这个对象的各种值
        form = ResetPWDModelForm()
        return render(request, "rbac/user_input.html", {"form": form})
    form = ResetPWDModelForm(instance=obj, data=request.POST)
    if form.is_valid():
        # 如果数据合法，就进行保存
        # 这里的密码加密还可以放到modelform中去做，对clean_data或者clean_password进行处理
        new_password = hashers.make_password(request.POST.get("password"))
        user = UserModelClass.objects.filter(id=pk)
        user.update(password=new_password)
        return redirect(memory_reverse(request, "rbac:user_list"))
    return render(request, 'rbac/user_input.html', {'form': form})
