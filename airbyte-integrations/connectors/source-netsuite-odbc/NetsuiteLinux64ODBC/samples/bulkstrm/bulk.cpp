#if defined (_WIN32) || defined (_WIN64)
#define _CRT_SECURE_NO_WARNINGS
#include "windows.h"
#include "malloc.h"
#else
#include "stdlib.h"
#include "string.h"
#include "alloca.h"
#endif

#define	SQL_NOUNICODEMAP

#include "sqlext.h"

#include "msgprintf.hpp"


typedef struct {
	SQLLEN		ColSize;
	void		*Data;
	SQLLEN		*Length;
	SQLSMALLINT	SqlType;
	SQLSMALLINT	Unsigned;
	SQLSMALLINT	CType;
	SQLSMALLINT	ParamScale;
	SQLSMALLINT	ParamSqlType;
} ColumnBinding;
typedef ColumnBinding *PColumnBinding;


int err (RETCODE rc, short handleType, SQLHANDLE handle)
{
	SQLCHAR		msg[5120];
	SQLCHAR		sqlState[8];
	SDWORD		nativeCode;
	SWORD		msgLen;

	if (rc == SQL_SUCCESS) return 0;

	if (rc == SQL_NO_DATA_FOUND) {
		msgprintf ("SQL_NO_DATA_FOUND\n");
		return 1;
	}

	if (rc == SQL_INVALID_HANDLE) {
		msgprintf ("SQL_INVALID_HANDLE\n");
		return 1;
	}

	RETCODE rc2 = SQLGetDiagRec (handleType, handle, 1, sqlState,
				     &nativeCode, msg,
				     sizeof (msg), &msgLen);
	int i;
	for (i = 2; (i <= 10) && (rc2 != SQL_NO_DATA_FOUND); i++) {
		sqlState[5] = 0;
		msgprintf ("%s (%d) : (%d) %s\n", (const char *) sqlState,
			   nativeCode, msgLen, (const char *) msg);

		rc2 = SQLGetDiagRec (handleType, handle, i, sqlState,
				     &nativeCode, msg,
				     sizeof (msg), &msgLen);
	}

	if (rc == SQL_SUCCESS_WITH_INFO) return 0;

	return 1;
}

int errEnv (RETCODE rc, SQLHENV henv)
{
	return err (rc, SQL_HANDLE_ENV, henv);
}

int errDB (RETCODE rc, SQLHDBC hdbc)
{
	return err (rc, SQL_HANDLE_DBC, hdbc);
}

int err (RETCODE rc, SQLHDBC hstmt)
{
	return err (rc, SQL_HANDLE_STMT, hstmt);
}

int errDesc (RETCODE rc, SQLHDESC desc)
{
	return err (rc, SQL_HANDLE_DESC, desc);
}


SQLSMALLINT sqlToCType (SQLSMALLINT	sqlType,
			SQLSMALLINT	unSigned,
			int		bUnicode)
{
	switch (sqlType) {
	case SQL_CHAR:
	case SQL_VARCHAR:
	case SQL_LONGVARCHAR:
	default:
		return bUnicode ? SQL_C_WCHAR : SQL_C_CHAR;
	case SQL_WCHAR:
	case SQL_WVARCHAR:
	case SQL_WLONGVARCHAR:
		return SQL_C_WCHAR;
	case SQL_BINARY:
	case SQL_VARBINARY:
	case SQL_LONGVARBINARY:
		return SQL_C_BINARY;
	case SQL_BIT:
		return SQL_C_UTINYINT;
	case SQL_TINYINT:
		return unSigned ? SQL_C_UTINYINT : SQL_C_STINYINT;
	case SQL_SMALLINT:
		return unSigned ? SQL_C_USHORT : SQL_C_SSHORT;
	case SQL_INTEGER:
		return unSigned ? SQL_C_ULONG : SQL_C_SLONG;
	case SQL_BIGINT:
		return unSigned ? SQL_C_UBIGINT : SQL_C_SBIGINT;
	case SQL_DOUBLE:
	case SQL_FLOAT:
		return SQL_C_DOUBLE;
	case SQL_REAL:
		return SQL_C_FLOAT;
	case SQL_TYPE_DATE:
		return SQL_C_DATE;
	case SQL_TYPE_TIME:
		return SQL_C_TIME;
	case SQL_TYPE_TIMESTAMP:
		return SQL_C_TIMESTAMP;
	}
}


