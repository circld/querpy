import unittest as ut
import re
from querpy import Query


class TestQuerpyFunctionality(ut.TestCase):

    def test_building_and_modifying_query(self):

        # John Doe needs to query a database with financial info
        # He begins by instantiating a Query() object
        query = Query()

        # He needs the data in the table DB01.dbo.Fund
        query.f += 'DB01.dbo.Fund'

        # He verifies that the FROM statement has been added correctly
        test_query = 'FROM DB01.dbo.Fund'
        self.assertEqual(query.statement, test_query)

        # The columns he needs from the table are: FundId, FundType, and FundAUM
        columns = ['FundId', 'FundType', 'FundAUM']
        query.s +=  columns

        # Again, he checks that the query is building correctly
        test_query = 'SELECT FundId, FundType, FundAUM ' + test_query
        self.assertEqual(query.statement, test_query)

        # Since he is only interested in Equity funds, he filters on this criterion
        query.w += "FundType = 'Equity'"
        test_query += " WHERE FundType = 'Equity'"
        self.assertEqual(query.statement, test_query)

        # John realizes he also wants to include Bond funds
        query.w |= "FundType = 'Bond'"
        test_query += " OR FundType = 'Bond'"
        self.assertEqual(query.statement, test_query)

        # He decides that he doesn't actually need the FundId column
        query.s.clear()
        query.s += ['FundType', 'FundAUM']
        test_query = re.sub('FundId, ', '', test_query)
        self.assertEqual(query.statement, test_query)
        
        # Satisfied, he passes query.statement to his DB connection to query the DB


if __name__ == '__main__':
    ut.main()