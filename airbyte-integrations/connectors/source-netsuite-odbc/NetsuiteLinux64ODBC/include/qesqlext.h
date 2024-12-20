/*
** QESQLEXT.H - This is the include file for applications using
**              the Progress DataDirect ODBC Extensions
**
** (C) Copyright 1993-2012 By Progress Software Corporation.
** All Rights Reserved.
*/

#ifndef __QESQLEXT
#define __QESQLEXT

/* DataDirect Technologies' SQL_GRAPHIC datatype extensions  */
#define SQL_GRAPHIC             (-95)
#define SQL_VARGRAPHIC          (-96)
#define SQL_LONGVARGRAPHIC      (-97)

/* DataDirect Technologies' SQLColAttributes extensions (1900 to 1949) */

#define SQL_COLATTR_START				1901

#define SQL_COLUMN_FULL_NAME			(SQL_COLATTR_START+0)
/* SQLBase - get fully qualified column name */

#define SQL_COLUMN_SEARCHABLE_COFC		(SQL_COLATTR_START+1)
/* Is column usable in a where clause for emulating current of cursor */

/*	SQL_DESC_DBMS_CODEPAGE
	Returns the CCSID of the associated column on the DB2 database.  
*/
#define SQL_DESC_DBMS_CODEPAGE			(SQL_COLATTR_START+2)

#define SQL_COLATTR_END					(SQL_COLATTR_START+2)


/* DataDirect Technologies' SQLSetConnectOption extensions (1040 to 1139) */

#define SQL_CONOPT_START				1040

#define SQL_TXN_CURSOR_STABILITY		(SQL_CONOPT_START+0)
#define SQL_ATTR_TXN_CURSOR_STABILITY	SQL_TXN_CURSOR_STABILITY
/* Set isolation level to SQL_TXN_READ_COMMITTED with the extra ability of
 * having a position lock on SELECTed rows.  In SQLBase, this is the
 * difference between RL and CS isolation levels.
 */

#define SQL_LIC_FILE_NAME				(SQL_CONOPT_START+1)
#define SQL_ATTR_LIC_FILE_NAME			SQL_LIC_FILE_NAME
/* Pass the name of the License file to use. */

#define SQL_LIC_FILE_PASSWORD			(SQL_CONOPT_START+2)
#define SQL_ATTR_LIC_FILE_PASSWORD		SQL_LIC_FILE_PASSWORD
/* Pass the password for the License file. */

#define SQL_MODIFY_SQL					(SQL_CONOPT_START+3)
#define SQL_ATTR_MODIFY_SQL				SQL_MODIFY_SQL
/* Alter the value of the ModifySql connection option. */

#define SQL_PROMPT_SETUP_DIALOG			(SQL_CONOPT_START+4)
#define SQL_ATTR_PROMPT_SETUP_DIALOG	SQL_PROMPT_SETUP_DIALOG
/* Prompt the driver's setup dialog box. */

#define SQL_CREATE_TYPE					(SQL_CONOPT_START+5)
#define SQL_ATTR_CREATE_TYPE			SQL_CREATE_TYPE
/* Pass NULL terminated string with create type specified. */

#define SQL_LIC_FILE_INI				(SQL_CONOPT_START+6)
#define SQL_ATTR_LIC_FILE_INI			SQL_LIC_FILE_INI
/* Get the license file password from ISODBC.INI
 * This avoids the thunking problem
 */

/* SequeLink-specific connection options */

#define SQL_SQLNK_DATADICTIONARY				(SQL_CONOPT_START+7)
#define SQL_SQLNK_DATADICTIONARYSCHEMA			(SQL_CONOPT_START+8)
#define SQL_SQLNK_DATADICTIONARYCATALOG			(SQL_CONOPT_START+9)
#define SQL_SQLNK_SERVERCOREVERSION				(SQL_CONOPT_START+10)
#define SQL_SQLNK_SERVERSERVICEVERSION			(SQL_CONOPT_START+11)
#define SQL_SQLNK_OEMID							(SQL_CONOPT_START+12)
#define SQL_SQLNK_APPID							(SQL_CONOPT_START+13)
#define SQL_SQLNK_AUTOMATICAPPID				(SQL_CONOPT_START+14)

