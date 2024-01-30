from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from core.decorators import restrict_user
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from apps.masterlist.models import Validation, Note
from django.shortcuts import HttpResponse, redirect, render
import datetime as dt
from django.db.models.query_utils import Q
import logging
from apps.upload.models import MasterlistBudget,UserProfile
from core.tasks import notify_validation_failed
from django.contrib.auth.models import User
from pyzabbix import ZabbixMetric, ZabbixSender
import requests
from core.settings import DAG_URL, DAG_USER, DAG_PASS
import uuid

mainPath = settings.MAINPATH
logger = logging.getLogger('main')
decorators = [login_required(login_url="/login/"), restrict_user("pid_group")]
zabbix_sender = ZabbixSender(settings.ZABBIX_SERVER, settings.ZABBIX_PORT)
dag_run_id_cache = {}

@method_decorator(decorators, name='dispatch')
class ValidationView(ListView):
    """_summary_
    Render page for validation page for both PIDs and Lead PIDs

    Args:
        ListView (_type_): _description_

    Returns:
        _type_: _description_
    """    
    model = Validation
    template_name = 'pid/validation.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        init_assc = list(UserProfile.objects.filter(
        user__username=self.request.user
        ).values_list('init_id_assc', flat=True))

        init_id = list(MasterlistBudget.objects.filter(
        id__in=init_assc
        ).values_list('sub_init_id', flat=True))
        
        context["object_validate"] = Validation.objects.filter(init_id__in=init_id).filter(
            Q(is_validate="Dalam Proses") | Q(is_validate="Gagal") | Q(is_validate=None)
            ).order_by('-date_modified')
        
        context["object_push"] = Validation.objects.filter(
            is_validate="Berjaya", is_push=False
            ).order_by('validation_date')
        return context
    
    
def edit_note(request):
    """_summary_
    Add note to the Validation table

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if request.method == 'POST':
        text = request.POST['text']
        object_id = request.POST['pk']
        init_id = request.POST['init_id']
        init_name = request.POST['init_name']
        text = text.replace('\n', ' ')
        saved_note = Note(note_assc_id=init_id, note_assc_name=init_name, 
                          text_note=text, editor=str(request.user.username), 
                          date_modified=dt.datetime.now())
        saved_note.save()
        Validation.objects.filter(
            id=object_id
            ).update(cur_note=text, 
                     edit_note_by=str(request.user.username), 
                     date_modified_note=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                     date_modified=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                     )
        logger.info("Successfully edit note in validation page " + init_id + " - " + 
                    str(request.user.username))
        try:
            packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                "Successfully edit note in validation page " + init_id + " - " + 
                                str(request.user.username))]
            zabbix_sender.send(packet)
        except:
            pass
        return HttpResponse(status=200)
    
    
def validate_data(request):
    """_summary_
    Validate data by row (PID)

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if request.method == 'POST':
        object_id = request.POST['pk']
        init_id = request.POST['init_id']
        Validation.objects.filter(
            id=object_id
            ).update(is_validate="Berjaya", 
                     validate_by=str(request.user.username), 
                     validation_date=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                     date_modified=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                     )
        logger.info("Successfully validate data in validation page " + init_id + " - " + 
                    str(request.user.username))
        try:
            packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                "Successfully validate data in validation page " + init_id + " - " + 
                                str(request.user.username))]
            zabbix_sender.send(packet)
        except:
            pass
        return HttpResponse(status=200)


