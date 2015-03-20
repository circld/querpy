# querpy - to make building SQL strings in Python as painless as possible

The Query class is intended to provide a high level interface for
building/editing SQL query strings.

Example usage:

    >>> from querpy import Query
    >>> new_query = Query()
    >>> new_query.f += 'ex_db.dbo.ex_table tbl'
    >>> new_query.s += ['col1', 'col2', 'col3']  # can take lists
    >>> new_query.s += 'col4'  # can take single strings
    >>> new_query.w += 'col1 = 1'
    >>> new_query.w &= 'col2 IS NULL'  # handles &= and |= operators
    >>> print new_query
    SELECT col1, col2, col3, col4 FROM ex_db.dbo.ex_table tbl WHERE col1 = 1 AND col2 IS NULL
    >>> new_query  # should print full query
    SELECT col1, col2, col3, col4 FROM ex_db.dbo.ex_table tbl WHERE col1 = 1 AND col2 IS NULL

The Query class avoids redundancy for similar queries by allowing you to modify a single component at a time:

    >>> new_query.s.clear()
    >>> new_query.s += 'col1'
    >>> new_query
    SELECT col1 FROM ex_db.dbo.ex_table tbl WHERE col1 = 1 AND col2 IS NULL

Suppose you want to extend your query by joining to another table and adding columns from this table:

    >>> new_query.j += 'ex_db.dbo.new_tbl new_tbl ON tbl.id = new_tbl.id'
    >>> new_query.s += 'new_tbl.id'
    >>> new_query
    SELECT col1, new_tbl.id FROM ex_db.dbo.ex_table tbl JOIN ex_db.dbo.new_tbl new_tbl ON tbl.id = new_tbl.id WHERE col1 = 1 AND col2 IS NULL


NOTE: the SQL constructed is **Not** validated.
