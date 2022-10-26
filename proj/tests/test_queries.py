from proj.factories import (
    CategoryFactory,
    OrderFactory,
    OrderItemFactory,
    ProductFactory,
    UserFactory,
)

from .util import assert_max_queries, execute_query

most_popular_products_query = """
query {
  categories {
    id
    mostPopularProduct {
      id
    }
  }
}
"""


def test_most_popular_product_query():
    u = UserFactory()
    cat1 = CategoryFactory()
    cat2 = CategoryFactory()

    prod1 = ProductFactory(category=cat1)
    prod2 = ProductFactory(category=cat1)
    prod3 = ProductFactory(category=cat2)
    prod4 = ProductFactory(category=cat2)

    order1 = OrderFactory()
    order2 = OrderFactory()

    OrderItemFactory(order=order1, product=prod1, quantity=1)
    OrderItemFactory(order=order1, product=prod2, quantity=4)
    OrderItemFactory(order=order1, product=prod3, quantity=4)
    OrderItemFactory(order=order1, product=prod4, quantity=1)

    OrderItemFactory(order=order2, product=prod1, quantity=1)
    OrderItemFactory(order=order2, product=prod4, quantity=1)

    with assert_max_queries(3):
        result = execute_query(most_popular_products_query, variables={})

    categories = result["categories"]
    assert len(categories) == 2
    assert {"id": str(cat1.id), "mostPopularProduct": {"id": str(prod2.id)}} in categories
    assert {"id": str(cat2.id), "mostPopularProduct": {"id": str(prod3.id)}} in categories
