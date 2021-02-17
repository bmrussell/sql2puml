# sql2puml

Convert MS SQL Schema to PlantUML diagram source

SQL code queries a bunch of system tables to get the tables, columns and oother information to generate a .puml file.

Text lines are inserted into an output table as a quick way to dump the text.

Seems to work; mostly. With a few wrinkles:

- Views are included. I should exclude those
- Composite keys aren't catered for well. e.g. on pubs, the Fk relationship from authors to titleauthors is identified as 1:1 where it should be 1:many. This is because the code isn't clever enough to see that au_id is part of a composite key (non unique) and not the whole key.

![](pubs.png)

