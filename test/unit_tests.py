import unittest as ut
import re
from querpy import *


class TestQueryComponent(ut.TestCase):

    def setUp(self):
       self.spaces = QueryComponent('COMMAND')
       self.commas = QueryComponent('COMMAND', ',')
       self.items = ['col1', 'col2', 'col3']

    def test_init(self):
        for comp, sep in zip([self.spaces, self.commas], [' ', ', ']):
            self.assertEqual(comp.header, 'COMMAND ')
            self.assertEqual(comp.components, [])
            self.assertEqual(comp.sep, sep)

    def test_empty_object_print(self):
        self.assertEqual(self.spaces(), '')

    def test_nonempty_object_print(self):
        self.spaces += 'some stuff'
        self.assertNotEqual(self.spaces(), '')
        self.assertEqual(self.spaces(), self.spaces.header + 'some stuff')

    def test_add_list_spaces(self):
        self.spaces += self.items
        self.assertEqual(self.spaces(), 
                         self.spaces.header + ' '.join(self.items))

    def test_add_list_commas(self):
        self.commas += self.items
        self.assertEqual(self.commas(),
                         self.commas.header + ', '.join(self.items))

    def test_add_wrong_type_raises_ValueError(self):
        self.assertRaises(ValueError, self.spaces.add_item, 5)

    def test_clear(self):
        self.commas += self.items
        self.commas.clear()
        self.assertEqual(self.commas(), '')


class TestSelectComponent(ut.TestCase):
    
    def setUp(self):
        self.comp = SelectComponent()
        self.items = ['col1', 'col2', 'col3']

    def test_init(self):
        for attr, val in zip(
            [self.comp.header, self.comp.components, self.comp.dist,
             self.comp.topN, self.comp.sep],
            ['SELECT ', [], False, False, ', ']
        ):
            self.assertEqual(attr, val)

    def test_distinct_regex(self):
        string = 'SELECT DISTINCT TOP 1000'
        subbed = re.sub(self.comp.dist_pattern, '', string)
        # nb. extra space is fine here--stripped out at Query level
        self.assertEqual(subbed, 'SELECT TOP 1000')

    def test_top_regex(self):
        string = 'SELECT TOP 5000 DISTINCT'
        subbed = re.sub(self.comp.top_pattern, '', string)
        # nb. extra space is fine here--stripped out at Query level
        self.assertEqual(subbed, 'SELECT DISTINCT')

    def test_distinct_False_to_True(self):
        self.comp.distinct = True
        self.assertEqual(self.comp(), '')
        self.comp += 'col2'
        self.assertEqual(self.comp(), 'SELECT DISTINCT col2')

    def test_distinct_True_to_False(self):
        self.comp.distinct = True
        self.assertEqual(self.comp(), '')
        self.comp += 'col2'
        self.assertEqual(self.comp(), 'SELECT DISTINCT col2')
        self.comp.distinct = False
        self.assertEqual(self.comp(), 'SELECT col2')

    def test_top_False_to_val(self):
        self.comp.top = 5
        self.assertEqual(self.comp(), '')
        self.comp += 'col2'
        self.assertEqual(self.comp(), 'SELECT TOP 5 col2')

    def test_top_val_to_False(self):
        self.comp.top = 5
        self.assertEqual(self.comp(), '')
        self.comp += 'col2'
        self.assertEqual(self.comp(), 'SELECT TOP 5 col2')
        self.comp.top = False
        self.assertEqual(self.comp(), 'SELECT col2')

    def test_distinct_top_set_wrong_type_raises_ValueError(self):
        self.assertRaises(ValueError, self.comp.__setattr__, 'distinct', 5)
        self.assertRaises(ValueError, self.comp.__setattr__, 'top', '5')

    def test_clear_resets_distinct_top(self):
        self.comp.top = 5
        self.comp.distinct = True
        self.comp.clear()
        self.assertFalse(self.comp.distinct)
        self.assertFalse(self.comp.top)


