from django.shortcuts import  render, redirect
from .forms import FileForm
from .models import Store
from .service import parse_file_form, calculate_store_balance, format_cnabs_by_store

def cnab(request):
    if request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            cnabs = parse_file_form(request.FILES['file'].file)
            for cnab in cnabs:
                cnab.store.balance = calculate_store_balance(store_name=cnab.store.name, 
                                                             type_id=cnab.transaction_type, 
                                                             value=cnab.value)
                cnab.store.save()
                cnab.save()
            return redirect('cnab')

    stores = Store.objects.all()
    formatted_result = format_cnabs_by_store(stores)
    return render(request=request, 
                  template_name="upload_file.html", 
                  context={'form':FileForm(), 'result': formatted_result})
