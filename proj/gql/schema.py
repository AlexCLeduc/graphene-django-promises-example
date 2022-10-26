import graphene

from .root_mutation import RootMutation
from .root_query import RootQuery

schema = graphene.Schema(query=RootQuery, mutation=RootMutation)