#define SQL_ATTR_SQLNK_DATADICTIONARY			SQL_SQLNK_DATADICTIONARY
#define SQL_ATTR_SQLNK_DATADICTIONARYSCHEMA		SQL_SQLNK_DATADICTIONARYSCHEMA
#define SQL_ATTR_SQLNK_DATADICTIONARYCATALOG	SQL_SQLNK_DATADICTIONARYCATALOG
#define SQL_ATTR_SQLNK_SERVERCOREVERSION		SQL_SQLNK_SERVERCOREVERSION
#define SQL_ATTR_SQLNK_SERVERSERVICEVERSION		SQL_SQLNK_SERVERSERVICEVERSION
#define SQL_ATTR_SQLNK_OEMID					SQL_SQLNK_OEMID
#define SQL_ATTR_SQLNK_APPID					SQL_SQLNK_APPID
#define SQL_ATTR_SQLNK_AUTOMATICAPPID			SQL_SQLNK_AUTOMATICAPPID

#define SQL_FMP_INDEX_EMULATION					(SQL_CONOPT_START+20)
#define SQL_ATTR_FMP_INDEX_EMULATION			SQL_FMP_INDEX_EMULATION
/* Used to turn index eumulation on/off for FileMaker driver.
 * Set to 0 for off, 15 to turn emulation on for all types.
 */


/* DataDirect Proprietary Connection/Env Attributes. */
#define SQL_ATTR_APP_WCHAR_TYPE					(SQL_CONOPT_START+21)
#define SQL_ATTR_DBMS_CODE_PAGE					(SQL_CONOPT_START+22)

#define SQL_DD_CP_ANSI				0
#define SQL_DD_CP_UCS2				1
#define SQL_DD_CP_UTF8				2
#define SQL_DD_CP_UTF16				SQL_DD_CP_UCS2

#define SQL_ATTR_IGNORE_UNICODE_FUNCTIONS		(SQL_CONOPT_START+23)
#define SQL_ATTR_APP_UNICODE_TYPE				(SQL_CONOPT_START+24)
#define SQL_ATTR_DRIVER_UNICODE_TYPE			(SQL_CONOPT_START+25)

#define SQL_DEPRECATED_OPTION_1066				(SQL_CONOPT_START+26)
#define SQL_DEPRECATED_OPTION_1067				(SQL_CONOPT_START+27)

/* Connection Pooling Attrs */
#define SQL_ATTR_CLEAR_POOLS					(SQL_CONOPT_START+28)

/* Connection Pooling Attr Values */
#define SQL_CLEAR_CURRENT_CONN_POOL		0	/* clears the connection pool
											of the connection that is associated
											with a specific connection. */

#define SQL_CLEAR_ALL_CONN_POOL			1	/* clears all the connection pools
											associated with a specific driver
											environment handle */

/* Calling SQLSetConnectAttr(SQL_ATTR_CURRENT_USER) 
   sets the current user for the connection handle. */
#define SQL_ATTR_CURRENT_USER				(SQL_CONOPT_START+29)

#define SQL_ATTR_POOL_INFO					(SQL_CONOPT_START+30)

#define SQL_ATTR_CURRENT_EDITION			(SQL_CONOPT_START+31)

#define SQL_ATTR_CLIENT_MONITORING_ACCOUNTING_INFO	(SQL_CONOPT_START+32)
#define SQL_ATTR_CLIENT_MONITORING_ACTION			(SQL_CONOPT_START+33)
#define SQL_ATTR_CLIENT_MONITORING_APPLICATION_NAME	(SQL_CONOPT_START+34)
#define SQL_ATTR_CLIENT_MONITORING_CLIENT_HOST_NAME	(SQL_CONOPT_START+35)
#define SQL_ATTR_CLIENT_MONITORING_CLIENT_IDENTIFIER (SQL_CONOPT_START+36)
#define SQL_ATTR_CLIENT_MONITORING_CLIENT_USER		(SQL_CONOPT_START+37)
#define SQL_ATTR_CLIENT_MONITORING_MODULE			(SQL_CONOPT_START+38)
#define SQL_ATTR_CLIENT_MONITORING_PROGRAM_ID		(SQL_CONOPT_START+39)


