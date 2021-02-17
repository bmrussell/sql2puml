DECLARE @OBJ_DBNAME VARCHAR(100) = 'pubs'
DECLARE @LINECTRL INTEGER

DECLARE @OUTTBL AS TABLE (
    LINECTRL INTEGER,
    HEADERTRAILER VARCHAR(200),
    TABLE_NAME VARCHAR(200),
    MANDATORY VARCHAR(10),
    NAME VARCHAR(200),
    DATATYPE VARCHAR(200),
    PRIMARY_KEY VARCHAR(4)
)

SET @LINECTRL = 1
INSERT INTO @OUTTBL VALUES(0, CONCAT('@startuml ', @OBJ_DBNAME), '', '', '', '', '')

DECLARE @mytbl AS TABLE(TABLE_NAME VARCHAR(500))
INSERT INTO @mytbl
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_CATALOG=@OBJ_DBNAME
GROUP BY TABLE_NAME

WHILE((SELECT COUNT(*) FROM @mytbl)>0)
BEGIN
    DECLARE @TBLNAME VARCHAR(200)
    SELECT TOP 1 @TBLNAME = TABLE_NAME
    FROM @mytbl
    GROUP BY TABLE_NAME

    INSERT INTO @OUTTBL VALUES(@LINECTRL, CONCAT('entity "', @TBLNAME, '" as ', @TBLNAME, ' {'), '', '', '', '', '')

    SET @LINECTRL = @LINECTRL+3
    INSERT INTO @OUTTBL
        SELECT  @LINECTRL,
                '',
                cols.TABLE_NAME, 
                (CASE when is_nullable = 'YES' 
                then '' 
                else '*'
                end) AS MANDATORY,                
                cols.COLUMN_NAME AS NAME, 
                CONVERT(varchar, DATA_TYPE) + 
                (case when ISNULL(cols.CHARACTER_MAXIMUM_LENGTH,-1)=-1 
                    then '' 
                    else '('+CONVERT(varchar, cols.CHARACTER_MAXIMUM_LENGTH)+')' 
                    end) AS DATATYPE, 
                (CASE WHEN EXISTS(
                    SELECT *
                    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                        JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE ccu 
                            ON tc.CONSTRAINT_NAME = ccu.Constraint_name
                    WHERE 
                        tc.TABLE_NAME = cols.TABLE_NAME AND 
                        tc.CONSTRAINT_TYPE = 'PRIMARY KEY' AND
                        ccu.COLUMN_NAME = cols.COLUMN_NAME
                    ) 
                THEN '(PK)'
                ELSE ''
                END
                ) AS PRIMARY_KEY         
        FROM INFORMATION_SCHEMA.COLUMNS cols
        WHERE cols.TABLE_CATALOG=@OBJ_DBNAME and cols.TABLE_NAME=@TBLNAME        
        
    SET @LINECTRL = @LINECTRL+3
    INSERT INTO @OUTTBL VALUES(@LINECTRL, '}', '', '', '', '', '')

    DELETE TOP(1) FROM @mytbl
END


UPDATE OT 
SET OT.LINECTRL=OT.LINECTRL-2 
FROM @OUTTBL OT
WHERE PRIMARY_KEY='(PK)'

INSERT INTO @OUTTBL
SELECT DISTINCT LINECTRL+1, '', TABLE_NAME, '', '--', '', '' 
FROM @OUTTBL WHERE PRIMARY_KEY='(PK)'

SET @LINECTRL = @LINECTRL+3
INSERT INTO @OUTTBL
SELECT
    @LINECTRL,
    CONCAT(
            tp.name,
            (CASE WHEN EXISTS(
                SELECT *
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE ccu 
                    ON tc.CONSTRAINT_NAME = ccu.Constraint_name
                WHERE 
                    tc.TABLE_NAME = tp.name AND 
                    tc.CONSTRAINT_TYPE = 'PRIMARY KEY' AND
                    ccu.COLUMN_NAME = cp.name
                ) 
                THEN ' ||'
                ELSE ' }o'
                END
            ),
            '..',
            (CASE WHEN EXISTS(
                SELECT *
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE ccu 
                    ON tc.CONSTRAINT_NAME = ccu.Constraint_name
                WHERE 
                    tc.TABLE_NAME = tr.name AND 
                    tc.CONSTRAINT_TYPE = 'PRIMARY KEY' AND
                    ccu.COLUMN_NAME = cr.name
                ) 
                THEN '|| '
                ELSE 'o{ '
                END
            ),
            tr.name,
            ' : ',    
        cp.name, 
        ' = ',
        cr.name),
        '', '', '', '', ''
FROM sys.foreign_keys fk
INNER JOIN sys.tables tp ON fk.parent_object_id = tp.object_id
INNER JOIN sys.tables tr ON fk.referenced_object_id = tr.object_id
INNER JOIN sys.foreign_key_columns fkc ON fkc.constraint_object_id = fk.object_id
INNER JOIN sys.columns cp ON fkc.parent_column_id = cp.column_id AND fkc.parent_object_id = cp.object_id
INNER JOIN sys.columns cr ON fkc.referenced_column_id = cr.column_id AND fkc.referenced_object_id = cr.object_id
ORDER BY tp.name, cp.column_id


SET @LINECTRL = @LINECTRL+3
INSERT INTO @OUTTBL VALUES(@LINECTRL, '@enduml', '', '', '', '', '')


SELECT CONCAT(
        HEADERTRAILER, 
        CASE WHEN (DATATYPE <> '' OR NAME = '--') THEN CHAR(9) ELSE '' END,
        MANDATORY, 
        CASE WHEN DATATYPE <> '' THEN ' ' ELSE '' END,
        NAME, 
        CASE WHEN DATATYPE <> '' THEN ' : ' ELSE '' END,
        DATATYPE
    )
FROM @OUTTBL ORDER BY LINECTRL, TABLE_NAME ASC, PRIMARY_KEY DESC
