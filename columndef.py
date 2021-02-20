import pyodbc

class Columndef:
    Name = ''    
    Datatype = ''
    IsMandatory = False
    IsKey = False           # Is the column part or all of the primary key
    IsUnique = False        # Does the column have a unique index on it
    IsCompositeKey = False  # True if this column is part of a composite primary key
    Parent = ''

    def __init__(self, name:str, mandatory:bool, datatype:int, parent):
        self.Name = name
        self.IsMandatory = mandatory
        self.Datatype = datatype
        self.Parent = parent
        self.IsKey = False
