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

    def __IsOne(self, connectionCursor, table, col:Columndef) -> bool:
        '''
        Find out the max number of references at either end
        Has only unique index referencing solely the column : ONE "|"
        otherwise : MANY "{" or "}" (it may have no index on the column or a non unique index)
        '''
        # Construct a dictionary for all the unique indexes containing 
        #   {index name, concatenation of column names}
        # Then find an index with the concatenation of column names matching our column
        # If we get a hit then that's a unique index on only that column
        # e.g. on pubs.sales:
        #   ('pubs', 'dbo', 'sales', None, None,    None,           0, None, None,       None, 21,   1,    None)
        #   ('pubs', 'dbo', 'sales', 0,    'sales', 'UPKCL_sales',  1, 1,    'stor_id',  'A',  21,   1,    None)
        #   ('pubs', 'dbo', 'sales', 0,    'sales', 'UPKCL_sales',  1, 2,    'ord_num',  'A',  21,   1,    None)
        #   ('pubs', 'dbo', 'sales', 0,    'sales', 'UPKCL_sales',  1, 3,    'title_id', 'A',  21,   1,    None)
        #   ('pubs', 'dbo', 'sales', 1,    'sales', 'titleidind',   3, 1,    'title_id', 'A',  None, None, None)
        # we'll get
        #   { [UPKCL_sales, stor_idord_numtitle_id] }

        # Make the dictionary
        indexes = {}
        stats = connectionCursor.statistics(table=table.Name).fetchall()
        for stat in stats:
            if stat.non_unique == False:
                if stat.index_name in indexes:
                    indexes[stat.index_name] = indexes[stat.index_name] + stat.column_name
                else:
                    indexes[stat.index_name] = stat.column_name

        # Now just see if we have any indexes only on our column in our dictionary
        uniques = dict(filter(lambda x: x[1] == col.Name, indexes.items()))

        # unique = False
        # for key, value in indexes.items():
        #     if value == col.Name:
        #         unique = True
        #         break
        
        return len(uniques) > 0


    def __init__(self, connectionCursor, name:str, primaryTable, primaryColumn:Columndef, foreignTable, foreignColumn:Columndef):
        self.Name = name
        self.PrimaryTable = primaryTable
        self.PrimaryColumn = primaryColumn
        self.ForeignTable = foreignTable
        self.ForeignColumn = foreignColumn
        self.PumlRelation = ''

        # Work out the relatioship type
        # Zero or One   |o--    --o|
        # Exactly One   ||--    --||
        # Zero or Many  }o--    --o{
        # One or Many   }|--    --|{


        # Find out if the relationship is mandatory "|" or optional "o" at either end
        if primaryColumn.IsMandatory:
            pmin = '|'
        else:
            pmin = 'o'

        if self.__IsOne(connectionCursor, primaryTable, primaryColumn):
            pmax = '|'
        else:
            pmax = '}'

        primary = pmax + pmin

        if foreignColumn.IsMandatory:
            fmin = '|'
        else:
            fmin =  'o'

        if self.__IsOne(connectionCursor, foreignTable, foreignColumn):
            fmax = '|'
        else:
            fmax = '{'

        foreign = fmin + fmax
        self.PumlRelation = primaryTable.Name + ' ' + primary + '--' + foreign + ' ' + foreignTable.Name
        

