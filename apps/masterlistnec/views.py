from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, UpdateView, FormView
from apps.upload.models import MasterlistBudget, MasterlistBudgetLog, AllocationMinistry
from django.urls import reverse_lazy
from django.conf import settings
import datetime as dt
from django.utils.decorators import method_decorator
from core.decorators import restrict_user
from django.contrib.auth.decorators import login_required
import logging
import datetime as dt
from pyzabbix import ZabbixMetric, ZabbixSender
from django.db.models import Q
import datetime as dt
from .forms import MasterlistNECFormEdit, MasterlistNECForm
from django.db.models import F

mainPath = settings.MAINPATH
logger = logging.getLogger('main')
zabbix_sender = ZabbixSender(settings.ZABBIX_SERVER, settings.ZABBIX_PORT)

decorators = [login_required(login_url="/login/"), restrict_user("pid_group")]
@method_decorator(decorators, name='dispatch')
class MasterlistNECView(ListView):
    """_summary_
    Render masterlist page for both PIDs and Lead PIDs (NEC)

    Args:
        ListView (_type_): _description_

    Returns:
        _type_: _description_
    """    
    model = MasterlistBudget
    template_name = 'pid/masterlist_nec.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['object'] = MasterlistBudget.objects.filter(is_active=True).filter(
            Q(program_code='NEC') | Q(program_code='B23 + NEC')).order_by(
            F('date_modified').desc(nulls_last=True))
        return context
    
@method_decorator(decorators, name='dispatch')
class MasterlistNECModifyView(ListView):
    """_summary_
    Render modifylist page for both PIDs and Lead PIDs (With edit button) (NEC)

    Args:
        ListView (_type_): _description_

    Returns:
        _type_: _description_
    """    
    model = MasterlistBudget
    template_name = 'pid/modifylist_nec.html'

    def get_queryset(self):
        return MasterlistBudget.objects.filter(is_active=True).filter(
            Q(program_code='NEC') | Q(program_code='B23 + NEC')).order_by(
            F('date_modified').desc(nulls_last=True))
    
@method_decorator(decorators, name='dispatch')
class MasterlistNECUpdate(SuccessMessageMixin, UpdateView):
    """_summary_
    Class for update masterlist (NEC)

    Args:
        SuccessMessageMixin (_type_): _description_
        UpdateView (_type_): _description_

    Returns:
        _type_: _description_
    """    
    model = MasterlistBudget
    form_class = MasterlistNECFormEdit
    template_name = 'pid/listedit_nec.html'
    success_message = "Inisiatif anda telah dikemaskini"
    success_url = reverse_lazy('modifylist_nec')
    
    def form_valid(self, form):
        allocation = form.cleaned_data['allocation']
        subinit_name = form.cleaned_data['subinit_name']
        self.object.date_modified = dt.datetime.now()
        self.object.modified_by = self.request.user.username
        
        get_master = self.model.objects.get(subinit_name=self.object.subinit_name, 
                                            sub_init_id=self.object.sub_init_id)
        field_object = self.model._meta.get_field('sub_init_id')
        field_object_alct = self.model._meta.get_field('allocation')
        
        field_value = getattr(get_master, field_object.attname)
        current_allocation = getattr(get_master, field_object_alct.attname)
        
        MasterlistBudgetLog(subinit_name=subinit_name, date_modified=dt.datetime.now(), 
                            sub_init_id=field_value, requestor=self.request.user.username).save()
            
        if allocation != current_allocation:
            AllocationMinistry(subinit_name=subinit_name, alct=allocation, 
                               date_modified=dt.datetime.now(), sub_init_id=field_value, 
                               requestor=self.request.user.username).save()
        
        logger.info("Edit initiative " + str(self.object.subinit_name) + " - " + 
                    str(self.request.user.username))
        try:
            packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                "Edit initiative " + str(self.object.subinit_name) + " - " + 
                                str(self.request.user.username))]
            zabbix_sender.send(packet)
        except:
            pass
        return super().form_valid(form)
    
@method_decorator(decorators, name='dispatch')
class MasterlistNECUpload(SuccessMessageMixin, FormView):
    """_summary_
    Class for add masterlist (NEC)

    Args:
        SuccessMessageMixin (_type_): _description_
        FormView (_type_): _description_

    Returns:
        _type_: _description_
    """    
    form_class = MasterlistNECForm
    template_name = 'pid/listadd_nec.html'
    success_message = "Inisiatif baru telah ditambah"
    success_url = reverse_lazy('masterlist_nec')
    
    def form_valid(self, form):
        obj = MasterlistBudget()
        obj.init_id = form.cleaned_data['sub_init_id']
        obj.sub_init_id = form.cleaned_data['sub_init_id']
        obj.init_name = form.cleaned_data['init_name']
        obj.subinit_name = form.cleaned_data['subinit_name']
        obj.stf = form.cleaned_data['stf']
        obj.category_nec = form.cleaned_data['category_nec']
        obj.ministry = form.cleaned_data['ministry']
        obj.agency = form.cleaned_data['agency']
        obj.allocation = form.cleaned_data['allocation']
        obj.target = form.cleaned_data['target']
        obj.status = form.cleaned_data['status']
        obj.program = form.cleaned_data['program']
        obj.nec_id = form.cleaned_data['sub_init_id']
        obj.program_code = "NEC"
        obj.is_active = True
        obj.modified_by = self.request.user.username
        obj.date_modified = dt.datetime.now()
        obj.save()
        MasterlistBudgetLog(subinit_name=obj.subinit_name, date_modified=dt.datetime.now(), 
                            sub_init_id=obj.sub_init_id, requestor=self.request.user.username).save()
        
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