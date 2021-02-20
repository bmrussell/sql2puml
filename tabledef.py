from columndef import Columndef
from relationdef import Relationdef

class Tabledef:
    Name = ''
    Columns = {}
    Relationships = {}
    CompositePK = False
    
    def __init__(self, name:str):
        self.Name = name
        self.Columns = {}
        self.Relationships = {}      # Relationdef[]
        self.CompositePK = False    

    
    def __GetColumns(self, connection, tablename:str) -> None:
        try:
            # get the columns for a table
            self.Columns = {}
            cursor = connection.cursor()
            for row in cursor.columns(table=tablename):
                if row.is_nullable == 'NO':
                    mandatory = True
                else:
                    mandatory = False
                
                pk = False
                self.Columns[row.column_name] = Columndef(row.column_name, mandatory, row.data_type, tablename)
            cursor.close()

            # See if there any columns have unique indexes
            # TODO: Only set unique if this index applies if this isn't a composite index
            # ('pubs', 'dbo', 'sales', None, None,    None,           0, None, None,       None, 21,   1,    None)
            # ('pubs', 'dbo', 'sales', 0,    'sales', 'UPKCL_sales',  1, 1,    'stor_id',  'A',  21,   1,    None)
            # ('pubs', 'dbo', 'sales', 0,    'sales', 'UPKCL_sales',  1, 2,    'ord_num',  'A',  21,   1,    None)
            # ('pubs', 'dbo', 'sales', 0,    'sales', 'UPKCL_sales',  1, 3,    'title_id', 'A',  21,   1,    None)
            # ('pubs', 'dbo', 'sales', 1,    'sales', 'titleidind',   3, 1,    'title_id', 'A',  None, None, None)
            # TODO: Work out how to handle composite indexes along with non unique indexes like above.

            cursor = connection.cursor()
            stats = cursor.statistics(table=tablename)
            for stat in stats:
                if stat.non_unique == True:
                    self.Columns[stat.column_name].IsUnique = False

            cursor.close()
        except Exception as e:
            self.Columns = None
        finally:
            return
    
    @classmethod
    def Get(cls, connection, dbschema:str):
        try:
            # Get the tables for this connection
            tables = {}
            cursor = connection.cursor()
            for tableRow in cursor.tables(schema=dbschema):
                table = Tabledef(tableRow.table_name)
                tables[table.Name] = table

            # For each table get the columns
            for key, value in tables.items():
                value.__GetColumns(connection, key)

            
    
            # Mark the columns comprising the primary key
            for key, value in tables.items():
                pks = cursor.primaryKeys(table=key).fetchall()
                if len(pks) > 1:
                    composite = True
                else:
                    composite = False
                for pk in pks:
                    value.Columns[pk.column_name].IsKey = True
                    value.Columns[pk.column_name].CompositePK = composite

                # Make sure Primary Keys are listed first
                value.Columns = dict(sorted(value.Columns.items(), key=lambda item: item[1].IsKey, reverse=True))

            # For each table get the relationships
            for tablename, table in tables.items():
                table.Relationships = {}
                cursor = connection.cursor()
                foreignKeys = cursor.foreignKeys(table=tablename)
                for foreignKey in foreignKeys:
                    table.Relationships[foreignKey.fk_name] = Relationdef(foreignKey.fk_name,
                                                                          tables[foreignKey.pktable_name],
                                                                          table.Columns[foreignKey.pkcolumn_name],
                                                                          tables[foreignKey.fktable_name],
                                                                          tables[foreignKey.fktable_name].Columns[foreignKey.fkcolumn_name])
        except Exception as e:            
            tables = None

        finally:
            cursor.close()
            return tables
        
