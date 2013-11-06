# coding: utf-8

from quokka import admin
from quokka.core.admin.models import ModelAdmin
from quokka.core.admin import _, _l
#from quokka.modules.cart.admin import ProductAdmin
from .models import Course, CourseSubscription


class CourseSubscriptionAdmin(ModelAdmin):
    roles_accepted = ('admin', 'editor')


admin.register(Course, category=_("Classes"), name=_l("Course"))
admin.register(CourseSubscription,
               CourseSubscriptionAdmin,
               category=_("Classes"),
               name=_l("Subscription"))
