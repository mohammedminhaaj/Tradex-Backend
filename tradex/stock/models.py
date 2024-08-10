from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Abstract model to track creation and modification timestamps
class AuditModel(models.Model):
    """
    An abstract model that includes fields for tracking creation and modification timestamps.
    """
    created_at = models.DateTimeField(
        verbose_name=_("created at"),
        auto_now_add=True,
        editable=False
    )
    modified_at = models.DateTimeField(
        verbose_name=_("modified at"),
        auto_now=True,
        editable=False
    )

    class Meta:
        abstract = True  # This model is abstract and won't create a table

# Model for storing stock information
class Stock(AuditModel):
    """
    A model to store stock information.
    """
    name = models.CharField(
        max_length=10,
        db_index=True
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=6
    )

    def __str__(self) -> str:
        """
        Return the string representation of the stock, which is its name.
        """
        return self.name

    class Meta:
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'
        db_table = 'stock'
        ordering = ['-id']  # Order stocks by ID in descending order

# Model for tracking user stock holdings and investments
class UserStock(AuditModel):
    """
    A model to track the stock holdings and investments of users.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField(
        default=0
    )
    invested_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    def __str__(self) -> str:
        """
        Return a string representation of the user stock entry, showing the username and stock name.
        """
        return f"{self.user.username} - {self.stock.name}"

    class Meta:
        verbose_name = 'User Stock'
        verbose_name_plural = 'User Stocks'
        db_table = 'user_stock'
        # Order user stocks by ID in descending order
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=("user", "stock"),
                name="unique_user_stock_mapping"
            )
        ]

# Model for auditing stock data files
class StockDataAudit(AuditModel):
    """
    A model to keep a record of stock data files.
    """
    file_name = models.CharField(
        max_length=256,
        unique=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Stock Data Audit'
        verbose_name_plural = 'Stock Data Audits'
        db_table = 'stock_data_audit'
        # Order stock data audits by ID in descending order
        ordering = ['-id']
