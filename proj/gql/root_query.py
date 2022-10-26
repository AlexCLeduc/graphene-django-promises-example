import graphene
from graphene import List, NonNull

from proj.models import Category as CategoryModel
from proj.models import Order as OrderModel
from proj.models import Product as ProductModel

from .types import Category, Order, Product


class RootQuery(graphene.ObjectType):

    order = graphene.Field(Order, id=graphene.Int(required=True))

    def resolve_order(self, info, id):
        return OrderModel.objects.get(id=id)

    product = graphene.Field(Product, id=graphene.Int(required=True))

    def resolve_product(self, info, id):
        return ProductModel.objects.get(id=id)

    categories = NonNull(graphene.List(NonNull(Category)))

    def resolve_categories(self, info):
        return CategoryModel.objects.all()

    products = NonNull(graphene.List(NonNull(Product)))

    def resolve_products(self, info):
        return ProductModel.objects.all()
