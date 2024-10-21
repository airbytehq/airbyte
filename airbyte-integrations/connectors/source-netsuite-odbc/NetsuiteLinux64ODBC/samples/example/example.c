/*
** (c) 2003-2008. Progress Software Corporation. All rights reserved
*/

/*
** File:	example.c
**
** Purpose:	To demonstrate some of the ODBC function calls and to allow
**		statements to be entered by the user at will.
*/

#ifdef __cplusplus
extern "C" {
#endif

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <locale.h>

#if defined(WIN32)
#include <windows.h>
#endif

#include <sqlext.h>

#ifdef __cplusplus
}
#endif

#include "example.h"

/*
** Define Some useful defines
*/
#if !defined (NULL)
#define	NULL	0
#endif

#if (ODBCVER >= 0x0300)
#define NO_ODBC_V2	 /* dont call ODBC 2.0 functions depreciated in ODBC v3.0 */
#endif

#define MAXRETRY 1

/* Reads a line from stdin, without the trailing newline-char */
#define readLine(buf,size) { fgets((char *)buf, size, stdin); buf[strlen((const char *)buf)-1]='\0'; }

/*
** function: ODBC_error
**
** Purpose:	Display to stdout current ODBC Errors
**
** Arguments:	(SQLHENV)henv    _ ODBC Environment handle.
**		(SQLHDBC)hdbc    - ODBC Connection Handle error generated on.
**		(SQLHSTMT)hstmt	- ODBC SQL Handle error generated on.
**
** Returns:	void
**
*/

void ODBC_error (			/* Obtain ODBC Error */
	HENV henv,			/* ODBC Environment */
	HDBC hdbc,			/* ODBC Connection Handle */
	HSTMT hstmt)			/* ODBC SQL Handle */
{
	UCHAR	sqlstate[10];
	UCHAR	errmsg[SQL_MAX_MESSAGE_LENGTH];
	SDWORD	nativeerr;
	SWORD	actualmsglen;
	RETCODE	rc;

loop:  	rc = SQLError((SQLHENV)henv, (SQLHDBC)hdbc, (SQLHSTMT)hstmt,
		sqlstate, &nativeerr, errmsg,
		SQL_MAX_MESSAGE_LENGTH - 1, &actualmsglen);

	if (rc == SQL_ERROR) {
		printf ("SQLError failed!\n");
		return;
	}

	if (rc != SQL_NO_DATA_FOUND) {
		printf ("SQLSTATE = %s\n",sqlstate);
		printf ("NATIVE ERROR = %d\n",nativeerr);
		errmsg[actualmsglen] = '\0';
		printf ("MSG = %s\n\n",errmsg);
		goto loop;
	}
}

/*
** function: ODBC_Connect
**
** Purpose:	Allocates ODBC HENV and HDBC.
**
** Arguments:	(SQLHENV)henv    _ Pointer to environment handle
**		(SQLHDBC)hdbc    - Pointer to connection handle
**
** Returns:	RETCODE - Return status from last ODBC Function.
**
*/

RETCODE ODBC_Connect(			/* Perform Driver Connection	*/
	HENV henv,			/* ODBC Environment Handle	*/
	HDBC hdbc,			/* ODBC Connection Handle	*/
	UCHAR *dataSourceName,		/* Data Source Name		*/
	UCHAR *uid,			/* User ID			*/
	UCHAR *pwd,			/* User Password		*/
  int   maxretry,
	UCHAR *opt1,			/* User Specified Option 1	*/
	UCHAR *opt2)			/* User Specified Option 2	*/
{
	RETCODE	rc;
	int	retries;

  if(maxretry <= 0)
    maxretry = 1;
/*
** try connecting up to maxretry times
*/
	for (retries = 1; retries <= maxretry; retries++) {
		rc = SQLConnect ((SQLHDBC) hdbc, dataSourceName, SQL_NTS,
		         uid, SQL_NTS, pwd, SQL_NTS);
		if (((rc == SQL_SUCCESS) || (rc == SQL_SUCCESS_WITH_INFO)) && (opt1 != NULL)) {
			return (rc);
                } else {
			ODBC_error ((HENV)henv, (HDBC)hdbc, SQL_NULL_HSTMT);
			if(maxretry > 1)
			printf("SQLConnect: Retrying Connect.\n");
		}
	}
/*
** Attempt to obtain a meaningful error as to why connect failed.
*/
	ODBC_error ((HENV)henv, (HDBC)hdbc, SQL_NULL_HSTMT);
	return (rc);
}


