# coding: utf-8
import random
from flask import request, url_for, redirect
from flask.ext.security import current_user
from flask.views import MethodView

from quokka.core.templates import render_template
from quokka.modules.cart.models import Cart, Item
from quokka.modules.accounts.models import User

from .models import Course, Subscriber, CourseSubscription, CourseVariant


class SubscribeView(MethodView):
    def post(self):
        course_id = request.form.get('course_id')
        classroom = request.form.get('classroom')
        phone = request.form.get('phone')
        name = request.form.get('name')
        email = request.form.get('email')
        variant = request.form.get('variant')

        try:
            course = Course.objects.get(id=course_id)
        except:
            return render_template('classes/subscription_error.html')

        user = self.get_user(email, name)
        if not user:
            return render_template('classes/subscription_error.html')

        subscriber = Subscriber.objects.create(
            name=name,
            email=email,
            phone=phone,
            user=user
        )

        if not variant in ['regular', None, False, '']:
            course_variant = course.variants.get(slug=variant)
            _variant = CourseVariant(
                title=course_variant.title + str(random.getrandbits(8)),
                description=course_variant.description,
                unity_value=course_variant.unity_value,
                slug=course_variant.slug
            )
        else:
            _variant = None

        cart = Cart.get_cart()

        subscription = CourseSubscription(
            subscriber=subscriber,
            student=subscriber,
            course=course,
            classroom=classroom,
            variant=_variant,
            cart=cart
        )

        subscription.save()

        item = Item(
            uid=subscription.get_uid(),
            product=course,
            reference=subscription,
            title=subscription.get_title(),
            description=subscription.get_description(),
            unity_value=subscription.get_unity_value(),
        )

        cart.items.append(item)
        # think on this
        cart.requires_login = False
        cart.addlog(u"Item added %s" % item.title)

        return redirect(url_for('cart.cart'))

    def get_user(self, email, name):
        if current_user.is_authenticated():
            if current_user.email == email:
                return User.objects.get(id=current_user.id)

        try:
            return User.objects.get(email=email)
        except:
            user = User.objects.create(
                name=name,
                email=email,
            )
            # autenticate
            # send email
            return user
