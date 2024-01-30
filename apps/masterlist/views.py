from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, UpdateView, FormView, View
from apps.upload.models import (MasterlistBudget, DisburseMinistry, GeneralRemark, 
                                AllocationMinistry, MasterlistBudgetLog, UserProfile)
from django.urls import reverse_lazy
from .forms import MasterlistForm, FileFormMasterlist, MasterlistFormEdit
from django.conf import settings
import datetime as dt
from django.utils.decorators import method_decorator
from core.decorators import restrict_user
from django.contrib.auth.decorators import login_required
import logging
from django.shortcuts import HttpResponse, redirect, render
from django.contrib import messages
import datetime as dt
from pyzabbix import ZabbixMetric, ZabbixSender
from django.db.models import Q
import pandas as pd
from django.utils.text import get_valid_filename
from django.views.decorators.csrf import csrf_protect
import os
import datetime as dt
from django.db.models import F

mainPath = settings.MAINPATH
logger = logging.getLogger('main')
zabbix_sender = ZabbixSender(settings.ZABBIX_SERVER, settings.ZABBIX_PORT)

decorators = [login_required(login_url="/login/"), restrict_user("pid_group")]
@method_decorator(decorators, name='dispatch')
class MasterlistView(ListView):
    """_summary_
    Render masterlist page for both PIDs and Lead PIDs

    Args:
        ListView (_type_): _description_

    Returns:
        _type_: _description_
    """    
    model = MasterlistBudget
    template_name = 'pid/masterlist.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['object'] = MasterlistBudget.objects.filter(is_active=True).filter(
            Q(program_code='B23') | Q(program_code='B23 + NEC')).order_by(
            F('date_modified').desc(nulls_last=True))
        context['userprofile'] = UserProfile.objects.all()
        return context
    

@method_decorator(decorators, name='dispatch')
class MasterlistModifyView(ListView):
    """_summary_
    Render modifylist page for both PIDs and Lead PIDs (With edit button)

    Args:
        ListView (_type_): _description_

    Returns:
        _type_: _description_
    """    
    model = MasterlistBudget
    template_name = 'pid/modifylist.html'

    def get_queryset(self):
        return MasterlistBudget.objects.filter(is_active=True).filter(
            Q(program_code='B23') | Q(program_code='B23 + NEC')).order_by(
            F('date_modified').desc(nulls_last=True))


