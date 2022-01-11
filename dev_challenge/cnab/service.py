
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

