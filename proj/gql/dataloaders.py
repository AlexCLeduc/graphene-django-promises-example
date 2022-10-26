from collections import defaultdict

from django.db.models import Count, OuterRef, Subquery, Sum

from pleasant_promises.dataloader import SingletonDataLoader

from proj.models import Category, Delivery, DeliveryLineItem, Order, OrderItem, Product

from .util import AbstractChildModelByAttrLoader, PrimaryKeyDataLoaderFactory


class ProductByCategoryIdLoader(AbstractChildModelByAttrLoader):
    model = Product
    attr = "category_id"


class OrderItemByOrderIdLoader(AbstractChildModelByAttrLoader):
    model = OrderItem
    attr = "order_id"


class OrderItemByProductIdLoader(AbstractChildModelByAttrLoader):
    model = OrderItem
    attr = "product_id"


class DeliveryLineItemByDeliveryIdLoader(AbstractChildModelByAttrLoader):
    model = DeliveryLineItem
    attr = "delivery_id"


class MostPopularProductByCategoryIdLoader(SingletonDataLoader):
    """
    example of complex dataloader that composes a simpler one
    """

    def batch_load(self, keys):
        most_popular_product_id_subq = Subquery(
            Product.objects.filter(category_id=OuterRef("pk"))
            .annotate(num_ordered=Sum("order_items__quantity"))
            .order_by("-num_ordered")
            .values_list("id")[:1]
        )

        annotated_categories = Category.objects.filter(pk__in=keys).annotate(
            most_popular_product_id=most_popular_product_id_subq
        )
        # now fetch products using dataloader, in case they've already been loaded

        product_loader_cls = PrimaryKeyDataLoaderFactory.get_model_by_id_loader(Product)
        product_loader = product_loader_cls(self.dataloader_instance_cache)
        most_popular_products = yield product_loader.load_many(
            [
                c.most_popular_product_id
                for c in annotated_categories
                if c.most_popular_product_id
            ]
        )
        by_category_id = {p.category_id: p for p in most_popular_products}
        return [by_category_id.get(k) for k in keys]
