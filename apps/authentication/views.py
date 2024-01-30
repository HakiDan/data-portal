from django.contrib.auth import update_session_auth_hash, authenticate, login
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.db.models.query_utils import Q
from .forms import (LoginForm, CustomPasswordChangeForm, 
                    CustomSetPasswordForm, NewUserForm, 
                    ProfileUpdate, UserForm)
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordContextMixin, INTERNAL_RESET_SESSION_TOKEN, UserModel
from django.views.generic.edit import FormView, View
from django.views.decorators.debug import sensitive_post_parameters
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.core.exceptions import ValidationError
from django.utils.http import (
    urlsafe_base64_decode,
)
from django.contrib.auth import (
    login as auth_login, update_session_auth_hash,
)
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
import datetime as dt
import logging
from django.contrib.auth.views import LogoutView
from core.tasks import notify_password_request, notify_register_user, notify_register_pid
from pyzabbix import ZabbixMetric, ZabbixSender
from core.decorators import restrict_user
from apps.upload.models import UserProfile, DQUser, AgencyList
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import F
import random
import string

from django.views.generic import ListView

logger = logging.getLogger('main')
zabbix_sender = ZabbixSender(settings.ZABBIX_SERVER, settings.ZABBIX_PORT)
decorators = [login_required(login_url="/login/"), restrict_user("pid_group")]

now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def update_last_update_password(sender, user, **kwargs):
    """_summary_
    Update last_update_password field for a user 

    Args:
        sender (_type_): _description_
        user (_type_): _description_
    """    
    user.userprofile.last_update_password = now
    user.userprofile.save(update_fields=['last_update_password'])
    

def login_view(request):
    """_summary_
    Render login page & login the user if all required fields are satisfied

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """    
    form = LoginForm(request.POST or None)
    msg = None
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                user = User.objects.get(username=username)
                last_update_password = user.userprofile.last_update_password
                login(request, user)
                if not last_update_password:
                    return redirect("/password_login")
                else:
                    logger.info("Log in - " + str(user))
                    try:
                        packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                               "Log in - " + str(user))]
                        zabbix_sender.send(packet)
                    except:
                        pass
                    return redirect("/")
            else:
                msg = 'Nama pengguna / Kata laluan salah'
        else:
            msg = 'Error validating the form'
    return render(request, "accounts/login.html", {"form": form, "msg": msg})


@login_required(login_url="/login/")
def change_password(request):
    """_summary_
    Change password for a user (In profile page)

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """    
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            username = User.objects.get(username=request.user.username)
            update_last_update_password(request, username)
            update_session_auth_hash(request, user)  
            messages.success(request, 'Kata laluan anda telah dikemaskini!')
            logger.info("Change password - " + str(username))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                       "Change password - " + str(username))]
                zabbix_sender.send(packet)
            except:
                pass
            return redirect('change_password')
        else:
            logger.info("Failed change password - " + 
                        str(request.user.username))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                       "Failed change password - " + str(request.user.username))]
                zabbix_sender.send(packet)
            except:
                pass
            messages.error(request, 'Sila betulkan ralat di bawah')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})
    
    
def change_password_login(request):
    """_summary_
    Change password for a user (First time login)

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """    
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            username = User.objects.get(username=request.user.username)
            update_last_update_password(request, username)
            update_session_auth_hash(request, user)
            messages.success(request, 'Kata laluan anda telah dikemaskini!')
            logger.info("Change password - " + str(username))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                       "Change password - " + str(username))]
                zabbix_sender.send(packet)
            except:
                pass
            return redirect('change_password_login')
        else:
            logger.info("Failed change password for the first time - " + 
                        str(request.user.username))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                       "Failed change password - " + str(request.user.username))]
                zabbix_sender.send(packet)
            except:
                pass
            messages.error(request, 'Sila betulkan ralat di bawah')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'accounts/change_password_login.html', {'form': form})
    
    
def password_reset_request(request):
    """_summary_
    Change password for a user (In profile page)

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """    
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    notify_password_request(user)
                    return redirect ("/password_reset/done/")
            else:
                logger.info("Failed request change password - " + str(data))
                try:
                    packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                           "Failed request change password - " + str(data))]
                    zabbix_sender.send(packet)
                except:
                    pass
                messages.error(request, "E-mel " + str(data) + " tidak dijumpai")
                return redirect("/password_reset")
    password_reset_form = PasswordResetForm()
    return render(request, "accounts/password_reset.html", {"password_reset_form":password_reset_form})