int bindColumns (SQLHSTMT	hstmt,
		 int		numRows,
		 int		maxBinding,
		 int		bUnicode,
		 SQLSMALLINT	*pNumCols,
		 PColumnBinding	*columnBindings)
{
	SQLSMALLINT	numCols;
	int		i;
	RETCODE		rc;
	SQLHDESC	ird;
	char		*data;
	SQLLEN		*len;
	SQLLEN		colSize, totalSize, totalSizeWithLens;

	*columnBindings = NULL;

	rc = SQLNumResultCols (hstmt, &numCols);
	if (err (rc, hstmt)) {
		return 1;
	}

	rc = SQLSetStmtAttr (hstmt, SQL_ATTR_ROW_ARRAY_SIZE,
			     (SQLPOINTER) numRows, SQL_IS_INTEGER);
	if (err (rc, hstmt)) {
		return 1;
	}

	rc = SQLGetStmtAttr (hstmt, SQL_ATTR_IMP_ROW_DESC,
			     &ird, SQL_IS_POINTER, NULL);
	if (err (rc, hstmt)) {
		return 1;
	}

	*columnBindings = new ColumnBinding [numCols];
	if (! *columnBindings) {
		msgprintf ("Memory allocation failure\n");
		return 2;
	}

	totalSize = 0;
	for (i = 0; i < numCols; i++) {
		rc = SQLGetDescField (ird, i + 1, SQL_DESC_OCTET_LENGTH,
				      &colSize, 0, NULL);
		if (errDesc (rc, ird)) {
			return 1;
		}

		if (colSize > maxBinding) {
			char	colName[128];

			rc = SQLGetDescField (ird, i + 1, SQL_DESC_NAME,
					      colName, sizeof (colName), NULL);
			if (errDesc (rc, ird)) {
				return 1;
			}
			msgprintf ("%s may be truncated (from %d to %d)\n",
				colName, colSize, maxBinding);
			colSize = maxBinding;
		}

		rc = SQLGetDescField (ird, i + 1, SQL_DESC_CONCISE_TYPE,
				      &(*columnBindings)[i].SqlType, 0, NULL);
		if (errDesc (rc, ird)) {
			return 1;
		}

		switch ((*columnBindings)[i].SqlType) {
		case SQL_WCHAR:
		case SQL_WVARCHAR:
		case SQL_WLONGVARCHAR:
#if defined (_WIN32) || defined (_WIN64)
			// Provide room for the UTF16 null-terminator
			colSize += 2;
			break;
#endif
		case SQL_CHAR:
		case SQL_VARCHAR:
		case SQL_LONGVARCHAR:
			if (bUnicode) {
				// Provide room for the UTF16 null-terminator
#if defined (_WIN32) || defined (_WIN64)
				// UTF16
				colSize *= 2;
				colSize += 2;
#else
				// UTF8
				colSize *= 3;
				colSize++;
#endif
				break;

			}
			// Provide room for the null-terminator
			colSize++;
			break;
		case SQL_BINARY:
		case SQL_VARBINARY:
		case SQL_LONGVARBINARY:
			break;
		case SQL_BIT:
		case SQL_TINYINT:
			colSize = 1;
			break;
		case SQL_SMALLINT:
			colSize = 2;
			break;
		case SQL_INTEGER:
			colSize = 4;
			break;
		case SQL_BIGINT:
			colSize = 8;
			break;
		case SQL_DECIMAL:
		case SQL_NUMERIC:
			colSize = sizeof (SQL_NUMERIC_STRUCT);
			break;
		case SQL_TYPE_DATE:
			colSize = sizeof (DATE_STRUCT);
			break;
		case SQL_TYPE_TIME:
			colSize = sizeof (TIME_STRUCT);
			break;
		case SQL_TYPE_TIMESTAMP:
			colSize = sizeof (TIMESTAMP_STRUCT);
			break;
		case SQL_DOUBLE:
		case SQL_FLOAT:
			colSize = sizeof (double);
			break;
		case SQL_REAL:
			colSize = sizeof (float);
			break;
		default:
			msgprintf ("Unsupported data type: %d\n", (*columnBindings)[i].SqlType);
			break;
		}

		// Align each column's data on an 8-byte boundary.
		(*columnBindings)[i].ColSize = colSize;
		totalSize += (colSize * numRows + 7) & (~ 7);

		rc = SQLGetDescField (ird, i + 1, SQL_DESC_UNSIGNED,
				      &(*columnBindings)[i].Unsigned, 0, NULL);
		if (errDesc (rc, ird)) {
			return 1;
		}
	}

	totalSizeWithLens = totalSize + numCols * numRows * sizeof (SQLLEN);

	data = (char *) malloc (totalSizeWithLens);
	if (! data) {
		delete [] *columnBindings;
		*columnBindings = NULL;
		msgprintf ("Memory allocation failure\n");
		return 2;
	}

	len = (SQLLEN *) (data + totalSize);

	for (i = 0; i < numCols; i++) {
		rc = SQLBindCol (hstmt, i + 1,
				 (*columnBindings)[i].CType = sqlToCType (
			(*columnBindings)[i].SqlType,
			(*columnBindings)[i].Unsigned,
			bUnicode),
				 data, (*columnBindings)[i].ColSize, len);
		if (err (rc, hstmt)) {
			return 1;
		}

		(*columnBindings)[i].Data = data;
		data += ((*columnBindings)[i].ColSize * numRows + 7) & (~ 7);
		(*columnBindings)[i].Length = len;
		len += numRows;
	}

	*pNumCols = numCols;

	return 0;
}


