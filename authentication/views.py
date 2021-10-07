from django.shortcuts import redirect, render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
import json
from validate_email import validate_email
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib import auth


from .utils import token_generator


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
                email.send(fail_silently=False)
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