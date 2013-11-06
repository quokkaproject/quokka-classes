# coding: utf-8

from quokka.core.app import QuokkaModule
from .views import SubscribeView

module = QuokkaModule('classes', __name__,
                      template_folder="templates", static_folder="static")

module.add_url_rule('/classes/subscribe/',
                    view_func=SubscribeView.as_view('subscribe'))
