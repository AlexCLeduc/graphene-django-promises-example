from django.db import transaction
from django.utils import timezone

import graphene
from graphene import List, NonNull

from proj.models import Order as OrderModel
from proj.models import OrderItem as OrderItemModel


class OrderItemInput(graphene.InputObjectType):
    product_id = graphene.ID()
    quantity = graphene.Int()


class CreateOrder(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        order_items = NonNull(List(NonNull(OrderItemInput)))

    order = graphene.Field("proj.gql.types.Order")

    def mutate(self, info, user_id, order_items):
        with transaction.atomic():
            order = OrderModel.objects.create(user_id=user_id, date=timezone.now())
            for item in order_items:
                OrderItemModel.objects.create(order=order, **item)

            return {"order": order}
