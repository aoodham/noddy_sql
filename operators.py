def formatList(values):
    return '({})'.format(', '.join([str(x) for x in values]))

class Operator:
    """Base operator class which generates the filter statements"""
    def __init__(self, column, value):
        self.column = column
        self.value = value

    def evaluate(self):
        return "{} {} {}".format(
                self.column.column_name,
                self.operator,
                self.formatValue(self.column.type.coerce(self.value)))

    def formatValue(self, value):
        return value

class Equals(Operator):
    operator = '='

class GreaterThan(Operator):
    operator = '>'

class LessThan(Operator):
    operator =  '<'

class In(Operator):
    operator = 'in'

    def formatValue(self, values):
        return formatList(values)

class NotIn(Operator):
    operator = 'not in'

    def formatValue(self, values):
        return formatList(values)
