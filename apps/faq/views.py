from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
import mimetypes
 
mainPath = settings.MAINPATH

@login_required(login_url="/login/")
def faq(request):
	"""_summary_
	Provide PODS user guideline file in FAQ page

	Args:
		request (_type_): _description_

	Returns:
		_type_: _description_
	"""    
	context = {'file_name':'PODS.pdf'}
	return render(request, 'home/faq.html', context)


def download_faq(request, file_name):
	"""_summary_
	Download PODS user guideline file in FAQ page

	Args:
		request (_type_): _description_
		file_name (_type_): _description_

	Returns:
		_type_: _description_
	"""    
	filename = "{}/guideline/{}".format(mainPath, file_name)
	fl = open(filename, 'rb')
	mime_type, _ = mimetypes.guess_type(filename)
	response = HttpResponse(fl, content_type=mime_type)
	response['Content-Disposition'] = "attachment; filename=%s" % file_name
	return response
