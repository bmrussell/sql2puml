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
            for row in cursor.columns(table=tablename).fetchall():
                if row.is_nullable == 'NO':
                    mandatory = True
                else:
                    mandatory = False
                
                pk = False
                self.Columns[row.column_name] = Columndef(row.column_name, mandatory, row.data_type, tablename)
            cursor.close()            
        except Exception as e:
            self.Columns = None
        finally:
            return
    
    @classmethod
    def Get(cls, connection, dbschema:str):
        try:
            # Get the tables for this connection
            cursor = connection.cursor()
            tables = {}
            cursorTables = cursor.tables(schema=dbschema, tableType='TABLE').fetchall()
            for tableRow in cursorTables:
                if tableRow.table_name[:3] == 'sys':
                    continue                                    # Exclude sys* tables 
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
                foreignKeys = cursor.foreignKeys(table=tablename).fetchall()
                for foreignKey in foreignKeys:
                    pktable = tables[foreignKey.pktable_name]
                    pkcol = pktable.Columns[foreignKey.pkcolumn_name]
                    fktable = tables[foreignKey.fktable_name]
                    fkcol = fktable.Columns[foreignKey.fkcolumn_name]
                    table.Relationships[foreignKey.fk_name] = Relationdef(cursor, foreignKey.fk_name, pktable, pkcol, fktable, fkcol)
        except Exception as e:            
            tables = None

        finally:
            cursor.close()
            return tables
        
