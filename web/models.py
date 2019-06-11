from django.db import models
from rbac import models as md

# Create your models here.


class School(models.Model):
    """校区表"""
    title = models.CharField(verbose_name="校区", max_length=32)

    def __str__(self):
        return self.title


class Department(models.Model):
    """部门表"""
    title = models.CharField(verbose_name="部门", max_length=32)

    def __str__(self):
        return self.title


class Staff(md.UserInfo):
    """员工表"""
    name = models.CharField(verbose_name="姓名", max_length=32)
    phone = models.CharField(verbose_name="手机号", max_length=32)
    age = models.CharField(verbose_name="年龄", max_length=32)
    gender_choice = ((1, "男"), (2, "女"))
    gender = models.IntegerField(verbose_name="性别", choices=gender_choice, default=1)
    depart = models.ForeignKey(verbose_name="部门", to="Department", on_delete=False)

    def __str__(self):
        return self.name


class Course(models.Model):
    """课程表"""
    name = models.CharField(verbose_name="课程", max_length=32)

    def __str__(self):
        return self.name


class ClassList(models.Model):
    """班级表"""
    school = models.ForeignKey(verbose_name="校区", to="School", on_delete=False)
    course = models.ForeignKey(verbose_name="课程名称", to="Course", on_delete=False)
    semester = models.IntegerField(verbose_name="班级(期)")
    price = models.IntegerField(verbose_name="学费")
    start_date = models.DateField(verbose_name="开班日期", null=True, blank=True)
    graduate_date = models.DateField(verbose_name="结业日期", null=True, blank=True)
    tutor = models.ForeignKey(verbose_name="班主任", to="Staff", related_name="classes", on_delete=False, limit_choices_to={"depart__title":"教务部"})
    teacher = models.ManyToManyField(verbose_name="任课老师", to="Staff", related_name="teach_class", limit_choices_to={"depart__title__in": ["python教学部", "Linux教学部", "java教学部", "大数据教学部"]})
    memo = models.CharField(verbose_name="说明", max_length=255, blank=True, null=True)

    def __str__(self):
        return "{0}{1}期".format(self.course.name, self.semester)


class Customer(models.Model):
    """客户表"""
    MAX_PRIVATE_CUSTOMER_COUNT = 150
    name = models.CharField(verbose_name="客户姓名", max_length=64)
    qq = models.CharField(verbose_name="联系方式", max_length=64, unique=True, help_text="QQ/微信/手机号")
    status_choices = [(1, "已报名"), (2, "未报名")]
    status = models.IntegerField(verbose_name="客户状态", choices=status_choices, default=2)
    gender_choices = [(1, "男"),(2, "女")]
    gender = models.IntegerField(verbose_name="性别", choices=gender_choices,)
    source_choices = [
        (1, "QQ群"),
        (2, "内部转介绍"),
        (3, "官方网站"),
        (4, "百度推广"),
        (5, "360推广"),
        (6, "搜狗推广"),
        (7, "腾旭课堂"),
        (8, "广点通"),
        (9, "高校宣讲"),
        (10, "渠道代理"),
        (11, "5lcto"),
        (12, "智汇推"),
        (13, "网流"),
        (14, "DSP"),
        (15, "SEO"),
        (16, "其他"),
    ]
    source = models.IntegerField(verbose_name="客户来源", choices=source_choices, default=1)
    referral_from = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        verbose_name="转介绍信息",
        help_text="若此客户是转介绍学员，请在此处选择内部学员姓名",
        related_name="internal_referral",
        on_delete=False,
    )
    course = models.ManyToManyField(verbose_name="咨询课程", to="Course")
    consultant = models.ForeignKey(verbose_name="课程顾问", to="Staff", related_name="consultant", null=True, blank=True, on_delete=False, limit_choices_to={"depart__title":"销售部"})
    education_choices = (
        (1, "重点大学"),
        (2, "普通本科"),
        (3, "独立院校"),
        (4, "民办本科"),
        (5, "大专"),
        (6, "民办专科"),
        (7, "高中"),
        (8, "其他"),
    )
    education = models.IntegerField(verbose_name="客户学历", choices=education_choices, blank=True, null=True)
    graduation_school = models.CharField(verbose_name="毕业院校", max_length=64, blank=True, null=True)
    major = models.CharField(verbose_name="所学专业", max_length=64, blank=True, null=True)
    experience_choices = [
        (1, "在校生"),
        (2, "应届毕业"),
        (3, "半年以内"),
        (4, "半年至一年"),
        (5, "一年至三年"),
        (6, "三年至五年"),
        (7, "五年以上"),
    ]
    experience = models.IntegerField(verbose_name="工作经验", blank=True, null=True, choices=experience_choices)
    work_status_choices = [
        (1, "在职"),
        (2, "无业"),
    ]
    work_status = models.IntegerField(verbose_name="职业状态", blank=True, null=True, choices=work_status_choices)
    company = models.CharField(verbose_name="目前就职公司", max_length=64, blank=True, null=True)
    date = models.DateField(verbose_name="咨询日期", auto_now_add=True)
    last_consult_date = models.DateField(verbose_name="最后跟进日期", auto_now_add=True)

    def __str__(self):
        return "姓名:{name},联系方式:{tel}".format(name=self.name, tel=self.qq)