#if defined(NO_ODBC_V2)
/*
** function:	EnvInit ODBC 3.0
**
** Purpose:	Allocates ODBC HENV and HDBC.
**
** Arguments:	(SQLHENV)henv    _ Pointer to environment handle
**		(SQLHDBC)hdbc    - Pointer to connection handle
** Returns:	RETCODE status from ODBC Functions.
*/
RETCODE EnvInit(HENV *henv, HDBC *hdbc)
{
	RETCODE rc;

	rc = SQLAllocHandle (SQL_HANDLE_ENV, SQL_NULL_HANDLE, (SQLHENV *)henv);
	if ((rc == SQL_SUCCESS) || (rc == SQL_SUCCESS_WITH_INFO))
		{
		/* set the version of ODBC application you write */
		rc = SQLSetEnvAttr(*henv, SQL_ATTR_ODBC_VERSION,
											  (SQLPOINTER) SQL_OV_ODBC3, SQL_NTS);
		if ((rc == SQL_SUCCESS) || (rc == SQL_SUCCESS_WITH_INFO))
			{
			rc = SQLAllocHandle(SQL_HANDLE_DBC, (SQLHENV)*henv, (SQLHDBC *)hdbc);
			}
		}
	return (rc);
}

/*
** function:	EnvClose ODBC 3.0

**
** Arguments:	(SQLHENV)henv    _ environment handle
**		(SQLHDBC)hdbc    - connection to handle
*/
void EnvClose(HENV henv, HDBC hdbc)
{
	SQLDisconnect ((SQLHDBC)hdbc);
	SQLFreeHandle(SQL_HANDLE_DBC, (SQLHDBC)hdbc);
	SQLFreeHandle(SQL_HANDLE_ENV, (SQLHENV)henv);
}

#else	/* ODBC 2.0  */
/*
** function:	EnvInit
**
** Purpose:	Allocates ODBC HENV and HDBC.
**
** Arguments:	(SQLHENV)henv    _ Pointer to environment handle
**		(SQLHDBC)hdbc    - Pointer to connection handle
** Returns:	RETCODE status from ODBC Functions.
*/
RETCODE EnvInit(HENV *henv, HDBC *hdbc)
{
	RETCODE rc;

	rc = SQLAllocEnv ((SQLHENV *)henv);
	if ((rc == SQL_SUCCESS) || (rc == SQL_SUCCESS_WITH_INFO))
		rc = SQLAllocConnect ((SQLHENV)*henv, (SQLHDBC *)hdbc);
	return (rc);
}

/*
** function:	EnvClose
**
** Arguments:	(SQLHENV)henv    _ environment handle
**		(SQLHDBC)hdbc    - connection to handle
*/
void EnvClose(HENV henv, HDBC hdbc)
{
	SQLDisconnect ((SQLHDBC)hdbc);
	SQLFreeConnect ((SQLHDBC)hdbc);
	SQLFreeEnv ((SQLHENV)henv);
}
#endif

