import logging
import traceback

from graphene_django.views import GraphQLView
from graphql_core_promise import PromiseExecutionContext
from pleasant_promises.graphene import promised_generator_middleware

from .gql.schema import schema
from .gql.util import GraphQLContext


class GraphiQLView(GraphQLView):
    logger = logging.getLogger("django.request")
    schema = schema

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def as_view(cls, *args, **kwargs):
        new_kwargs = {
            "schema": cls.schema,
            "graphiql": True,
            "middleware": [promised_generator_middleware],
            "execution_context_class": PromiseExecutionContext,
            **kwargs,
        }
        return super().as_view(*args, **new_kwargs)

    def execute_graphql_request(self, *args, **kwargs):
        result = super().execute_graphql_request(*args, **kwargs)
        if result.errors:
            self._log_exceptions(result.errors)
        return result

    def _log_exceptions(self, errors):
        for error in errors:
            error_to_log = error
            if hasattr(error, "original_error"):
                error_to_log = error.original_error
            traceback_str = "".join(traceback.format_tb(error_to_log.__traceback__))
            self.logger.error(f"{error_to_log.__class__.__name__}: {error_to_log}")
            self.logger.error(traceback_str)

    def get_context(self, request):
        dataloaders = {}
        return GraphQLContext(dataloaders, user=self.request.user)
