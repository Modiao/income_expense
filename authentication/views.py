import json
from lib2to3.fixes.fix_input import context

from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import (DjangoUnicodeDecodeError, force_bytes,
                                   force_text)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from validate_email import validate_email

from .utils import token_generator
import threading

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    
    def run(self):
        self.email.send(fail_silently=False)


# Create your views here.
class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({"username_error": "username can only contain alphanumeric characters"}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({"username_error": "username in use, choose another one"}, status=400)
        return JsonResponse({"username_valid": True})

class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            print("here")
            return JsonResponse({"email_error": "email invalid"}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({"email_error": "email in use, choose another one"}, status=400)
        return JsonResponse({"email_valid": True})

class RegistrationView(View):

    def get(self, request):
        return render(request, 'authentication/register.html')
    
    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password= request.POST['password']

        context = {
            "fieldsValues": request.POST
        }
        if not User.objects.filter(username=username) and username !="":
            if not User.objects.filter(email=email) and email !="":
                if len(password) <6:
                    messages.error(request, "password too short")
                    return render(request, 'authentication/register.html', context)

                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()

                domain = get_current_site(request).domain
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                link = reverse('activate', kwargs={"uidb64": uidb64, "token": token_generator.make_token(user)})
                active_url = "http://"+domain+link
                email_subject = "Activate your account"
                email_body = "Hi " + username + " please use this link to activate your account :\n" + active_url
                email = EmailMessage(
                    email_subject,
                    email_body,
                    'noreply@semycolon.com',
                    [email]
                )
                EmailThread(email).start()
                messages.success(request, "user successfully created")
                return render(request, 'authentication/register.html')
        messages.error(request, "the field must not null")
        return render(request, 'authentication/register.html')

class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)
            if not token_generator.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')
            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()
            messages.success(request, 'Account activate successfully')
            return redirect('login')
        except Exception as e:
            pass
        return redirect('login')
    

class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')
    
    def post(self, request):
        print("They call me")
        print(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, "Welcome, "+ user.username + 
                            " you are now logged in")
                    return redirect('expenses')
                messages.error(request, 'Account not activated, please check your email')
                return render(request, 'authentication/login.html')
                        
            messages.error(request, 'Invalid credentials, try again')
            return render(request, 'authentication/login.html')
        messages.error(request, 'username and password must not be empty')
        return render(request, 'authentication/login.html')

class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logoed out')
        return redirect('login')

class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')
    
    def post(self, request):
        email = request.POST.get('email')
        if not validate_email(email):
            messages.error(request, 'Please supply a valid email')
            return render(request, 'authentication/reset-password.html')

        user = User.objects.filter(email=email)
        if user.exists():
            email_contents = {
                "user": user[0],
                "domain": get_current_site(request).domain,
                "uid": urlsafe_base64_encode(force_bytes(user[0].pk)),
                "token": PasswordResetTokenGenerator().make_token(user[0])
            }

            link = reverse('reset-user-password', kwargs={"uidb64": email_contents['uid'], "token": email_contents['token']})
            reset_password_url = "http://"+email_contents['domain']+link
            email_subject = "Reset Password Instructions"
            email_body = "Hi "+ user[0].username + ", please click the link below to reset your password     :\n" + reset_password_url
            email = EmailMessage(
                email_subject,
                email_body,
                'noreply@semycolon.com',
                [email]
            )
            EmailThread(email).start()
        messages.success(request, 'We have sent you an email to reset your password')
        return render(request, 'authentication/reset-password.html')
    

class CompletePasswordReset(View):
    def get(self, request, uidb64, token):
        context = {
            "uidb64": uidb64,
            "token": token
        }

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, 'Password link is invalid, please request a new one')
                return redirect('request-password')
        except Exception as e:
                pass
        return render(request, 'authentication/set-new-password.html', context)

    def post(selef, request, uidb64, token):
        context = {
            "uidb64": uidb64,
            "token": token
        }
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request,'password do not match')
            return render(request, 'authentication/set-new-password.html', context)
        if len(password) < 6:
            messages.error(request,'password too short')
            return render(request, 'authentication/set-new-password.html', context)
        
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.password = password
            user.set_password(password)
            user.save()
            messages.success(request, 'password reset successfully, you can login with your new password')
            return redirect('login')
        except Exception as e:
            messages.error(request,'Something went wrong, please try again')
            return render(request, 'authentication/set-new-password.html')