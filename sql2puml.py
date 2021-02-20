import pyodbc

from tabledef import Tabledef
from columndef import Columndef
from relationdef import Relationdef

def Connect(server, port, dbname):
    connstr = ('Driver={SQL Server Native Client 11.0};'
               'Server=' + server + ',' + port + ';'
               'Database=' + dbname +
               ';Trusted_Connection=yes;')
    connection = pyodbc.connect(connstr)
    return connection


def Disconnect(connection) -> None:
    connection.close()


def EmitPumlHeader(dbname):
    print('@startuml ' + dbname + '\n')
    print('skinparam Linetype ortho\n')


def EmitPumlFooter():
    print('\n@enduml')


def EmitTableHeader(tablename):
    # Use table name lowercased and with spaces replaced by underscores
    pumlName = tablename.lower()
    pumlName.replace(' ', '_')
    print('entity "' + tablename + '" as ' + pumlName + ' {')


def EmitTableDef(connection, table:Tabledef):
    line = ''
    seperated = False

    for columnName, column in table.Columns.items():
        if column.IsKey == False:               # Put out primary key seperator
            if seperated == False:              # before the first non primary key column
                print('\t--')
                seperated = True

        if column.IsMandatory:
            line = '\t* '
        else:
            line = '\t'
        
        line = line + column.Name
        if column.IsUnique:
            line = line + '*'

        line = line + ':'
        print(line)


def EmitTableFooter():
    print('}\n')


def EmitTable(connection, table:Tabledef):
    EmitTableHeader(table.Name)
    EmitTableDef(connection, table)
    EmitTableFooter()

def EmitRelations(connection, table:Tabledef):
    for name, rel in table.Relationships.items():
        print(rel.PumlRelation)

def main() -> None:
    try:
        server = 'localhost'
        port = '1433'
        dbname = 'pubs'
        schema = 'dbo'
        conn = Connect(server, port, dbname)

        tables = Tabledef.Get(conn, schema)
        EmitPumlHeader(dbname)
        for name, table in tables.items():
            EmitTable(conn, table)

        print('\n')
        for name, table in tables.items():
            EmitRelations(conn, table)


        EmitPumlFooter()

    except Exception as e:
        print('EXCEPTION: ' + e)

    finally:
        Disconnect(conn)


if __name__ == '__main__':
    main()