class TestJoinComponent(ut.TestCase):

    def test_call_adds_joins(self):
        join = JoinComponent()
        join += 'tbl1 ON var1 = other1'
        join += 'tbl2 ON var2 = other2'
        self.assertEqual(
            join(), 'JOIN tbl1 ON var1 = other1 JOIN tbl2 ON var2 = other2'
        )

    def test_change_join_type(self):
        join = JoinComponent()
        join.join_type = 'LEFT'
        join += ['tbl1 t1 ON t1.id = oid', 'tbl2 t2 ON t2.id = oid']
        self.assertEqual(join.join_type, 'LEFT')
        self.assertEqual(
            join(),
            'LEFT JOIN tbl1 t1 ON t1.id = oid LEFT JOIN tbl2 t2 ON t2.id = oid'
        )
        join.join_type = ''
        join += 'tbl3 t3 ON t3.id = oid'
        self.assertEqual(
            join(),
            'LEFT JOIN tbl1 t1 ON t1.id = oid LEFT JOIN tbl2 t2 ON t2.id = oid'
            ' JOIN tbl3 t3 ON t3.id = oid'
        )

    def test_set_join_type_wrong_val_type_raises_error(self):
        join = JoinComponent()
        self.assertRaises(ValueError, join.__setattr__, 'join_type', 5)


class TestWhereComponent(ut.TestCase):
    # Will add extra AND or OR to first element;
    # this is removed at the Query level (Query.statement)
    def setUp(self):
       self.comp = WhereComponent()
       self.items = ['col1 = 1', 'col2 = 2', 'col3 IS NULL']
        
    def test_add_single_and(self):
        self.comp += 'some stuff'
        self.assertEqual(self.comp(), 
                         self.comp.header + 'AND some stuff')

    def test_add_list_and(self):
        self.comp += 'col0'
        self.comp &= self.items
        self.assertEqual(
            self.comp(), 
            self.comp.header + 'AND col0 AND ' + ' AND '.join(self.items)
        )

    def test_add_single_or(self):
        self.comp += 'some stuff'
        self.assertEqual(self.comp(), 
                         self.comp.header + 'AND some stuff')

    def test_add_list_or(self):
        self.comp |= 'col0'
        self.comp |= self.items
        self.assertEqual(
            self.comp(), 
            self.comp.header + 'OR col0 OR ' + ' OR '.join(self.items)
        )


