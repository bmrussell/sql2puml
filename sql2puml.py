import pyodbc

from tabledef import Tabledef
from columndef import Columndef


def Connect(server, port, dbname):
    connstr = ('Driver={SQL Server Native Client 11.0};'
                'Server=' + server + ',' + port + ';' 
                'Database=' + dbname +
                ';Trusted_Connection=yes;')

    connection = pyodbc.connect(connstr)


    # cursor = connection.cursor()
    # for table in cursor.tables():
    #     print(table.table_name)

    return connection

def Disconnect(connection) -> None:
    connection.close()

def GetTables(connection):
    # Get the list of tables in the database
    cursor = connection.cursor()
    cursor.execute('SELECT TABLE_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_CATALOG=? GROUP BY TABLE_NAME', connection.getinfo(pyodbc.SQL_DATABASE_NAME))
    tablesRows = cursor.fetchall()
    arr = []
    for tableRow in tablesRows:
        arr.append(tableRow[0])
    return arr

def EmitTableDef(connection, tablename):
    cursor = connection.cursor()
    query =("SELECT cols.TABLE_NAME, "
            "(CASE WHEN is_nullable = 'YES' THEN 'N' ELSE 'Y' END) AS MANDATORY,"
            "cols.COLUMN_NAME AS NAME,"
            "CONVERT(varchar, DATA_TYPE) + "
            " (case when ISNULL(cols.CHARACTER_MAXIMUM_LENGTH,-1)=-1 "
            " then '' "
            " else '('+CONVERT(varchar, cols.CHARACTER_MAXIMUM_LENGTH)+')' "
            " end) AS DATATYPE,"
            "(CASE WHEN EXISTS("
            "                   SELECT * FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc"
            "                   JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE ccu"
            "                   ON tc.CONSTRAINT_NAME = ccu.Constraint_name"
            "                   WHERE "
            "                   tc.TABLE_NAME = cols.TABLE_NAME AND"
            "                   tc.CONSTRAINT_TYPE = 'PRIMARY KEY' AND"
            "                   ccu.COLUMN_NAME = cols.COLUMN_NAME"
            "                  ) "
            " THEN 'Y' "
            " ELSE 'N' "
            " END) AS PRIMARY_KEY "
            " FROM INFORMATION_SCHEMA.COLUMNS cols "
            "WHERE cols.TABLE_CATALOG=? and cols.TABLE_NAME=? "
            "ORDER BY PRIMARY_KEY DESC")

    cursor.execute(query, connection.getinfo(pyodbc.SQL_DATABASE_NAME), tablename)
    rows = cursor.fetchall()

    doneFirstNonPKColumn = False
    for row in rows:
        if row[4] == 'N':                       # A non PK field
            if doneFirstNonPKColumn == False:   # If we haven't emitted the PK seperator
                print('\t--')                   # then do so
                doneFirstNonPKColumn = True     # and don't do that again

        output = '\t'                           # Column def is
        if row[1] == 'Y':                       # * name : datatype (where * = not NULL)
            output = output + '*'
        output = output + row[2] + ' : ' + row[3]

        print(output)

def EmitPumlHeader(connection):
    print('@startuml ' + connection.getinfo(pyodbc.SQL_DATABASE_NAME) + '\n')
    print('skinparam Linetype ortho\n')

def EmitPumlFooter():
    print('\n@enduml')

def EmitTableHeader(tablename):
    # Use table name lowercased and with spaces replaced by underscores
    pumlName = tablename.lower()
    pumlName.replace(' ', '_')
    print('entity "' + tablename + '" as ' + pumlName + ' {')

def EmitTableFooter():
    print('}\n')

def EmitTable(connection, tablename):
    EmitTableHeader(tablename)
    EmitTableDef(connection, tablename)
    EmitTableFooter()

def main() -> None:
    try:
        server = 'localhost'
        port = '1433'
        dbname = 'pubs'
        schema = 'dbo'
        conn = Connect(server, port, dbname)

        tables = Tabledef.Get(conn, schema)

        # tables = GetTables(conn)

        # EmitPumlHeader(conn)
        # for table in tables:
        #     EmitTable(conn, table)
        # EmitPumlFooter()

    except Exception as e:
        print('EXCEPTION: ' + e)

    finally:
        Disconnect(conn)


if __name__ == '__main__':
    main()