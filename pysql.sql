SELECT cols.TABLE_NAME,
    (CASE when is_nullable = 'YES' 
                then 'N'
                else 'Y'
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
                THEN 'Y'
                ELSE 'N'
                END) AS PRIMARY_KEY
FROM INFORMATION_SCHEMA.COLUMNS cols
WHERE cols.TABLE_CATALOG='pubs' and cols.TABLE_NAME='authors'