#define SQL_CONOPT_END						(SQL_CONOPT_START+39)

#define SQL_DEPRECATED_OPTION_1139			(SQL_CONOPT_START+99)


typedef struct{
	SQLLEN		Version;				// The version of this structure

	SQLLEN		CurrentSize;			// Total size of the pool,
										// includes open ODBC connections.
	SQLLEN		ConnectionsInUse;		// # of connections in the pool that are In Use.

	SQLLEN		AvailableConnections;	// # of available connections in the pool.

	SQLLEN		MinSize;				// Min size as set through 
										// MinSize connection option.
	SQLLEN		MaxSize;				// Max size as set through
										// MaxSize connection option.
} PoolInfoStruct;




/* DataDirect Technologies SQLSetStmtOption extensions (1040 to 1139) */

#define SQL_STMTOPT_START				1040

#define SQL_INSERT_A_RECORD				(SQL_STMTOPT_START+0)
#define SQL_ATTR_INSERT_A_RECORD		SQL_INSERT_A_RECORD
/* Pass row number to insert as vParam to SQLSetStmtOption */

#define SQL_DELETE_A_RECORD				(SQL_STMTOPT_START+1)
#define SQL_ATTR_DELETE_A_RECORD		SQL_DELETE_A_RECORD
/* Pass row number to delete as vParam to SQLSetStmtOption
 * should be positioned to row before using backdoor
 */

#define SQL_PREPARE_FOR_BACKDOOR		(SQL_STMTOPT_START+2)
#define SQL_ATTR_PREPARE_FOR_BACKDOOR	SQL_PREPARE_FOR_BACKDOOR
/* Pass operation (SQL_UPDATE_RECORD or SQL_INSERT_RECORD)
 * as vParam to SQLSetStmtOption
 */

#define SQL_UPDATE_COLUMN				(SQL_STMTOPT_START+3)
#define SQL_ATTR_UPDATE_COLUMN			SQL_UPDATE_COLUMN
/* Pass a pointer to backdoor_column_info structure defined below
 * as vParam to SQLSetStmtOption
 */

#define SQL_UPDATE_A_RECORD				(SQL_STMTOPT_START+4)
#define SQL_ATTR_UPDATE_A_RECORD		SQL_UPDATE_A_RECORD
/* Pass row number to update as vParam to SQLSetStmtOption
 * should be positioned to row before using backdoor
 */

#define SQL_LOCK_A_RECORD				(SQL_STMTOPT_START+5)
#define SQL_ATTR_LOCK_A_RECORD			SQL_LOCK_A_RECORD
/* Pass row number to lock as vParam to SQLSetStmtOption
 * should be positioned to row before using backdoor
 */

#define SQL_GET_ROWCOUNT				(SQL_STMTOPT_START+7)
#define SQL_ATTR_GET_ROWCOUNT			SQL_GET_ROWCOUNT
/* The driver guesses the number of rows a SELECT will return. */

#define SQL_GET_ROWID					(SQL_STMTOPT_START+8)
#define SQL_ATTR_GET_ROWID				SQL_GET_SERIAL_VALUE
/* Get the rowid for the last row inserted */

#define SQL_GET_SERIAL_VALUE			(SQL_STMTOPT_START+9)
#define SQL_ATTR_GET_SERIAL_VALUE		SQL_GET_SERIAL_VALUE
/* Get the value for the serial column in the last row inserted  */

#define SQL_ABORT_BACKDOOR				(SQL_STMTOPT_START+10)
#define SQL_ATTR_ABORT_BACKDOOR			SQL_ABORT_BACKDOOR
/* Abort the last backdoor call.  Do the necessary clean up (e.g., free up
 * semaphores)
 */

