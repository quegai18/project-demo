# -*- coding: utf-8 -*-
# __author__ = "LiuWei"
# Email: 512774725@qq.com
from stark.service.start_assembly import site
from web import models
from web.views.school import SchoolHandler
from web.views.department import DepartmentHandler
from web.views.staff import StaffHandler
from web.views.course import CourseHandler
from web.views.classlist import ClassListHandler
from web.views.private_customer import PrivateCustomerHandler
from web.views.public_customer import PunlicCustomerHandler
from web.views.consultrecord import ConsultrecordHandler
from web.views.paymentrecord import PaymentRecordHandler
from web.views.student import StudentHandler
from web.views.check_paymentrecord import CheckPaymentRecordHandler
from web.views.score import ScoreHandler
from web.views.courserecord import CourseRecordHandler
from web.views.studyrecord import StudyRecordHandler

site.register(model_class=models.School, handler_class=SchoolHandler)

site.register(model_class=models.Department, handler_class=DepartmentHandler)

site.register(model_class=models.Staff, handler_class=StaffHandler)

site.register(model_class=models.Course, handler_class=CourseHandler)

site.register(model_class=models.ClassList, handler_class=ClassListHandler)

site.register(model_class=models.Customer, handler_class=PrivateCustomerHandler, prev="private")

site.register(model_class=models.Customer, handler_class=PunlicCustomerHandler, prev="public")

site.register(model_class=models.ConsultRecord, handler_class=ConsultrecordHandler)

site.register(model_class=models.PaymentRecord, handler_class=PaymentRecordHandler)

site.register(model_class=models.PaymentRecord, handler_class=CheckPaymentRecordHandler, prev="check")

site.register(model_class=models.Student, handler_class=StudentHandler)

site.register(model_class=models.ScoreRecord, handler_class=ScoreHandler)

site.register(model_class=models.CourseRecord, handler_class=CourseRecordHandler)

site.register(model_class=models.StudyRecord, handler_class=StudyRecordHandler)