/*
** Program:	example
**
** Purpose:	To enable driver testing by allowing online queries.
**
** Written By:  Anantanarayanan Iyengar
*/
int main(int argc, char * argv[])
{
	HDBC	hdbc;
	HENV	henv;
	HSTMT	hstmt;
	RETCODE	rc;
	UCHAR	uid[UID_LEN];
	UCHAR	pwd[PWD_LEN];
	UCHAR	dataSource[DSN_LEN];
	UCHAR	sqlStatement[SQL_STATEMENT_LEN];
	UCHAR	opt1[OPT1_LEN],
		opt2[OPT2_LEN];
	SWORD  numCols = 0 ;
	SWORD 	icol ;


#if !defined (__cplusplus) && defined (hppa)
/*
** C programs must call the HP C++ Object initializer function.
*/
  _main ();
#endif

  setlocale(LC_ALL, "");


	for (icol = 0 ; icol < MAX_COLUMNS ; icol++)
	{
		memset ((void *)&dataStruct [icol], 0, sizeof (DataInfoStruct) ) ;
		memset ((void *)&infoStruct [icol], 0, sizeof (ColInfoStruct) ) ;
	}

/*
** Define Table and Driver
*/
	printf(BANNER, argv[0]);
	uid[0] = '\0';
	pwd[0] = '\0';
	opt1[0] = '\0';
	opt2[0] = '\0';

/*
** Prompt for the data source name, the user name and the password.
*/
  if(argc > 1 && *argv[1] != (char)0 )
    {
    strncpy((char *)dataSource, argv[1], DSN_LEN);
    dataSource[DSN_LEN -1] = (UCHAR)0;
    }
  else
    {
    printf ("\nEnter the data source name : ") ;
    readLine(dataSource, DSN_LEN);
    }

  if(argc > 2 )
    {
    strncpy((char *)uid, argv[2], UID_LEN);
    uid[UID_LEN-1] = (UCHAR)0;
    }
  else
    {
    printf ("\nEnter the user name        : ") ;
    readLine(uid, UID_LEN);
    }

  if(argc > 3 )
    {
    strncpy((char *)pwd, argv[3], PWD_LEN);
    pwd[PWD_LEN-1] = (UCHAR)0;
    }
  else
    {
    printf ("\nEnter the password         : ") ;
    readLine(pwd, PWD_LEN);
    }

	EnvInit (&henv, &hdbc);
	rc = ODBC_Connect ((HENV)henv, (HDBC)hdbc, dataSource, uid, pwd, MAXRETRY , opt1, opt2);
	if ((rc != SQL_SUCCESS) && (rc != SQL_SUCCESS_WITH_INFO))
    {
		EnvClose ((HENV)henv, (HDBC)hdbc);
    exit(255);	/* Exit with failure */
    }
/*
** Allocate a HSTMT to communicate with ODBC DB Driver.
*/
#if defined(NO_ODBC_V2)
	rc = SQLAllocHandle(SQL_HANDLE_STMT, (SQLHDBC)hdbc, (SQLHSTMT *)&hstmt);
#else /* odbc 2.0 */
	rc = SQLAllocStmt ((SQLHDBC)hdbc, (SQLHSTMT *)&hstmt);
#endif
	if ((rc != SQL_SUCCESS) && (rc != SQL_SUCCESS_WITH_INFO)) {
		ODBC_error ((HENV)henv, (HDBC)hdbc, (HSTMT)hstmt);
		EnvClose ((HENV)henv, (HDBC)hdbc);
		exit (255);
	}

/*
** Start the infinite loop for accepting statements from the user
*/
	while (TRUE)
	{
		printf ("\nEnter SQL statements (Press ENTER to QUIT)\n") ;
		printf("SQL> ");
		readLine(sqlStatement, SQL_STATEMENT_LEN) ;
		if (strlen ((char *)sqlStatement) == 0)
		{
			printf ("Exiting from the Example ODBC program\n") ;
			break ;
		}
/*
** Since the SQL statements would be typed online, here SQLPrepare is
** not required. So we can directly use the SQLExecDirect function
*/
		rc = SQLExecDirect ((SQLHSTMT)hstmt, sqlStatement, SQL_NTS) ;
		if ((rc != SQL_SUCCESS) && (rc != SQL_SUCCESS_WITH_INFO))
		{
			ODBC_error ((HENV)henv, (HDBC)hdbc, (HSTMT)hstmt) ;
			SQLFreeStmt ((SQLHSTMT)hstmt, SQL_CLOSE) ;
			continue ;
		}

/*
** We use SQLNumResultCols to return the number of columns in the
** result set. If the number of result columns is 0 then it can be safely
** assumed that the statement entered by the user was not a select statement
*/
		numCols = 0 ;
		rc = SQLNumResultCols ( (SQLHSTMT)hstmt,
					(SWORD FAR *)&numCols) ;
		if ((rc != SQL_SUCCESS) && (rc != SQL_SUCCESS_WITH_INFO))
		{
			ODBC_error ((HENV)henv, (HDBC)hdbc, (HSTMT)hstmt) ;
			SQLFreeStmt ((SQLHSTMT)hstmt, SQL_CLOSE) ;
			continue ;
		}
/* Not a result set */
		if (numCols == 0)
			continue ;
		printf ("\n") ;
		for (icol = 0 ; icol < numCols ; icol ++)
		{
			rc = SQLDescribeCol ( (SQLHSTMT)hstmt,
				(UWORD) (icol + 1),
				(UCHAR FAR *) infoStruct[icol].szColName,
				(SWORD) COL_NAME_LEN,
				(SWORD FAR *) &infoStruct[icol].cbColName,
				(SWORD FAR *) &infoStruct[icol].fSqlType,
				(SQLULEN FAR *)&infoStruct[icol].cbColDef,
				(SWORD FAR *) &infoStruct[icol].ibScale,
				(SWORD FAR *) &infoStruct[icol].fNullable) ;
			if ((rc != SQL_SUCCESS) &&
				(rc != SQL_SUCCESS_WITH_INFO))
			{
				ODBC_error ((HENV)henv, (HDBC)hdbc, (HSTMT)hstmt) ;
				break ;
			}
			rc = BindColumns ((SQLHSTMT)hstmt,
				(ColInfoStruct *)&infoStruct[icol],
				(DataInfoStruct *)&dataStruct [icol],
				(SWORD)icol) ;
			if ((rc != SQL_SUCCESS) &&
				(rc != SQL_SUCCESS_WITH_INFO))
			{
				ODBC_error ((HENV)henv, (HDBC)hdbc, (HSTMT)hstmt) ;
				break ;
			}
			printf ("%-*s",
					(infoStruct[icol].cbColName + COLUMN_SEPERATOR_OFFSET),
					  infoStruct[icol].szColName) ;
		}
		rc = DisplayResults ((SQLHSTMT)hstmt, numCols) ;
		if ((rc != SQL_SUCCESS) &&
			(rc != SQL_SUCCESS_WITH_INFO))
		{
			ODBC_error ((HENV)henv, (HDBC)hdbc, (HSTMT)hstmt) ;
			SQLFreeStmt ((SQLHSTMT)hstmt, SQL_CLOSE) ;
			continue ;
		}
/*
** Unbind all the columns which were bound earlier before calling SQLFreeStmt
** with the SQL_CLOSE option
*/
		SQLFreeStmt ((SQLHSTMT)hstmt, SQL_UNBIND) ;
		SQLFreeStmt ((SQLHSTMT)hstmt, SQL_CLOSE) ;

/*
** Before continuing the process again close any open cursors on the
** statement handle. This is done by the SQLFreeStmt with the SQL_CLOSE
** option
*/
	}

	rc = SQLFreeStmt ((SQLHSTMT)hstmt, SQL_UNBIND);
	EnvClose((HENV)henv, (HDBC)hdbc);

   return(0);
}