class TestQuery(ut.TestCase):

    def setUp(self):
        self.query = Query()

    def test_init(self):
        attrs = ['s', 'f', 'j', 'w', 'g']
        classes = [SelectComponent, QueryComponent, JoinComponent,
                   QueryComponent, QueryComponent]
        com = ', '
        spc = ' '
        seps = [com, spc, spc, spc, com] 
        for a, c in zip(attrs, classes):
            self.assertTrue(
                isinstance(getattr(self.query, a), c),
                'self.query.{a} is not an instance of {c}'.format(
                    a = a, c = c.__name__
                )
            )
        for a, s in zip(attrs, seps):
            self.assertEqual(getattr(self.query, a).sep, s,
                             'self.query.{a}.sep != {s})'.format(
                                 a = a, s = s
                             ))

    def test_whitespace_regex(self):
        string = '  leading space and  spaces    and trailing spaces      '
        subbed = re.subn(self.query.pattern, '', string)[0]
        self.assertEqual(subbed, 
                         'leading space and spaces and trailing spaces')

    def test_clean_up_regex(self):
        string = 'WHERE   AND WHERE  OR'
        subbed = re.subn(self.query.clean_up, '', string)[0]
        self.assertEqual(subbed, 
                         'WHERE  WHERE ')

    def test_fmt_regex(self):
        string = ' FROM stuff WHERE otherstuff GROUP BY stuff'
        subbed = re.subn(self.query.fmt, '\n', string)[0]
        self.assertEqual(subbed, 
                         '\nFROM stuff\nWHERE otherstuff\nGROUP BY stuff')

    def test_fmt_after_regex(self):
        string = 'SELECT col1 FROM tbl1 WHERE cond1 GROUP BY col1'
        subbed = re.subn(self.query.fmt_after, '\n', string)[0]
        self.assertEqual(subbed, 
                         'SELECT\ncol1 FROM\ntbl1 WHERE\ncond1 GROUP BY\ncol1')

    def test_fmt_join_regex(self):
        string = 'JOIN JOIN JOIN'
        subbed = re.subn(self.query.fmt_join, '\n', string)[0]
        self.assertEqual(subbed, 
                         'JOIN\nJOIN\nJOIN')
        string2 = 'stuff LEFT JOIN other stuff'
        subbed2 = re.subn(self.query.fmt_join, '\n', string2)[0]
        self.assertEqual(subbed2, 
                         'stuff\nLEFT JOIN other stuff')

    def test_fmt_commas_regex(self):
        string = 'SELECT col1 [c1], col2 [c2], col3 [c3]'
        subbed = re.subn(self.query.fmt_commas, '\n', string)[0]
        self.assertEqual(subbed, 
                         'SELECT col1 [c1],\ncol2 [c2],\ncol3 [c3]')

    def test_fmt_and(self):
        # test that AND is indented in WHERE clause but not JOIN
        string = (
            'JOIN tbl2 ON col1 = col2 AND col3 = col4 '
            'WHERE col1 = col3 AND col4 = col5 AND col5 = col6'
        )
        subbed = re.subn(self.query.fmt_and, replace_and, string)[0]
        self.assertEqual(
            subbed,
            'JOIN tbl2 ON col1 = col2 AND col3 = col4 '
            'WHERE col1 = col3 \n      AND col4 = col5 '
            '\n      AND col5 = col6'
        )


    def test_statement(self):
        self.query.s += ['col1', 'col2']
        self.query.f += 'dbo.a_table'
        self.query.j += 'dbo.b_table ON a_table.id = b_table.id'
        self.query.w += 'col1 IS NOT NULL'
        self.query.g += ['col1', 'col2']
        self.assertEqual(
            self.query.statement,
            'SELECT col1, col2 FROM dbo.a_table '
            'JOIN dbo.b_table ON a_table.id = b_table.id '
            'WHERE col1 IS NOT NULL '
            'GROUP BY col1, col2'
        )

    def test_distinct(self):
        self.query.distinct = True
        self.assertTrue(self.query.distinct)
        self.query.s += 'hello'
        self.assertEqual(self.query.statement, 'SELECT DISTINCT hello')
        self.query.distinct = False
        self.assertFalse(self.query.distinct)
        self.assertEqual(self.query.statement, 'SELECT hello')

    def test_top(self):
        self.query.top = 10
        self.assertEquals(self.query.top, 10)
        self.query.s += 'hello'
        self.assertEqual(self.query.statement, 'SELECT TOP 10 hello')
        self.query.top = False
        self.assertFalse(self.query.top)
        self.assertEqual(self.query.statement, 'SELECT hello')


class TestJoinFunction(ut.TestCase):

    def setUp(self):
        self.item1 = ['tbl1 t1', 't1.id', 'oid']
        self.item2 = ['tbl2 t2', 't2.id', 'oid', 't2.city', 'city']

    def test_join_valid_items(self):
        to_test1 = build_join(*self.item1)
        to_test2 = build_join(*self.item2)
        self.assertEqual(to_test1, 'tbl1 t1 ON t1.id = oid')
        self.assertEqual(to_test2, 'tbl2 t2 ON t2.id = oid AND t2.city = city')

    def test_invalid_num_items_passed_as_args(self):
        invalid = self.item2[:-1]
        self.assertRaises(BaseException, build_join, invalid)


if __name__ == '__main__':

    ut.main()