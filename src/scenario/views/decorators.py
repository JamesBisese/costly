from django.db import connection, reset_queries
import time
import functools
from textwrap import wrap

def database_debug(func):
    def inner_func(*args, **kwargs):
        reset_queries()
        results = func()
        query_info = connection.queries
        print('function_name: {}'.format(func.__name__))
        print('query_count: {}'.format(len(query_info)))
        queries = ['{}\n'.format(query['sql']) for query in query_info]
        print('queries: \n{}'.format(''.join(queries)))
        return results
    return inner_func


def query_debugger2(func):
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()

        # start_queries = len(connection.queries)

        start = time.perf_counter()
        print(f"Start Function : {func.__name__}")
        result = func(*args, **kwargs)
        end = time.perf_counter()
        query_info = connection.queries
        # end_queries = len(connection.queries)

        print(f"End Function : {func.__name__}")
        print(f"Number of Queries : {len(query_info)}")
        queries = ['{}\n\n'.format(query['sql']) for query in query_info]
        for q in queries:
            (select_clause, from_onward) = q.split(' FROM ')
            select_strings = wrap(select_clause, width=200)
            first_select_strings = select_strings.pop(0)

            print(first_select_strings)

            if len(select_strings) > 0:
                select_strings[0] = "\t" + select_strings[0]
                print("\n\t".join(select_strings))

            if ' WHERE ' in from_onward:
                (from_onward, where_clause) = from_onward.split(' WHERE ')
            else:
                where_clause = None

            from_strings = wrap(from_onward, width=200)

            from_strings[0] = 'FROM ' + from_strings[0]
            first_from_strings = from_strings.pop(0)
            print(first_from_strings)
            if len(from_strings) > 0:
                from_strings[0] = "\t" + from_strings[0]
                print("\n\t".join(from_strings))

            if where_clause is not None:
                where_strings = wrap(where_clause, width=200)
                where_strings[0] = 'WHERE ' + where_strings[0]
                first_where_strings = where_strings.pop(0)
                print(first_where_strings)

                if len(where_strings) > 0:
                    where_strings[0] = "\t" + where_strings[0]
                    print("\n\t".join(where_strings))

            print()

        # print('queries: \n{}'.format(''.join(queries)))
        print(f"Finished in : {(end - start):.2f}s")

        return result

    return inner_func
