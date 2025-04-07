from .category_views import CategoryViewSet
from .spare_part_views import SparePartViewSet
from .transaction_views import TransactionViewSet as SparePartTransactionViewSet

__all__ = [
    'CategoryViewSet',
    'SparePartViewSet',
    'SparePartTransactionViewSet',
] 