"""
The Query class is intended to provide a high level interface for
building/editing SQL queries.

Example usage:
    >>> new_query = Query()
    >>> new_query.f += 'ex_db.dbo.ex_table AS tbl'
    >>> new_query.s += ['col1', 'col2', 'col3']  # can take lists
    >>> new_query.s += 'col4'  # can take single strings
    >>> new_query.w += 'col1 = 1'
    >>> new_query.w &= 'col2 IS NULL'  # handles &= and |= operators
    >>> print new_query
    >>> new_query  # should print full query
"""

__author__ = 'Paul Garaud'
__version__ = '0.1'
__date__ = '2015-03-19'


import re


class Query(object):

    # A series of precompiled regex to perfom various SQL related string tasks

    whitespace_regex = re.compile('(^\s+|(?<=\s)\s+|\s+$)')
    where_clean_up = re.compile('(?<=WHERE )\s.*?AND|(?<=WHERE )\s.*?OR')

    fmt = re.compile('\s(?=FROM)|\s(?=WHERE)|\s(?=GROUP BY)')
    fmt_after = re.compile(
        '(?<=SELECT)\s|(?<=FROM)\s|(?<=WHERE)\s|(?<=GROUP BY)\s'
    )
    fmt_join = re.compile(
        '\s(?={l} JOIN)|\s(?={o} JOIN)|\s(?={r} JOIN)'
        '|\s(?={i} JOIN)|(?<!{l})\s(?=JOIN)|(?<!{r})\s(?=JOIN)'
        '&(?<!{i})\s(?=JOIN)&(?<!{o})\s(?=JOIN)'.format(
            r='RIGHT', l='LEFT', i='INNER', o='OUTER'
        )
    )
    fmt_commas = re.compile('(?<=,)\s')
    fmt_and = re.compile('(?<=WHERE).*$', flags=re.S)
    fmt_or = re.compile('OR')

    def __init__(self):
        self.s = SelectComponent()
        self.f = QueryComponent('FROM')
        self.j = JoinComponent()
        self.w = WhereComponent()
        self.g = QueryComponent('GROUP BY', sep=',')

    @property
    def statement(self):
        elements = [self.s(), self.f(), self.j(), self.w(), self.g()]
        full_statement = re.subn(self.where_clean_up, '', ' '.join(elements))[0] # removes messy contents of WHERE statements? Note sure why this is needed or why it is run on the whole SQL statement
        full_statement = re.subn(self.whitespace_regex, '', full_statement)[0]  # flattens pretty print SQL to a single line by removing whitespace
        if full_statement:
            return full_statement
        else:
            return ''

    @property
    def distinct(self):
        return self.s.distinct

    @distinct.setter
    def distinct(self, value):
        self.s.distinct = value

    @property
    def top(self):
        return self.s.top

    @top.setter
    def top(self, value):
        self.s.top = value

    @property
    def join_type(self):
        """
        join_type prepends the type before each 'JOIN'
        """
        return self.j.join_type

    @join_type.setter
    def join_type(self, value):
        self.j.join_type = value

    def __str__(self):
        query = self.statement
        query = re.subn(self.fmt, '\n  ', query)[0]
        query = re.subn(self.fmt_after, '\n    ', query)[0]
        query = re.subn(self.fmt_join, '\n      ', query)[0]
        query = re.subn(self.fmt_commas, '\n    ', query)[0]
        query = re.subn(self.fmt_and, replace_and, query)[0]
        query = re.subn(self.fmt_or, '\n      OR', query)[0]
        
        return query

    __repr__ = __str__


