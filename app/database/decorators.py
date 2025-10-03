from functools import wraps


def with_db_connection(func):
    # manage db connection
    def wrapper(obj):
        if not obj.conn:
            obj.connect_to_db()
        func(obj)
    return wrapper