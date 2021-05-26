import pyodbc
import sys
import getopt

from tabledef import Tabledef
from columndef import Columndef
from relationdef import Relationdef

def Connect(driverOverride, server, host, port, dbname, username, password):

    if server == 'mssql':
        driver = '{SQL Server}'
        if driverOverride != '':
            driver = driverOverride
        
        if (port != '1433'):
            thePort = ',' + port
        else:
            thePort = ''

        if username == '':
            #Driver={SQL Server};Server=myServerAddress;Database=myDataBase;Trusted_Connection=Yes;
            connstr = ('Driver=' + driver + ';'
                    'Server=' + host + thePort + ';'
                    'Database=' + dbname +
                    ';Trusted_Connection=yes;')
        else:
            # Driver={SQL Server};Server=myServerAddress;Database=myDataBase;Uid=myUsername;Pwd=myPassword;
            connstr = ('Driver=' + driver + ';'
                    'Server=' + host + thePort + ';'
                    'Database=' + dbname +
                    ';Uid=' + username + ';Pwd=' + password + ';'
                    )
    elif server == 'mysql':
        # Driver={MySQL ODBC 8.0 Unicode Driver};Server=myServerAddress;Port=3306;Database=myDataBase;User=myUsername;Password=myPassword;Option=3;
        driver = '{MySQL ODBC 8.0 Unicode Driver}'
        if driverOverride != '':
            driver = driverOverride
        connstr = ('Driver=' + driver + ';'
                'Server=' + host + ';Port=' + port + ';' + 'Database=' + dbname +
                ';User=' + username + ';Password=' + password + ';Option=3;'
                )

    print(connstr)
    connection = pyodbc.connect(connstr)
    return connection


def Disconnect(connection) -> None:
    connection.close()


def EmitPumlHeader(dbname):
    print('@startuml ' + dbname + '\n')
    print('skinparam Linetype ortho\n')


def EmitPumlFooter():
    print('\n@enduml')


# Use table name lowercased and with spaces replaced by underscores
def PumlName(sqlName) -> str:
    pumlName = sqlName.lower().replace(' ', '_')
    return pumlName

def EmitTableHeader(tablename):
    print('entity "' + tablename + '" as ' + PumlName(tablename) + ' {')


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
        print(PumlName(rel.PrimaryTable.Name) + ' ' + rel.PumlRelation + ' ' + PumlName(rel.ForeignTable.Name))


def printStderr(*a): 
	# Here a is the array holding the objects 
	# passed as the arguement of the function 
	print(*a, file = sys.stderr) 


def PrintUsage():
    printStderr('Usage: python sql2puml.py OPTIONS [FILE]')
    printStderr('OPTIONS')    
    printStderr('\t-d, --database <database name>\tName of database to get diagram for')    
    printStderr('\t[-s, --schema <schema name>]\tName of schema within the database, default dbo with SQL Server')
    printStderr('\t[-S, --server <RDBMS Server>]\tSupply one of mssql, mysql. Default is mssql')
    printStderr('\t[-h, --host <server name>]\tServer to connect to, default localhost')
    printStderr('\t[-p, --port <SQL listen port>]\tPort to connect to, default 1433')
    printStderr('\t[-o, --out <output filename>]\tFilename to save output to, default write to console')
    printStderr('\t[-u, --user <username>]\tUsername to connect as')
    printStderr('\t[-P, --password <password>]\tPassword to connect with')
    printStderr('\nExample: python sql2puml.py -server localhost -port 1433 -dbname pubs -schema dbo')


def main(argv) -> None:
    server = 'mssql'
    host = 'localhost'
    port = '1433'
    dbname = ''
    schema = ''
    filename = ''
    conn = None
    fileHandle = None
    username = ''
    password=''
    driver = ''

    try:
        opts, args = getopt.getopt(argv, 'S:d:s:h:p:o:u:P:D:', ['server=','database=','schema=','host=','port=','out=','user=','password=','driver='])
        for opt, arg in opts:
            if opt in ('-S', '--server'):
                server = arg.lower()
            elif opt in ('-d', '--database'):
                dbname = arg 
            elif opt in ('-s', '--schema'):
                schema = arg
            elif opt in ('-h', '--host'):
                host = arg
            elif opt in ('-p', '--port'):
                port = arg
            elif opt in ('-o', '--out'):
                filename = arg
            elif opt in ('-u', '--user'):
                username = arg
            elif opt in ('-P', '--password'):
                password = arg
            elif opt in ('-D', '--driver'):
                driver = arg


        if filename != '':            
            original_stdout = sys.stdout
            fileHandle = open(filename, 'w')                # Change the standard output to filename
            sys.stdout = fileHandle

        if dbname == '':
            raise ValueError('No database name supplied')

        if server == 'msql':
            schema = ''

        if server == 'mssql' and schema == '':
            schema = 'dbo'

        conn = Connect(driver, server, host, port, dbname, username, password)
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
        printStderr('EXCEPTION: ' + e.args[1])
    
    finally:
        if fileHandle != None:
            sys.stdout = fileHandle

        if conn != None:
            Disconnect(conn)

if __name__ == '__main__':
    main(sys.argv[1:])
