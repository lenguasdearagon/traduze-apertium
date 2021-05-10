from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('lector', views.reader, name='reader'),
    path('ajax/translate_text', views.translate_text, name='translate_text'),
    path('ajax/translate_document', views.translate_document, name='translate_document'),
    path('ajax/translate_url', views.translate_url, name='translate_url'),

    #info
    path('contact', views.contact, name="contact"),
    path('help', views.help, name="help"),
    path('legal_notice', views.legal_notice, name="legal_notice"),
    path('privacy_policy', views.privacy_policy, name="privacy_policy")
]