class ConsultRecord(models.Model):
    """客户跟进表"""
    customer = models.ForeignKey(verbose_name="客户", to="Customer", on_delete=False)
    consultant = models.ForeignKey(verbose_name="跟踪人", to="Staff", on_delete=False, limit_choices_to={"depart__title":"销售部"})
    date = models.DateField(verbose_name="跟进日期", auto_now_add=True)
    note = models.TextField(verbose_name="跟进内容")

    def __str__(self):
        return self.customer


class PaymentRecord(models.Model):
    """缴费记录表"""
    customer = models.ForeignKey(verbose_name="客户", to="Customer", on_delete=False)
    consultant = models.ForeignKey(verbose_name="课程顾问", to="Staff", help_text="谁签单就选谁", on_delete=False)
    pay_type_choice = [
        (1, "报名费"),
        (2, "学费"),
        (3, "退费"),
        (4, "其他"),
    ]
    pay_type = models.IntegerField(verbose_name="费用类型", choices=pay_type_choice, default=1)
    paid_fee = models.IntegerField(verbose_name="金额", default=0)
    class_list = models.ForeignKey(verbose_name="申请班级", to="ClassList", on_delete=False)
    apply_date = models.DateField(verbose_name="申请日期", auto_now_add=True)
    confirm_status_choices = [
        (1, "申请中"),
        (2, "已确认"),
        (3, "已驳回"),
    ]
    confirm_status = models.IntegerField(verbose_name="确认状态", choices=confirm_status_choices, default=1)
    confirm_date = models.DateField(verbose_name="确认日期", null=True, blank=True)
    confirm_user = models.ForeignKey(verbose_name="审批人", to="Staff", related_name="confirms", null=True, blank=True, on_delete=False)
    note = models.TextField(verbose_name="备注", blank=True, null=True)


class Student(models.Model):
    """正式学员表"""
    customer = models.OneToOneField(verbose_name="客户姓名", to="Customer", on_delete=False)
    qq = models.CharField(verbose_name="QQ号", max_length=32)
    mobile = models.CharField(verbose_name="手机号", max_length=32)
    emergency_contract = models.CharField(verbose_name="紧急联系人", max_length=32)
    class_list = models.ManyToManyField(verbose_name="已报班级", to="ClassList", blank=True)
    student_status_choices = [
        (1, "申请中"),
        (2, "在读"),
        (3, "毕业"),
        (4, "退学"),
    ]
    score = models.IntegerField(verbose_name="学分", default=100)
    student_status = models.IntegerField(verbose_name="学员状态", choices=student_status_choices, default=1)
    memo = models.CharField(verbose_name="备注", max_length=255, blank=True, null=True)

    def __str__(self):
        return self.customer.name


class ScoreRecord(models.Model):
    """积分管理表"""
    student = models.ForeignKey(verbose_name="学生", to="Student", on_delete=False)
    content = models.TextField(verbose_name="扣分理由")
    score = models.IntegerField(verbose_name="分值", help_text="违纪扣分写负值，表现良好写正值")
    user = models.ForeignKey(verbose_name="执行人", to="Staff", on_delete=False)


class CourseRecord(models.Model):
    """上课记录表"""
    class_object = models.ForeignKey(verbose_name="班级", to="ClassList", on_delete=False)
    day_num = models.IntegerField(verbose_name="节次")
    teacher = models.ForeignKey(verbose_name="讲师", to="Staff", on_delete=False)
    date = models.DateField(verbose_name="上课日期", auto_now_add=True)

    def __str__(self):
        return "{0}day{1}".format(self.class_object, self.day_num)


class StudyRecord(models.Model):
    """考勤记录表"""
    course_record = models.ForeignKey(verbose_name="出勤课程", to="CourseRecord", on_delete=False)
    student = models.ForeignKey(verbose_name="学员", to="Student", on_delete=False)
    record_choices = (
        (1, "已签到"),
        (2, "请假"),
        (3, "迟到"),
        (4, "缺勤"),
        (5, "早退"),
    )
    record = models.IntegerField(verbose_name="上课记录", choices=record_choices, default=1,)
