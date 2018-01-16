from dateutil import parser as dateParser
from operators import Equals, LessThan, GreaterThan, In, NotIn

class InvalidTypeError(Exception):

    def __init__(self, message):
        self.message = message

class InvalidOperation(Exception):

    def __init__(self, message):
        self.message = message

class ColumnType:
    """Base class for specifying the data type in a column. Controls which operations
    are permitted and handles data coercion"""
    supportedOperations = ['equals', 'less', 'greater', 'in', 'not in']

    def supportedOperation(self, operation):
        if operation not in self.supportedOperations:
            raise InvalidOperation("Unsupported operand '{}'".format(operation))

    def coerce(self, value):
        if type(value) == list:
            coerced = [self.coerceFn(x) for x in value]
        else:
            coerced = self.coerceFn(value)
        return coerced

    def isValid(self, value):
        try:
            self.coerceFn(value)
            return True
        except (ValueError) as err:
            raise InvalidTypeError(str(err))

class Integer(ColumnType):
    def coerceFn(self, value):
        return int(value)

class String(ColumnType):
    supportedOperations = ['equals', 'in', 'not in']
    def coerceFn(self, value):
        return "'{}'".format(value)

class DateTime(ColumnType):
    def coerceFn(self, value):
        datetime = dateParser.parse(str(value))
        return "'{}'".format(datetime.isoformat())


class Column:
    """Class for specifying a column. Needs to be given a name and data type"""

    def __init__(self, column_name, type_):
        self.column_name = column_name
        self.type = type_
        self.range = []

    def checkTypeMatches(self, value):
        if type(value) == list:
            [self.type.isValid(x) for x in value]
        else:
            self.type.isValid(value)

    def reset(self):
        self.range = []

    def __eq__(self, other):
        self.checkTypeMatches(other)
        return [Equals(self, other)]

    def __gt__(self, other, *args, **kwargs):
        self.type.supportedOperation('greater')
        self.checkTypeMatches(other)
        self.range.append(GreaterThan(self, other))
        return self.range

    def __lt__(self, other, *args, **kwargs):
        self.type.supportedOperation('less')
        self.checkTypeMatches(other)
        self.range.append(LessThan(self, other))
        return self.range

    def in_(self, array):
        self.checkTypeMatches(array)
        return [In(self, array)]

    def notIn(self, array):
        self.checkTypeMatches(array)
        return [NotIn(self, array)]