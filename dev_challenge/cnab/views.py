from django.shortcuts import  render, redirect
from .forms import FileForm
from .models import Cnab, Store
from .service import parse_file_form, calculate_store_balance, format_cnabs_by_store
from .exceptions import InvalidTransactionType

def cnab(request):
    exception = None
    if request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                cnabs = parse_file_form(request.FILES['file'].file)
                for cnab in cnabs:
                    cnab.store.balance = calculate_store_balance(store_name=cnab.store.name, 
                                                                type_id=cnab.transaction_type, 
                                                                value=cnab.value)
                    cnab.store.save()
                Cnab.objects.bulk_create(cnabs)
            except InvalidTransactionType:
                exception = 'There is an invalid transaction type, check if the file is correct!'
            except Exception:
                exception = 'There was an error trying to read the file, check if the file is correct!'
            
            if not exception:
                return redirect('cnab')

    stores = Store.objects.all()
    formatted_result = format_cnabs_by_store(stores)
    return render(request=request, 
                  template_name="upload_file.html", 
                  context={'form':FileForm(), 'result': formatted_result, 'exception': exception})
