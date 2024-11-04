from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from mailing.views import MailingViewSet, ClientViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'mailings', MailingViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
