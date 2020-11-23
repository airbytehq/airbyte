---
description: 'Data warehouses, data lakes, databases...'
---

# Destinations



## BigQuery Naming

[BigQuery Datasets Naming](https://cloud.google.com/bigquery/docs/datasets#dataset-naming)

When you create a dataset in BigQuery, the dataset name must be unique for each project. The dataset name can contain the following:

- Up to 1,024 characters.
- Letters (uppercase or lowercase), numbers, and underscores.

    Note: In the Cloud Console, datasets that begin with an underscore are hidden from the navigation pane. You can query tables and views in these datasets even though these datasets aren't visible.

- Dataset names are case-sensitive: mydataset and MyDataset can coexist in the same project.
- Dataset names cannot contain spaces or special characters such as -, &, @, or %.

## Snowflake Naming

[Snowflake Identifiers syntax](https://docs.snowflake.com/en/sql-reference/identifiers-syntax.html)

### Unquoted:

- Start with a letter (A-Z, a-z) or an underscore (“_”).
- Contain only letters, underscores, decimal digits (0-9), and dollar signs (“$”).
- Are case-insensitive.

When an identifier is unquoted, it is stored and resolved in uppercase.

### Quoted:

- The identifier is case-sensitive.
- Delimited identifiers (i.e. identifiers enclosed in double quotes) can start with and contain any valid characters, including:
    - Numbers
    - Special characters (., ', !, @, #, $, %, ^, &, *, etc.)
    - Extended ASCII and non-ASCII characters
    - Blank spaces

When an identifier is double-quoted, it is stored and resolved exactly as entered, including case.

### Note
- Regardless of whether an identifier is unquoted or double-quoted, the maximum number of characters allowed is 255 (including blank spaces).
- Identifiers can also be specified using string literals, session variables or bind variables. For details, see SQL Variables.
- If an object is created using a double-quoted identifier, when referenced in a query or any other SQL statement, the identifier must be specified exactly as created, including the double quotes. Failure to include the quotes might result in an Object does not exist error (or similar type of error).
- Also, note that the entire identifier must be enclosed in quotes when referenced in a query/SQL statement. This is particularly important if periods (.) are used in identifiers because periods are also used in fully-qualified object names to separate each object.

## Postgres Naming

[Postgres SQL Identifiers syntax](https://www.postgresql.org/docs/9.0/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS)

- SQL identifiers and key words must begin with a letter (a-z, but also letters with diacritical marks and non-Latin letters) or an underscore (_).
- Subsequent characters in an identifier or key word can be letters, underscores, digits (0-9), or dollar signs ($).

  Note that dollar signs are not allowed in identifiers according to the letter of the SQL standard, so their use might render applications less portable. The SQL standard will not define a key word that contains digits or starts or ends with an underscore, so identifiers of this form are safe against possible conflict with future extensions of the standard.

- The system uses no more than NAMEDATALEN-1 bytes of an identifier; longer names can be written in commands, but they will be truncated. By default, NAMEDATALEN is 64 so the maximum identifier length is 63 bytes
- Quoted identifiers can contain any character, except the character with code zero. (To include a double quote, write two double quotes.) This allows constructing table or column names that would otherwise not be possible, such as ones containing spaces or ampersands. The length limitation still applies.
- Quoting an identifier also makes it case-sensitive, whereas unquoted names are always folded to lower case. 
- If you want to write portable applications you are advised to always quote a particular name or never quote it.

## Redshift Naming

[Redshift Names & Identifiers](https://docs.aws.amazon.com/redshift/latest/dg/r_names.html)

### Standard Identifiers
- Begin with an ASCII single-byte alphabetic character or underscore character, or a UTF-8 multibyte character two to four bytes long.
- Subsequent characters can be ASCII single-byte alphanumeric characters, underscores, or dollar signs, or UTF-8 multibyte characters two to four bytes long.
- Be between 1 and 127 bytes in length, not including quotation marks for delimited identifiers.
- Contain no quotation marks and no spaces.

### Delimited Identifiers

Delimited identifiers (also known as quoted identifiers) begin and end with double quotation marks ("). If you use a delimited identifier, you must use the double quotation marks for every reference to that object. The identifier can contain any standard UTF-8 printable characters other than the double quotation mark itself. Therefore, you can create column or table names that include otherwise illegal characters, such as spaces or the percent symbol.
ASCII letters in delimited identifiers are case-insensitive and are folded to lowercase. To use a double quotation mark in a string, you must precede it with another double quotation mark character.
