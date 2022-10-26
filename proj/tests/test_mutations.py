from proj.factories import ProductFactory, UserFactory
from proj.models import Order

from .util import execute_query

create_order_mutation = """
mutation CreateOrder($userId: Int!, $orderItems: [OrderItemInput!]!) {
    createOrder(userId: $userId, orderItems: $orderItems) {
        order {
            id
        }
    }
}
"""


def test_most_popular_product_query():
    u = UserFactory()
    p1 = ProductFactory()
    p2 = ProductFactory()

    result = execute_query(
        create_order_mutation,
        variables={
            "userId": u.id,
            "orderItems": [
                {"productId": p1.id, "quantity": 1},
                {"productId": p2.id, "quantity": 2},
            ],
        },
    )

    created_id = result["createOrder"]["order"]["id"]
    assert created_id is not None

    created_order = Order.objects.get(id=created_id)
    assert created_order.user == u
    assert created_order.order_items.count() == 2
    assert created_order.order_items.filter(product=p1, quantity=1).exists()
    assert created_order.order_items.filter(product=p2, quantity=2).exists()