/*
** function: BindColumns
**
** Purpose : Binds the buffers to the proper columns specified by the column no
**
** Arguments:	SQLHSTMT hstmt  _ The statement handle
**		ColInfoStruct *colInfo - Pointer to the ColInfoStruct
**		DataInfoStruct *colInfo - Pointer to the DataInfoStruct
**		SWORD icol - The current column number
**
** Returns:	RETCODE - Return status from last ODBC Function.
**
*/
RETCODE BindColumns (SQLHSTMT hstmt, ColInfoStruct *colInfo,
			DataInfoStruct *dataInfo, SWORD icol)
{
	SWORD fCType ;
	RETCODE rc ;
	SQLLEN FAR *colDisplaySize = &dataInfo->length;

	fCType = SQL_C_CHAR ;

	rc = SQLBindCol ( (SQLHSTMT)hstmt,
			  (UWORD) (icol + 1),
			  (SWORD) fCType,
			  (PTR) &(dataInfo->charCol[0]),
			  (SQLLEN) 255,
			  (SQLLEN FAR *) colDisplaySize ) ;
/*
** Get the column display size by using the SQLColAttributes funtion
*/
	if (rc == SQL_SUCCESS || rc == SQL_SUCCESS_WITH_INFO)
	{
 #if defined(NO_ODBC_V2)
		rc = SQLColAttribute ((SQLHSTMT)hstmt,
					(UWORD) (icol + 1),
					SQL_DESC_DISPLAY_SIZE,
					NULL, 0, NULL,
					(SQLLEN FAR *)colDisplaySize ) ;
#else
		rc = SQLColAttributes ((SQLHSTMT)hstmt,
					(UWORD) (icol + 1),
					SQL_COLUMN_DISPLAY_SIZE,
					NULL, 0, NULL,
					(SQLLEN FAR *)colDisplaySize ) ;
#endif		
		if (*colDisplaySize > (SDWORD) MAX_DISPLAY_SIZE)
			*colDisplaySize = (SDWORD) MAX_DISPLAY_SIZE ;

	}
	return rc ;
}

