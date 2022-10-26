import graphene

from .mutations.create_order import CreateOrder


class RootMutation(graphene.ObjectType):
    create_order = CreateOrder.Field()
