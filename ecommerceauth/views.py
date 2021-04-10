from django.core.mail.message import EmailMessage
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
#to_activate_user_account
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.urls import NoReverseMatch,reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,force_text,DjangoUnicodeDecodeError
#getting tokens from utils.py
from .utils import TokenGenerator,generate_token
#threading
import threading
#emails
from django.core.mail import send_mail,EmailMultiAlternatives
from django.core.mail import BadHeaderError,send_mail
from django.core import mail
from django.conf import settings
from django.core.mail import EmailMessage


# Create your views here.
class EmailThread(threading.Thread):
    def __init__(self,email_message):
        self.email_message=email_message
        threading.Thread.__init__(self)


    def run(self):
        self.email_message.send()




def signup(request):
    if request.method=="POST":
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['pass1']
        confirm_password=request.POST['pass2']
        if password!=confirm_password:
            messages.warning(request,"Password is Not Matching")
            return render(request,'auth/signup.html')
            
            
        try:
            if User.objects.get(username=username):


                messages.warning(request,"UserName is Taken")
                return render(request,'auth/signup.html')

        except Exception as identifier:
            pass

        try:
            if User.objects.get(email=email):
                messages.warning(request,"Email is Taken")
                return render(request,'auth/signup.html')

        except Exception as identifier:
            pass
        
        user = User.objects.create_user(username,email,password)
        user.is_active=False
        user.save()
        current_site=get_current_site(request)
        email_subject="Activate your account"
        message=render_to_string('auth/activate.html',{
            'user':user,
            'domain':'127.0.0.1:8000/',
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':generate_token.make_token(user)

        })

        email_message= EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email],)

        EmailThread(email_message).start()
        messages.info(request,"Activate Your account by clicking link your email")
        return redirect('/ecommerceauth/login')

    return render(request,'auth/signup.html')

class ActivateAccountView(View):
    def get(self,request,uidb64,token):
        try:
            uid=force_text(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=uid)
        except Exception as identifier:
            user=None

        if user is not None and generate_token.check-token(user,token):
            user.is_active=True
            user.save()
            messages.info(request,"Account Activated successfully")
            return redirect('/ecommerceauth/login')
        return render(request,'auth/activatefail.html')

def handlelogin(request):
    if request.method=="POST":

        username=request.POST['username']
        userpassword=request.POST['pass1']
        myuser=authenticate(username=username,password=userpassword)

        if myuser is not None:
            login(request,myuser)
            messages.success(request,"Login Success")
            return render(request,'index.html')

        else:
            messages.error(request,"Invalid Credentials")
            return redirect('/ecommerceauth/login')

    return render(request,'auth/login.html')

def handlelogout(request):
    logout(request)
    messages.success(request,"Logout Success")
    return redirect('/ecommerceauth/login')