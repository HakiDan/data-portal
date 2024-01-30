from django.views.generic.base import View
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.conf import settings
from apps.upload.models import *
from django.utils.decorators import method_decorator
from core.decorators import restrict_user
import logging
from django.contrib.auth.decorators import login_required
from pyzabbix import ZabbixMetric, ZabbixSender

mainPath = settings.MAINPATH
logger = logging.getLogger('main')
zabbix_sender = ZabbixSender(settings.ZABBIX_SERVER, settings.ZABBIX_PORT)

def get_standard_data():
    """_summary_
    Get standard data for gender, race, state

    Returns:
        _type_: _description_
    """
    list_gender = list(StandardGender.objects.values_list('gender', flat=True))
    list_race = list(StandardRace.objects.values_list('race', flat=True))
    list_state = list(StandardState.objects.values_list('state', flat=True))
    list_biz_ownership_type = list(StandardBizOwnershipType.objects.values_list('biz_ownership_type', flat=True))
    list_bumi_status = list(StandardBumiStatus.objects.values_list('bumi_status', flat=True))
    list_biz_sector = list(StandardBizSector.objects.values_list('biz_sector', flat=True))
    
    return list_gender, list_race, list_state, list_biz_ownership_type, list_bumi_status, list_biz_sector


def get_data_clean(request):
    """_summary_
    Check standard data if it exists in dataframe for column jantina_ind, bangsa_ind, negeri_ind

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    col_gender, col_race, col_state, col_biz_ownership_type, col_biz_sector, col_bumi_status = ([] for i in range(6))
    master = list(UserProfile.objects.filter(
        user__username=request.user
        ).values_list('init_id_assc', flat=True))
    map_gender = list(MapTableGender.objects.filter(
        sub_init_id__in=master
        ).values_list('std_gender', flat=True).distinct()
    )
    map_race = list(MapTableRace.objects.filter(
        sub_init_id__in=master
        ).values_list('std_race', flat=True).distinct()
    )
    map_state = list(MapTableState.objects.filter(
        sub_init_id__in=master
        ).values_list('std_state', flat=True).distinct()
    )
    map_biz_ownership_type = list(MapTableBizOwnershipType.objects.filter(
        sub_init_id__in=master
        ).values_list('std_biz_ownership_type', flat=True).distinct()
    )
    map_bumi_status = list(MapTableBumiStatus.objects.filter(
        sub_init_id__in=master
        ).values_list('std_bumi_status', flat=True).distinct()
    )
    map_biz_sector = list(MapTableBizSector.objects.filter(
        sub_init_id__in=master
        ).values_list('std_biz_sector', flat=True).distinct()
    )
        
    for gender in map_gender:
        if gender not in get_standard_data()[0]:
            col_gender.append(gender)
            
    for race in map_race:
        if race not in get_standard_data()[1]:
            col_race.append(race)
        
    for state in map_state:
        if state not in get_standard_data()[2]:
            col_state.append(state)
            
    for biz_own in map_biz_ownership_type:
        if biz_own not in get_standard_data()[3]:
            col_biz_ownership_type.append(biz_own)
            
    for bumi in map_bumi_status:
        if bumi not in get_standard_data()[4]:
            col_bumi_status.append(bumi)
            
    for biz_sector in map_biz_sector:
        if biz_sector not in get_standard_data()[5]:
            col_biz_sector.append(biz_sector)
                
    colCountTotal = (len(col_gender) + len(col_race) + len(col_state) + 
                     len(col_biz_ownership_type) + len(col_bumi_status) + len(col_biz_sector)
                    )
    return col_gender, col_race, col_state, colCountTotal, col_biz_ownership_type, col_bumi_status, col_biz_sector

decorators_all = [login_required(login_url="/login/"), restrict_user("dq_group")]

@method_decorator(decorators_all, name='dispatch')
class DataCleaning(View):
    """_summary_
    Render history page for DQs

    Args:
        View (_type_): _description_

    Returns:
        _type_: _description_
    """    
    template_name = 'datacleaning/datacleaning.html'
    
    def get(self, request):
        extra_context = {
            'col_gender':get_data_clean(request)[0],
            'col_race':get_data_clean(request)[1],
            'col_state':get_data_clean(request)[2],
            'col_biz_ownership_type':get_data_clean(request)[4],
            'col_bumi_status':get_data_clean(request)[5],
            'col_biz_sector':get_data_clean(request)[6],
            'std_gender':get_standard_data()[0],
            'std_race':get_standard_data()[1],
            'std_state':get_standard_data()[2],
            'std_biz_ownership_type':get_standard_data()[3],
            'std_bumi_status':get_standard_data()[4],
            'std_biz_sector':get_standard_data()[5],
            'colCountTotal':get_data_clean(request)[3],
        }
        return render(request, self.template_name, extra_context)
    
    
@restrict_user("dq_group")
@csrf_protect
def submitValue(request):
    """_summary_
    Update submitted data from datacleaning/dataupdate to mapping table

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if request.method == 'POST':
        col_name = request.POST['col_name']
        
        if col_name == "jantina_ind":
            iaValue_gender = request.POST['IAValue']
            selectedValue_gender = request.POST['selectedValue']
            a = MapTableGender.objects.filter(
                gender=iaValue_gender
                ).update(std_gender=selectedValue_gender)
            logger.info("Update value for DQLV2 " + iaValue_gender + " to " 
                        + selectedValue_gender + " - " + str(request.user.username))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                       "Update value for DQLV2 " + iaValue_gender + " to " 
                                       + selectedValue_gender + " - " + str(request.user.username))]
                zabbix_sender.send(packet)
            except:
                pass
        
        elif col_name == "bangsa_ind":
            iaValue_race = request.POST['IAValue']
            selectedValue_race = request.POST['selectedValue']
            b = MapTableRace.objects.filter(
                race=iaValue_race
                ).update(std_race=selectedValue_race)
            logger.info("Update value for DQLV2 " + iaValue_race + " to " 
                        + selectedValue_race + " - " + str(request.user.username))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                       "Update value for DQLV2 " + iaValue_race + " to " 
                                       + selectedValue_race + " - " + str(request.user.username))]
                zabbix_sender.send(packet)
            except:
                pass
        
        elif col_name == "negeri_ind":
            iaValue_state = request.POST['IAValue']
            selectedValue_state = request.POST['selectedValue']
            c = MapTableState.objects.filter(
                state=iaValue_state
                ).update(std_state=selectedValue_state)
            logger.info("Update value for DQLV2 " + iaValue_state + " to " 
                        + iaValue_state + " - " + str(request.user.username))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                       "Update value for DQLV2 " + iaValue_state + " to " 
                                       + iaValue_state + " - " + str(request.user.username))]
                zabbix_sender.send(packet)
            except:
                pass
            
        elif col_name == "negeri":
            iaValue_state = request.POST['IAValue']
            selectedValue_state = request.POST['selectedValue']
            c2 = MapTableState.objects.filter(
                state=iaValue_state
                ).update(std_state=selectedValue_state)
            logger.info("Update value for DQLV2 " + iaValue_state + " to " 
                        + selectedValue_state + " - " + str(request.user.username))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                       "Update value for DQLV2 " + iaValue_state + " to " 
                                       + selectedValue_state + " - " + str(request.user.username))]
                zabbix_sender.send(packet)
            except:
                pass
        
        elif col_name == "negeri_entiti":
            iaValue_state = request.POST['IAValue']
            selectedValue_state = request.POST['selectedValue']
            c3 = MapTableState.objects.filter(
                state=iaValue_state
                ).update(std_state=selectedValue_state)
            logger.info("Upload value for DQLV2 " + iaValue_state + " to " 
                        + selectedValue_state + " - " + str(request.user.username))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                       "Upload value for DQLV2 " + iaValue_state + " to " 
                                       + selectedValue_state + " - " + str(request.user.username))]
                zabbix_sender.send(packet)
            except:
                pass
            
        elif col_name == "jenis_entiti":
            iaValue_biz_ownership_type = request.POST['IAValue']
            selectedValue_biz_ownership_type = request.POST['selectedValue']
            d = MapTableBizOwnershipType.objects.filter(
                biz_ownership_type=iaValue_biz_ownership_type
                ).update(std_biz_ownership_type=selectedValue_biz_ownership_type)
            logger.info("Update value for DQLV2 " + iaValue_biz_ownership_type + " to " 
                        + selectedValue_biz_ownership_type + " - " + str(request.user.username))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                       "Update value for DQLV2 " + iaValue_biz_ownership_type + " to " 
                                       + selectedValue_biz_ownership_type + " - " + str(request.user.username))]
                zabbix_sender.send(packet)
            except:
                pass
        
        elif col_name == "status_bumiputera_entiti":
            iaValue_bumi_status = request.POST['IAValue']
            selectedValue_bumi_status = request.POST['selectedValue']
            e = MapTableBumiStatus.objects.filter(
                bumi_status=iaValue_bumi_status
                ).update(std_bumi_status=selectedValue_bumi_status)
            logger.info("Update value for DQLV2 " + iaValue_bumi_status + " to " 
                        + selectedValue_bumi_status + " - " + str(request.user.username))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                       "Update value for DQLV2 " + iaValue_bumi_status + " to " 
                                       + selectedValue_bumi_status + " - " + str(request.user.username))]
                zabbix_sender.send(packet)
            except:
                pass
        
        elif col_name == "sektor_entiti":
            iaValue_biz_sector = request.POST['IAValue']
            selectedValue_biz_sector = request.POST['selectedValue']
            f = MapTableBizSector.objects.filter(
                biz_sector=iaValue_biz_sector
                ).update(std_biz_sector=selectedValue_biz_sector)
            logger.info("Update value for DQLV2 " + iaValue_biz_sector + " to " 
                        + selectedValue_biz_sector + " - " + str(request.user.username))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                       "Update value for DQLV2 " + iaValue_biz_sector + " to " 
                                       + selectedValue_biz_sector + " - " + str(request.user.username))]
                zabbix_sender.send(packet)
            except:
                pass
        return HttpResponse(status=200)