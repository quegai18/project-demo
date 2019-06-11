from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import auth
from rbac.service import init_permission
from django.urls import reverse


def login(request):
    """用户登录（关联了django自带的用户表，所有可以用auth）"""
    # 1.用户登陆
    if request.method == "GET":
        return render(request, "rbac/login.html")
    current_user = auth.authenticate(
        username=request.POST.get("user"),
        password=request.POST.get("pwd")
    )
    if current_user:
        # 2.权限的初始化
        init_permission.init_permission(request, current_user)
        auth.login(request, current_user)
        return redirect(reverse("index"))
    else:
        return render(request, "rbac/login.html", {"state": "用户名或密码错误"})


def logout(request):
    """用户登录状态注销"""
    auth.logout(request)
    return redirect(reverse("login"))


def index(request):
    """登录后的首页"""
    return render(request, "rbac/index.html")