@login_required
def password_reset_request_home(request):
    """_summary_
    Change a password for a user (Forgot password)

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """    
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    notify_password_request(user)
                    return redirect ("/password_reset/done/")
            else:
                logger.info("Failed request change password - " + str(data))
                try:
                    packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                           "Failed request change password - " + str(data))]
                    zabbix_sender.send(packet)
                except:
                    pass
                messages.error(request, "E-mel " + str(data) + " tidak dijumpai")
                return redirect("/password_reset_home")
    password_reset_form = PasswordResetForm()
    return render(request, "accounts/password_reset_home.html", {"password_reset_form":password_reset_form})


class CustomPasswordResetConfirmView(PasswordContextMixin, FormView):
    """_summary_
    Class define in Django before overriding its methods

    Args:
        PasswordContextMixin (_type_): _description_
        FormView (_type_): _description_

    Returns:
        _type_: _description_
    """    
    form_class = CustomSetPasswordForm
    post_reset_login = False
    post_reset_login_backend = None
    reset_url_token = 'set-password'
    success_url = reverse_lazy('password_reset_complete')
    template_name = 'accounts/password_reset_confirm.html'
    title = _('Enter new password')
    token_generator = default_token_generator

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])

        if self.user is not None:
            token = kwargs['token']
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(token, self.reset_url_token)
                    return HttpResponseRedirect(redirect_url)

        # Display the "Password reset unsuccessful" page.
        return self.render_to_response(self.get_context_data())

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist, ValidationError):
            user = None
        return user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        if self.post_reset_login:
            auth_login(self.request, user, self.post_reset_login_backend)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context['validlink'] = True
        else:
            context.update({
                'form': None,
                'title': _('Password reset unsuccessful'),
                'validlink': False,
            })
        return context

  
def customLogout(request):
    """_summary_
    Logout the user from PODS

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """    
    logger.info("Logout - " + str(request.user.username))
    try:
        packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                               "Logout - " + str(request.user.username))]
        zabbix_sender.send(packet)
    except:
        pass
    return LogoutView.as_view()(request)

class UserView(ListView):
    """_summary_
    Render masterlist page for both PIDs and Lead PIDs

    Args:
        ListView (_type_): _description_

    Returns:
        _type_: _description_
    """    
    model = User
    template_name = 'accounts/user_table.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        users = User.objects.filter(is_active=True, groups__name="ia_group")
        object_profile = UserProfile.objects.filter(user__is_active=True, user__groups__name="ia_group")   
        
        context['user_table'] = zip (users,object_profile)

        return context


@method_decorator(decorators, name='dispatch')
class RegisterRequestView(View):
    """_summary_
    Register class view for user registration (IA)

    Args:
        View (_type_): _description_

    Returns:
        _type_: _description_
    """
    form_class = NewUserForm
    form_profile = ProfileUpdate
    template = 'accounts/register.html'
    
    def get(self, request):
        context = {
                    'form': self.form_class,
                    'form_profile': self.form_profile,
                   }
        return render(request, self.template, context)
    
    def post(self, request):
        form = self.form_class(request.POST)
        form_profile = self.form_profile(request.POST)
        if form.is_valid() and form_profile.is_valid():
            user = form.save(commit=False)
            profile = form_profile.save(commit=False)
            user.email = user.username
            characters = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(random.choice(characters) for i in range(12))
            user.password1 = password
            user.password2 = user.password1
            is_lead = form_profile.cleaned_data['is_lead']
            user.save()
            dq_user = DQUser.objects.get(dq_user=profile.dq_name)
            UserProfile.objects.filter(user__username=user).update(
                agency_name=profile.agency_name,
                phone_number=profile.phone_number,
                dq_name=dq_user,
                is_lead = is_lead,
                )
            ia_group = Group.objects.get(name='ia_group') 
            ia_group.user_set.add(user)
            subinit_name = form_profile.cleaned_data['init_id_assc']
            user_ia = UserProfile.objects.get(user__username=user.username)
            user_dq = UserProfile.objects.get(user__username=profile.dq_name)
            for sub in subinit_name:
                user_ia.init_id_assc.add(sub)
                user_dq.init_id_assc.add(sub)
            messages.success(request, 'Pendaftaran pengguna berjaya')
            user_info = {
                        'user_email':user.email, 
                        'user_password':user.password2,
                        'user_agency':str(profile.agency_name),
                        'user_phone_number':str(profile.phone_number),
                        'user_subinit_name':list(subinit_name.values_list('subinit_name', flat=True)),
                        'requestor':request.user.username,
                        'requestor_email':request.user.email, 
                        }
            notify_register_user(user_info)
            notify_register_pid(user_info)
            logger.info("User " + user.username + " created by - " + 
                        str(request.user.username))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                       "User " + user.username + " created by - " + 
                                       str(request.user.username))]
                zabbix_sender.send(packet)
            except:
                pass
            return redirect('/register')
        else:
            messages.error(request, 'Pendaftaran pengguna tidak berjaya')
            logger.info("Failed user creation " + request.user.username + " by - " + 
                        str(request.user.username))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                       "Failed user creation " + request.user.username + " by - " + 
                                        str(request.user.username))]
                zabbix_sender.send(packet)
            except:
                pass
            context = {
                    'form': form,
                    'form_profile': form_profile,
                    }
            return render(request, self.template, context)
            
            
