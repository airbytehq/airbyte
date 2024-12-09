#if defined (_WIN32) || defined (_WIN64)
#define _CRT_SECURE_NO_WARNINGS
#include "windows.h"
#include "malloc.h"
#else
#include "stdlib.h"
#include "string.h"
#include "alloca.h"
#endif

#include "stdio.h"


extern int bulk (const char	*connStrIn,
		 const char	*sqlIn,
		 const char	*tableName,
		 const char	*connStrOut,
		 int		numRows,
		 int		maxBinding,
		 int		bUnicode,
		 size_t		*numRowsLoaded);


void msgprintf (const char *fmt)
{
	printf (fmt);
	return;
}

void msgprintf (const char *fmt, int v1)
{
	printf (fmt, v1);
	return;
}

void msgprintf (const char *fmt, size_t v1)
{
	printf (fmt, v1);
	return;
}

void msgprintf (const char *fmt, const char *v1, int v2, int v3)
{
	printf (fmt, v1, v2, v3);
	return;
}

void msgprintf (const char *fmt, const char *v1, int v2, int v3, const char *v4)
{
	printf (fmt, v1, v2, v3, v4);
	return;
}

void msgprintf (const char *fmt, int v1, int v2, const void *v3, int v4, const void *v5)
{
	printf (fmt, v1, v2, v3, v4, v5);
	return;
}

void msgprintf (const char *fmt, int v1, int v2, int v3, int v4, int v5, const void *v6, int v7, const void *v8)
{
	printf (fmt, v1, v2, v3, v4, v5, v6, v7, v8);
	return;
}


void loadDone (size_t numRows)
{
}


int main (int argc, char **argv)
{
	int		maxBinding = 4096;
	const char	*connStrIn, *connStrOut = NULL;
	int		requiredVal = 0;
	int		numRows = 128;
	int		bUnicode = 0;
	const char	*sqlIn, *tableName;
	int		i;
	size_t		numRowsLoaded = 0;

	for (i = 1; i < argc; i++) {
		if (! strcmp (argv[i], "-maxBindSize")) {
			maxBinding = atoi (argv[++i]);
			continue;
		}
		if (! strcmp (argv[i], "-numRows")) {
			numRows = atoi (argv[++i]);
			continue;
		}
		if (! strcmp (argv[i], "-Unicode")) {
			bUnicode = 1;
			continue;
		}

		switch (requiredVal) {
			case 0:
				connStrIn = argv[i];
				break;
			case 1:
				sqlIn = argv[i];
				break;
			case 2:
				tableName = argv[i];
				break;
			case 3:
				connStrOut = argv[i];
				break;
			default:
				printf ("Ignored: %s\n", argv[i]);
				requiredVal--;
				break;
		}
		requiredVal++;
	}

	if (requiredVal < 3) {
		printf ("%s <source conn str> <source SQL> <destination table> [<dest conn str>]\n", argv[0]);
		printf ("\tThe following options may appear anywhere:\n");
		printf ("\t-maxBindSize <#> : Maximum fetch size for a column; defaults to 4096\n");
		printf ("\t-numRows <#> : Number of rows to fetch and insert at-a-time; defaults to 128\n");
		printf ("\t-Unicode : Bind all character data as Unicode (SQL_C_WCHAR)\n");
		return 0;
	}

	int rc = bulk (connStrIn, sqlIn, tableName, connStrOut, numRows, maxBinding, bUnicode, &numRowsLoaded);

	printf ("%d row%s loaded.\n", numRowsLoaded, (numRowsLoaded == 1) ? "" : "s");

	return rc;
}
