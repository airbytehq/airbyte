/*
** Copyright 2013-2016 Progress Software Corporation. All rights reserved
*/

/*
** File:	bulk.c
**
** Purpose:	To demonstrate the bulk export, load, and validate operations.
*/

#ifdef __cplusplus
extern "C" {
#endif

#if defined (WIN32) || defined (WIN64)
#include <windows.h>
#define strcasecmp _stricmp

#elif defined (hpux)
#else
#include <dlfcn.h>
#endif



#include <stdlib.h>
#include <memory.h>
#include <string.h>
#include <stdio.h>
#include <locale.h>
#include <sqlext.h>
#include <qesqlext.h>

#ifdef __cplusplus
}
#endif


/*
** Define Some useful defines
*/
#ifndef NULL
#define	NULL	0
#endif

/* Reads a line from stdin, without the trailing newline-char */
#define readLine(buf,size) { fgets((char *)buf, size, stdin); buf[strlen((const char*)buf)-1]='\0'; }


/* Get the address of a routine in a shared library or DLL. */
void * resolveName (
	HMODULE		hmod,
	const char 	*name)
{
#if defined (WIN32) || defined (WIN64)

	return GetProcAddress (hmod, name);
#elif defined (hpux)
	void	*routine = shl_findsym (hmod, name);

	shl_findsym (hmod, name, TYPE_PROCEDURE, &routine);

	return routine;
#else
	return dlsym (hmod, name);
#endif
}

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
	UCHAR		sqlstate[10];
	UCHAR		errmsg[SQL_MAX_MESSAGE_LENGTH];
	SDWORD		nativeerr;
	SWORD		actualmsglen;
	RETCODE		rc;
	SQLHANDLE	handle;
	SQLSMALLINT	handleType, i;

	if (hstmt != SQL_NULL_HSTMT) {
		handleType = SQL_HANDLE_STMT;
		handle = hstmt;
	}
	else if (hdbc != SQL_NULL_HDBC) {
		handleType = SQL_HANDLE_DBC;
		handle = hdbc;
	}
	else if (henv != SQL_NULL_HENV) {
		handleType = SQL_HANDLE_ENV;
		handle = henv;
	}
	else {
		printf ("No valid handle!\n");
		return;
	}

	i = 1;
loop:  	rc = SQLGetDiagRec (handleType, handle, i++,
		sqlstate, &nativeerr, errmsg,
		SQL_MAX_MESSAGE_LENGTH - 1, &actualmsglen);

	if (rc == SQL_ERROR) {
		printf ("SQLGetDiagRec failed!\n");
		return;
	}

	if (rc == SQL_NO_DATA_FOUND) return;

	printf ("SQLSTATE = %s\n",sqlstate);
	printf ("NATIVE ERROR = %d\n",nativeerr);
	errmsg[actualmsglen] = '\0';
	printf ("MSG = %s\n\n",errmsg);
	goto loop;
}



