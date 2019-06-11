# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from django import forms
from django.conf.urls import url
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import QueryDict
from django.db.models import Q
from django.db.models import ForeignKey
from django.db.models import ManyToManyField
from types import FunctionType
from stark.utils.pagination import Pagination
import functools


class BootstrapModelForms(forms.ModelForm):
    """
    用于统一定制每个forms组件的html样式，自定义Form类直接继承就OK
    """
    def __init__(self, *args, **kwargs):
        super(BootstrapModelForms, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "icon": continue
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs["style"] = "width: 300px;"


def get_datetime_text(title, field, format="%Y-%m-%d"):
    """
    用于格式化数据库中的date数据，把该方法名写入list_display列表中，title传入字符串格式的表头内容，field传入字符串格式的字段名，format用于定制时间格式
    例：get_datetime_text("开班日期", "start_date"),
    """
    def inner(self, obj=None, is_header=None):
        if is_header:
            return title
        datetime = getattr(obj, field)
        return datetime.strftime(format)
    return inner


def get_Many_to_Many_text(title, field):
    """用于格式化数据库中的多对多字段"""
    def inner(self, obj=None, is_header=None):
        if is_header:
            return title
        queryset = getattr(obj, field).all()
        text_list =  [str(row) for row in queryset]
        return (",").join(text_list)
    return inner


class SearchGroupRow(object):
    """这里用于封装组合搜索需要展示的数据，一共有两种，Queryset和元祖"""
    def __init__(self, verbose_name, queryset_or_tuple, option, GET_data):
        """

        :param verbose_name: 组合搜索用到的字段的别名
        :param queryset_or_tuple: 组合搜索用到的字段对应的数据集合
        :param option: 封装后的字段对象
        :param GET_data: 当前request.GET中的数据
        """
        self.data_list = queryset_or_tuple
        self.option = option
        self.verbose_name = verbose_name
        self.GET_data = GET_data

    def __iter__(self):
        """
        为了让传进来的对象都变成可迭代对象，就需要这个方法
        :return: 需要返回一个迭代器
        """

        elment_a = "<a href='?{url}'>{text}</a>"
        yield "<div class='whole'>"
        yield "<strong>{0}</strong>".format(self.verbose_name)
        yield "</div>"
        yield "<div class='other'>"

        total_query_dict = self.GET_data.copy()
        total_query_dict._mutable = True
        orgin_value_list = self.GET_data.getlist(self.option.field)  # 获取request.GET中传过来的已选中的数据
        if not orgin_value_list:
            yield "<a href='?%s' class='active'>全部</a>" % total_query_dict.urlencode()
        else:
            total_query_dict.pop(self.option.field)
            yield "<a href='?%s'>全部</a>" % total_query_dict.urlencode()

        for item in self.data_list:
            text = self.option.get_text_func(item)              # 这是每条数据的文本信息
            value = str(self.option.get_value_func(item))       # 这是每条数据对应的编号或者是ID

            query_dict = self.GET_data.copy()
            query_dict._mutable = True
            if not self.option.is_multi:                        # 这是支持单选的模式
                query_dict[self.option.field] = value
                if value in orgin_value_list:
                    query_dict.pop(self.option.field)            # 这是为了在同一个按钮上点击两次，可以取消原有的条件
                    yield "<a href='?{url}' class='active'>{text}</a>".format(text=text, url=query_dict.urlencode())
                else:
                    yield "<a href='?{url}'>{text}</a>".format(text=text, url=query_dict.urlencode())
            else:                                               # 这是支持多选的模式
                multi_value_list = query_dict.getlist(self.option.field)        # 先获取到当前字段所有的值
                if value in multi_value_list:
                    multi_value_list.remove(value)
                    query_dict.setlist(self.option.field, multi_value_list)
                    yield "<a href='?{url}' class='active'>{text}</a>".format(text=text, url=query_dict.urlencode())
                else:
                    multi_value_list.append(value)
                    query_dict.setlist(self.option.field, multi_value_list)
                    yield "<a href='?{url}'>{text}</a>".format(text=text, url=query_dict.urlencode())
        yield "</div>"


class SearchOption(object):
    """
    这是一个用于组合搜索功能的进行封装的类
    """
    def __init__(self, field, db_condition=None, text_func=None, value_func=None, is_choice=False, is_multi=False):
        """
        :param field: 组合搜索关联的字段
        :param db_condition:是数据库关联查询时的条件
        :param text_func:用于设置组合搜索按钮的文本内容
        :param value_func:用于设置组合搜索按钮的值或者ID
        """
        self.field = field
        if not db_condition:
            db_condition = {}
        self.db_condition = db_condition
        self.text_func = text_func
        self.value_func = value_func
        self.is_choice = is_choice
        self.is_multi = is_multi

    def get_db_condition(self, request, *args, **kwargs):
        """
        用于获取数据筛选条件，方便复写
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return self.db_condition

    def get_queryset_or_tuple(self, model_class, request, *args, **kwargs):
        """
        根据字段去获取关联的数据库关联的数据
        :return:
        """
        field_obj = model_class._meta.get_field(self.field)                                         # 获取到字段对象(万物皆对象嘛)
        if isinstance(field_obj, ForeignKey) or isinstance(field_obj,ManyToManyField):              # 判断字段的类型，是否为ForeignKey字段或者是否为ManyToManyField字段
            db_condition = self.get_db_condition(request, *args, **kwargs)
            # field_obj.related_model.objects.filter(**db_condition)这个是Queryset类型
            return SearchGroupRow(                                                                  # 通过字段对象获取ForeignKey的关联表，然后从关联表内取出符合配置要求的数据
                verbose_name=field_obj.verbose_name,
                queryset_or_tuple=field_obj.related_model.objects.filter(**db_condition),
                option=self,
                GET_data=request.GET,
            )
        else:                                                                                       # 判断字段的类型，是否为choice字段
            # field_obj.choices这个是元祖类型
            self.is_choice = True
            return SearchGroupRow(                                                                  # choices字段和其他的关联方式是不一样的，字段对象就带有一个choices属性，指向choices元祖
                verbose_name=field_obj.verbose_name,
                queryset_or_tuple=field_obj.choices,
                option=self,
                GET_data=request.GET,
            )

    def get_text_func(self, field_obj):
        """
        用于定制页面组合搜索展示的数据的文本内容
        :param field_obj:
        :return:
        """
        if self.text_func:          # 这是为开发者预留的钩子
            return self.text_func(field_obj)
        if self.is_choice:          # 这是当数据为元祖格式时
            return field_obj[1]
        else:                       # 这是当数据为Queryset格式时
            return str(field_obj)

    def get_value_func(self, field_obj):
        """
        用于定制页面组合搜索展示的数据的值或是ID
        :param field_obj:
        :return:
        """
        if self.value_func:  # 这是为开发者预留的钩子
            return self.value_func(field_obj)
        if self.is_choice:  # 这是当数据为元祖格式时
            return field_obj[0]
        else:  # 这是当数据为Queryset格式时
            return field_obj.pk


class StarkHandler(object):
    """
    这是一个公共的视图函数基类
    """
    per_page_count = 10                             # 默认每页显示的数量
    list_display = []                               # 开发者可以在'ModelHandler'中复写该属性，内置需要展示的表中的字段名称
    has_add_btn = True                             # 添加数据的按钮，默认每张表都有
    order_list = []                                 # 用于排序，默认按照id字段的降序进行排列（参考get_ordered_list方法）
    search_list = []                                # 为当前表配置搜索的字段，默认为空，'field'_contains表示或的意思, 例search_list = ["name_contains", "email_contains"]
    search_group = []                               # 配置需要进行组合搜索的字段，默认为空
    change_list_template = None                    # 展示页面的模板，可以使用默认的，也可以自定制
    edit_template = None                           # 展示页面的模板，可以使用默认的，也可以自定制
    delete_template = None                         # 展示页面的模板，可以使用默认的，也可以自定制

    def __init__(self, site, model_class, prev):
        """
        :param model_class: 这是models中的Depart表类
        """
        self.model_class = model_class
        self.prev = prev            # 开发者自定义的给表生成的URL所要加的前缀
        self.site = site            # 这是StarkSite单例模式的对象
        self.request = None         # 初始化request

    def get_ordered_list(self):
        """
        用于控制页面展示列表时的排序
        配合order_list属性使用
        默认按照ID字段的降序排列
        :return:
        """
        return self.order_list or ["-id",]

    def get_search_list(self):
        """
        search_list的钩子方法
        :return:
        """
        return self.search_list

    def get_search_group(self):
        """
        search_group的钩子方法
        :return:
        """
        return self.search_group

    @staticmethod
    def memory_reverse(request, name, *args, **kwargs):
        """
        这是当路由中有querydict保存的数据时，用来解析数据并反向解析生成URL的
        专门用来给反向解析的url携带上GET里面的数据
            例：http://127.0.0.1:8000/rbac/menu/edit/1/?_filter=mid%3D1
            - 在url中获取query_dict打包存入的数据
            - reverse反向解析生成url：/menu/list/
            - 对数据和url进行拼接
                /menu/list/?mid=1
        """
        url = reverse(name, args=args, kwargs=kwargs)  # 反向解析路径
        GET_data = request.GET.get("_filter")  # 获取原来url中的GET数据
        if GET_data:  # 如果有，进行字段拼接，返回新路径
            url = "%s?%s" % (url, GET_data)  # 把GET数据和url进行拼接
        return url

    @staticmethod
    def memory_url(request, name, *args, **kwargs):
        """
        这是保存GET数据使用的，把数据拼接到新的URL中
        用于保存原路径的GET数据，以便在新路径跳转回原路径时能携带上原路径的GET数据
        :param request: 用于获取request.GET中的数据
        :param name: url别名，用于反向生成url
        :param args: 要看自己写的url中是否有其他参数传入，例如{"pk":1}
        :param kwargs:
        :return:
        """
        basic_url = reverse(name, args=args, kwargs=kwargs)  # 先反向解析生成新的url
        if not request.GET:  # 当前路径中没有GET数据
            return basic_url
        GET_data = request.GET.urlencode()  # 获取GET中的所有数据
        # from django.http import QueryDict 需要引入
        query_dict = QueryDict(mutable=True)  # 实例化一个特殊的字典
        query_dict["_filter"] = GET_data  # 打包存入GET数据
        # query_dict.urlencode() 进行数据转译，防止造成"/menu/add/_filter=mid=1"这样改变结构的数据，而应该是"/menu/add/_filter=‘mid=1’"
        #         # 对反向解析的路径与GET数据进行拼接，做成新的url
        return "%s?%s" % (basic_url, query_dict.urlencode())

    def get_add_btn(self, request, *args, **kwargs):
        """
        通过判断来获取添加按钮
        :return:
        """
        if self.has_add_btn:
            # 别名需要手动拼接namespace:name
            name = "%s:%s" % (self.site.namespace, self.get_add_url_name)
            add_url = StarkHandler.memory_url(self.request, name, *args, **kwargs)
            add_btn = mark_safe("""
            <a class="btn btn-default" class="margin-right:20px;" href="%s">
                <i class="fa fa-plus-square" aria-hidden="true"></i> 添加数据
            </a>
            """ %(add_url))
            return add_btn
        return None

    @staticmethod
    def get_choice_text(title, field, *args, **kwargs):
        """
        用于对choices类型的字段进行表头和表体数据的展示
        :param title: 页面上展示的表头
        :param field: 数据库中choices类型的字段名
        :return:
        """
        def inner(self, obj=None, is_header=None, *args, **kwargs):
            """
            :param self:
            :param obj: 当前记录的对象
            :param is_header: 判断内容是在表头展示还是在表体
            :return:
            """
            if is_header:
                return title
            method = "get_%s_display" % field  # 手动拼接获取字段中文名的方法(get_field_display)
            return getattr(obj, method)()
        return inner

    def display_operation(self, obj=None, is_header=None, *args, **kwargs):
        """
        这里可以写上业务逻辑来根据用户的权限高低判断需要是否需要展示页面中的修改删除按钮
        :param obj:每一行的记录对象
        :param is_header:用于判断是放在表头还是在表内
        :return:mark_safe(字符串格式的标签) 或者其他内容
        """
        if is_header:                   # 如果这是是True，就表示这是对表头进行的编辑
            return "操作"
        else:                           #这表示对行内进行编辑
            # 这里进行别名拼接，用url的别名和路由分发的名称空间这两个值进行拼接
            # 这里进行拼接的namespace来自于StarkSite中的namespace属性
            edit_name = "%s:%s" %(self.site.namespace, self.get_edit_url_name)              # 修改按钮的别名
            delete_name = "%s:%s" %(self.site.namespace, self.get_delete_url_name)          # 删除按钮的别名
            edit_url = StarkHandler.memory_url(self.request, edit_name, *[obj.pk])
            delete_url = StarkHandler.memory_url(self.request, delete_name, *[obj.pk])
            # 这里放了编辑和修改两个按钮
            button = mark_safe("""
                <a style="color: #333333;" href="{0}">
                    <i class="fa fa-edit" aria-hidden="true"></i></a>
                |
                <a style="color: #d9534f;" href="{1}"><i
                        class="fa fa-trash-o"></i></a>
            """.format(edit_url, delete_url))
            return button

    def multi_delete(self, request, *args, **kwargs):
        """这是一段示范代码，用于示范添加一个自定义的批量操作选项,如果完成功能后想跳转其他页面，可以进行return，这里返回什么视图函数就返回什么"""
        pk_list = request.POST.getlist("pk")                    # 通过getlist把页面传来的所有被选中的数据ID都获取到
        self.model_class.objects.filter(id__in=pk_list).delete()
        # return redirect("https:\\www.baidu.com")
    multi_delete.text = "批量删除"

    action_list = [multi_delete, ]                        # 表展示界面的自定义批量操作，里面放的是实现功能的函数（函数一定要添加一个text属性，赋值这个操作的中文名字）

    def get_action_list(self):
        """
        获取自定义批量操作的钩子
        :return:
        """
        return self.action_list

    def display_checkbox(self, obj=None, is_header=None, *args, **kwargs):
        """
        这里用于生成批量操作的复选框按钮
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:                   # 如果这是是True，就表示这是对表头进行的编辑
            return "选择"
        else:                           #这表示对行内进行编辑
            button = mark_safe('<input type="checkbox" name="pk" value="%s">'% obj.pk)
            return button

    def get_list_display(self, request, *args, **kwargs):
        """
        开发者可以根据用户的不同在'Model'Handler类中通过复写(get_list_display)方法来控制页面上应该显示的列
        这个跟'Model'Handler类复写list_display不影响，因为get_list_display方法是根据用户不同来控制的，里面还有控制的逻辑
        :return:
        """
        value = []
        if self.list_display:
            value.extend(self.list_display)
            value.append(type(self).display_operation)
        return value

    model_form_class = None

    def get_model_form(self, add_or_edit, request, *args, **kwargs):
        """
        用于生成对应表的ModelForm
        self.model_form_class方便开发者自定义某个表是否需要增加或减少展示的字段
        add_or_edit用于判断传进来的这个ModelForm是用于修改的还是用于新增的
        :return:
        """
        if self.model_form_class:
            return self.model_form_class

        class DynamicModelForm(BootstrapModelForms):
            class Meta:
                model = self.model_class
                fields = "__all__"
        return DynamicModelForm

    def get_search_group_condition(self, request):
        """
        获取组合搜索的条件
        :return:
        """
        condition = {}
        for option in self.get_search_group():                              # 遍历组合搜索的所有条件字段
            if option.is_multi:
                value_list = request.GET.getlist(option.field)                   # 获取当前字段对应的URL中所有的搜索参数
                if not value_list:
                    continue
                else:
                    condition["%s__in" % option.field] = value_list             # 这里手动拼接SQL搜索条件{字段__in : [1,2,3,4....等等筛选数据ID]}
            else:
                value_list = request.GET.get(option.field)
                if not value_list:
                    continue
                else:
                    condition[option.field] = value_list
        return condition

    def get_queryset(self, request, *args, **kwargs):
        """一个用于开发者自定义筛选条件的钩子，通过自定义的条件来筛选符合的数据用于展示"""
        return self.model_class.objects

    def changelist_view(self, request, *args, **kwargs):
        """
        列表页面
            - self.list_display的查找顺序
                - 'Model'Handler()对象中找
                - 'Model'Handler类中找
                - StarkHandler类中找
        :param request:
        :param self.list_display: 页面要显示的列(要显示的表中的字段)
        :param self.model_class: 用户要访问的表
        :return:
        """
        # ********************************************需要初始化的数据**************************************************
        order_list = self.get_ordered_list()  # 获取排序
        # ********************************************自定义批量操作下拉菜单********************************************
        action_list = self.get_action_list()                                         # 获取自定义批量操作函数的列表
        action_dict = {func.__name__: func.text for func in action_list}            # 为了页面能进行展示并方便后期调用函数，选择使用字典格式，key是函数名，value是函数的中文名
        """
        action_dict = {
            函数名:函数中文名,
        }
        """
        if request.method == "POST":
            func_name = request.POST.get("batch_operation")                       # 获取被选中的批量操作的函数名称
            if func_name and func_name in action_dict:                              # 判断批量操作选项是否忘记了选，从而设置了默认选项
                action_response = getattr(self, func_name)(request, *args, **kwargs) # 通过反射来查找批量操作的函数，执行对应的函数，并把提交来的所有数据的ID的列表传进函数内
                if action_response:
                    return action_response
        # ********************************************进行关键字搜索操作************************************************
        search_list = self.get_search_list()  # 获取搜索位置的字段
        if not search_list:                                        # 如果当前表没有定义搜索的字段，则不显示搜索框，反之就显示
            search_list = None
        keyword = request.GET.get("keyword", "")
        conn = Q()  # 实例化一个Q查询对象，用于构造搜索条件
        if keyword:                                                 # 获取搜索关键字
            conn.connector = "OR"                                   # 指明里面的多个关系之间用or(或)链接
            for condition in search_list:
                conn.children.append((condition, keyword))          # 批量导入搜索的字段和关键字，来批量生成搜索条件
        prev_queryset = self.get_queryset(request, *args, **kwargs)
        search_group_condition = self.get_search_group_condition(request)                       # 获取组合搜索的条件也同样加到filter里面进行过滤
        query_set = prev_queryset.filter(conn).filter(**search_group_condition).order_by(*order_list)
        # ********************************************做一个分页器******************************************************
        # 实例化一个分页器对象
        """
        做一个分页器
        1.根据用户访问的页面，计算出数据库索引的位置
        2.生成HTML中的页码
        """
        data_count = query_set.count()                              # 从数据库中获取所有的数据
        query_params = request.GET.copy()                           # 复制GET中的所有数据
        query_params._mutable = True                                # 设置request.GET中的数据可以被修改
        pager = Pagination(
            current_page=request.GET.get("page"),                   # 获取当前页码
            all_count=data_count,                                    # 表中数据的数量
            base_url=request.path_info,                              # 基础URL
            query_params=query_params,                               # GET中原有的数据
            per_page=self.per_page_count,                            # 每页显示的条数
        )
        # ********************************************进行页面表头部分的展示********************************************
        # 获取表头需要展示的部分
        header_list = []                                                                    # 用于存放表头的verbose_name(中文名称)
        list_display = self.get_list_display(request, *args, **kwargs)                                              # 根据用户的不同来定制不同的列
        if list_display:                                                                    # 这里是表进行了自定义展示列的情况
            for field_or_func in list_display:
                if isinstance(field_or_func, FunctionType):                                 # 判断列表中这个元素是一个字符串还是一个函数(用于展示修改删除按钮的)
                    verbose_name = field_or_func(self, obj=None, is_header=True, *args, **kwargs)           # 如果是一个函数，就执行这个函数
                else:
                    verbose_name = self.model_class._meta.get_field(field_or_func).verbose_name         # 通过字段获取当初在表中设置的该字段的verbose_name
                header_list.append(verbose_name)
        else:                                                                               # 这里是默认展示的情况
            header_list.append(self.model_class._meta.model_name)
        # ********************************************进行页面表内部分的展示********************************************
        # 处理表内展示的内容
        data_list = []
        # 从数据库中获取所有的数据(通过页码来进行切片，决定一次取出多少数据)
        data_queryset = query_set[pager.start:pager.end]
        for row in data_queryset:
            row_list = []                                                                       # 为每个row记录初始化一个空列表用于存放每个对应字段的值
            if list_display:                                                                    # 这是当自定义展示时的处理
                for field_or_func in list_display:
                    if isinstance(field_or_func, FunctionType):                                 # 用于判断开发者是否在列表内放了函数(用于展示的修改删除按钮)
                        row_list.append(field_or_func(self, obj=row, is_header=False, *args, **kwargs))          # 把生成的按钮也放入需要展示的列表中
                    else:
                        row_list.append(getattr(row, field_or_func))                            # 通过反射来获取每个记录中对应字段的值
            else:
                row_list.append(row)                                                            # 如果是默认展示的情况，就直接展示记录对象，不对记录字段进行展开显示
            data_list.append(row_list)                                                          # 把一个row完整的数据存放到汇总的列表中
        # ********************************************组合搜索功能******************************************************
        search_group_row_list = []
        search_group = self.get_search_group()                                                               # 获取组合搜索字段列表
        for search_option_obj in search_group:                                                              # 根据str格式的字段名去对应的表中获取字段，并根据对象去获取关联数据
            # 这个row可能是元祖类型或者是Queryset类型
            row = search_option_obj.get_queryset_or_tuple(self.model_class, request, *args, **kwargs)       # 根据开发者自定义的字段和条件来获取相应的数据，用于展示组合搜索
            search_group_row_list.append(row)
        # ********************************************给页面设置一个公用的数据添加按钮**********************************
        add_btn = self.get_add_btn(request, *args, **kwargs)                    # 处理添加按钮

        return render(
            request,
            self.change_list_template or "stark/change_list.html",
            {
            "data_list": data_list,
            "header_list": header_list,
            "pager": pager,
            "add_btn":add_btn,
            "search_list": search_list,
            "current_keyword": keyword,
            "action_dict": action_dict,
            "search_group_row_list": search_group_row_list,
            }
        )

    def save(self, request, form, is_update, *args, **kwargs):
        """
        如果自定义的modelform类中有没有展示的字段，但是在添加或者修改记录时需要这个字段，这里就用来给这些字段
        添加默认值，防止其报错，开发者只需要在对应的"ModelHandler"内复写该方法然后自己设置默认值即可。
        :param form:当前使用的form对象
        :param is_update:判断是添加操作的form还是修改操作的form
        :return:
        """
        form.save()

    def add_view(self, request, *args, **kwargs):
        """
        添加页面
        :return:
        """
        model_form_class = self.get_model_form("add", request, *args, **kwargs)
        if request.method == "GET":
            form = model_form_class()
            return render(request, "stark/change.html", {"form": form})
        form = model_form_class(data=request.POST)
        if form.is_valid():                                                         # 判断用户输入的内容是否合法
            response = self.save(request, form, False, *args, **kwargs)
            name = "%s:%s" % (self.site.namespace, self.get_list_url_name)
            return response or redirect(StarkHandler.memory_reverse(self.request, name, *args, **kwargs))       # 跳转会列表页面
        return render(request, self.edit_template or "stark/change.html", {"form": form})

    def get_edit_object(self, request, pk, is_delete, *args, **kwargs):
        return self.model_class.objects.filter(id=pk).first()

    def edit_view(self, request, pk, *args, **kwargs):
        """
        修改页面
        :param request:
        :param pk:
        :return:
        """
        current_obj = self.get_edit_object(request, pk, False, *args, **kwargs)        # 获取当前要修改数据的对象
        model_form_class = self.get_model_form("edit", request, *args, **kwargs)
        if not current_obj:
            return render(request, "rbac/refuse.html", {"error_msg": "违规操作：未找到需要修改的数据，请重新选择！"})
        if request.method == "GET":
            form = model_form_class(instance=current_obj)
            return render(request, "stark/change.html", {"form": form})
        form = model_form_class(data=request.POST, instance=current_obj)
        if form.is_valid():  # 判断用户输入的内容是否合法
            response = self.save(request, form, True, *args, **kwargs)
            name = "%s:%s" % (self.site.namespace, self.get_list_url_name)
            return response or redirect(StarkHandler.memory_reverse(self.request, name, *args, **kwargs))  # 跳转会列表页面
        return render(request, self.edit_template or "stark/change.html", {"form": form})

    def delete_object(self, request, pk, *args, **kwargs):
        return self.model_class.objects.filter(id=pk)

    def delete_view(self, request, pk, *args, **kwargs):
        """
        删除页面
        :param request:
        :param pk:
        :return:
        """
        name = "%s:%s" % (self.site.namespace, self.get_list_url_name)
        url = StarkHandler.memory_reverse(request, name, *args, **kwargs)
        current_obj = self.delete_object(request, pk, *args, **kwargs)
        if request.method == "GET":
            # delete模板中的取消按钮，没有具体指向哪个页面，就是为了其他地方也能复用，于是决定从views中灵活传送这个跳转地址
            return render(request, self.delete_template or "rbac/delete.html", {"cancel_url": url})
        if not current_obj:
            return render(request, "rbac/refuse.html", {"error_msg": "违规操作：未找到需要删除的数据，请重新选择！"})
        current_obj.delete()
        return redirect(url, *args, **kwargs)

    def get_url_name(self, param):
        """
        动态生成url的别名
        :param param: [list, add, edit, del ...]
        :return:
        """
        app_name = self.model_class._meta.app_label
        model_name = self.model_class._meta.model_name
        if self.prev:
            return "%s_%s_%s_%s" % (app_name, model_name, self.prev, param)
        return "%s_%s_%s" % (app_name, model_name, param)

    @property
    def get_list_url_name(self):
        """
        获取列表页面URL的name
        :return:
        """
        return self.get_url_name("list")

    @property
    def get_add_url_name(self):
        """
        获取添加页面URL的name
        :return:
        """
        return self.get_url_name("add")

    @property
    def get_edit_url_name(self):
        """
        获取修改页面URL的name
        :return:
        """
        return self.get_url_name("edit")

    @property
    def get_delete_url_name(self):
        """
        获取删除页面URL的name
        :return:
        """
        return self.get_url_name("del")

    def wapper(self, func):
        """
        这个闭包用于更新request
        :param func: 各个视图函数
        :return:
        """
        @functools.wraps(func)              # 用于保留原函数的原信息
        def inner(reuqest, *args, **kwargs):
            self.request = reuqest
            return func(reuqest, *args, **kwargs)
        return inner

    def get_urls(self):
        """
        注：这个只能减少URL
        开发者可以通过在'ModelHandler'类中复写get_urls方法来减少一张表中的URL
        在这里做一个路由分发，让开发者自定义一张表需要几个操作URL
        例：
            class DepartHandler(StarkHandler):
                def get_urls(self):
                    patterns = [
                        url("^add/$", self.add_view),
                        url("^edit/(\d+)/$", self.edit_view),
                        url("^del/(\d+)/$", self.delete_view),
                    ]
        :return:
        """
        patterns = [
            url("^list/$", self.wapper(self.changelist_view), name=self.get_list_url_name),
            url("^add/$", self.wapper(self.add_view), name=self.get_add_url_name),
            url("^edit/(?P<pk>\d+)/$", self.wapper(self.edit_view), name=self.get_edit_url_name),
            url("^del/(?P<pk>\d+)/$", self.wapper(self.delete_view), name=self.get_delete_url_name),
        ]
        patterns.extend(self.extra_urls())
        return patterns

    def extra_urls(self):
        """
        注：这个只能增加URL
        开发者可以通过在'ModelHandler'类中复写extra_urls方法来增加一张表中的URL
        这是一个钩子函数，用于查看开发者是否为表定制了多于现有4种的URL，如果就，就让开发者自定义的extra_urls来为get_urls传值
        然后通过patterns.extend(self.extra_urls())来把用户多加的URL给传进来
        例：
            注：路由别名：app名称_表名称_操作名称
            例：app01_depart_test
            app_name = self.model_class._meta.app_label
            model_name = self.model_class._meta.model_name
            class DepartHandler(StarkHandler):
                def extra_urls(self):
                    patterns = [
                        url("^test/$", self.test_view, name=要注意别名的获取),
                    ]
                def test_view(self, request, pk):
                    这里就可以写用户为第五个URL写的视图函数
                    pass
        :return:
        """
        return []


class StarkSite(object):
    """
    这是一个单例模式的类，用于给各个APP自动生成对表进行操作(增删改查)的URL
    """
    def __init__(self):
        """
        初始化三个参数
            - _registry
                - 数据格式为：
                    site._register = [
                        {
                            'model_class': <class 'app01.models.Depart'>,
                            'handler': <app01.stark.DepartHandler object at 0x029CF110>
                            # handler里面对象有一个model_class = models.Depart
                        },
                        {
                            'model_class': <class 'app01.models.Customer'>,
                            'handler': <app01.stark.CustomerHandler object at 0x029CF0F0>
                            # handler里面对象有一个model_class = models.Customer
                        },
                        {
                            'model_class': <class 'app02.models.Host'>,
                            'handler': <app02.stark.HostHandler object at 0x029CF290>
                            # handler里面对象有一个model_class = models.Host
                        }
                    ]
            - app_name
            - namespace
        """
        self._registry = []                 # 用于存放各处添加来的项目中需要进行增删改查操作的表类
        self.app_name = "stark"             # 设置的路由分发的app_name
        self.namespace = "stark"            # 设置的路由分发的namespace

    def register(self, model_class, handler_class=None, prev=None):
        """
        用于获取在项目启动前获取来的所有表类和用于生成增删改查的视图函数类
        :param model_class: Models各个表对应的类(models.Host  models.Customer  models.Depart)
        :param handler_class: 处理请求的视图函数所在的类，默认为StarkHandler
        :param prev: 用于可能加在url中的前缀，位置可以自己设置，默认为None
        :return:
        """
        if not handler_class:
            handler_class = StarkHandler
        self._registry.append({
            "model_class": model_class,                                     # 接受的是需要操作的表类对象
            "handler": handler_class(self, model_class, prev),              # 实例化视图函数类，并把表类传参进去
            "prev": prev,                                                   # 接受的是可能需要加到url各种位置的前缀
        })

    def get_urls(self):
        """
        为所有表类动态生成增删改查的URL和视图函数
        :return:
        """
        partterns = []                                      # 这个空列表用于存放当前函数产出的为每一个models表生成的4个URL(增删改查)
        for item in self._registry:                         # 在此遍历self._registry，在项目启动前已经把所有APP中的model添加到这里面了
            model_class = item["model_class"]               # 获取当前循环对象的表类
            app_label = model_class._meta.app_label         # 获取这个表类所在的APP的名称
            model_name = model_class._meta.model_name       # 获取这个表类的名称
            handler = item["handler"]                       # 获取当前这个表的操作类的对象，用于生成增删改查视图函数
            prev = item["prev"]                             # 需要加入到路径url中的前缀，默认为空

            if prev:
                # 针对在路由中添加自定义前缀的情况，就给这个路由再做一级路由分发，这里就是通过/appname/model_name/ 这个URL再往后进行分发
                partterns.append(url(r"^%s/%s/%s/" % (app_label, model_name, prev), (handler.get_urls(), None, None)))

            else:
                # 对于任何一级的路由，之后还有后缀就可以做分发，这里就是通过/appname/model_name/ 这个URL再往后进行分发
                # 进行url拼接和绑定视图函数，并把组合好的url传进partterns列表
                partterns.append(url(r"^%s/%s/" % (app_label, model_name), (handler.get_urls(), None, None)))
        return partterns

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.namespace           # 按照include函数的方式返回路由分发的三个参数


site = StarkSite()
