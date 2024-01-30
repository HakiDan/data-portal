from django import forms
from apps.upload.models import MasterlistBudget, AgencyList, DisburseMinistry, GeneralRemark
from apps.masterlist.models import FileMasterlist
import os
from .models import *
import datetime as dt
from django.contrib.auth.models import User

class MasterlistForm(forms.ModelForm):
   tekad = forms.CharField(required=True)
   ikhtiar = forms.CharField(required=True)
   init_name = forms.CharField(required=True)
   subinit_name = forms.CharField(required=True)
   class Meta:
      model = MasterlistBudget
      fields = ['fokus', 'tekad', 'ikhtiar', 'sub_1', 'sub_2', 'subinit_name', 
                'init_id', 'sub_init_id', 'init_name', 'allocation', 'ministry', 
                'agency', 'category', 'status', 'cur_disb', 'cur_remark', 'program_code', 
                'nec_id', 'stf', 'category_nec', 'program', 'target']
   
   def masterName(self):
      return os.path.basename(self.MasterlistBudget.name)
   
   def clean(self):
      super(MasterlistForm, self).clean()
      tekad = self.cleaned_data.get('tekad')
      ikhtiar = self.cleaned_data.get('ikhtiar')
      sub_1 = self.cleaned_data.get('sub_1')
      sub_2 = self.cleaned_data.get('sub_2')
      
      if (not sub_1 and not sub_2) or (not sub_1):
         init_id = str(tekad) + str(ikhtiar)
         sub_init_id = str(tekad) + str(ikhtiar)
      elif not sub_2:
         init_id = str(tekad) + str(ikhtiar) + '_' + str(sub_1)
         sub_init_id = str(tekad) + str(ikhtiar) + '_' + str(sub_1)
      else:
         init_id = str(tekad) + str(ikhtiar) + '_' + str(sub_1) + '_' + str(sub_2)
         sub_init_id = str(tekad) + str(ikhtiar) + '_' + str(sub_1) + '_' + str(sub_2)
         
      if tekad.startswith('T') is False:
         self._errors['tekad'] = self.error_class(["Tekad menggunakan huruf 'T' sebagai rujukan"])
      
      if ikhtiar.startswith('I') is False:
         self._errors['ikhtiar'] = self.error_class(["Ikhtiar menggunakan huruf 'I' sebagai rujukan"])
               
      if MasterlistBudget.objects.filter(init_id=init_id).exists():
         self._errors['init_name'] = self.error_class(['Indeks data telah wujud - ' + init_id])
         
      if MasterlistBudget.objects.filter(sub_init_id=sub_init_id).exists():
         self._errors['subinit_name'] = self.error_class(['Sub indeks data telah wujud - ' + sub_init_id])
         
      return self.cleaned_data
   
class MasterlistFormEdit(forms.ModelForm):
   class Meta:
      model = MasterlistBudget
      fields = ['fokus', 'tekad', 'ikhtiar', 'sub_1', 'sub_2', 'subinit_name', 
                'init_id', 'sub_init_id', 'init_name', 'allocation', 'ministry', 
                'agency', 'category', 'status', 'cur_disb', 'cur_remark', 'modified_by',
                'nec_id', 'stf', 'category_nec', 'program', 'target']
   
   def masterName(self):
      return os.path.basename(self.MasterlistBudget.name)
   
class DisbForm(forms.ModelForm):
   class Meta:
      model = DisburseMinistry
      fields = ['subinit_name', 'disb']
   
   def disbName(self):
      return os.path.basename(self.DisburseMinistry.name)
   
class RemForm(forms.ModelForm):
   class Meta:
      model = GeneralRemark
      fields = ['subinit_name', 'remark']
   
   def remName(self):
      return os.path.basename(self.GeneralRemark.name)
   
class FileFormMasterlist(forms.ModelForm):
   class Meta:
      model = FileMasterlist
      fields = ['Fail']
   
   def fileName(self):
      return os.path.basename(self.Fail.name)