@method_decorator(decorators, name='dispatch')
class UserEdit(SuccessMessageMixin, View):
    """_summary_
    Class for update user

    Args:
        SuccessMessageMixin (_type_): _description_
        UpdateView (_type_): _description_

    Returns:
        _type_: _description_
    """
    form_class = UserForm
    form_profile = ProfileUpdate
    template_name = 'accounts/user_edit.html'

    def get(self, request, *args, **kwargs):
        self.object = get_object_or_404(User, pk=kwargs['pk'])
        user_profile = UserProfile.objects.get(user__username=self.object)
        form = self.form_class(instance=self.object)
        form_profile = self.form_profile(instance=user_profile)
        context = {
                    'form': form,
                    'form_profile': form_profile,
                   }
        return render(request, self.template_name, context)
        
    def post(self, request, *args, **kwargs):
        self.object = get_object_or_404(User, pk=kwargs['pk'])
        form = self.form_class(request.POST, instance=self.object)
        form_profile = self.form_profile(request.POST)
        if form.is_valid() and form_profile.is_valid():
            username = form.cleaned_data.get('username')
            first_name = form.cleaned_data.get('first_name')
            email = form.cleaned_data.get('email')
            phone_number = form_profile.cleaned_data.get('phone_number')
            dq_user = form_profile.cleaned_data.get('dq_name')
            agency_name = form_profile.cleaned_data.get('agency_name')
            subinit_name = form_profile.cleaned_data.get('init_id_assc')
            User.objects.filter(username=self.object).update(
                username=username,
                email=email,
                first_name=first_name,
            )
            dq_name = DQUser.objects.get(dq_user=dq_user)
            UserProfile.objects.filter(user__username=self.object).update(
            phone_number=phone_number,
            dq_name=dq_name,
            agency_name=agency_name,
            )
            user_ia = UserProfile.objects.get(user__username=self.object)
            user_dq = UserProfile.objects.get(user__username=dq_user)
            if subinit_name:
                user_ia.init_id_assc.clear()
                for sub in subinit_name:
                    user_ia.init_id_assc.add(sub)
                    user_dq.init_id_assc.add(sub)
            else:
                user_ia.init_id_assc.clear()

            messages.success(request, 'Pengguna ' + username + ' telah dikemaskini')
            context = {
                    'form': form,
                    'form_profile': form_profile,
                    }
            return render(request, self.template_name, context)
        else:
            username = form.cleaned_data.get('username')
            messages.error(request, 'Kemaskini pengguna ' + username + ' tidak berjaya')
            context = {
                    'form': form,
                    'form_profile': form_profile,
                    }
            return render(request, self.template_name, context)


def check_username_exist(request):
    """_summary_
    Check username (IA) if exists

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if request.method == 'POST':
        username_name = request.POST['username_name']
        user_exist = User.objects.filter(groups__name='ia_group', username=username_name).exists()
        if user_exist:
            pk = User.objects.get(groups__name='ia_group', username=username_name).pk
            url = "/register/user-edit/{}".format(pk)
            response = {'pk':pk, 'status_code':"success", 'urls':url}
        else:
            response = {'pk':None, 'status_code':"failed", 'urls':None}
        return JsonResponse(response)
    
    
def add_agency(request):
    """_summary_
    View to add agency

    Args:
        request (_type_): _description_
    """
    if request.method == 'POST':
        agency_abbr = request.POST['agency_abbr']
        agency_fullname = request.POST['agency_fullname']
        AgencyList(agency_abbr=agency_abbr, agency_fullname=agency_fullname).save()
        return HttpResponse(status=200)
    
    
    