int bindParameters (SQLHSTMT		hstmt,
		    int			numRows,
		    int			numCols,
		    PColumnBinding	columnBindings)
{
	int		i;
	RETCODE		rc;
	SQLHDESC	ird;
	SQLLEN		colSize;
	SQLSMALLINT	precision;

	rc = SQLSetStmtAttr (hstmt, SQL_ATTR_PARAMSET_SIZE,
			     (SQLPOINTER) numRows, SQL_IS_INTEGER);
	if (err (rc, hstmt)) {
		return 1;
	}

	rc = SQLGetStmtAttr (hstmt, SQL_ATTR_IMP_ROW_DESC,
			     &ird, SQL_IS_POINTER, NULL);
	if (err (rc, hstmt)) {
		return 1;
	}

	for (i = 0; i < numCols; i++) {
		rc = SQLGetDescField (ird, i + 1, SQL_DESC_CONCISE_TYPE,
				      &columnBindings[i].ParamSqlType, 0, NULL);
		if (errDesc (rc, ird)) {
			return 1;
		}

		rc = SQLGetDescField (ird, i + 1, SQL_DESC_SCALE,
				      &columnBindings[i].ParamScale, 0, NULL);
		if (errDesc (rc, ird)) {
			return 1;
		}

		switch (columnBindings[i].ParamSqlType) {
		case SQL_CHAR:
		case SQL_VARCHAR:
		case SQL_LONGVARCHAR:
		case SQL_WCHAR:
		case SQL_WVARCHAR:
		case SQL_WLONGVARCHAR:
		case SQL_BINARY:
		case SQL_VARBINARY:
		case SQL_LONGVARBINARY:
			rc = SQLGetDescField (ird, i + 1, SQL_DESC_LENGTH,
					      &colSize, 0, NULL);
			break;
		default:
			rc = SQLGetDescField (ird, i + 1, SQL_DESC_PRECISION,
					      &precision, 0, NULL);
			colSize = precision;
			break;
		}
		if (errDesc (rc, ird)) {
			return 1;
		}

		rc = SQLBindParameter (hstmt, i + 1, SQL_PARAM_INPUT,
				       columnBindings[i].CType,
				       columnBindings[i].ParamSqlType,
				       colSize,
				       columnBindings[i].ParamScale,
				       columnBindings[i].Data,
				       columnBindings[i].ColSize,
				       columnBindings[i].Length);
		if (err (rc, hstmt)) {
			return 1;
		}
	}

	return 0;
}