#define SQL_GET_SESSIONID				(SQL_STMTOPT_START+11)
#define SQL_ATTR_GET_SESSIONID			SQL_GET_SESSIONID
/* Get the value of the current session id. */

#define SQL_OPT_PLAN					(SQL_STMTOPT_START+12)
#define SQL_ATTR_OPT_PLAN				SQL_OPT_PLAN
/* Get the optimization debug information */

#define SQL_PERSIST_AS_XML				(SQL_STMTOPT_START+13)
#define SQL_ATTR_PERSIST_AS_XML			SQL_PERSIST_AS_XML
/* Persist a result set as XML. */

#define SQL_PERSIST_XML_TYPE			(SQL_STMTOPT_START+14)
#define SQL_ATTR_PERSIST_XML_TYPE		SQL_PERSIST_XML_TYPE
/* Set the XML Type to persist a result set as. */

#define SQL_BULK_EXPORT					(SQL_STMTOPT_START+15)
#define SQL_ATTR_BULK_EXPORT			SQL_BULK_EXPORT
/* File name to which a statement's result set will be exported. */

#define SQL_BULK_EXPORT_PARAMS			(SQL_STMTOPT_START+16)
#define SQL_ATTR_BULK_EXPORT_PARAMS		SQL_BULK_EXPORT_PARAMS
/* Export parameters for exporting a statement's result set. */

#define SQL_ATTR_PARAM_ARRAY_ATOMIC		(SQL_STMTOPT_START+17)
/* Are parameter array executions atomic or not. */
/* If ATOMIC either all the elements of the array are processed */
/*  successfully, or none at all. (This is the default.) */
/* With NOT ATOMIC execution will continue even if an error */
/*  is detected with one of the intermediate array elements. */

/* SQL_ATTR_PARAM_ARRAY_ATOMIC Values */
#define SQL_PA_ATOMIC_YES				1
#define SQL_PA_ATOMIC_NO				0


#define SQL_STMTOPT_END					(SQL_STMTOPT_START+17)

#define SQL_DEPRECATED_OPTION_1120		(SQL_STMTOPT_START+80)


typedef struct {
	SQLLEN	Version;			/* Must be the value 1. */
	SQLLEN	IANAAppCodePage;	/* Code page for the export file. */
	SQLLEN	EnableLogging;		/* Log to <file name>.log */
	SQLLEN	ErrorTolerance;		/* How many errors are allowed before
									export quits. */
	SQLLEN	WarningTolerance;	/* How many warnings are allowed before
									export quits. */
} BulkExportParams;

