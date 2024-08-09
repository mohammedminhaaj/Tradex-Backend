from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Create your models here.


class AuditModel(models.Model):
    created_at = models.DateTimeField(verbose_name=_(
        "created at"), auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(verbose_name=_(
        "modified at"), auto_now=True, editable=False)

    class Meta:
        abstract = True


class Stock(AuditModel):
    name = models.CharField(max_length=10, db_index=True)
    price = models.DecimalField(max_digits=12, decimal_places=6)

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'
        db_table = 'stock'
        ordering = ['-id']


class UserStock(AuditModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    invested_amount = models.DecimalField(
        max_digits=8, decimal_places=2, default=0)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.stock.name}"

    class Meta:
        verbose_name = 'User Stock'
        verbose_name_plural = 'User Stocks'
        db_table = 'user_stock'
        ordering = ['-id']
        constraints = [models.UniqueConstraint(
            fields=("user", "stock"), name="unique_user_stock_mapping")]
