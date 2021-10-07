import django.contrib
from django.shortcuts import redirect, render
import django.urls
import os
import json
from django.conf import settings
from .models import UserPreference
from django.contrib import messages

# Create your views here.


def index(request):
    is_user_exist = UserPreference.objects.filter(user=request.user).exists()
    print(is_user_exist)
    user_preferences = None
    if is_user_exist:
        user_preferences = UserPreference.objects.get(user=request.user)
        messages.success(request, "Please choose your currency")
    currencies = []
    if request.method == 'GET':
        file_path = os.path.join(settings.BASE_DIR , 'currencies.json')

        with open(file_path, 'r') as f:
            data = json.load(f)
            for n, v in data.items():
                currencies.append({"name": n, "value": v})
        return render(request, 'preferences/index.html', {"currencies": currencies})
    else:
        currency = request.POST.get('currency')
        if is_user_exist:
            user_preferences.currency = currency
            user_preferences.save()
            return render(request, 'preferences/index.html', {"currencies": currencies, "user_preferences": user_preferences})
        user_preferences = UserPreference.objects.create(user=request.user, currency=currency)
        messages.success(request, "Change Saved")
        return render(request, 'preferences/index.html', {"currencies": currencies, "user_preferences": user_preferences})
