from django.db import connection, reset_queries
import time
import functools
from textwrap import wrap
import sqlparse

def sql_query_debugger(func):
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()

        start = time.perf_counter()
        print(f"Start Function : {func.__name__}")
        result = func(*args, **kwargs)
        end = time.perf_counter()
        query_info = connection.queries
        queries = ['{}\n\n'.format(query['sql']) for query in query_info]
        for sql in queries:
            print(sqlparse.format(sql, reindent=True, keyword_case='upper'))
            print()
        print(f"End Function : {func.__name__}")
        print(f"Number of Queries : {len(query_info)}")
        print(f"Finished in : {(end - start):.2f}s")

        return result

    return inner_func