/* Get errors directly from the driver's connection handle. */
void driverError (void *driverHandle, HMODULE hmod)
{
	UCHAR           sqlstate[16];
	UCHAR           errmsg[SQL_MAX_MESSAGE_LENGTH * 2];
	SDWORD          nativeerr;
	SWORD           actualmsglen;
	RETCODE         rc;
	SQLSMALLINT     i;
	PGetBulkDiagRec getBulkDiagRec;

	getBulkDiagRec = (PGetBulkDiagRec)
		resolveName (hmod, "GetBulkDiagRec");

	if (! getBulkDiagRec) {
		printf ("Cannot find GetBulkDiagRec!\n");
		return;
	}


	i = 1;
loop:  	rc = (*getBulkDiagRec) (SQL_HANDLE_DBC,
		driverHandle, i++,
		sqlstate, &nativeerr, errmsg,
		SQL_MAX_MESSAGE_LENGTH - 1, &actualmsglen);

	if (rc == SQL_ERROR) {
		printf ("GetBulkDiagRec failed!\n");
		return;
	}

	if (rc == SQL_NO_DATA_FOUND) return;

	printf ("SQLSTATE = %s\n", sqlstate);
	printf ("NATIVE ERROR = %d\n", nativeerr);
	errmsg[actualmsglen] = '\0';
	printf ("MSG = %s\n\n", errmsg);
	goto loop;
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
	HENV	henv,			/* ODBC Environment Handle	*/
	HDBC	hdbc,			/* ODBC Connection Handle	*/
	char	*connectionString)	/* Connection String		*/
{
	RETCODE		rc;
	SQLCHAR		connStrOut[2048];
	SQLSMALLINT	connStrOutLen;

	rc = SQLDriverConnect (hdbc, NULL,
		(SQLCHAR *) connectionString, SQL_NTS,
		connStrOut, sizeof (connStrOut), &connStrOutLen,
		SQL_DRIVER_NOPROMPT);
	ODBC_error (SQL_NULL_HENV, hdbc, SQL_NULL_HSTMT);
	return rc;
}

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

	rc = SQLAllocHandle (SQL_HANDLE_ENV, SQL_NULL_HANDLE, henv);
	if ((rc == SQL_SUCCESS) || (rc == SQL_SUCCESS_WITH_INFO))
		rc = SQLSetEnvAttr (*henv, SQL_ATTR_ODBC_VERSION,
			(SQLPOINTER) SQL_OV_ODBC3, SQL_IS_INTEGER);
	if ((rc == SQL_SUCCESS) || (rc == SQL_SUCCESS_WITH_INFO))
		rc = SQLAllocHandle (SQL_HANDLE_DBC, *henv, hdbc);
	return rc;
}

/*
** function:	EnvClose
**
** Arguments:	(SQLHENV)henv    _ environment handle
**		(SQLHDBC)hdbc    - connection to handle
*/
void EnvClose(HENV henv, HDBC hdbc)
{
	SQLDisconnect (hdbc);
	SQLFreeHandle (SQL_HANDLE_DBC, hdbc);
	SQLFreeHandle (SQL_HANDLE_ENV, henv);
}

