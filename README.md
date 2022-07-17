# querpy - to make building SQL strings in Python as painless as possible

The Query class is intended to provide a high level interface for
building/editing SQL query strings.

Example usage:
```python
    >>> from querpy import Query
    >>> new_query = Query()
    >>> new_query.f += 'ex_db.dbo.ex_table tbl'
    >>> new_query.s += ['col1', 'col2', 'col3']  # can take lists
    >>> new_query.s += 'col4'  # can take single strings
    >>> new_query.w += 'col1 = 1'  # can also take a list (separated by AND)
    >>> new_query.w &= 'col2 IS NULL'  # handles &= and |= operators
    >>> print new_query
    SELECT
        col1,
        col2,
        col3,
        col4
      FROM
        ex_db.dbo.ex_table tbl
      WHERE
        col1 = 1 
          OR col2 IS NULL
    
	>>> new_query  # also prints full query
    SELECT
        col1,
        col2,
        col3,
        col4
      FROM
        ex_db.dbo.ex_table tbl
      WHERE
        col1 = 1 
          OR col2 IS NULL
```    
The Query class avoids redundancy for similar queries by allowing you to modify a single component at a time:
```python
    >>> new_query.s.clear()  # clear SELECT component
    >>> new_query.s += 'col1'
    >>> new_query
    SELECT
        col1
      FROM
        ex_db.dbo.ex_table tbl
      WHERE
        col1 = 1 
          OR col2 IS NULL
```
Another way to edit the SELECT clause is to use indexing:
```python
    >>> new_query.s[0] = 'col2'
    >>> print new_query.s  # printing the component shows indices
    index: item
    0: 'col2'
```
Suppose you want to extend your query by joining to another table and adding columns from this table:
```python
    >>> new_query.j += 'ex_db.dbo.new_tbl nt ON tbl.id = nt.id'
    >>> new_query.s += 'nt.id'
    >>> new_query
    SELECT
        col1,
        nt.id
      FROM
        ex_db.dbo.ex_table tbl
          JOIN ex_db.dbo.new_tbl nt ON tbl.id = nt.id
      WHERE
        col1 = 1 
          OR col2 IS NULL
```
While this works, we are returning to the land of long strings. We can do the same thing (n.b. we'll LEFT JOIN this time) using the build_join helper function to make the join step more readable and modular:
```python	
    >>> from querpy import build_join
    >>> new_query.j.clear()
    >>> new_query.join_type = 'LEFT'
    >>> new_query.j += build_join('ex_db.dbo.new_tbl nt', 'tbl.id', 'nt.id', 'tbl.city', 'nt.city')
    >>> new_query.join_type = ''  # set back to regular join
    >>> new_query
    SELECT
        col1,
        nt.id
      FROM
        ex_db.dbo.ex_table tbl
          LEFT JOIN ex_db.dbo.new_tbl nt ON tbl.id = nt.id AND tbl.city = nt.city
      WHERE
        col1 = 1 
          OR col2 IS NULL
```
When your query string is ready to be passed to the function that will execute the query, simply pass it using `statement` (without the pretty print fluff):
```python
    >>> new_query.statement
    SELECT col2, nt.id FROM ex_db.dbo.ex_table tbl LEFT JOIN ex_db.dbo.new_tbl nt ON tbl.id = nt.id AND tbl.city = nt.city WHERE col1 = 1 OR col2 IS NULL
```
NOTE: the SQL constructed is **not** validated.

Test edit