/*
** function: DisplayResults
**
** Purpose : Displays the results returned by SQLFetch
**
** Arguments:	SQLHSTMT hstmt  _ The statement handle
**		SWORD hdbc      - The total no of columns
**
** Returns:	RETCODE - Return status from last ODBC Function.
**
*/
RETCODE DisplayResults (SQLHSTMT hstmt, SWORD noOfColumns)
{
	RETCODE rc ;
	int index = 0 ;

	printf ("\n") ;

	while (TRUE)
	{
		index = 0 ;
		rc = SQLFetch(hstmt) ;
		if (rc != SQL_SUCCESS && rc != SQL_SUCCESS_WITH_INFO )
			break ;
		while (index < noOfColumns)
		{
			if (dataStruct [index].charCol == NULL ||
			    dataStruct [index].charCol[0] == '\0' ||
			    dataStruct [index].charCol[0] == ' ')
			{
				dataStruct[index].length =
						infoStruct[index].cbColName  +
							COLUMN_SEPERATOR_OFFSET ;
				strcpy ((char *)dataStruct[index].charCol, "NULL") ;
			}
/*
** Check the display length of the value. If it is lesser than the column name
** length added to the column seperator length, then display the value left
** aligned by the proper length.
*/
			if (dataStruct[index].length <
					(infoStruct[index].cbColName +
				         COLUMN_SEPERATOR_OFFSET) )
			{
				printf ("%-*s", (infoStruct[index].cbColName
						+ COLUMN_SEPERATOR_OFFSET) ,
						dataStruct[index].charCol) ;
			}
			else
			{
				printf ("%-*s", dataStruct[index].length,
						dataStruct[index].charCol ) ;
			}
			index ++ ;
		}
		printf ("\n") ;
	}

	printf ("\n") ;

	if (rc == SQL_NO_DATA_FOUND)
		return SQL_SUCCESS ;
	return rc ;
}
