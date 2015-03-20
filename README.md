# querpy - to make building SQL strings in Python as painless as possible

The Query class is intended to provide a high level interface for
building/editing SQL query strings.

Example usage:

    >>> from querpy import Query
    >>> new_query = Query()
    >>> new_query.f += 'ex_db.dbo.ex_table AS tbl'
    >>> new_query.s += ['col1', 'col2', 'col3']  # can take lists
    >>> new_query.s += 'col4'  # can take single strings
    >>> new_query.w += 'col1 = 1'
    >>> new_query.w &= 'col2 IS NULL'  # handles &= and |= operators
    >>> print new_query
    SELECT col1, col2, col3, col4 FROM ex_db.dbo.ex_table AS tbl WHERE col1
    = 1 AND col2 IS NULL
    >>> new_query  # should print full query
