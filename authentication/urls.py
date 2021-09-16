from django.urls import path


from expenses.urls import urlpatterns
from .views import RegistrationView

urlpatterns = [
    path('register', RegistrationView.as_view(), name='register')
]