/*
** Program:	bulk
**
** Purpose:	To illustrate usage of bulk export, load, and validate.
**
** Written By:  John Hobson
*/
int main(int argc, char * argv[])
{
	HDBC	hdbc;
	HENV	henv;
	RETCODE	rc;
	char	operation[64];
	BOOL	bFirstTime = 1;

#if !defined (__cplusplus) && defined (hppa)
/*
** C programs must call the HP C++ Object initializer function.
*/
	_main ();
#endif
	if (argc < 2) {
		printf ("%s <connection string>\n", argv[0]);
		return 0;
	}

/* This is make sure that OS string functions work correctly with DBCS */
	setlocale(LC_ALL,"");

/*
** Define Table and Driver
*/
	printf("%s Progress Software Corporation Bulk Operations Example\n", argv[0]);

	rc = EnvInit (&henv, &hdbc);
	if (rc != SQL_SUCCESS) {
		printf ("Failed to allocate handles (%d).\n", rc);
		exit (255);
	}
	rc = ODBC_Connect (henv, hdbc, argv[1]);
	if ((rc != SQL_SUCCESS) && (rc != SQL_SUCCESS_WITH_INFO))
		exit(255);	/* Exit with failure */
/*
** Start the infinite loop for accepting statements from the user
*/
	while (1)
	{
		void	*driverHandle;
		HMODULE	hmod;

		char	tableName[128];
		char	fileName[512];
		char	configFile[512];
		char	logFile[512];
		char	discardFile[512];
		char	tmp[512];
		int	errorTolerance;
		int	warningTolerance;
		int	loadStart;
		int	loadCount;
		int	readBufferSize;
		int	codePage;
		char	*p;
		char	messageList[10240];
		SQLLEN	numMessages;

		printf("Operation: export, load, validate, or <ENTER> to quit\n> ");
		readLine(operation, sizeof (operation)) ;
		if (strlen (operation) == 0)
		{
			printf ("Exiting\n") ;
			break ;
		}

/* Get the driver's connection handle from the DM.
   This handle must be used when calling directly into the driver. */

		rc = SQLGetInfo (hdbc, SQL_DRIVER_HDBC, &driverHandle, 0, NULL);
		if (rc != SQL_SUCCESS) {
			ODBC_error (henv, hdbc, SQL_NULL_HSTMT);
			EnvClose (henv, hdbc);
			exit (255);
		}

/* Get the DM's shared library or DLL handle to the driver. */

		rc = SQLGetInfo (hdbc, SQL_DRIVER_HLIB, &hmod, 0, NULL);
		if (rc != SQL_SUCCESS) {
			ODBC_error (henv, hdbc, SQL_NULL_HSTMT);
			EnvClose (henv, hdbc);
			exit (255);
		}

		if (bFirstTime) {
			printf ("Use <ENTER> to use the default value.\n");
			printf ("Enter NONE (case-insensitive) to omit a file default.\n");
			bFirstTime = 0;
		}

		if (! strcasecmp (operation, "export")) {
			PExportTableToFile	exportTableToFile;

			exportTableToFile = (PExportTableToFile)
				resolveName (hmod, "ExportTableToFile");
			if (! exportTableToFile) {
				printf ("Cannot find ExportTableToFile!\n");
				continue;
			}

			printf ("Table name> ");
			readLine (tableName, sizeof (tableName));

			strcpy (fileName, tableName);
			strcat (fileName, ".csv");

			printf ("File name (%s)> ", fileName);
			readLine (tmp, sizeof (tmp));
			if (strlen (tmp)) {
				strcpy (fileName, tmp);
			}

#if defined (_WIN32) || defined (_WIN64)

			codePage = GetACP ();
			if ((codePage <= 1258) && (codePage >= 1250)) {
				codePage += 1000;
			}
			else {
				codePage = 0;
			}
#else
			codePage = 4;
#endif
			if (codePage) {
				printf ("Code page (%d)> ", codePage);
			}
			else {
				printf ("Code page> ");
			}
			readLine (tmp, sizeof (tmp));
			if ((codePage == 0) || strlen (tmp)) {
				codePage = atoi (tmp);
			}

			printf ("Error tolerance (-1)> ");
			readLine (tmp, sizeof (tmp));
			if (strlen (tmp)) {
				errorTolerance = atoi (tmp);
			}
			else {
				errorTolerance = -1;
			}
			printf ("Warning tolerance (-1)> ");
			readLine (tmp, sizeof (tmp));
			if (strlen (tmp)) {
				warningTolerance = atoi (tmp);
			}
			else {
				warningTolerance = -1;
			}

			strcpy (logFile, fileName);
			p = strstr (fileName, ".csv");
			if (p && (! strcmp (p, ".csv"))) {
				logFile[p - fileName] = 0;
			}
			strcat (logFile, ".log");

			printf ("Log file (%s)> ", logFile);
			readLine (tmp, sizeof (tmp));
			if (strlen (tmp)) {
				if (! strcasecmp (tmp, "none")) {
					logFile[0] = 0;
				}
				else {
					strcpy (logFile, tmp);
				}
			}

			rc = (*exportTableToFile) (
				driverHandle,
				(const SQLCHAR *) tableName,
				(const SQLCHAR *) fileName,
				codePage,
				errorTolerance, warningTolerance,
				(const SQLCHAR *) logFile);
			if (rc == SQL_SUCCESS) {
				printf ("Export succeeded.\n");
			}
			else {
				driverError (driverHandle, hmod);
			}
		}
		else if (! strcasecmp (operation, "load")) {
			PLoadTableFromFile	loadTableFromFile;

			loadTableFromFile = (PLoadTableFromFile)
				resolveName (hmod, "LoadTableFromFile");
			if (! loadTableFromFile) {
				printf ("Cannot find LoadTableFromFile!\n");
				continue;
			}

			printf ("Table name> ");
			readLine (tableName, sizeof (tableName));

			strcpy (fileName, tableName);
			strcat (fileName, ".csv");
			printf ("File name (%s)> ", fileName);
			readLine (tmp, sizeof (tmp));
			if (strlen (tmp)) {
				strcpy (fileName, tmp);
			}

			printf ("Error tolerance (-1)> ");
			readLine (tmp, sizeof (tmp));
			if (strlen (tmp)) {
				errorTolerance = atoi (tmp);
			}
			else {
				errorTolerance = -1;
			}
			printf ("Warning tolerance (-1)> ");
			readLine (tmp, sizeof (tmp));
			if (strlen (tmp)) {
				warningTolerance = atoi (tmp);
			}
			else {
				warningTolerance = -1;
			}

			strcpy (configFile, fileName);
			p = strstr (fileName, ".csv");
			if (p && (! strcmp (p, ".csv"))) {
				configFile[p - fileName] = 0;
			}
			strcat (configFile, ".xml");

			printf ("Config file (%s)> ", configFile);
			readLine (tmp, sizeof (tmp));
			if (strlen (tmp)) {
				if (! strcasecmp (tmp, "none")) {
					configFile[0] = 0;
				}
				else {
					strcpy (configFile, tmp);
				}
			}

			strcpy (logFile, fileName);
			p = strstr (fileName, ".csv");
			if (p && (! strcmp (p, ".csv"))) {
				logFile[p - fileName] = 0;
			}
			strcat (logFile, ".log");

			printf ("Log file (%s)> ", logFile);
			readLine (tmp, sizeof (tmp));
			if (strlen (tmp)) {
				if (! strcasecmp (tmp, "none")) {
					logFile[0] = 0;
				}
				else {
					strcpy (logFile, tmp);
				}
			}

			printf ("Discard file> ");
			readLine (discardFile, sizeof (discardFile));
			printf ("Load start (1)> ");
			readLine (tmp, sizeof (tmp));
			if (strlen (tmp)) {
				loadStart = atoi (tmp);
			}
			else {
				loadStart = 1;
			}
			printf ("Load count (2GB)> ");
			readLine (tmp, sizeof (tmp));
			if (strlen (tmp)) {
				loadCount = atoi (tmp);
			}
			else {
				loadCount = 0x7fffffff;
			}
			printf ("Read buffer size in KB (2048 == 2MB)> ");
			readLine (tmp, sizeof (tmp));
			if (strlen (tmp)) {
				readBufferSize = atoi (tmp);
			}
			else {
				readBufferSize = 2048;
			}

			rc = (*loadTableFromFile) (
				driverHandle,
				(const SQLCHAR *) tableName,
				(const SQLCHAR *) fileName,
				errorTolerance, warningTolerance,
				(const SQLCHAR *) configFile,
				(const SQLCHAR *) logFile,
				(const SQLCHAR *) discardFile,
				loadStart, loadCount,
				readBufferSize);
			if (rc == SQL_SUCCESS) {
				printf ("Load succeeded.\n");
			}
			else {
				driverError (driverHandle, hmod);
			}
		}
		else if (! strcasecmp (operation, "validate")) {
			PValidateTableFromFile	validateTableFromFile;

			validateTableFromFile = (PValidateTableFromFile)
				resolveName (hmod, "ValidateTableFromFile");
			if (! validateTableFromFile) {
				printf ("Cannot find ValidateTableFromFile!\n");
				continue;
			}

			printf ("Table name> ");
			readLine (tableName, sizeof (tableName));

			strcpy (configFile, tableName);
			strcat (configFile, ".xml");
			printf ("Config file (%s)> ", configFile);
			readLine (tmp, sizeof (tmp));
			if (strlen (tmp)) {
				strcpy (configFile, tmp);
			}

			messageList[0] = 0;
			numMessages = 0;

			rc = (*validateTableFromFile) (
				driverHandle,
				(const SQLCHAR *) tableName,
				(const SQLCHAR *) configFile,
				(SQLCHAR *) messageList,
				sizeof (messageList),
				&numMessages);
			printf ("%ld message%s%s\n", numMessages,
				(numMessages == 0) ? "s" :
				((numMessages == 1) ? " : " : "s : "),
				(numMessages > 0) ? messageList : "");
			if (rc == SQL_SUCCESS) {
				printf ("Validate succeeded.\n");
			}
			else {
				driverError (driverHandle, hmod);
			}
		}
	}

	EnvClose(henv, hdbc);

	return 0;
}
