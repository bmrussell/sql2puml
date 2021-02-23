import pyodbc


class Columndef:
    Name = ''
    Datatype = ''
    IsMandatory = False
    IsKey = False           # Is the column part or all of the primary key
    IsUnique = False        # Does the column have a unique index on it
    IsCompositeKey = False  # True if this column is part of a composite primary key
    Parent = ''

    def __init__(self, name: str, mandatory: bool, datatype: int, size: int, parent):
        dataTypeInfo = ''
        self.Name = name
        self.IsMandatory = mandatory

        # Dictonary of {numeric datatype, [text name, has length]}
        switcher = {
            pyodbc.SQL_CHAR:['char',True],
            pyodbc.SQL_VARCHAR:['varchar',True],
            pyodbc.SQL_LONGVARCHAR:['longvarchar',True],
            pyodbc.SQL_WCHAR:['wchar',True],
            pyodbc.SQL_WVARCHAR:['wvarchar',True],
            pyodbc.SQL_WLONGVARCHAR:['wlongvarchar',True],
            pyodbc.SQL_DECIMAL:['decimal',False],
            pyodbc.SQL_NUMERIC:['numeric',False],
            pyodbc.SQL_SMALLINT:['smallint',False],
            pyodbc.SQL_INTEGER:['integer',False],
            pyodbc.SQL_REAL:['real',False],
            pyodbc.SQL_FLOAT:['float',False],
            pyodbc.SQL_DOUBLE:['double',False],
            pyodbc.SQL_BIT:['bit',False],
            pyodbc.SQL_TINYINT:['tinyint',False],
            pyodbc.SQL_BIGINT:['bigint',False],
            pyodbc.SQL_BINARY:['binary',True],
            pyodbc.SQL_VARBINARY:['varbinary',True],
            pyodbc.SQL_LONGVARBINARY:['longvarbinary',True],
            pyodbc.SQL_TYPE_DATE:['date',False],
            pyodbc.SQL_TYPE_TIME:['time',False],
            pyodbc.SQL_TYPE_TIMESTAMP:['timestamp',False],
            # Not in pyodbc pyodbc.SQL_TYPE_UTCDATETIME :['utcdatetime', False],
            # Not in pyodbc pyodbc.SQL_TYPE_UTCTIME :['utctime', False],
            pyodbc.SQL_INTERVAL_MONTH:['interval_month',False],
            pyodbc.SQL_INTERVAL_YEAR:['interval_year',False],
            pyodbc.SQL_INTERVAL_YEAR_TO_MONTH:['interval_year_to_month',False],
            pyodbc.SQL_INTERVAL_DAY:['interval_day',False],
            pyodbc.SQL_INTERVAL_HOUR:['interval_hour',False],
            pyodbc.SQL_INTERVAL_MINUTE:['interval_minute',False],
            pyodbc.SQL_INTERVAL_SECOND:['interval_second',False],
            pyodbc.SQL_INTERVAL_DAY_TO_HOUR:['interval_day_to_hour',False],
            pyodbc.SQL_INTERVAL_DAY_TO_MINUTE:['interval_day_to_minute',False],
            pyodbc.SQL_INTERVAL_DAY_TO_SECOND:['interval_day_to_second',False],
            pyodbc.SQL_INTERVAL_HOUR_TO_MINUTE:['interval_hour_to_minute',False],
            pyodbc.SQL_INTERVAL_HOUR_TO_SECOND:['interval_hour_to_second',False],
            pyodbc.SQL_INTERVAL_MINUTE_TO_SECOND:['interval_minute_to_second',False],
            pyodbc.SQL_GUID:['guid',False]
        }
        dataTypeInfo = switcher.get(datatype, "Invalid day of week")

        if dataTypeInfo[1]:
            # Column type with a length such as varchar
            self.Datatype = dataTypeInfo[0] + '[' + str(size) + ']'
        else:
            # Atomic, no size
            self.Datatype = dataTypeInfo[0]

        self.Parent = parent
        self.IsKey = False