def validate_data_comments(request):
    """_summary_
    Validate data by row (PID) with comments

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if request.method == 'POST':
        object_id = request.POST['pk']
        text = request.POST['text']
        init_id = request.POST['init_id']
        init_name = request.POST['init_name']
        text = text.replace('\n', ' ')
        saved_note = Note(note_assc_id=init_id, note_assc_name=init_name,
                          text_note=text, editor=str(request.user.username),
                          date_modified=dt.datetime.now())
        saved_note.save()
        Validation.objects.filter(
            id=object_id
            ).update(cur_note=text, 
                     edit_note_by=str(request.user.username), 
                     date_modified_note=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                     is_validate="Berjaya", validate_by=str(request.user.username), 
                     validation_date=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                     date_modified=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                     )
        logger.info("Successfully validate data in validation page " + init_id + " - " + 
                    str(request.user.username))
        try:
            packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                "Successfully validate data in validation page " + init_id + " - " + 
                                str(request.user.username))]
            zabbix_sender.send(packet)
        except:
            pass
        return HttpResponse(status=200)


def push_data(request):
    """_summary_
    Push data by row (Lead PID)

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if request.method == 'POST':
        object_id = request.POST['pk']
        init_id = request.POST['init_id']
        Validation.objects.filter(
            id=object_id
            ).update(
                is_push=True, push_by=str(request.user.username), 
                push_date=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                date_modified=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
        logger.info("Successfully push data in validation page " + init_id + " - " + 
                    str(request.user.username))
        try:
            packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                "Successfully push data in validation page " + init_id + " - " + 
                                str(request.user.username))]
            zabbix_sender.send(packet)
        except:
            pass
        return HttpResponse(status=200)
    
    
def push_data_comments(request):
    """_summary_
    Push data by row (Lead PID) with comments

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if request.method == 'POST':
        object_id = request.POST['pk']
        init_id = request.POST['init_id']
        text = request.POST['text']
        text = text.replace('\n', ' ')
        Validation.objects.filter(
            id=object_id
            ).update(
                is_push=True, push_by=str(request.user.username), 
                push_date=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                date_modified=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        logger.info("Successfully push data in validation page " + init_id + " - " + 
                    str(request.user.username))
        try:
            packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                "Successfully push data in validation page " + init_id + " - " + 
                                str(request.user.username))]
            zabbix_sender.send(packet)
        except:
            pass
        return HttpResponse(status=200)
    
    
def delete_data(request):
    """_summary_
    Remove data by row (Lead PID)

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if request.method == 'POST':
        object_id = request.POST['pk']
        text = request.POST['text']
        cur_note = request.POST['cur_note']
        init_id = request.POST['init_id']
        text = text.replace('\n', ' ')
        get_master = MasterlistBudget.objects.get(init_id=init_id)
        field_object = MasterlistBudget._meta.get_field('init_name')
        field_value = getattr(get_master, field_object.attname)
        
        Validation.objects.filter(
            id=object_id
            ).update(is_validate="Gagal", failed_reason_user=text, 
                     date_modified=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        pid_user_list = list(User.objects.filter(
                        masterlistbudget__init_id=init_id, userprofile__is_lead=False, 
                        userprofile__validation_perm=True, groups__name='pid_group'
                        ).exclude(email='').values_list('email', flat=True))
        information = {'pid_users':pid_user_list, 'init_id':init_id,
                       'init_name':str(field_value), 'date':dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                       'rejection_note':text, 'current_note':cur_note}
        notify_validation_failed(information)
        logger.info("Successfully reject data in validation page " + init_id + " - " + 
                    str(request.user.username))
        try:
            packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                "Successfully reject data in validation page " + init_id + " - " + 
                                str(request.user.username))]
            zabbix_sender.send(packet)
        except:
            pass
        return HttpResponse(status=200)
    
    
def create_dag_id(dag_run_id):
    """_summary_
    Create DAG id

    Args:
        dag_run_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    if dag_run_id in dag_run_id_cache:
        return dag_run_id_cache[dag_run_id]

    url = DAG_URL
    data = {
        "conf": {
            "variable": "my variable"
        },
        "dag_run_id": dag_run_id
    }

    auth = (DAG_USER, DAG_PASS)
    
    try:
        response = requests.post(url, json=data, auth=auth, verify=False)
        response.raise_for_status()

        if response.status_code == 200:
            print("DAG run created successfully.")
        else:
            print(f"Error creating DAG run. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    dag_run_id_cache[dag_run_id] = dag_run_id
    return dag_run_id
    
    
def create_dag_run(request):
    """_summary_
    Create DAG run

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if request.method == "POST":
        try:
            dag_run_id = f"airflow-runid-{uuid.uuid4()}"
            create_dag_id(dag_run_id)
        except Exception as e:
            print(f"Failed to trigger Airflow DAG: {e}")
        return redirect('/validation')