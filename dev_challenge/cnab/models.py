from django.db import models

class File(models.Model):
    class Meta:
        abstract: True
    file = models.FileField()


class Store(models.Model):  
    name = models.CharField(max_length=19, primary_key=True)
    owner = models.CharField(max_length=14)
    balance = models.DecimalField(decimal_places=2, max_digits=10, default=0)

    def __str__(self):
        return f"Name: {self.name} - Owner:{self.owner} - Balance: {self.balance}"


class Cnab(models.Model):
    class Meta:
        verbose_name = 'CNAB'
        verbose_name_plural = 'CNABs'
        
    transaction_type = models.CharField(max_length=1)
    date = models.DateTimeField()
    value = models.DecimalField(decimal_places=2, max_digits=10)
    cpf = models.CharField(max_length=11)
    card = models.CharField(max_length=12)

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='cnabs')

    def __str__(self):
        return f"{self.pk} {self.date} {self.transaction_type} {self.cpf} {self.card}"
