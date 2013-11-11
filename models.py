# coding: utf-8

from quokka.core.db import db
from quokka.utils import get_current_user
from quokka.core.models import Publishable, Slugged
from quokka.modules.cart.models import BaseProduct, BaseProductReference, Cart
from flask.ext.babel import lazy_gettext as _l


class ClassRoom(Slugged, Publishable, db.EmbeddedDocument):
    WEEKDAYS = (
        ("sun", _l("Sunday")),
        ("mon", _l("Monday")),
        ("tue", _l("Tuesday")),
        ("wed", _l("Wednesday")),
        ("thu", _l("Thursday")),
        ("fri", _l("Friday")),
        ("sat", _l("Saturday")),
    )
    title = db.StringField(required=True, max_length=100)
    description = db.StringField()
    weekdays = db.ListField(db.StringField(choices=WEEKDAYS), default=[])
    start_date = db.DateTimeField()
    end_date = db.DateTimeField()
    status = db.StringField()

    def get_description(self):
        return "<br>".join(
            [self.title,
             self.description,
             ",".join(self.weekdays),
             self.start_date.strftime("%Y-%m-%d") if self.start_date else '']
        )

    def get_weekdays_display(self, **kwargs):
        data = dict(self.WEEKDAYS)
        data.update(kwargs)
        return [data.get(k) for k in self.weekdays]

    def clean(self):
        self.validate_slug()

    def __unicode__(self):
        return self.title


class CourseVariant(Slugged, db.EmbeddedDocument):
    title = db.StringField(required=True, max_length=100)
    description = db.StringField()
    unity_value = db.FloatField()

    def get_description(self):
        return "<br>".join([self.title, self.description])

    def __unicode__(self):
        return self.title


class Course(BaseProduct):
    pre_requisites = db.StringField()
    duration = db.StringField()
    classes = db.ListField(db.EmbeddedDocumentField(ClassRoom))
    variants = db.ListField(db.EmbeddedDocumentField(CourseVariant))

    def get_description(self, *args, **kwargs):

        try:
            classroom = self.classes.get(slug=kwargs.get('classroom'))
        except:
            classroom = None

        if not classroom:
            return self.description

        return "".join([self.description, classroom.get_description()])

    def get_summary(self, *args, **kwargs):

        try:
            classroom = self.classes.get(slug=kwargs.get('classroom'))
        except:
            classroom = None

        summary = getattr(self, 'summary', None)
        if not summary:
            try:
                return self.get_description(*args, **kwargs)[:140]
            except:
                summary = self.title

        if not classroom:
            return summary

        return "<br>".join([summary, classroom.get_description()])

    def is_unique_slug(self, items):
        if not items:
            return True
        slugs = [item.slug for item in items]
        return len(slugs) == len(set(slugs))

    def clean(self):
        [cls.clean() for cls in self.classes]
        if not self.is_unique_slug(self.classes):
            raise db.ValidationError("Classroom slugs duplicated")
        if not self.is_unique_slug(self.variants):
            raise db.ValidationError("Variants slugs duplicated")


class Subscriber(db.DynamicDocument):
    name = db.StringField()
    email = db.EmailField()
    document = db.StringField()
    phone = db.StringField()
    address = db.StringField()
    user = db.ReferenceField('User', default=get_current_user,
                             reverse_delete_rule=db.NULLIFY)

    def __unicode__(self):
        return self.name


class CourseSubscription(BaseProductReference,
                         Publishable, db.DynamicDocument):
    subscriber = db.ReferenceField(Subscriber, reverse_delete_rule=db.NULLIFY)
    student = db.ReferenceField(Subscriber, reverse_delete_rule=db.NULLIFY)
    course = db.ReferenceField(Course, required=True,
                               reverse_delete_rule=db.DENY)
    classroom = db.StringField()
    variant = db.EmbeddedDocumentField(CourseVariant)
    status = db.StringField(default="pending")
    unity_value = db.FloatField()
    total_value = db.FloatField()
    cart = db.ReferenceField(Cart, reverse_delete_rule=db.NULLIFY)
    confirmed_date = db.DateTimeField()

    def clean(self):
        self.unity_value = self.get_unity_value()

    def __unicode__(self):
        if self.variant:
            return u"{s.course.title} {s.classroom} {s.variant}".format(s=self)
        else:
            return self.course.title

    def get_title(self):
        return self.course.get_title()

    def get_description(self):
        return "<br>".join(
            [self.course.get_summary(classroom=self.classroom),
             self.variant.get_description() if self.variant else '',
             self.student.name if self.student else '']
        )

    def get_unity_value(self):
        if self.unity_value:
            return self.unity_value
        if self.variant and self.variant.unity_value:
            return self.variant.unity_value
        return self.course.get_unity_value()

    def get_weight(self):
        return getattr(self, 'weight', None)

    def get_dimensions(self):
        return getattr(self, 'dimensions', None)

    def get_extra_value(self):
        return getattr(self, 'extra_value', None)

    def get_uid(self):
        return str(self.id)

    def set_status(self, status, *args, **kwargs):
        self.status = status
        if status == "confirmed":
            self.confirmed_date = kwargs.get('date')
        self.save()
