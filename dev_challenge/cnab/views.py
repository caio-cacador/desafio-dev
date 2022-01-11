from django.shortcuts import  render, redirect
from .forms import FileForm

def cnab(request):
    if request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            return redirect('cnab')

    return render(request=request, 
					template_name="upload_file.html", 
					context={'form':FileForm()})
