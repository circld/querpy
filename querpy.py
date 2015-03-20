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

    pattern = re.compile('(^\s+|(?<=\s)\s+|\s+$)')

    def __init__(self):
        self.s = SelectComponent('SELECT')
        self.f = QueryComponent('FROM')
        self.j = QueryComponent('JOIN')
        self.w = QueryComponent('WHERE')
        self.g = QueryComponent('GROUP BY')

    @property
    def statement(self):
        elements = [self.s(), self.f(), self.j(), self.w(), self.g()]
        full_statement = re.subn(self.pattern, '', ' '.join(elements))[0]
        if full_statement:
            return full_statement

    def __str__(self):
        return self.statement

    __repr__ = __str__


class QueryComponent(object):

    def __init__(self, header):
        self.header = header + ' '
        self.components = list()

    def __iadd__(self, item):
        self.__add_item(item)
        return self

    def __iand__(self, item):
        self.__add_item(item, 'AND')
        return self

    def __ior__(self, item):
        self.__add_item(item, 'OR')
        return self

    def __add_item(self, item, prefix=''):
        if prefix:
            prefix = ' ' + prefix + ' '
        if type(item) == str:
            self.components.append(''.join([prefix, item]))
        elif type(item) == list:
            items = [''.join([prefix, i]) for i in item]
            self.components.extend(items)
        else:
            raise ValueError('Item must be a string or list')

    def __call__(self):
        if len(self.components) > 1:
            return self.header + ' '.join(self.components)
        return ''


class SelectComponent(QueryComponent):

    def __call__(self):
        if len(self.components) > 1:
            return self.header + ', '.join(self.components)
        return ''