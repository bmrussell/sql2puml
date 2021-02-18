import pyodbc


def Connect(server, port, dbname):
    connstr = ('Driver={SQL Server Native Client 11.0};'
                'Server=' + server + ',' + port + ';' 
                'Database=' + dbname +
                ';Trusted_Connection=yes;')

    connection = pyodbc.connect(connstr)
    return connection

def Disconnect(connection) -> None:
    connection.close()

def GetTables(connection):
    # Get the list of tables in the database
    cursor = connection.cursor()
    cursor.execute('SELECT DB_NAME()')
    dbNameRows = cursor.fetchall()
    dbName = dbNameRows[0][0]

    cursor = connection.cursor()
    cursor.execute('SELECT TABLE_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_CATALOG=? GROUP BY TABLE_NAME', dbName)
    tablesRows = cursor.fetchall()
    return list(tablesRows)

def main() -> None:
    try:
        server = 'localhost'
        port = '1433'
        dbname = 'pubs'
        conn = Connect(server, port, dbname)
        tables = GetTables(conn)
        print(tables)

    except Exception as e:
        print('Exception: ' + e)

    finally:
        Disconnect(conn)


if __name__ == '__main__':
    main()