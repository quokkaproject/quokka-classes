# coding: utf-8

from quokka import admin
from quokka.core.admin.models import ModelAdmin, BaseContentAdmin
from quokka.core.admin import _, _l
from quokka.core.widgets import TextEditor, PrepopulatedText
from .models import Course, CourseSubscription, Subscriber


class CourseAdmin(BaseContentAdmin):

    column_searchable_list = ('title', 'description', 'summary')

    form_args = {
        "description": {"widget": TextEditor()},
        "slug": {"widget": PrepopulatedText(master='title')}
    }

    form_columns = ['title', 'slug', 'channel', 'related_channels', 'summary',
                    'description', 'published',
                    'unity_value',
                    'pre_requisites',
                    'duration',
                    'classes',
                    'variants',
                    'contents',
                    'show_on_channel', 'available_at', 'available_until',
                    'tags', 'values', 'template_type']

    form_subdocuments = {
        'classes': {
            'form_subdocuments': {
                None: {
                    'form_columns': (
                        'title', 'slug', 'description',
                        'start_date', 'end_date',
                        'weekdays', 'status', 'published'
                    )
                }
            }
        },
        'contents': {
            'form_subdocuments': {
                None: {
                    'form_columns': ('content', 'caption', 'purpose', 'order'),
                    'form_ajax_refs': {
                        'content': {
                            'fields': ['title', 'long_slug', 'summary']
                        }
                    }
                }
            }
        },
    }


class CourseSubscriptionAdmin(ModelAdmin):
    roles_accepted = ('admin', 'editor')
    column_list = [
        'course', 'classroom', 'variant',
        'student', 'subscriber',
        'status', 'confirmed_date',
        'unity_value',
        'published'
    ]

    form_columns = [
        'course', 'classroom', 'variant',
        'student', 'subscriber',
        'status', 'confirmed_date',
        'unity_value',
        'published', 'available_at', 'available_until',
        'created_at',
        'cart'
    ]


class SubscriberAdmin(ModelAdmin):
    roles_accepted = ('admin', 'editor')

admin.register(Course, CourseAdmin, category=_("Classes"), name=_l("Course"))

admin.register(Subscriber,
               SubscriberAdmin,
               category=_("Classes"),
               name=_l("Subscriber"))

admin.register(CourseSubscription,
               CourseSubscriptionAdmin,
               category=_("Classes"),
               name=_l("Subscription"))