class QueryComponent(object):

    def __init__(self, header, sep=''):
        self.header = header + ' '
        self.components = list()
        self.sep = sep + ' '

    def __iadd__(self, item):
        self.add_item(item)
        return self

    __iand__ = __ior__ = __iadd__

    def add_item(self, item, prefix=''):
        if prefix:
            prefix = prefix + ' '
        if type(item) == str:
            self.components.append(''.join([prefix, item]))
        elif type(item) == list:
            items = [''.join([prefix, i]) for i in item]
            self.components.extend(items)
        else:
            raise ValueError('Item must be a string or list')

    def clear(self):
        self.components = list()

    def __call__(self):
        if self.components:
            return self.header + self.sep.join(self.components)
        return ''

    def __getitem__(self, key):
        return self.components[key]

    def __setitem__(self, key, value):
        self.components[key] = value

    def __str__(self):
        to_print = list()
        for n, c in enumerate(self.components):
            to_print.append("{0}: '{1}'".format(n, c))
        return 'index: item\n' + ', '.join(to_print)

    __repr__ = __str__


class SelectComponent(QueryComponent):

    header = 'SELECT'
    dist_pattern = re.compile(' DISTINCT')
    top_pattern = re.compile(' TOP \d+')

    def __init__(self):
        self.header = self.header + ' '
        self.components = list()
        self.dist = False
        self.topN = False
        self.sep = ', '

    def clear(self):
        self.components = list()
        self.dist = False
        self.topN = False

    @property
    def distinct(self):
        return self.dist

    @distinct.setter
    def distinct(self, value):
        if type(value) != bool:
            raise ValueError('distinct may only be set to True or False.')

        # remove DISTINCT from header if self.dist changed from True to False
        if self.dist != value:
            if self.dist:
                self.header = re.sub(self.dist_pattern, '', self.header)
            else:
                self.header += 'DISTINCT '

        self.dist = value

    @property
    def top(self):
        return self.topN

    @top.setter
    def top(self, value):
        if type(value) != int and value is not False:
            raise ValueError('top must be set to an integer or None')

        # remove TOP N from header if self.top changed to None
        if self.topN != value:
            if self.topN:
                self.header = re.sub(self.top_pattern, '', self.header)
            else:
                self.header += 'TOP ' + str(value) + ' '

        self.topN = value
        

class JoinComponent(QueryComponent):

    def __init__(self, sep = ''):
        QueryComponent.__init__(self, '', sep)
        self.type = ''

    @property
    def join_type(self):
        return self.type

    @join_type.setter
    def join_type(self, value):
        if type(value) != str:
            raise ValueError('join_type must be set to a string value.')
        self.type = value.upper()

    def __iadd__(self, item):
        if self.type:
            join = ' '.join([self.type, 'JOIN'])
        else:
            join = 'JOIN'
        self.add_item(item, join)
        return self

    __iand__ = __ior__ = __iadd__

    def __call__(self):
        if self.components:
            return self.sep.join(self.components)
        return ''


class WhereComponent(QueryComponent):

    header = 'WHERE'

    def __init__(self, sep=''):
        self.header = self.header + ' '
        QueryComponent.__init__(self, self.header, sep)

    def __iand__(self, item):
        self.add_item(item, 'AND')
        return self

    def __ior__(self, item):
        self.add_item(item, 'OR')
        return self

    __iadd__ = __iand__

    def __str__(self):
        components = self.components
        if components:
            components = self.components[:]
            components[0] = re.sub('^AND |^OR ', '', components[0])
        to_print = list()
        for n, c in enumerate(components):
            to_print.append("{0}: '{1}'".format(n, c))
        return 'index: item\n' + ', '.join(to_print)

    __repr__ = __str__



def build_join(*args):
    tbl_name = args[0]
    args = args[1:]
    if len(args) % 2 != 0 or args == ():
        raise BaseException(
            'You must provide an even number of columns to join on.'
        )

    args_expr = ['{0} = {1}'.format(args[2 * i], args[2 * i + 1]) 
                 for i in range(int(len(args) / 2))]  # int() for Python 3
    args_expr = ' AND '.join(args_expr)
    join_str = ' '.join([tbl_name, 'ON', args_expr])

    return join_str


def replace_and(match):
    """
    helper function for indenting AND in WHERE clause
    """
    string = match.group(0)
    raw_newlines = re.subn('AND', '\n      AND', string)[0]
    out = re.subn('(?<=BETWEEN)( \w+? )\n\s*?(AND)', r'\1\2', raw_newlines)[0]
    return out