#if defined (__cplusplus)
extern "C" {
#endif
typedef SQLRETURN (SQL_API *PLoadTableFromFile) (
	SQLHDBC			ConnectionHandle,	// Connection handle
	const SQLCHAR*	TableName,			// Name of table to insert into
	const SQLCHAR*	FileName,			// Name of file with data
	SQLLEN			ErrorTolerance,		// Number of errors allowed
	SQLLEN			WarningTolerance,	// Number of warnings allowed
	const SQLCHAR*	ConfigFile,			// Name of the configuration file
										//	May be NULL
	const SQLCHAR*	LogFile,			// Name of the log file
										//	May be NULL
	const SQLCHAR*	DiscardFile,		// Name of the discard file
										//	May be NULL
	SQLULEN			LoadStart,			// Start load at this row #
	SQLULEN			LoadCount,			// Number of rows to load
	SQLULEN			ReadBufferSize);	// File read size

typedef SQLRETURN (SQL_API *PLoadTableFromFileW) (
	SQLHDBC			ConnectionHandle,	// Connection handle
	const SQLWCHAR*	TableName,			// Name of table to insert into
	const SQLWCHAR*	FileName,			// Name of file with data
	SQLLEN			ErrorTolerance,		// Number of errors allowed
	SQLLEN			WarningTolerance,	// Number of warnings allowed
	const SQLWCHAR*	ConfigFile,			// Name of the configuration file
										//	May be NULL
	const SQLWCHAR*	LogFile,			// Name of the log file
										//	May be NULL
	const SQLWCHAR*	DiscardFile,		// Name of the discard file
										//	May be NULL
	SQLULEN			LoadStart,			// Start load at this row #
	SQLULEN			LoadCount,			// Number of rows to load
	SQLULEN			ReadBufferSize);	// File read size


typedef SQLRETURN (SQL_API *PValidateTableFromFile) (
	SQLHDBC			ConnectionHandle,	// Connection handle
	const SQLCHAR	*TableName,			// Name of table to export
	const SQLCHAR*	ConfigFile,			// Name of the configuration file
	SQLCHAR			*MessageList,		// Buffer for warnings/errors
	SQLLEN			MessageListSize,	// Size of MessageList, in bytes
	SQLLEN			*NumMessages);		// Number of messages returned

typedef SQLRETURN (SQL_API *PValidateTableFromFileW) (
	SQLHDBC			ConnectionHandle,	// Connection handle
	const SQLWCHAR	*TableName,			// Name of table to export
	const SQLWCHAR*	ConfigFile,			// Name of the configuration file
	SQLWCHAR		*MessageList,		// Buffer for warnings/errors
	SQLLEN			MessageListSize,	// Size of MessageList, in characters
	SQLLEN			*NumMessages);		// Number of messages returned


typedef SQLRETURN (SQL_API *PExportTableToFile) (
	SQLHDBC			ConnectionHandle,	// Connection handle
	const SQLCHAR	*TableName,			// Name of table to export
	const SQLCHAR	*FileName,			// Name of export file
	SQLINTEGER		IANAAppCodePage,	// Export file character set
	SQLLEN			ErrorTolerance,		// Error tolerance
	SQLLEN			WarningTolerance,	// Warning tolerance
	const SQLCHAR	*LogFile);			// Name of log file

typedef SQLRETURN (SQL_API *PExportTableToFileW) (
	SQLHDBC			ConnectionHandle,	// Connection handle
	const SQLWCHAR	*TableName,			// Name of table to export
	const SQLWCHAR	*FileName,			// Name of export file
	SQLLEN			IANAAppCodePage,	// Export file character set
	SQLLEN			ErrorTolerance,		// Error tolerance
	SQLLEN			WarningTolerance,	// Warning tolerance
	const SQLWCHAR	*LogFile);			// Name of log file

typedef SQLRETURN (SQL_API *PGetBulkDiagRecW) (
	SQLSMALLINT		HandleType,
	SQLHANDLE		Handle,
	SQLSMALLINT		RecNumber,
	SQLWCHAR		*Sqlstate,
	SQLINTEGER		*NativeError,
	SQLWCHAR		*MessageText,
	SQLSMALLINT		BufferLength,
	SQLSMALLINT		*TextLength);

typedef SQLRETURN (SQL_API *PGetBulkDiagRec) (
	SQLSMALLINT		HandleType,
	SQLHANDLE		Handle,
	SQLSMALLINT		RecNumber,
	SQLCHAR			*Sqlstate,
	SQLINTEGER		*NativeError,
	SQLCHAR			*MessageText,
	SQLSMALLINT		BufferLength,
	SQLSMALLINT		*TextLength);

typedef SQLRETURN (SQL_API *PGetBulkOperation) (SQLHDBC	ConnectionHandle,	// Connection handle
												SQLULEN	*pOperation);		// Bulk operation

typedef SQLRETURN (SQL_API *PSetBulkOperation) (SQLHDBC	ConnectionHandle,	// Connection handle
												SQLULEN	Operation);			// Bulk operation

#define BULK_OPERATION_INSERT 1
#define BULK_OPERATION_UPDATE 2
#define BULK_OPERATION_DELETE 3
#define BULK_OPERATION_UPSERT 4

#if defined (__cplusplus)
}
#endif


/* DataDirect Technologies' SQLGetInfo extensions (1011 to 1110) */

#define SQL_GETINF_START				1011

#define SQL_RESERVED_WORDS				(SQL_GETINF_START+0)
/* Comma separated list of reserved words.  ANSI SQL reserved words
 * are not included in this list.
 */

