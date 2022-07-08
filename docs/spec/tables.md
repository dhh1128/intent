# Tables
Intent supports the [table syntax of Github-flavored markdown](https://github.github.com/gfm/#tables-extension-).

Intent also adds some extra features.

## colspan
A cell (including in the header row) can be given an HTML `colspan` value (merging it with the cell(s) to its right) by preceding its delimiting pipe character with one or more greater-than (`>`) characters (where the number of `>` characters tells how many rightward cells to merge):

```iml
Month |	Savings
--- | ---
January	| $100
February | $80
|> Sum : $180
```

To begin a cell's content with a `>` character, simply put a space between the pipe delimiter and the content.

## rowspan
A cell can be given an HTML `rowspan` value (merging it with the cell(s) below it) by preceding its delimiting pipe character with one or more underscore (`_`) characters (where the number of `_` characters tells how many downward cells to merge):


```iml
Month | Savings | Savings for holiday!
--- | --- | ---
January | $100 |_ $50
February | $80
```

To begin a cell's content with a `>` character, simply put a space between the pipe delimiter and the content.

## multiline cells

Table rows in markdown must fit onto a single line. This means that if you want complex substructure inside a cell (e.g., multiple paragraphs, lists), [you must use HTML constructs](https://stackoverflow.com/a/48754707).   