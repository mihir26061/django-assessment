from django.http import JsonResponse
from .models import Order

def order_summary(request):
    
    # orders = Order._base_manager.all()
    orders = (
            Order._base_manager
            .select_related("customer")
            .prefetch_related("items")
        )

    data = []
    print("length of orders:", len(orders))
    for order in orders:
        data.append({
            "id": order.id,
            "customer": order.customer.name,
            "items": [i.name for i in order.items.all()]
        })

    return JsonResponse(data, safe=False)