#define SQL_PSEUDO_COLUMNS				(SQL_GETINF_START+1)
/* Comma separated list of pseudo columns.  Combinations, such as DB2's
 * CURRENT DATE and CURRENT TIME, appear as separate multiword entries.
 */

#define SQL_FROM_RESERVED_WORDS			(SQL_GETINF_START+2)
/* Comma separated list of reserved words that can only appear in
 * the FROM clause.  SQLServer's HOLDLOCK is such an example.
 */

#define SQL_WHERE_CLAUSE_TERMINATORS	(SQL_GETINF_START+3)
/* Comma separated list of reserved words that end a WHERE clause.
 * ANSI standard words (UNION, ORDER BY, etc.) are not included.
 * Examples include Oracle's INTERSECT and CONNECT BY.
 */

#define SQL_COLUMN_FIRST_CHARS			(SQL_GETINF_START+4)
/* List of characters (other than A-Z) that are valid as the first
 * character in an unquoted column name.
 */

#define SQL_COLUMN_MIDDLE_CHARS			(SQL_GETINF_START+5)
/* List of characters (other than A-Z) that are valid as middle
 * characters in an unquoted column name.
 */

#define SQL_TABLE_FIRST_CHARS			(SQL_GETINF_START+7)
/* List of characters (other than A-Z) that are valid as the first
 * character in an unquoted table name.
 */

#define SQL_TABLE_MIDDLE_CHARS			(SQL_GETINF_START+8)
/* List of characters (other than A-Z) that are valid as middle
 * characters in an unquoted table name.
 */

#define SQL_DATADICT_EXTENSIONS			(SQL_GETINF_START+9)
/* TRUE if the driver can handle file name extensions, FALSE if it cannot.
 * The TEXT driver is an example of a driver than can nadle file name
 * extensions in SQLColumns calls.
 */

#define SQL_FAST_SPECIAL_COLUMNS		(SQL_GETINF_START+10)
/* The maximum scope which SQLSpecialColumns can return a pseudo column
 * without querying the database.  For example, the Oracle driver returns
 * "ROWID" for scopes less than or equal to SQL_SCOPE_TRANSACTION.  This
 * option applies to SQL_BEST_ROWID SQLSpecialColumns only.
 */

#define SQL_ACCESS_CONFLICTS			(SQL_GETINF_START+11)
/* TRUE if a "SELECT * FROM table" statement that has not fetched all its rows
 * may cause an "UPDATE table SET..." to hang.  In other words, SELECT
 * statements may acquire locks that cause UPDATE statements to wait forever.
 */

#define SQL_LOCKING_SYNTAX				(SQL_GETINF_START+12)
/* The words an application needs to add to a SELECT statement to make a
 * driver lock records.  This is either "FOR UPDATE OF" or "HOLDLOCK".
 */

#define SQL_LOCKING_DURATION			(SQL_GETINF_START+13)
/* How long the driver holds a record lock.  The driver returns either
 * 0 - record-level locking not supported, 1 - record is locked only while
 * positioned on it, 2 - record is locked until transaction ends.
 */

#define SQL_RECORD_OPERATIONS			(SQL_GETINF_START+14)
/* Which of the SQLSetStmtOption backdoors are supported by this driver. */
#define SQL_RECORD_DELETE   0x80000000L	/* Backdoor record delete supported */
#define SQL_RECORD_INSERT   0x40000000L	/* Backdoor record insert supported */
#define SQL_RECORD_UPDATE   0x20000000L	/* Backdoor record update supported */
#define SQL_RECORD_LOCK     0x10000000L	/* Backdoor record locking supported */
#define SQL_ROWCOUNT        0x08000000L	/* Backdoor for guessing the number of */
										/* rows a SELECT will return supported */

#define SQL_QUALIFIER_SYNTAX			(SQL_GETINF_START+15)
/* Information needed to build a table name using table qualifier. */
#define SQL_QUALIFIER_LAST	0x0001	/* Qualifier appears after table name */
#define SQL_OWNER_OPTIONAL	0x0002	/* Owner name is optional */

#define SQL_MAC_FILE_TYPE				(SQL_GETINF_START+16)
/* Macintosh file type the driver operates on. */

