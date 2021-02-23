import pyodbc
import sys
import getopt

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

        line = line + ':' + column.Datatype
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




def printStderr(*a): 
	# Here a is the array holding the objects 
	# passed as the arguement of the function 
	print(*a, file = sys.stderr) 


def PrintUsage():
    printStderr('Usage: python sql2puml.py OPTIONS [FILE]')
    printStderr('OPTIONS')
    printStderr('\t-d, --database <database name>\tName of database to get diagram for')
    printStderr('\t-s, --schema <schema name>\tName of schema within the database, default dbo')
    printStderr('\t[-h, --host <server name>]\tServer to connect to, default localhost')
    printStderr('\t[-p, --port <SQL listen port>]\tPort to connect to, default 1433')
    printStderr('\t[-o, --out <output filename>]\tFilename to save output to, default write to console')
    printStderr('\nExample: python sql2puml.py -server localhost -port 1433 -dbname pubs -schema dbo')


def main(argv) -> None:

    host = 'localhost'
    port = '1433'
    dbname = ''
    schema = 'dbo'
    filename = ''
    conn = None
    fileHandle = None

    try:
        opts, args = getopt.getopt(argv, 'd:s:h:p:o:', ['database=','schema=','host=','port=','out='])
        for opt, arg in opts:
            if opt in ('-d', '--database'):
                dbname = arg 
            elif opt in ('-s', '--schema'):
                schema = arg
            elif opt in ('-h', '--host'):
                host = arg
            elif opt in ('-p', '--port'):
                port = arg
            elif opt in ('-o', '--out'):
                filename = arg


        if filename != '':            
            original_stdout = sys.stdout
            fileHandle = open(filename, 'w')                # Change the standard output to filename
            sys.stdout = fileHandle

        if dbname == '':
            raise ValueError('No database name supplied')

        conn = Connect(host, port, dbname)
        tables = Tabledef.Get(conn, schema)
        EmitPumlHeader(dbname)
        for name, table in tables.items():
            EmitTable(conn, table)

        for name, table in tables.items():
            EmitRelations(conn, table)

        EmitPumlFooter()

    except getopt.GetoptError:
        PrintUsage()

    except ValueError as ve:
        PrintUsage()

    except Exception as e:
        printStderr('EXCEPTION: ' + e)
    
    finally:
        if fileHandle != None:
            sys.stdout = fileHandle

        if conn != None:
            Disconnect(conn)

if __name__ == '__main__':
    main(sys.argv[1:])
