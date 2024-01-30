from django.urls import reverse, NoReverseMatch
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.shortcuts import render
import logging
from typing import Callable
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import get_user_model, logout
from django.contrib.messages import info
from django_auto_logout.utils import now, seconds_until_idle_time_end, seconds_until_session_end
from pyzabbix import ZabbixMetric, ZabbixSender

ALLOWED_IPS = settings.ALLOWED_IPS
logger = logging.getLogger('main')
zabbix_sender = ZabbixSender(settings.ZABBIX_SERVER, settings.ZABBIX_PORT)
class InternalUseOnlyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            admin_index = reverse('admin:index')
            pid_app_masterlist = reverse('masterlist')
            pid_app_report = reverse('report')
            pid_app_dataconfirmation = reverse('dataconfirmation')
            pid_app_validation = reverse('validation')
            dq_app_datacleaning = reverse('datacleaning')
            dq_app_dataupdate = reverse('dataupdate')
            dq_app_datacatalogue = reverse('datacatalogue')
            dq_app_inventory = reverse('inventory')
        except NoReverseMatch:
            return
        if (not request.path.startswith(admin_index) and not request.path.startswith(pid_app_masterlist) and not request.path.startswith(pid_app_report) and not request.path.startswith(pid_app_dataconfirmation) and not request.path.startswith(pid_app_validation) and not request.path.startswith(dq_app_datacleaning) and not request.path.startswith(dq_app_dataupdate) and not request.path.startswith(dq_app_datacatalogue) and not request.path.startswith(dq_app_inventory)):
            return
        remote_addr = request.META.get(
            'HTTP_X_REAL_IP', request.META.get('REMOTE_ADDR', None))
        if (not remote_addr in ALLOWED_IPS):
            return render(request, 'home/page-401.html', status=401)
        
        
def _auto_logout(request: HttpRequest, options):
    should_logout = False
    current_time = now()

    if 'SESSION_TIME' in options:
        session_time = seconds_until_session_end(request, options['SESSION_TIME'], current_time)
        should_logout |= session_time < 0

    if 'IDLE_TIME' in options:
        idle_time = seconds_until_idle_time_end(request, options['IDLE_TIME'], current_time)
        should_logout |= idle_time < 0

        if should_logout and 'django_auto_logout_last_request' in request.session:
            del request.session['django_auto_logout_last_request']
        else:
            request.session['django_auto_logout_last_request'] = current_time.isoformat()

    if should_logout:
        logger.info("End user session - " + str(request.user.username))
        try:
            packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', "End user session - " + str(request.user.username))]
            zabbix_sender.send(packet)
        except:
            pass
        logout(request)

        if 'MESSAGE' in options:
            info(request, options['MESSAGE'])


def auto_logout(get_response: Callable[[HttpRequest], HttpResponse]) -> Callable:
    def middleware(request: HttpRequest) -> HttpResponse:
        if not request.user.is_anonymous and hasattr(settings, 'AUTO_LOGOUT'):
            _auto_logout(request, settings.AUTO_LOGOUT)

        return get_response(request)
    return middleware