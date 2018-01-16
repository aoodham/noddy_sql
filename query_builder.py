from column import Integer, DateTime, String, Column


"""This is largely an academic exercise as SQLAlchemy provides a much richer 
API for these types of things, but it wasn't clear to me if using a pre-existing library was wanted.
This code implements an API for building queries, and rendering them as an SQL statement which then needs to be 
executed against the SQL server, through some pre-exisiting database connection.
For all column types I have implemented equals, in and not in as anything which can have an equals method defined, 
should be able to test for membership in a list. The less than and greater than methods only exist for 
integer and datetime fields"""

class Query:
    """Base class for building queries. At present only selects all columns from the table"""
    base_string = "SELECT * FROM {}"

    def __init__(self, table, columns):
        self.table = table
        self.columns = columns
        self.filters = []

    def filter(self, expression):
        self.filters.extend(expression)
        #Reset the columns now they're in the query
        expression[0].column.reset()
        return self

    def toSQL(self):
        """Build the sql statement based on the filters registered.
        Currently only supports 'AND' operations between filters"""
        statement = self.base_string.format(self.table.table_name)
        if self.filters:
            statement += ' WHERE '
            *filters, last = self.filters
            for f in filters:
                statement += "{} AND ".format(f.evaluate())
            statement += last.evaluate()
        statement += ';'
        return statement

class Table:
    """Base class for all tables. Implements a method to generate a Query object"""
    @classmethod
    def query(cls):
        cols = {}
        for prop in cls.__dict__.values():
            if isinstance(prop, Column):
                cols[prop.column_name] = prop
        return Query(cls, cols)

class WebRating(Table):
    """The table specified in Task 3"""
    table_name = 'test'

    id =  Column('id', Integer())
    url = Column('url', String())
    date = Column('date', DateTime())
    rating = Column('rating', String())

