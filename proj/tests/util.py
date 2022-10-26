import logging
import traceback

from django.db import connection

from graphene.test import Client
from graphql.error import GraphQLError
from graphql.language.parser import parse
from graphql.validation import validate
from graphql_core_promise import PromiseExecutionContext
from pleasant_promises.graphene import promised_generator_middleware

from proj.gql.schema import schema
from proj.gql.util import GraphQLContext


class RaiseExceptionsMiddleware:
    logger = logging.getLogger("django.request")

    def on_error(self, error, *args, **kwargs):
        traceback_str = "".join(traceback.format_tb(error.__traceback__))
        self.logger.error(f"{error.__class__.__name__}: {error}")
        self.logger.error(traceback_str)

        raise error

    def resolve(self, next, root, info, **kwargs):
        return next(root, info, **kwargs)


class GraphQLExecutionErrorSet(Exception):
    def __init__(self, graphql_errors):
        self.graphql_errors = graphql_errors
        # err_str = json.dumps(graphql_errors, indent=4, sort_keys=True)
        super().__init__(graphql_errors)


class GraphqlExecutor:
    """
    - must define class variable "schema"

    if you want to execute multiple graphQL queries against the same data-loaders
    you must re-use instances of this class
    """

    schema = schema

    def __init__(self):
        self.client = Client(self.schema, execution_context_class=PromiseExecutionContext)
        self.dataloaders = {}

    def execute_query(
        self, query: str, root: any = None, variables: dict = None, user=None
    ):
        context = GraphQLContext(self.dataloaders, user)

        middleware = [RaiseExceptionsMiddleware(), promised_generator_middleware]

        resp = self.client.execute(
            query,
            root,
            context,
            variables,
            middleware=middleware,
        )

        if "errors" in resp:
            err = GraphQLExecutionErrorSet(resp["errors"])
            raise err
        return resp["data"]

    def build_query(self, query):
        validation_errors = validate(self.schema.graphql_schema, parse(query))
        if validation_errors:
            raise GraphQLError(validation_errors)

        def execute(*, context=None, **variables):
            return self.execute_query(query, context, variables=variables)

        return execute


def execute_query(query: str, variables: dict, user=None):
    executor = GraphqlExecutor()
    return executor.execute_query(query, variables=variables)


class QueryCollector:
    """
    usage:

    from django.db import connection
    qc = QueryCollector()
    with connection.execute_wrapper(qc):
        do_queries()
    # Now we can print the log.
    print(qc.queries)
    """

    def __init__(self):
        self.queries = []

    def __call__(self, execute, sql, params, many, context):
        current_query = {"sql": sql, "params": params, "many": many}
        try:
            result = execute(sql, params, many, context)
        except Exception as e:
            current_query["status"] = "error"
            current_query["exception"] = e
            raise
        else:
            current_query["status"] = "ok"
            return result
        finally:
            self.queries.append(current_query)


class QueryCounter:
    """
    usage:
        with QueryCounter() as qc:
            # arbitrary code that execs sql

        assert( qc.count < 10 )
    """

    def __init__(self):
        self.query_collector = QueryCollector()
        self.connection_ctx_manager = connection.execute_wrapper(self.query_collector)

    def __enter__(self):
        self.connection_ctx_manager.__enter__()

    def __exit__(self, *excp):
        self.connection_ctx_manager.__exit__(*excp)
        self.count = len(self.query_collector.queries)


class MaxQueryCountExceededError(Exception):
    pass


class assert_max_queries:
    """
    usage:

    with assert_max_queries(n):
        ... code_that_should_make_up_to_n_queries
    """

    def __init__(self, max_queries: int):
        self.qc = QueryCounter()
        self.max_queries = max_queries

    def __enter__(self):
        self.qc.__enter__()

    def __exit__(self, *excp):
        self.qc.__exit__(*excp)
        if self.qc.count > self.max_queries:
            raise MaxQueryCountExceededError(
                f"Expected a maximum of {self.max_queries} but got {self.qc.count} queries"
            )
