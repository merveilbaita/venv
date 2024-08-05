from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes
from django.contrib.auth.forms import SetPasswordForm
from django.utils.http import urlsafe_base64_decode


User = get_user_model()

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        messages.success(request, 'Votre compte est créé avec succès')
        return redirect('login')  

        


def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Utilisation correcte de `authenticate` avec des mots-clés
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_admin:
                return redirect('/admin/')
            else:
                return redirect('index')  # Redirige vers la page d'accueil ou autre
        else:
            # Optionnel : Ajouter un message d'erreur si les informations de connexion sont incorrectes
            return render(request, 'accounts/login.html', {'error': 'Nom d\'utilisateur ou mot de passe incorrect'})
    
    return render(request, 'accounts/login.html')


def logout_user(request):
    logout(request)
    return redirect('index')



def password_reset_request(request):
    if request.method == "POST":
        email = request.POST['email']
        associated_users = User.objects.filter(email=email)
        if associated_users.exists():
            for user in associated_users:
                subject = "Password Reset Requested"
                email_template_name = "accounts/password_reset_email.html"
                c = {
                    "email": user.email,
                    'domain': request.get_host(),
                    'site_name': 'Website',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http',
                }
                email = render_to_string(email_template_name, c)
                try:
                    send_mail(subject, email, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
                except Exception as e:
                    return render(request, 'accounts/forget_pass.html', {'error': str(e)})
        return redirect("password_reset_done")
    return render(request, 'accounts/forget_pass.html')


def password_reset_confirm(request, uidb64=None, token=None):
    if uidb64 is not None and token is not None:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User, pk=uid)
        
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    return redirect('password_reset_complete')
            else:
                form = SetPasswordForm(user)
            return render(request, 'accounts/password_reset_confirm.html', {'form': form})
        else:
            return render(request, 'accounts/password_reset_confirm.html', {'invalid': True})
    else:
        return redirect('password_reset')
    

def password_reset_done(request):
    return render(request, 'accounts/password_reset_done.html')

def password_reset_complete(request):
    return render(request, 'accounts/password_reset_complete.html')