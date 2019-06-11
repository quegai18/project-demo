from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.


class Permission(models.Model):
    """这是权限表,这里面存放的菜单都是二级菜单，"""
    title = models.CharField(verbose_name="标题", max_length=32)
    url = models.CharField(verbose_name="含正则的url", max_length=128)
    menu = models.ForeignKey(verbose_name="所属的一级菜单", to="Menu", null=True, blank=True, help_text="如果为空则表示不是菜单, 如果有值就为二级菜单", on_delete=False)
    icon = models.CharField(verbose_name="菜单图标", max_length=32, null=True, blank=True)
    pid = models.ForeignKey(verbose_name="用于关联显示的二级菜单", to="Permission", null=True, blank=True, on_delete=False)
    name = models.CharField(verbose_name="URL的别名", max_length=32, unique=True, default=None)

    def __str__(self):
        return self.title


class Role(models.Model):
    """这是角色表"""
    title = models.CharField(verbose_name="角色名称", max_length=32)
    permission = models.ManyToManyField(verbose_name="角色所有权限", to="Permission", blank=True)

    def __str__(self):
        return self.title


class Menu(models.Model):
    """这张表用于存放所有的一级菜单"""
    title = models.CharField(verbose_name="一级菜单标题", max_length=32, )
    icon = models.CharField(verbose_name="菜单图标", max_length=32, null=True, blank=True)

    def __str__(self):
        return self.title


class UserInfo(AbstractUser, ):
    """这是用来被项目继承用户表"""
    role = models.ManyToManyField(verbose_name="用户的角色", to=Role, blank=True)

    class Meta:
        """Django就不会生成这张用户表了，还有用户与角色的关联表也不会生成，但是这个类可以当做一个父类，被其他类所继承"""
        abstract = True
