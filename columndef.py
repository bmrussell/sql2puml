import pyodbc

class Columndef:
    Name = ''
    Mandatory = False
    Datatype = ''
    IsKey = False
    IsCompositeKey = False  # True if this column is part of a composite primary key
    Parent = ''

    def __init__(self, name:str, mandatory:bool, datatype:int, parent):
        self.Name = name
        self.Mandatory = mandatory
        self.Datatype = datatype
        self.Parent = parent
        self.IsKey = False

    @classmethod
    def Get(cls, connection:str, tablename):
        try:
            # get the columns for a table
            columns = {}
            cursor = connection.cursor()
            for row in cursor.columns(table=tablename):
                if row.is_nullable == 'NO':
                    mandatory = True
                else:
                    mandatory = False
                
                pk = False

                columns[row.column_name] = Columndef(row.column_name, mandatory, row.data_type, tablename)

        except Exception as e:
            columns = None

        finally:
            cursor.close()
            return columns