int createRS (SQLHSTMT		hstmt,
	      const char	*sql,
	      int		numRows,
	      int		maxBinding,
	      int		bUnicode,
	      SQLSMALLINT	*pNumCols,
	      PColumnBinding	*columnBindings)
{
	RETCODE		rc;

	rc = SQLExecDirect (hstmt, (SQLCHAR *) sql, SQL_NTS);
	if (err (rc, hstmt)) return 1;

	if (bindColumns (hstmt, numRows, maxBinding, bUnicode,
			 pNumCols, columnBindings)) return 1;

	return 0;
}


int copyData (SQLHDBC		hdbc,
	      SQLHSTMT		hstmtIn,
	      const char	*tableName,
	      int		numRows,
	      SQLSMALLINT	numCols,
	      int		bUnicode,
	      size_t		displayProgressEveryRows,
	      PColumnBinding	columnBindings,
	      size_t		*numRowsLoaded)
{
	RETCODE		rc;
	SQLHSTMT	hstmtOut;
	int		i, j, retVal = 1;
	size_t		tableNameLen = strlen (tableName);
	char		*sql;
	size_t		selectLen, insertLen, sqlLen;
	SQLLEN		rowsFetched;
	size_t		numProgressRows;

	selectLen = tableNameLen + sizeof ("SELECT * FROM  WHERE 0=1");
	insertLen = tableNameLen + sizeof ("INSERT INTO  VALUES ()") + numCols * 2;

	sqlLen = (insertLen >= selectLen) ? insertLen : selectLen;

	sql = (char *) alloca (sqlLen);

	strcpy (sql, "SELECT * FROM ");
	strcat (sql, tableName);
	strcat (sql, " WHERE 0=1");

	rc = SQLAllocHandle (SQL_HANDLE_STMT, hdbc, &hstmtOut);
	if (errDB (rc, hdbc)) return 1;

	rc = SQLPrepare (hstmtOut, (SQLCHAR *) sql, SQL_NTS);
	if (err (rc, hstmtOut)) return 1;

	if (bindParameters (hstmtOut, numRows, numCols, columnBindings)) goto freeStmt;

	strcpy (sql, "INSERT INTO ");
	strcat (sql, tableName);
	strcat (sql, " VALUES (?");
	for (i = 1; i < numCols; i++) {
		strcat (sql, ",?");
	}
	strcat (sql, ")");

	rc = SQLPrepare (hstmtOut, (SQLCHAR *) sql, SQL_NTS);
	if (err (rc, hstmtOut)) goto freeStmt;

	rc = SQLSetStmtAttr (hstmtIn, SQL_ATTR_ROWS_FETCHED_PTR,
			     &rowsFetched, SQL_IS_POINTER);
	if (err (rc, hstmtIn)) goto freeStmt;

	rc = SQLSetConnectAttr (hdbc, SQL_ATTR_AUTOCOMMIT, (SQLPOINTER) SQL_AUTOCOMMIT_OFF, SQL_IS_INTEGER);
	if (errDB (rc, hdbc)) goto freeStmt;

	numProgressRows = 0;
	rc = SQLFetchScroll (hstmtIn, SQL_FETCH_NEXT, 0);
	while ((rc == SQL_SUCCESS) || (rc == SQL_SUCCESS_WITH_INFO)) {
		if (numProgressRows >= displayProgressEveryRows) {
			if (sizeof (size_t) == 4) {
				msgprintf ("%u rows loaded\n", *numRowsLoaded);
			} else {
				msgprintf ("%llu rows loaded\n", *numRowsLoaded);
			}

			numProgressRows = 0;
		}

		if (rc == SQL_SUCCESS_WITH_INFO) {
			err (rc, hstmtIn);

// Fix the lengths for any truncated columns.

			for (i = 0; i < numCols; i++) {
				SQLLEN colSize = columnBindings[i].ColSize;

				switch (columnBindings[i].SqlType) {
				case SQL_CHAR:
				case SQL_VARCHAR:
				case SQL_LONGVARCHAR:
#if defined (_WIN32) || defined (_WIN64)
					if (! bUnicode) {
						// Adjust for null-terminator
						colSize--;
						break;
					}
#endif
				case SQL_WCHAR:
				case SQL_WVARCHAR:
				case SQL_WLONGVARCHAR:
					// Adjust for null-terminator
#if defined (_WIN32) || defined (_WIN64)
					colSize -= 2;
#else
					colSize--;
#endif
					break;
				}

				SQLLEN	*len = columnBindings[i].Length;
				for (j = 0; j < rowsFetched; j++, len++) {
					if ((*len == SQL_NO_TOTAL) ||
					    (*len > colSize)) {
						*len = colSize;
					}
				}
			}
		}

		if (rowsFetched != numRows) {
			rc = SQLSetStmtAttr (hstmtOut, SQL_ATTR_PARAMSET_SIZE,
					     (SQLPOINTER) rowsFetched, SQL_IS_INTEGER);
			if (err (rc, hstmtIn)) {
				goto freeStmt;
			}
		}

		rc = SQLExecute (hstmtOut);
		if (err (rc, hstmtOut)) goto freeStmt;

		*numRowsLoaded += rowsFetched;
		numProgressRows += rowsFetched;

		rc = SQLFetchScroll (hstmtIn, SQL_FETCH_NEXT, 0);
	}
	if (rc != SQL_NO_DATA_FOUND) {
		if (err (rc, hstmtIn)) goto freeStmt;
	}

	retVal = 0;

freeStmt:
	rc = SQLEndTran (SQL_HANDLE_DBC, hdbc, retVal ? SQL_ROLLBACK : SQL_COMMIT);
	errDB (rc, hdbc);

	rc = SQLSetConnectAttr (hdbc, SQL_ATTR_AUTOCOMMIT, (SQLPOINTER) SQL_AUTOCOMMIT_ON, SQL_IS_INTEGER);
	errDB (rc, hdbc);

	rc = SQLFreeHandle (SQL_HANDLE_STMT, hstmtOut);
	err (rc, hstmtOut);

	return retVal;
}


