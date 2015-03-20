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
        self.j = JoinComponent('JOIN')
        self.w = QueryComponent('WHERE')
        self.g = QueryComponent('GROUP BY', sep=',')

    @property
    def statement(self):
        elements = [self.s(), self.f(), self.j(), self.w(), self.g()]
        full_statement = re.subn(self.pattern, '', ' '.join(elements))[0]
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

    def __str__(self):
        return self.statement

    __repr__ = __str__


class QueryComponent(object):

    def __init__(self, header, sep=''):
        self.header = header + ' '
        self.components = list()
        self.sep = sep + ' '

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

    def clear(self):
        self.components = list()

    def __call__(self):
        if self.components:
            return self.header + self.sep.join(self.components)
        return ''


class SelectComponent(QueryComponent):

    dist_pattern = re.compile('DISTINCT')
    top_pattern = re.compile('TOP \d+')

    def __init__(self, header):
        self.header = header + ' '
        self.components = list()
        self.dist = False
        self.topN = False
        self.sep = ', '

    def __call__(self):
        if self.components:
            header = self.header + ' '
            return header + self.sep.join(self.components)
        return ''

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

    def __call__(self):
        if self.components:
            components = [' '.join(['JOIN', i]) for i in self.components]
            return self.sep.join(components)
        return ''