#define SQL_THREADING_MODEL				(SQL_GETINF_START+17)
/* Describes the driver's threading model.  An application which exceeds
 * a driver's capability may have threads blocked inside the driver. 
 */
#define SQL_THREAD_PER_STMT		0x0000	/* Threaded per statement */
#define SQL_THREAD_PER_CON		0x0001	/* Threaded per connection */
#define SQL_THREAD_PER_DRIVER	0x0002	/* Threaded per driver */

#define SQL_DEPRECATED_OPTION_1029		(SQL_GETINF_START+18)

#define SQL_GETINF_END					(SQL_GETINF_START+18)


/* DataDirect Technologies' packet for SQL_UPDATE_COLUMN */

struct BackdoorColumnInfo {
	SWORD	CType;			/* ODBC C data type of value */
	PTR		Value;			/* value */
	SDWORD	Length;			/* length of value */
							/*	(or SQL_NULL_DATA or SQL_NTS) */
	UWORD	ColNum;			/* which column (1, 2, 3, ...) */
};

/* DataDirect Technologies' packet for SQL_PREPARE_FOR_BACKDOOR */

struct BackdoorPrepareInfo {
	UWORD	BackdoorOp;		/* which operation (SQL_UPDATE_A_RECORD, */
							/*	SQL_INSERT_A_RECORD) */
	UWORD	ColNum;			/* which column (1, 2, 3, ...) */
							/*	ignored on inserts */
};

/* DataDirect Technologies' packet for SQL_PROMPT_SETUP_DIALOG */

struct BackdoorSetupDialogStruct {
	HWND		ParentWindowHandle;
	UCHAR FAR 	*FileName;	/* changed from PCU8 is an
							 * internal type.  Since this is
							 * an external file only
							 * ODBC types should be used 
							 */
};

#if defined (__cplusplus)
extern "C" {
#endif

/*  DataDirect Technologies' Version String Information function */
#if defined (_WIN32) || (_WIN64)
__declspec(dllexport)
#endif
const unsigned char * getFileVersionString ();

#if defined (_WIN32) || (_WIN64)
__declspec(dllexport)
#endif
const unsigned short * getFileVersionStringW ();

#if defined (__cplusplus)
} // extern "C"
#endif

/*----------------------------------------------------------------------*/
/* Declaration of Shadow specific SQLGetInfo values :                   */
/*----------------------------------------------------------------------*/
/* SQL_NEON_MACHINE_ID returns the Shadow Machine ID of the current     */
/*   client; this value may not be set, only gotten                     */
/*----------------------------------------------------------------------*/
#define SQL_NEON_MACHINE_ID         1227


/*----------------------------------------------------------------------*/
/* Declaration of Shadow specific Connection attributes                 */
/*----------------------------------------------------------------------*/
/* SQL_NEON_ENABLE_KEY may be used to                                   */
/*----------------------------------------------------------------------*/
#define SQL_NEON_ENABLE_KEY         1800

/*----------------------------------------------------------------------*/
/* SQL_NEON_FAILURE_INDEX may be used to retrieve the failure index     */
/*   for a block of chained operations (the failure index shows         */
/*   which operation in a block failed)                                 */
/*----------------------------------------------------------------------*/
#define SQL_NEON_FAILURE_INDEX      1850

/*----------------------------------------------------------------------*/
/*----------------------------------------------------------------------*/
#define SQL_NEON_MQ_MSGID           1851

/*----------------------------------------------------------------------*/
/* SQL_NEON_ENLIST_IN_TUXEDO is used to enlist a Shadow resource        */
/*   manager in a Tuxedo transaction                                    */
/*----------------------------------------------------------------------*/
#define SQL_NEON_ENLIST_IN_TUXEDO   1852

/*----------------------------------------------------------------------*/
/* SQL_NEON_ENLIST_IN_JTS is used to enlist a Shadow resource manager   */
/*   in a JTS coordinated transaction.                                  */
/*----------------------------------------------------------------------*/
#define SQL_NEON_ENLIST_IN_JTS      1858