int bulk (const char	*connStrIn,
	  const char	*sqlIn,
	  const char	*tableName,
	  const char	*connStrOut,
	  int		numRows,
	  int		maxBinding,
	  int		bUnicode,
	  size_t	*numRowsLoaded)
{
	RETCODE		rc;
	SQLHENV		henv;
	SQLHDBC		hdbcIn, hdbcOut = SQL_NULL_HDBC;
	SQLHSTMT	hstmtIn, hstmtOut = SQL_NULL_HSTMT;
	SQLCHAR		connStrTemp[2048];
	SQLSMALLINT	connStrTempLen;
	SQLSMALLINT	numCols;

	int		retVal = 1;
	PColumnBinding	columnBindings = NULL;

	*numRowsLoaded = 0;

	rc = SQLAllocHandle (SQL_HANDLE_ENV, SQL_NULL_HANDLE, &henv);
	if (rc != SQL_SUCCESS) {
		if (rc != SQL_SUCCESS_WITH_INFO) {
			msgprintf ("SQLAllocHandle (SQL_HANDLE_ENV) failed!\n");
			return 1;
		}
		msgprintf ("SQLAllocHandle (SQL_HANDLE_ENV) returned a warning\n");
	}

	rc = SQLSetEnvAttr (henv, SQL_ATTR_ODBC_VERSION,
			    (SQLPOINTER) SQL_OV_ODBC3, SQL_IS_INTEGER);
	if (errEnv (rc, henv)) goto freeEnv;

	rc = SQLAllocHandle (SQL_HANDLE_DBC, henv, &hdbcIn);
	if (errEnv (rc, henv)) {
		goto freeEnv;
	}

	rc = SQLDriverConnect (hdbcIn, NULL, (SQLCHAR *) connStrIn,
			       SQL_NTS, connStrTemp, sizeof (connStrTemp),
			       &connStrTempLen,
#if defined (_WIN32) || defined (_WIN64)
			       SQL_DRIVER_COMPLETE
#else
			       SQL_DRIVER_NOPROMPT
#endif
			      );
	if (errDB (rc, hdbcIn)) goto freeConn;

	if (connStrOut) {
		/*if ((! strstr (connStrOut, "EnableBulkLoad")) &&
		    (! strstr (connStrOut, "EBL"))) {
			size_t	len = strlen (connStrOut);
			char *tmp = (char *) alloca (len + sizeof (";EBL=1"));
			strcpy (tmp, connStrOut);
			strcpy (tmp + len, ";EBL=1");
			connStrOut = tmp;
		}*/
destConnect:
		rc = SQLAllocHandle (SQL_HANDLE_DBC, henv, &hdbcOut);
		if (errEnv (rc, henv)) goto disconn;

		rc = SQLDriverConnect (hdbcOut, NULL, (SQLCHAR *) connStrOut,
				       SQL_NTS, connStrTemp, sizeof (connStrTemp),
				       &connStrTempLen,
#if defined (_WIN32) || defined (_WIN64)
				       SQL_DRIVER_COMPLETE
#else
				       SQL_DRIVER_NOPROMPT
#endif
				      );
		if (errDB (rc, hdbcOut)) goto disconn;
	}
	/*else if ((! strstr (connStrIn, "EnableBulkLoad")) &&
		 (! strstr (connStrIn, "EBL"))) {
		size_t	len = strlen (connStrIn);
		char *tmp = (char *) alloca (len + sizeof (";EBL=1"));
		strcpy (tmp, connStrIn);
		strcpy (tmp + len, ";EBL=1");
		connStrOut = tmp;
		goto destConnect;
	}*/

	rc = SQLAllocHandle (SQL_HANDLE_STMT, hdbcIn, &hstmtIn);
	if (errDB (rc, hdbcIn)) goto disconn;

	if (createRS (hstmtIn, sqlIn, numRows, maxBinding, bUnicode,
		      &numCols, &columnBindings)) goto freeStmt;

	if (copyData ((hdbcOut == SQL_NULL_HDBC) ? hdbcIn : hdbcOut, hstmtIn,
		      tableName, numRows, numCols, bUnicode, 0x4000, // 16K
		      columnBindings, numRowsLoaded)) goto freeStmt;

	retVal = 0;

freeStmt:
	if (hstmtOut != SQL_NULL_HSTMT) {
		rc = SQLFreeHandle (SQL_HANDLE_STMT, hstmtOut);
		err (rc, hstmtOut);
	}

	rc = SQLFreeHandle (SQL_HANDLE_STMT, hstmtIn);
	err (rc, hstmtIn);

disconn:
	delete [] columnBindings;

	if (hdbcOut != SQL_NULL_HDBC) {
		rc = SQLDisconnect (hdbcOut);
		errDB (rc, hdbcOut);
	}

	rc = SQLDisconnect (hdbcIn);
	errDB (rc, hdbcIn);

freeConn:
	if (hdbcOut != SQL_NULL_HDBC) {
		rc = SQLFreeHandle (SQL_HANDLE_DBC, hdbcOut);
		errDB (rc, hdbcOut);
	}

	rc = SQLFreeHandle (SQL_HANDLE_DBC, hdbcIn);
	errDB (rc, hdbcIn);

freeEnv:
	rc = SQLFreeHandle (SQL_HANDLE_ENV, henv);
	errEnv (rc, henv);

	return retVal;
}
