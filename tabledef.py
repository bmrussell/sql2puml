import pyodbc
from columndef import Columndef
from relationdef import Relationdef


class Tabledef:
    Name = ''    
    Columns = {}
    Relationships = {}
    CompositePK = False
    RowCount = None
    
    def __init__(self, name:str):
        self.Name = name
        self.Columns = {}
        self.Relationships = {}      # Relationdef[]
        self.CompositePK = False    
        self.RowCount = None

    
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
                self.Columns[row.column_name] = Columndef(row.column_name, mandatory, row.data_type, row.column_size, tablename)
            cursor.close()            
        except Exception as e:
            self.Columns = None
        finally:
            return

    def __GetRowCount(self, connection, tablename:str) -> None:
        queries = { "Microsoft SQL Server": f"""SELECT p.rows AS RowCounts FROM sys.tables t INNER JOIN sys.partitions p ON t.object_id = p.OBJECT_ID WHERE t.NAME = '{tablename}' AND t.is_ms_shipped = 0 GROUP BY t.Name, p.Rows""",
                    "MySQL": f"""SELECT table_rows from information_schema.tables where table_type = 'BASE TABLE' and table_schema not in('information_schema', 'sys', 'performance_schema', 'mysql') and table_name = '{tablename}' group by table_name;"""
                    }
        try:
            self.RowCount = None
            dbms = connection.getinfo(pyodbc.SQL_DBMS_NAME)
            cursor = connection.cursor()
            cursor.execute(queries[dbms])
            row = cursor.fetchone()
            while row:
                self.RowCount = row[0]
                row = cursor.fetchone()
            cursor.close()
        except Exception as e:
            self.RowCount = None
        finally:
            return
    
    @classmethod
    def Get(cls, connection, dbschema:str):
        try:
            # Get the tables for this connection
            cursor = connection.cursor()
            tables = {}
            if dbschema == '':
                cursorTables = cursor.tables(tableType='TABLE').fetchall()
            else:
                cursorTables = cursor.tables(schema=dbschema, tableType='TABLE').fetchall()
            for tableRow in cursorTables:
                if tableRow.table_name[:3] == 'sys':
                    continue                                    # Exclude sys* tables 
                table = Tabledef(tableRow.table_name)
                tables[table.Name] = table

            # For each table get the columns
            for key, value in tables.items():
                value.__GetColumns(connection, key)          
                value.__GetRowCount(connection, key)
    
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
        
