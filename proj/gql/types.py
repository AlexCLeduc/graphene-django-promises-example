import graphene
from graphene import Field, Int, List, NonNull, String
from graphene_django import DjangoObjectType

from proj.gql.util import PrimaryKeyDataLoaderFactory
from proj.models import Category as CategoryModel
from proj.models import Delivery as DeliveryModel
from proj.models import DeliveryLineItem as DeliveryLineItemModel
from proj.models import Order as OrderModel
from proj.models import OrderItem as OrderItemModel
from proj.models import Product as ProductModel
from proj.models import User as UserModel

from .dataloaders import MostPopularProductByCategoryIdLoader, OrderItemByOrderIdLoader


class User(DjangoObjectType):
    class Meta:
        model = UserModel
        fields = ("id", "username")


class Category(DjangoObjectType):
    class Meta:
        model = CategoryModel
        fields = ["id", "name"]

    most_popular_product = Field(lambda: Product)

    def resolve_most_popular_product(self, info):
        return MostPopularProductByCategoryIdLoader(info.context.dataloaders).load(
            self.id
        )


class Product(DjangoObjectType):
    class Meta:
        model = ProductModel
        fields = ["id", "name", "price", "description"]

    num_ordered = NonNull(Int)

    def resolve_num_ordered(self, info):
        order_items = yield OrderItemByOrderIdLoader(info.context.dataloaders).load(
            self.id
        )
        return sum([order_item.quantity for order_item in order_items])

    users = NonNull(List(NonNull(User)))

    def resolve_users(self, info):
        order_items = yield OrderItemByOrderIdLoader(info.context.dataloaders).load(
            self.id
        )
        if not order_items:
            return []
        order_loader = yield PrimaryKeyDataLoaderFactory.get_model_by_id_loader(
            OrderModel
        )(info.context.dataloaders)
        orders = yield order_loader.load_many(
            list({order_item.order_id for order_item in order_items})
        )
        user_loader = PrimaryKeyDataLoaderFactory.get_model_by_id_loader(UserModel)(
            info.context.dataloaders
        )
        users = yield user_loader.load_many(list({order.user_id for order in orders}))
        return users


class Order(DjangoObjectType):
    class Meta:
        model = OrderModel
        fields = ["id", "date"]

    order_items = NonNull(graphene.List(lambda: NonNull(OrderItem)))

    def resolve_order_items(self, info):
        return OrderItemByOrderIdLoader(info.context.dataloaders).load(self.id)

    price = NonNull(Int)

    def resolve_price(self, info):
        order_items = yield OrderItemByOrderIdLoader(info.context.dataloaders).load(
            self.id
        )
        return sum(
            [order_item.product.price * order_item.quantity for order_item in order_items]
        )


class OrderItem(DjangoObjectType):
    class Meta:
        model = OrderItemModel
        fields = ["id", "quantity"]


class Delivery(DjangoObjectType):
    class Meta:
        model = DeliveryModel
        fields = [
            "address",
            "city",
            "country",
            "zip_code",
        ]


class DeliveryLineItem(DjangoObjectType):
    class Meta:
        model = DeliveryLineItemModel
        fields = ["id", "quantity"]
