# coding: utf-8

from quokka.core.app import QuokkaModule
module = QuokkaModule('classes', __name__,
                      template_folder="templates", static_folder="static")