@method_decorator(decorators, name='dispatch')
class MasterlistUpload(SuccessMessageMixin, FormView):
    """_summary_
    Class for add masterlist

    Args:
        SuccessMessageMixin (_type_): _description_
        FormView (_type_): _description_

    Returns:
        _type_: _description_
    """    
    form_class = MasterlistForm
    template_name = 'pid/listadd.html'
    success_message = "Inisiatif baru telah ditambah"
    success_url = reverse_lazy('masterlist')

    def form_valid(self, form):
        obj = MasterlistBudget()
        obj.tekad = form.cleaned_data['tekad']
        obj.ikhtiar = form.cleaned_data['ikhtiar']
        obj.sub_1 = form.cleaned_data['sub_1']
        obj.sub_2 = form.cleaned_data['sub_2']
        obj.init_name = form.cleaned_data['init_name']
        obj.subinit_name = form.cleaned_data['subinit_name']
        obj.allocation = form.cleaned_data['allocation']
        obj.cur_disb = form.cleaned_data['cur_disb']
        obj.cur_remark = form.cleaned_data['cur_remark']
        obj.ministry = form.cleaned_data['ministry']
        obj.agency = form.cleaned_data['agency']
        obj.category = form.cleaned_data['category']
        obj.status = form.cleaned_data['status']
        obj.nec_id = form.cleaned_data['nec_id']
        obj.stf = form.cleaned_data['stf']
        obj.category_nec = form.cleaned_data['category_nec']
        obj.program = form.cleaned_data['program']
        obj.target = form.cleaned_data['target']
        obj.is_active = True
        obj.modified_by = self.request.user.username
        obj.date_modified = dt.datetime.now()

        
        if (not obj.sub_1 and not obj.sub_2) or (not obj.sub_1):
            obj.init_id = str(obj.tekad) + str(obj.ikhtiar)
            obj.sub_init_id = str(obj.tekad) + str(obj.ikhtiar)
        elif not obj.sub_2:
            obj.init_id = str(obj.tekad) + str(obj.ikhtiar) + '_' + str(obj.sub_1)
            obj.sub_init_id = str(obj.tekad) + str(obj.ikhtiar) + '_' + str(obj.sub_1)
        else:
            obj.init_id = str(obj.tekad) + str(obj.ikhtiar) + '_' + str(obj.sub_1) + '_' + str(obj.sub_2)
            obj.sub_init_id = str(obj.tekad) + str(obj.ikhtiar) + '_' + str(obj.sub_1) + '_' + str(obj.sub_2)
        
        if obj.sub_init_id and obj.nec_id:
            obj.program_code = "B23 + NEC"
        elif obj.sub_init_id:
            obj.program_code = "B23"
        else:
            pass
        
        obj.save()
        MasterlistBudgetLog(subinit_name=obj.subinit_name, date_modified=dt.datetime.now(), 
                            sub_init_id=obj.sub_init_id, requestor=self.request.user.username).save()
        
        if obj.cur_disb:
            DisburseMinistry(subinit_name=obj.subinit_name, disb=obj.cur_disb, 
                             date_modified=dt.datetime.now(), sub_init_id=obj.sub_init_id, 
                             requestor=self.request.user.username).save()
        
        if obj.cur_remark:
            GeneralRemark(subinit_name=obj.subinit_name, remark=obj.cur_remark, 
                          date_modified=dt.datetime.now(), sub_init_id=obj.sub_init_id, 
                          requestor=self.request.user.username).save()
        
        if obj.allocation:
            AllocationMinistry(subinit_name=obj.subinit_name, alct=obj.allocation, 
                               date_modified=dt.datetime.now(), sub_init_id=obj.sub_init_id, 
                               requestor=self.request.user.username).save()
        
        logger.info("Upload initiative " + str(obj.subinit_name) + " - " + str(self.request.user.username))
        try:
            packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                   "Upload initiative " + str(obj.subinit_name) + " - Pending for Lead PID approval - " 
                                   + str(self.request.user.username))]
            zabbix_sender.send(packet)
        except:
            pass

        return super().form_valid(form)


@method_decorator(decorators, name='dispatch')
class MasterlistUpdate(SuccessMessageMixin, UpdateView):
    """_summary_
    Class for update masterlist

    Args:
        SuccessMessageMixin (_type_): _description_
        UpdateView (_type_): _description_

    Returns:
        _type_: _description_
    """    
    model = MasterlistBudget
    form_class = MasterlistFormEdit
    template_name = 'pid/listedit.html'
    success_message = "Inisiatif anda telah dikemaskini"
    success_url = reverse_lazy('modifylist')

    def form_valid(self, form):
        allocation = form.cleaned_data['allocation']
        cur_disb = form.cleaned_data['cur_disb']
        cur_remark = form.cleaned_data['cur_remark']
        subinit_name = form.cleaned_data['subinit_name']
        self.object.init_id = self.object.sub_init_id
        self.object.date_modified = dt.datetime.now()
        self.object.modified_by = self.request.user.username
        
        get_master = self.model.objects.get(subinit_name=self.object.subinit_name, 
                                            sub_init_id=self.object.sub_init_id)
        field_object = self.model._meta.get_field('sub_init_id')
        field_object_alct = self.model._meta.get_field('allocation')
        field_object_rem = self.model._meta.get_field('cur_remark')
        field_object_disb = self.model._meta.get_field('cur_disb')
        
        field_value = getattr(get_master, field_object.attname)
        current_allocation = getattr(get_master, field_object_alct.attname)
        current_remark = getattr(get_master, field_object_rem.attname)
        current_disb = getattr(get_master, field_object_disb.attname)
        
        MasterlistBudgetLog(subinit_name=subinit_name, date_modified=dt.datetime.now(), 
                            sub_init_id=field_value, requestor=self.request.user.username).save()
        
        if cur_disb != current_disb:
            DisburseMinistry(subinit_name=subinit_name, disb=cur_disb, 
                             date_modified=dt.datetime.now(), sub_init_id=field_value, 
                             requestor=self.request.user.username).save()
        
        if cur_remark != current_remark:
            GeneralRemark(subinit_name=subinit_name, remark=cur_remark, 
                          date_modified=dt.datetime.now(), sub_init_id=field_value, 
                          requestor=self.request.user.username).save()
            
        if allocation != current_allocation:
            AllocationMinistry(subinit_name=subinit_name, alct=allocation, 
                               date_modified=dt.datetime.now(), sub_init_id=field_value, 
                               requestor=self.request.user.username).save()
        
        logger.info("Edit initiative " + str(self.object.subinit_name) + " - " + 
                    str(self.request.user.username))
        try:
            packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                   "Edit initiative " + str(object.subinit_name) + " - " + 
                                   str(self.request.user.username))]
            zabbix_sender.send(packet)
        except:
            pass
        return super().form_valid(form)
    
    
