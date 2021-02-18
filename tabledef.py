from columndef import Columndef
from relationdef import Relationdef

class Tabledef:
    Name = ''
    Columns = {}
    Relationships = {}
    CompsitePK = False
    
    def __init__(self, name:str):
        self.Name = name
        self.Columns = {}
        self.Relationships = {}      # Relationdef[]
        self.CompsitePK = False    

    @classmethod
    def Get(cls, connection:str, dbschema:str):
        try:
            # Get the tables for this connection
            tables = {}
            cursor = connection.cursor()
            for tableRow in cursor.tables(schema=dbschema):
                print(tableRow.table_cat, tableRow.table_schem, tableRow.table_name, tableRow.table_type)
                table = Tabledef(tableRow.table_name)
                tables[table.Name] = table

            # For each table get the columns
            for key, value in tables.items():
                value.Columns = Columndef.Get(connection, key)
    
            # Mark the columns comprising the primary key
            for key, value in tables.items():
                pks = cursor.primaryKeys(table=key).fetchall()
                if len(pks) > 1:
                    composite = True
                else:
                    composite = False
                for pk in pks:
                    value.Columns[pk.column_name].IsKey = True
                    value.Columns[pk.column_name].CompsitePK = composite

            # Add the foreign keys
            rels = {}
            for key, value in tables.items():
                fks = cursor.foreignKeys(table=key, schema=dbschema).fetchall()
                for fk in fks:
                    print(key + '\t' + fk.fk_name + ':' + fk.pktable_name  + '.'  + fk.pkcolumn_name  + '='  + fk.fktable_name  + '.'  + fk.fkcolumn_name)


        except Exception as e:            
            tables = None

        finally:
            cursor.close()
            return tables
        
