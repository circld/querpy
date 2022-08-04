"""
Build README.md example

>>> python doc_example.py > file_name.txt
"""

commands = [
    '>>> from querpy import Query',
    '>>> new_query = Query()',
    ">>> new_query.f += 'ex_db.dbo.ex_table tbl'",
    ">>> new_query.s += ['col1', 'col2', 'col3']",
    ">>> new_query.s += 'col4'  # can take single strings",
    ">>> new_query.w += 'col1 = 1'  # can also take a list",
    ">>> new_query.w |= 'col2 IS NULL'  # handles &= and |= operators",
    ">>> print(new_query)",
    ">>> new_query",
    ">>> new_query.s.clear()  # clear SELECT component",
    ">>> new_query.s += 'col1'",
    ">>> new_query",
    ">>> new_query.s[0] = 'col2'",
    ">>> print(new_query.s)",
    ">>> new_query.j += 'ex_db.dbo.new_tbl nt ON tbl.id = nt.id'",
    ">>> new_query.s += 'nt.id'",
    ">>> new_query",
    ">>> new_query.j.clear()",
    ">>> new_query.join_type = 'LEFT'",
    ">>> new_query.j += Query.build_join('ex_db.dbo.new_tbl nt', 'tbl.id', 'nt.id',"
    " 'tbl.city', 'nt.city')",
    ">>> new_query.join_type = ''  # set back to regular join",
    ">>> new_query.ci += 'thisDB.thatTable'  # set back to regular join",
    ">>> new_query.l += ' 10, 100' ",
    ">>> new_query.g += 'col1' ",
    ">>> new_query.g += 'col3' ",
    ">>> new_query.o += 'col1' ",
    ">>> new_query.o += 'col3' ",
    ">>> new_query",
    ">>> new_query",
    ">>> new_query.statement",
]

def main():

    for c in commands:
        print(c)
        if c in ('>>> new_query', '>>> new_query.statement'):
            print(eval(c[4:]))
        else:
            exec(c[4:])


if __name__ == '__main__':

    main()