def convert_to_csv(nameFile, file_ext):
    """_summary_
    Convert any text format to csv

    Args:
        nameFile (_type_): _description_
        file_ext (_type_): _description_

    Returns:
        _type_: _description_
    """
    if file_ext == "csv":
        return "{}/masterlist_upload/{}.csv".format(mainPath, nameFile)
        
    elif file_ext in ("xlsx", "xls"):
        read_file = pd.read_excel(r"{}/masterlist_upload/{}.{}".format(mainPath, nameFile, file_ext))
        read_file.to_csv(r"{}/masterlist_upload/{}.csv".format(mainPath, nameFile), index = False, header = True)
        read_file = read_file.fillna("NA")
        return "{}/masterlist_upload/{}.csv".format(mainPath, nameFile)
    
    
@csrf_protect
def cancel_submission_masterlist(request):
    """_summary_
    Remove working file from /masterlist_upload folder

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if request.method == 'POST':
        file_name = request.POST['file_name']
        os.remove(r"{}/masterlist_upload/{}.csv".format(mainPath, file_name))
        logger.info("Cancel masterlist file " + file_name + ".csv - " + 
                    str(request.user.username))
        try:
            packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                   "Cancel masterlist file " + file_name + ".csv - " + 
                                   str(request.user.username))]
            zabbix_sender.send(packet)
        except:
            pass
        return HttpResponse(status=200)
    logger.info("Failed cancel masterlist file " + file_name + ".csv - " + 
                str(request.user.username))
    try:
        packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                "Failed cancel masterlist file " + file_name + ".csv - " + 
                                str(request.user.username))]
        zabbix_sender.send(packet)
    except:
        pass
    return HttpResponse(status=400)


@csrf_protect
def submit_masterlist(request):
    """_summary_
    Save masterlist record to the database (remark, allocation and disbursement)

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if request.method == 'POST':
        file_name = request.POST['file_name']
        df = pd.read_csv("{}/masterlist_upload/{}.csv".format(mainPath, file_name))
        for index, row in df.iterrows():
            get_master = MasterlistBudget.objects.get(sub_init_id=row['indeks_data'])
            field_object = MasterlistBudget._meta.get_field('sub_init_id')
            field_object_subinitname = MasterlistBudget._meta.get_field('subinit_name')
            field_value = getattr(get_master, field_object.attname)
            field_value_subinitname = getattr(get_master, field_object_subinitname.attname)
            
            if 'nota' in df.columns:
                MasterlistBudget.objects.filter(sub_init_id=row['indeks_data']).update(cur_remark=row['nota'])
                GeneralRemark(subinit_name=field_value_subinitname, 
                              date_modified=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                              sub_init_id=field_value, requestor=str(request.user.username), 
                              remark=row['nota']).save()
                logger.info("Successfully update masterlist remark " + field_value + " - " + 
                            str(request.user.username))
                try:
                    packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                        "Successfully update masterlist remark " + field_value + " - " + 
                                        str(request.user.username))]
                    zabbix_sender.send(packet)
                except:
                    pass
            
            if 'penyaluran' in df.columns:
                MasterlistBudget.objects.filter(sub_init_id=row['indeks_data']).update(cur_disb=row['penyaluran'])
                DisburseMinistry(subinit_name=field_value_subinitname, 
                                 date_modified=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                                 sub_init_id=field_value, requestor=str(request.user.username), 
                                 disb=row['penyaluran']).save()
                logger.info("Successfully update masterlist disbursement " + field_value + " - " + 
                            str(request.user.username))
                try:
                    packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                        "Successfully update masterlist disbursement " + field_value + " - " + 
                                        str(request.user.username))]
                    zabbix_sender.send(packet)
                except:
                    pass
            
            if 'peruntukan' in df.columns:
                MasterlistBudget.objects.filter(sub_init_id=row['indeks_data']).update(allocation=row['peruntukan'])
                AllocationMinistry(subinit_name=field_value_subinitname, 
                                   date_modified=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                                   sub_init_id=field_value, requestor=str(request.user.username), 
                                   alct=row['peruntukan']).save()
                logger.info("Successfully update masterlist allocation " + field_value + " - " + 
                            str(request.user.username))
                try:
                    packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                        "Successfully update masterlist allocation " + field_value + " - " + 
                                        str(request.user.username))]
                    zabbix_sender.send(packet)
                except:
                    pass
                
        messages.success(request, "Fail serahan anda berjaya dimuat naik")
        logger.info("Successfully submit masterlist file " + file_name + ".csv - " + 
                    str(request.user.username))
        try:
            packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                "Successfully submit masterlist file " + file_name + ".csv - " + 
                                str(request.user.username))]
            zabbix_sender.send(packet)
        except:
            pass
        return HttpResponse(status=200)
    logger.info("Failed submit masterlist file " + file_name + ".csv - " + 
                str(request.user.username))
    try:
        packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                            "Failed submit masterlist file " + file_name + ".csv - " + 
                            str(request.user.username))]
        zabbix_sender.send(packet)
    except:
        pass
    return HttpResponse(status=400)
    
    
