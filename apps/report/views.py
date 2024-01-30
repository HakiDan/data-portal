from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import mimetypes
import os
from core.decorators import restrict_user
import datetime as dt 
from django.contrib.auth.decorators import login_required
import logging
from pyzabbix import ZabbixMetric, ZabbixSender
 
mainPath = settings.MAINPATH
logger = logging.getLogger('main')
zabbix_sender = ZabbixSender(settings.ZABBIX_SERVER, settings.ZABBIX_PORT)

def download_pm_report(request):
    """_summary_
    Download Laporan PM

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if request.method == "POST" :
        file_name = request.POST['file_name']
        filename = "{}/report/pm/{}".format(mainPath, file_name)

        fl = open(filename, 'rb')
        mime_type, _ = mimetypes.guess_type(filename)
        response = HttpResponse(fl, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % file_name
        logger.info("Download PM report " + file_name + " - " + str(request.user.username))
        try:
            packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', "Download PM report " + file_name + " - " + str(request.user.username))]
            zabbix_sender.send(packet)
        except:
            pass
        return response
      
   
def download_jkk_report(request):
    """_summary_
    Download Laporan JKK

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if request.method == "POST" :
        file_name = request.POST['file_name']
        filename = "{}/report/jkk/{}".format(mainPath, file_name)

        fl = open(filename, 'rb')
        mime_type, _ = mimetypes.guess_type(filename)
        response = HttpResponse(fl, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % file_name
        logger.info("Download JKK report " + file_name + " - " + str(request.user.username))
        try:
            packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', "Download JKK report " + file_name + " - " + str(request.user.username))]
            zabbix_sender.send(packet)
        except:
            pass
        return response


def modification_date(filename):
    """_summary_
    Get file modification date

    Args:
        filename (_type_): _description_

    Returns:
        _type_: _description_
    """
    t = os.path.getmtime(filename)
    ut = dt.datetime.fromtimestamp(t)
    return ut.strftime("%Y-%m-%d")


@login_required(login_url="/login/")
@restrict_user("pid_group", "lead_pid_group")
def report(request):
    """_summary_
    Rendering Laporan page for PID

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    jkk_report_path = os.listdir(mainPath + "/report/jkk")
    pm_report_path = os.listdir(mainPath + "/report/pm")
    pm_time, jkk_time = [], []
    
    for report in jkk_report_path:
        time_report = modification_date(mainPath + "/report/jkk/" + report)
        jkk_time.append(time_report)
    
    for report in pm_report_path:
        time_report = modification_date(mainPath + "/report/pm/" + report)
        pm_time.append(time_report)
    
    items_pm = zip(pm_report_path, pm_time)
    items_jkk = zip(jkk_report_path, jkk_time)
        
    context = {
        "items_pm": items_pm,
        "items_jkk": items_jkk,
    }
    return render(request, 'pid/report.html', context)