/*----------------------------------------------------------------------*/
#define SQL_NEON_GENERIC_USERID     1853

/*----------------------------------------------------------------------*/
/*----------------------------------------------------------------------*/
#define SQL_NEON_EXTENDED_USERID    1854

/*----------------------------------------------------------------------*/
/*----------------------------------------------------------------------*/
#define SQL_NEON_USER_LANGUAGE_ID   1855

/*----------------------------------------------------------------------*/
/*----------------------------------------------------------------------*/
#define SQL_NEON_MAX_BUFFER_SIZE    1856

/*----------------------------------------------------------------------*/
/*----------------------------------------------------------------------*/
#define SQL_NEON_ROW_COUNT          1857

/*----------------------------------------------------------------------*/
/*  The next option is used by the JDBC driver to tell the              */
/*  ODBC driver that JDBC is active. In some cases, this                */
/*  option changes the behavior of the ODBC driver.                     */
/*----------------------------------------------------------------------*/
#define SQL_NEON_JDBC_ACTIVE        1859

/*----------------------------------------------------------------------*/
/*  The next option is to inform Shadow the next SQL operation          */
/*  will be used to handle LOB data                                     */
/*----------------------------------------------------------------------*/
#define SQL_NEON_LOB_OPERATION      1860    /* deprecated */

/*----------------------------------------------------------------------*/
/*  The next option is to inform Shadow the host functional level       */
/*----------------------------------------------------------------------*/
#define SQL_NEON_HOST_FUNCTIONAL_LEVEL  1861

/*----------------------------------------------------------------------*/
/*  The next option is used to return driver information                */
/*----------------------------------------------------------------------*/
#define SQL_NEON_DRIVER_INFO        1862

/*----------------------------------------------------------------------*/
/*  The next option is used by the JCA driver to tell the               */
/*  ODBC driver that JCA is active. In some cases, this                 */
/*  option changes the behavior of the ODBC driver.                     */
/*----------------------------------------------------------------------*/
#define SQL_NEON_JCA_ACTIVE         1863


/*----------------------------------------------------------------------*/
/*----------------------------------------------------------------------*/
#define SQL_COPT_NEON_CONNECTION_DEAD  1864  /* connection is dead?   */

/*----------------------------------------------------------------------*/
/*----------------------------------------------------------------------*/
#define SQL_NEON_DAOP_STATUS        1865  /* SQLDescribeParam sup? */

/*----------------------------------------------------------------------*/
/*----------------------------------------------------------------------*/
#define SQL_NEON_WITH_HOLD          1866  /* WITH HOLD status */

/*----------------------------------------------------------------------*/
/*----------------------------------------------------------------------*/
#define SQL_NEON_CNID               1867  /* CNID (NEON_CNID) */

/*----------------------------------------------------------------------*/
/*----------------------------------------------------------------------*/
#define SQL_NEON_VCID               1868  /* VCID (NEON_VCID) */

/*----------------------------------------------------------------------*/
/*----------------------------------------------------------------------*/
#define SQL_NEON_SERVER_VER         1869  /* Server Version/SVFX level */

/*----------------------------------------------------------------------*/
/* Declaration of Shadow specific Statement Attributes :                */
/*----------------------------------------------------------------------*/


/*----------------------------------------------------------------------*/
/* SQL[Get|Set]ConnectAttr Extended Client Information attribute values */
/*----------------------------------------------------------------------*/

#ifndef SQL_ATTR_INFO_USERID
#define SQL_ATTR_INFO_USERID         1281
#endif

#ifndef SQL_ATTR_INFO_WRKSTNNAME
#define SQL_ATTR_INFO_WRKSTNNAME     1282
#endif

#ifndef SQL_ATTR_INFO_APPLNAME
#define SQL_ATTR_INFO_APPLNAME       1283
#endif

#ifndef SQL_ATTR_INFO_ACCTSTR
#define SQL_ATTR_INFO_ACCTSTR        1284
#endif

#ifndef SQL_DYNAMIC_XA
#define SQL_DYNAMIC_XA               1285
#endif

#endif