@method_decorator(decorators, name='dispatch')
class BulkUpdateInit(View):
    """_summary_
    Class for masterlist upload (Update remark, allocation & disbursement simultaneously)

    Args:
        View (_type_): _description_

    Returns:
        _type_: _description_
    """    
    form_class = FileFormMasterlist
    template = 'pid/bulk_update_init.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template, {'form':form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        file_name = str(request.FILES['Fail'])
        nameFile = file_name.rsplit(".", 1)[0]
        nameFile = get_valid_filename(nameFile)
        
        if form.is_valid():
            if file_name != '':
                file_ext = file_name.split('.')[1]
                
                if (file_ext not in ['xlsx', 'xls', 'csv']):
                    messages.error(request, "Format fail tidak diterima")
                    return render(request, self.template, {'form':form})
                else:
                    form.save()
                    logger.info("Successfully upload masterlist file " + file_name + " - " + str(request.user.username))
                    workingPath = convert_to_csv(nameFile, file_ext)
                    workingFile = pd.read_csv(workingPath)
                    
                    if 'indeks_data' not in workingFile.columns:
                        messages.error(request, 'Kolum indeks_data tiada dalam fail serahan')
                        return redirect('/masterlist-budget/bulk-update-init')
                    
                    context = {"workingFile": workingFile, "file_name":nameFile}
                    return render(request, "pid/update_init.html", context)
        else:
            logger.info("Failed upload masterlist file " + file_name + " - " + 
                        str(request.user.username))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                    "Failed upload masterlist file " + file_name + " - " + 
                                    str(request.user.username))]
                zabbix_sender.send(packet)
            except:
                pass
            messages.error(request, "Format fail tidak diterima")
            return render(request, self.template, {'form':form})