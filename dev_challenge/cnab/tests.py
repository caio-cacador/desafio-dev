from datetime import datetime, timezone
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from io import BytesIO
from .models import Store
from .service import *
from .exceptions import InvalidTransactionType


class CnabTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    @staticmethod
    def create_cnab(store: Store, type_: int, date: str, value: str, cpf: str,
                    card: str, hour: str):
        return f"{type_}{date}{value.rjust(10, '0')}{cpf}{card}{hour}{store.owner.ljust(14)}{store.name.ljust(19)}\r\n"

    def send_post(self, file_in_bytes):
        return self.client.post(reverse('cnab'), {'name': 'fake.txt', 'file': BytesIO(file_in_bytes)})

    def test_import_all_fields_from_cnab(self):
        store = Store(name='fake name', owner='fake owner')
        cnab = self.create_cnab(store=store, type_=TRX_FINANCIAL, date='20220101', value='10000', 
                                cpf='12312312300', card='123456789123', hour='151733')
        
        response = self.send_post(cnab.encode())
        self.assertEquals(302, response.status_code)

        store = Store.objects.get(pk='fake name')
        self.assertEquals('fake owner', store.owner)
        self.assertEquals('-100.00', str(store.balance))

        self.assertEqual(1, store.cnabs.count())
        for cnab in store.cnabs.iterator():
            self.assertEquals('3', cnab.transaction_type)
            self.assertEquals(datetime(2022, 1, 1, 18, 17, 33, tzinfo=timezone.utc), cnab.date)
            self.assertEquals('100.00', str(cnab.value))
            self.assertEquals('12312312300', cnab.cpf)
            self.assertEquals('123456789123', cnab.card)
            self.assertEquals('fake name', cnab.store_id)

    def test_normalized_strings(self):
        store_1 = Store(name='fake name', owner='fake owner')
        store_2 = Store(name='FAKEee NAME', owner='FAKEee owner')
        store_3 = Store(name='fâÂãÃke Name', owner='fâÂãÃke owner')

        cnabs = self.create_cnab(store=store_1, type_=TRX_DEBIT, date='20220103', value='1000', 
                                 cpf='00000000000', card='000000000000', hour='081129') \
              + self.create_cnab(store=store_2, type_=TRX_DEBIT, date='20220103', value='1000', 
                                 cpf='00000000000', card='000000000000', hour='081129') \
              + self.create_cnab(store=store_3, type_=TRX_DEBIT, date='20220103', value='1000', 
                                 cpf='00000000000', card='000000000000', hour='081129')
        
        response = self.send_post(cnabs.encode())
        self.assertEquals(302, response.status_code)

        stores = Store.objects.all()
        self.assertEquals(3, stores.count())
        self.assertEquals('fake name', stores.get(pk='fake name').name)
        self.assertEquals('fake owner', stores.get(pk='fake name').owner)
        self.assertEquals('fakeee name', stores.get(pk='fakeee name').name)
        self.assertEquals('fakeee owner', stores.get(pk='fakeee name').owner)
        self.assertEquals('fââããke name', stores.get(pk='fââããke name').name)
        self.assertEquals('fââããke owner', stores.get(pk='fââããke name').owner)
        
    def test_normalized_value(self):
        store = Store(name='fake name', owner='fake owner')
        cnab = self.create_cnab(store=store, type_=TRX_DEBIT, date='20220103', value='12345', 
                                 cpf='00000000000', card='000000000000', hour='081129')
        
        response = self.send_post(cnab.encode())
        self.assertEquals(302, response.status_code)

        store = Store.objects.get(pk='fake name')
        self.assertEquals('123.45', str(store.balance))

    def test_format_cnabs_by_store(self):
        store = Store(name='fake name', owner='fake owner')
        fake_cpf = '00000000000'
        fake_card = '000000000000'
        fake_date = '20220103'
        fake_hour = '081129'
        fake_value = '1000'
        cnabs = self.create_cnab(type_=TRX_DEBIT, store=store, date=fake_date, value=fake_value, 
                                 cpf=fake_cpf, card=fake_card, hour=fake_hour) \
              + self.create_cnab(type_=TRX_TICKET, store=store, date=fake_date, value=fake_value, 
                                 cpf=fake_cpf, card=fake_card, hour=fake_hour) \
              + self.create_cnab(type_=TRX_FINANCIAL, store=store, date=fake_date, value=fake_value, 
                                 cpf=fake_cpf, card=fake_card, hour=fake_hour) \
              + self.create_cnab(type_=TRX_CREDIT, store=store, date=fake_date, value=fake_value, 
                                 cpf=fake_cpf, card=fake_card, hour=fake_hour) \
              + self.create_cnab(type_=TRX_LOAN_RECEIPT, store=store, date=fake_date, value=fake_value, 
                                 cpf=fake_cpf, card=fake_card, hour=fake_hour) \
              + self.create_cnab(type_=TRX_SALES, store=store, date=fake_date, value=fake_value, 
                                 cpf=fake_cpf, card=fake_card, hour=fake_hour) \
              + self.create_cnab(type_=TRX_TED_RECEIPT, store=store, date=fake_date, value=fake_value, 
                                 cpf=fake_cpf, card=fake_card, hour=fake_hour) \
              + self.create_cnab(type_=TRX_DOC_RECEIPT, store=store, date=fake_date, value=fake_value, 
                                 cpf=fake_cpf, card=fake_card, hour=fake_hour) \
              + self.create_cnab(type_=TRX_RENT, store=store, date=fake_date, value=fake_value, 
                                 cpf=fake_cpf, card=fake_card, hour=fake_hour) \

        
        response = self.send_post(cnabs.encode())
        self.assertEquals(302, response.status_code)

        stores = Store.objects.all().order_by('cnabs__transaction_type')
        self.assertEquals(1, stores.count())
        self.assertEqual(9, stores.first().cnabs.count())
        
        formatted_result = format_cnabs_by_store(stores)
        for key, value in formatted_result.items():
            self.assertEquals('fake name', key)
            self.assertEquals('fake name', value['store']['name'])
            self.assertEquals('fake owner', value['store']['owner'])
            self.assertEquals('30.00', str(value['store']['balance']))

            for transaction_type, cnab in enumerate(value['cnabs'], 1):
                transaction = TRANSACTIONS[str(transaction_type)]
                self.assertEquals('03/01/2022', cnab['date'])
                self.assertEquals('11:11:29', cnab['hour'])
                self.assertEquals(transaction['description'], cnab['description'])
                self.assertEquals(transaction['nature'], cnab['nature'])
                self.assertEquals(fake_cpf, cnab['cpf'])
                self.assertEquals(fake_card, cnab['card'])

    def test_balance_calculation_with_all_transaction_types(self):
        store = Store(name='fake name', owner='fake owner', balance='0')
        store.save()
        self.assertEquals('0.00', str(Store.objects.get(pk=store.pk).balance))

        new_balance = calculate_store_balance(store.name, TRX_DEBIT, '10.00')
        self.assertEquals(10.0, new_balance)

        new_balance = calculate_store_balance(store.name, TRX_TICKET, '10.00')
        self.assertEquals(-10.0, new_balance)

        new_balance = calculate_store_balance(store.name, TRX_FINANCIAL, '10.00')
        self.assertEquals(-10.0, new_balance)

        new_balance = calculate_store_balance(store.name, TRX_CREDIT, '10.00')
        self.assertEquals(10.0, new_balance)

        new_balance = calculate_store_balance(store.name, TRX_LOAN_RECEIPT, '10.00')
        self.assertEquals(10.0, new_balance)

        new_balance = calculate_store_balance(store.name, TRX_SALES, '10.00')
        self.assertEquals(10.0, new_balance)

        new_balance = calculate_store_balance(store.name, TRX_TED_RECEIPT, '10.00')
        self.assertEquals(10.0, new_balance)

        new_balance = calculate_store_balance(store.name, TRX_DOC_RECEIPT, '10.00')
        self.assertEquals(10, new_balance)

        new_balance = calculate_store_balance(store.name, TRX_RENT, '10.00')
        self.assertEquals(-10.0, new_balance)

    def test_parse_file_form_with_invalid_transaction_type(self):
        store = Store(name='fake name', owner='fake owner')
        cnab = self.create_cnab(store=store, type_=0, date='20220101', value='10000', 
                                cpf='12312312300', card='123456789123', hour='151733')
        
        with self.assertRaises(InvalidTransactionType):
            parse_file_form(BytesIO(cnab.encode()))
