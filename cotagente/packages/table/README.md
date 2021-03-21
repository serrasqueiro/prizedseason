# table modules

Main modules are:
- stable.py
  + Keying with text tables
- tabular.py
  + Tabular text tables, made easy
- tabproc.py
  + Helper/ wrapper classes included within Tabular() class.

## stable

`stable` module stands for Simple Tables (Textual).
tbd.

## tabular

`tabular` allows developer to instantiate a table and provide the keys for that table.
`key_fields = ['abc', 'def']` will force read for a text file indexed by the two columns, `abc` and `def`;
they should be unique within the entire text table.
Heading on these text tables should indicate a star ('*') for those keys;
heading should be the first line, and should start with an hash sign ('#').

Example:
```
#myid(int)*;path;URL(str)
101;/new/path1;http://world.com/1/
102;/new/path2;http://world.com/2/
```

