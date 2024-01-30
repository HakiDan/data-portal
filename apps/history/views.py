from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from apps.datacleaning.views import get_data_clean
from django.template import loader
from django.conf import settings
from apps.upload.models import *
from core.tasks import *
import pandas as pd
import mimetypes
from django.utils import timezone
import os.path
from pyzabbix import ZabbixMetric, ZabbixSender
from datetime import timedelta
from django.db.models import F

mainPath = settings.MAINPATH
logger = logging.getLogger('main')
zabbix_sender = ZabbixSender(settings.ZABBIX_SERVER, settings.ZABBIX_PORT)

def downloadfile_accepted(request):
    """_summary_
    Download accepted rows

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if request.method == 'POST':
        file_name = request.POST['file']
        filename = "{}/home_download_accepted/{}".format(mainPath, file_name)
        file_name = "{}".format(file_name)

        fl = open(filename, encoding='UTF-8')
        mime_type, _ = mimetypes.guess_type(filename)
        response = HttpResponse(fl, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % file_name
        logger.info("Download accepted file " + file_name + " - " + str(request.user.username))
        try:
            packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                   "Download accepted file " + file_name + " - " 
                                   + str(request.user.username))]
            zabbix_sender.send(packet)
        except:
            pass
        return response
    
    
def downloadfile_rejected(request):
    """_summary_
    Download rejected rows

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if request.method == 'POST':
        file_name = request.POST['file']
        filename = "{}/home_download_rejected/{}".format(mainPath, file_name)
        file_name = "{}".format(file_name)

        fl = open(filename, encoding='UTF-8')
        mime_type, _ = mimetypes.guess_type(filename)
        response = HttpResponse(fl, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % file_name
        logger.info("Download rejected file " + file_name + " - " + str(request.user.username))
        try:
            packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                   "Download rejected file " + file_name + " - " 
                                   + str(request.user.username))]
            zabbix_sender.send(packet)
        except:
            pass
        return response


@login_required(login_url="/login/")
def history_submission(request):
    """_summary_
    Rendering home page with list of data and download data (accepted & rejected)
    
    Args:
        request (_type_): _description_
    
    Returns:
        _type_: _description_
    """
    init_assc = list(UserProfile.objects.filter(
        user__username=request.user
        ).values_list('init_id_assc', flat=True))
    init_id = list(MasterlistBudget.objects.filter(
        id__in=init_assc
        ).values_list('sub_init_id', flat=True))
    subinit_id = list(UserLogSubmission.objects.filter(
        sub_init_id__in=init_id
        ).order_by('-id').values_list('sub_init_id', flat=True)
    )
    master_id = list(UserLogSubmission.objects.filter(
        sub_init_id__in=init_id
        ).order_by('-id')
    )
    init_name = list(UserLogSubmission.objects.filter(
        sub_init_id__in=init_id
        ).order_by('-id').values_list('initiative', flat=True)
    )

    print(init_name)
    
    timestamp_str = list(UserLogSubmission.objects.filter(
        sub_init_id__in=init_id
        ).order_by('-id').values_list('submission_time', flat=True)
    )
    user_full_name = list(UserLogSubmission.objects.filter(
        sub_init_id__in=init_id
        ).order_by('-id').values_list('full_name', flat=True)
    )
    agency_name = list(UserLogSubmission.objects.filter(
        sub_init_id__in=init_id
        ).order_by('-id').values_list('agency_name', flat=True)
    )
    files = UserLogSubmission.objects.annotate(
        exp_date=models.ExpressionWrapper(F('submission_time')+timedelta(days=100), 
                                          output_field=models.DateTimeField())
                                        ).filter(sub_init_id__in=init_id).order_by('-id')
    
    download_new_reject = []
    download_new_accept = []
    for file in files:
        if os.path.isfile("{}/home_download_rejected/{}".format(mainPath, file.rejected_filename)) is True:
            data_reject = pd.read_csv("{}/home_download_rejected/{}".format(mainPath, file.rejected_filename))
            if timezone.now() <= file.exp_date:
                if not data_reject.empty:
                    download_new_reject.append(file.rejected_filename)
                else:
                    download_new_reject.append('')
            else:
                download_new_reject.append('TELAH TAMAT TEMPOH')
        else:
            download_new_reject.append('')
            
        if os.path.isfile("{}/home_download_accepted/{}".format(mainPath, file.accepted_filename)) is True:
            data_accept = pd.read_csv("{}/home_download_accepted/{}".format(mainPath, file.accepted_filename))
            if timezone.now() <= file.exp_date:
                if not data_accept.empty:
                    download_new_accept.append(file.accepted_filename)
                else:
                    download_new_accept.append('')
            else:
                download_new_accept.append('TELAH TAMAT TEMPOH')
        else:
            download_new_accept.append('')
                
    sector, users_pic = [],[]
    for sub in subinit_id:
        get_sector = MasterlistBudget.objects.get(sub_init_id=sub)
        field_object = MasterlistBudget._meta.get_field('sector')
        sect = getattr(get_sector, field_object.attname)
        sector.append(sect)
    
    for sub in subinit_id:
        test = MasterlistBudget.objects.get(sub_init_id=sub)
        pic = UserProfile.objects.filter(
            init_id_assc=test, user__groups__name='pid_group', 
            validation_perm=True).first()
        users_pic.append(pic)

    
    items_ia = zip(init_name, timestamp_str, download_new_accept, download_new_reject)
    items_dq = zip(timestamp_str, subinit_id, init_name, sector, agency_name, 
                   user_full_name, users_pic, download_new_accept, download_new_reject)
    items_pid = zip(subinit_id, init_name, user_full_name, timestamp_str, download_new_accept, download_new_reject)
    count_file = len(init_name)
    
    context = {
                'segment':'index',
                'items_ia': items_ia,
                'init_id': init_id,
                'items_dq':items_dq,
                'items_pid':items_pid,
                'count_file':count_file,
                'col_gender':get_data_clean(request)[0],
                'col_race':get_data_clean(request)[1],
                'col_state':get_data_clean(request)[2],
                'col_biz_ownership_type':get_data_clean(request)[4],
                'col_bumi_status':get_data_clean(request)[5],
                'col_biz_sector':get_data_clean(request)[6],
                'colCountTotal':get_data_clean(request)[3],
                'col_state_summary':get_data_clean(request)[2],
               }
    html_template = loader.get_template('history/history.html')
    return HttpResponse(html_template.render(context, request))

    