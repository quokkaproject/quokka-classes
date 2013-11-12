# coding: utf-8
import random
from flask import request, url_for, redirect, current_app
from flask.views import MethodView
from flask.ext.security.utils import login_user
from quokka.utils import get_current_user
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

        self.current_user = get_current_user()
        self.cart = Cart.get_cart()

        try:
            course = Course.objects.get(id=course_id)
        except:
            self.cart.addlog("Error getting course %s" % course_id)
            return render_template('classes/subscription_error.html')

        student = self.get_student(email, name, phone)
        if not student:
            self.cart.addlog("Error getting student")
            return render_template('classes/subscription_error.html')

        if not variant in ['regular', None, False, '']:
            course_variant = course.variants.get(slug=variant)
            _variant = CourseVariant(
                title=course_variant.title + "<!-- {0}  -->".format(
                    str(random.getrandbits(8))
                ),
                description=course_variant.description,
                unity_value=course_variant.unity_value,
                slug=course_variant.slug
            )
        else:
            _variant = None

        subscription = CourseSubscription(
            subscriber=self.get_subscriber(),  # if none will set on pipeline
            student=student,
            course=course,
            classroom=classroom,
            variant=_variant,
            cart=self.cart
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

        self.cart.items.append(item)

        # think on this
        # in sites with multiple e-commerce apps
        # if cart has items from multiple apps ex:
        #   items: course, product, signature etc..
        # which app has precedence in cart settings?

        self.cart.requires_login = current_app.config.get(
            "CLASSES_CART_REQUIRES_LOGIN",
            self.cart.requires_login
        )
        self.cart.continue_shopping_url = current_app.config.get(
            "CLASSES_CART_CONTINUE_SHOPPING_URL",
            self.cart.continue_shopping_url
        )
        self.cart.pipeline = current_app.config.get(
            "CLASSES_CART_PIPELINE",
            self.cart.pipeline
        )
        self.cart.config = current_app.config.get(
            "CLASSES_CART_CONFIG",
            self.cart.config
        )
        self.cart.course_subscription_id = subscription.id
        self.cart.addlog(u"Item added %s" % item.title, save=True)

        return redirect(url_for('cart.cart'))

    def get_subscriber(self):
        if not self.current_user:
            return None

        try:
            return Subscriber.objects.get(user=self.current_user)
        except:
            self.cart.addlog("Creating a new subscriber", save=False)
            return Subscriber.objects.create(
                name=self.current_user.name,
                email=self.current_user.email,
                user=self.current_user
            )

    def get_student(self, email, name, phone):

        if self.current_user and self.current_user.email == email:
            try:
                return Subscriber.objects.get(user=self.current_user)
            except:
                self.cart.addlog("Creating a new student", save=False)
                return Subscriber.objects.create(
                    name=name,
                    email=email,
                    phone=phone,
                    user=self.current_user
                )

        try:
            user = User.objects.get(email=email)
        except:
            self.cart.addlog("Creating new user %s" % email)
            user = User.objects.create(
                name=name,
                email=email,
                password=""
            )

            # autenticar e mandar email password
            login_user(user)

        return Subscriber.objects.create(
            name=name,
            email=email,
            phone=phone,
            user=user
        )
