from typing import List
from io import BytesIO
from datetime import datetime

from .models import Cnab, Store

TRX_DEBIT = '1'
TRX_TICKET = '2'
TRX_FINANCIAL = '3'
TRX_CREDIT = '4'
TRX_LOAN_RECEIPT = '5'
TRX_SALES = '6'
TRX_TED_RECEIPT = '7'
TRX_DOC_RECEIPT = '8'
TRX_RENT = '9'

TRANSACTIONS = {
    TRX_DEBIT: {'description': 'Débito', 'nature': 'Entrada', 'signal': '+'},
    TRX_TICKET: {'description': 'Boleto', 'nature': 'Saída', 'signal': '-'},
    TRX_FINANCIAL: {'description': 'Financeiro', 'nature': 'Saída', 'signal': '-'},
    TRX_CREDIT: {'description': 'Crédito', 'nature': 'Entrada', 'signal': '+'},
    TRX_LOAN_RECEIPT: {'description': 'Recebimento Empréstimo', 'nature': 'Entrada', 'signal': '+'},
    TRX_SALES: {'description': 'Vendas', 'nature': 'Entrada', 'signal': '+'},
    TRX_TED_RECEIPT: {'description': 'Recebimento TED', 'nature': 'Entrada', 'signal': '+'},
    TRX_DOC_RECEIPT: {'description': 'Recebimento DOC', 'nature': 'Entrada', 'signal': '+'},
    TRX_RENT: {'description': 'Aluguel', 'nature': 'Saída', 'signal': '-'}
}

def parse_file_form(file: BytesIO) -> List[Cnab]:

    cnabs = []
    for line in file.readlines():
        content = line.decode('UTF-8').strip()
        date_in_str = f'{content[1:5]}-{content[5:7]}-{content[7:9]}  {content[42:44]}:{content[44:46]}:{content[46:48]} -0300'
        
        cnabs.append(Cnab(
            transaction_type = content[0],
            date = datetime.strptime(date_in_str, '%Y-%m-%d %H:%M:%S %z'),
            value = int(content[9:19]) / 100,
            cpf = content[19:30],
            card = content[30:42],
            store = Store(owner = content[48:62].strip().lower(),
                          name = content[62:81].strip().lower())
        ))

    return cnabs

def calculate_store_balance(store_name, type_id, value) -> float:
    store = Store.objects.filter(name=store_name).first()
    current_balance = store.balance if store else 0.0

    return eval(f'{current_balance} {TRANSACTIONS[type_id]["signal"]} {value}')

def format_cnabs_by_store(stores: List[Store]) -> dict:
    result = {}
    for store in stores:
        result[store.pk] = {
            'cnabs': [],
            'store': {'name': store.name,
                      'owner': store.owner,
                      'balance': store.balance}
        }

        cnabs_sorted_by_date = sorted(store.cnabs.iterator(), key=lambda cnab: cnab.date)
        for cnab in cnabs_sorted_by_date:
            transaction = TRANSACTIONS[cnab.transaction_type]
            result[store.pk]['cnabs'].append({
                'date': cnab.date.strftime('%d/%m/%Y'),
                'hour': cnab.date.strftime('%X'),
                'description': transaction['description'],
                'nature': transaction['nature'],
                'cpf': cnab.cpf,
                'card': cnab.card
            })
    return result
