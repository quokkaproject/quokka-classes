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
    weekdays = db.ListField(db.StringField(choices=WEEKDAYS))
    start_date = db.DateTimeField()
    end_date = db.DateTimeField()
    status = db.StringField()

    def clean(self):
        self.validate_slug()


class CourseVariant(Slugged, db.EmbeddedDocument):
    title = db.StringField(required=True, unique=True, max_length=100)
    description = db.StringField()
    unity_value = db.FloatField()

    def get_description(self):
        return "<br>".join([self.title, self.description])

class Course(BaseProduct):
    pre_requisites = db.StringField()
    duration = db.StringField()
    classes = db.ListField(db.EmbeddedDocumentField(ClassRoom))
    variants = db.ListField(db.EmbeddedDocumentField(CourseVariant))

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


class CourseSubscription(BaseProductReference,
                         Publishable, db.DynamicDocument):
    belongs_to = db.ReferenceField('User', default=get_current_user)
    student_user = db.ReferenceField('User', default=get_current_user)
    course = db.ReferenceField(Course, required=True)
    classroom = db.StringField()
    variant = db.EmbeddedDocumentField(CourseVariant)
    status = db.StringField(default="pending")
    unity_value = db.FloatField()
    total_value = db.FloatField()
    cart = db.ReferenceField(Cart)
    confirmed_date = db.DateTimeField()

    def get_title(self):
        return self.course.get_title()

    def get_description(self):
        return "<br>".join(
            [self.course.get_description(),
             self.variant.get_description() if self.variant else '']
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
