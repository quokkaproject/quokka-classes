# coding: utf-8

from flask import request
from quokka.modules.cart.pipelines.base import CartPipeline
from quokka.utils import get_current_user
from .models import CourseSubscription, Subscriber


class SetSubscriber(CartPipeline):
    def process(self):

        name = request.form.get("name")
        email = request.form.get("email")
        area_code = request.form.get("area_code")
        phone = request.form.get("phone")
        document = request.form.get("document")
        address = request.form.get("address")
        confirm = request.form.get("classes_setsubscriber_confirm")

        if not confirm:
            return self.render('classes/setsubscriber.html', cart=self.cart)

        formdata = dict(name=name, email=email, area_code=area_code,
                        phone=phone, document=document, address=address)

        subscriptions = CourseSubscription.objects.filter(
            cart=self.cart
        )

        user = get_current_user()
        for subscription in subscriptions:
            subscription.subscriber = self.get_subscriber(user, **formdata)
            subscription.save()

        self.cart.sender_data = {
            "name": name or user.name,
            "email": email or user.email,
            "area_code": area_code,
            "phone": phone.replace('-', '').replace('(', '').replace(')', ''),
        }

        self.cart.addlog("SetSubscriber Pipeline: defined sender data")

        return self.go()

    def get_subscriber(self, user, **kwargs):
        if not user:
            return None

        try:
            sub = Subscriber.objects.get(user=user)
            sub.name = kwargs.get('name')
            sub.email = kwargs.get('email')
            sub.document = kwargs.get('document')
            sub.address = kwargs.get('address')
            sub.phone = u"%(area_code)s%(phone)s" % kwargs
            sub.save()
            return sub
        except:
            self.cart.addlog("Creating a new subscriber", save=False)
            return Subscriber.objects.create(
                name=kwargs.get('name'),
                email=kwargs.get('email'),
                user=user,
                document=kwargs.get('document'),
                address=kwargs.get('address'),
                phone=u"%(area_code)s%(phone)s" % kwargs
            )
