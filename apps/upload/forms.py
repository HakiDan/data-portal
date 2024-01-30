from django import forms
from .models import File
import os
from .models import *

class FileForm(forms.ModelForm):
   class Meta:
      model = File
      fields = ['Inisiatif', 'Fail', 'Helaian']
   
   def __init__(self, user=None, *args, **kwargs):
      super(FileForm, self).__init__(*args, **kwargs)
      if user:
         init_assc = list(UserProfile.objects.filter(
                     user__username=user
                  ).values_list('init_id_assc', flat=True))
         self.fields['Inisiatif'].queryset = MasterlistBudget.objects.filter(id__in=init_assc)
   
   def fileName(self):
      return os.path.basename(self.Fail.name)
