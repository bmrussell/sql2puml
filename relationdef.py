import pyodbc
from columndef import Columndef
class Relationdef:
    Name = ''               # Name of the relation

    PrimaryTable = None     # From table
    PrimaryColumn = None    # and column
    PrimaryRelation = ''    # ZEROorONE, One, ZEROorMANY ONEorMANY

    ForeignTable = None    
    ForeignColumn = None
    ForeignRelation = ''
    PumlRelation = ''       # Plant UML representation of relationship

    def __init__(self, name:str, primaryTable, primaryColumn:Columndef, foreignTable, foreignColumn:Columndef):
        self.Name = name
        self.PrimaryTable = primaryTable
        self.PrimaryColumn = primaryColumn
        self.ForeignTable = foreignTable
        self.ForeignColumn = foreignColumn
        self.PumlRelation = ''

        # Work out the relatioship type
        # Zero or One   |o--    --o|
        # Exactly One   ||--    --||
        # Zero or Many  }o--    -o{
        # One or Many   }|--    --|{
                
        if primaryColumn.IsUnique:
            primary = '|'
        else:
            primary = '}'
        
        if primaryColumn.IsMandatory:
            primary = primary + '|'
            line = '--'
        else:
            primary = primary + 'o'
            line = '..'

        if foreignColumn.IsMandatory:
            foreign = '|'
        else:
            foreign =  'o'

        if foreignColumn.IsUnique:
            foreign = foreign + '|'
        else:
            foreign = foreign + '{'

        self.PumlRelation = primaryTable.Name + ' ' + primary + line + foreign + ' ' + foreignTable.Name
        

