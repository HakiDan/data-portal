from django import forms
from apps.upload.models import MasterlistBudget
import os
from .models import *
import datetime as dt

class MasterlistNECForm(forms.ModelForm):
   sub_init_id = forms.CharField(required=True)
   init_name = forms.CharField(required=True)
   subinit_name = forms.CharField(required=True)
   class Meta:
      model = MasterlistBudget
      fields = ['modified_by', 'stf', 'stf_id', 'category_nec', 'category_id', 'ministry', 
                'agency', 'allocation', 'target', 'program', 'status', 'program_code',
                'sub_init_id', 'init_name', 'subinit_name']
      
   def masterNECName(self):
      return os.path.basename(self.MasterlistBudget.name)
   
   def clean(self):
      super(MasterlistNECForm, self).clean()
      sub_init_id = self.cleaned_data.get('sub_init_id')
      init_name = self.cleaned_data.get('init_name')
      subinit_name = self.cleaned_data.get('subinit_name')
      
      if MasterlistBudget.objects.filter(sub_init_id=sub_init_id).exists():
         self._errors['sub_init_id'] = self.error_class(['Indeks data telah wujud - ' + sub_init_id])
         
      if MasterlistBudget.objects.filter(sub_init_id=init_name).exists():
         self._errors['init_name'] = self.error_class(['Nama inisiatif telah wujud - ' + init_name])
         
      if MasterlistBudget.objects.filter(sub_init_id=sub_init_id).exists():
         self._errors['subinit_name'] = self.error_class(['Nama subinisiatif telah wujud - ' + subinit_name])
         
      return self.cleaned_data
   
class MasterlistNECFormEdit(forms.ModelForm):
   class Meta:
      model = MasterlistBudget
      fields = ['sub_init_id', 'init_name', 'subinit_name', 'modified_by', 
                'stf', 'stf_id', 'category_nec', 'category_id', 'ministry', 
                'agency', 'allocation', 'target', 'program', 'status']
   
   def masterNameNEC(self):
      return os.path.basename(self.MasterlistBudget.name)