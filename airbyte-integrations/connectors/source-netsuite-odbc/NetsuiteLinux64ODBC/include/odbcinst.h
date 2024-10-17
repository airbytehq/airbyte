/*--------------------------------------------------------------+
|  Purpose: Contains definitions of installer functions.        |
|                                                               |
|  Date: Jan 2004                                               |
|                                                               |
|  Copyright: 2004-2012 Progress Software Corporation.          |
|                       All Rights Reserved.                    |
|    This software contains confidential and proprietary        |
|    information of Progress Software Corporation.              |
|                                                               |
+--------------------------------------------------------------*/


#ifndef __ODBCINST_H
#define __ODBCINST_H

#ifndef __SQL
#include "sql.h"
#endif

#ifdef __cplusplus
extern "C" {                               /* Assume C declarations for C++ */
#endif	/* __cplusplus */

#ifndef ODBCVER
#define ODBCVER 0x0351					   /* Assume ODBC 3.51 */
#endif

#ifndef WINVER
#define  WINVER  0x0400                     /* Assume Windows 4.0 */
#endif

/* Constants ---------------------------------------------------------------
// SQLConfigDataSource request flags
*/
#define  ODBC_ADD_DSN     1               /* Add data source */
#define  ODBC_CONFIG_DSN  2               /* Configure (edit) data source */
#define  ODBC_REMOVE_DSN  3               /* Remove data source */

#if (ODBCVER >= 0x0250)
#define  ODBC_ADD_SYS_DSN 4                     /* add a system DSN */
#define  ODBC_CONFIG_SYS_DSN    5                 /* Configure a system DSN */
#define  ODBC_REMOVE_SYS_DSN    6                 /* remove a system DSN */
#if (ODBCVER >= 0x0300)
#define  ODBC_REMOVE_DEFAULT_DSN        7               /* remove the default DSN */
#endif  /* ODBCVER >= 0x0300 */

/* install request flags */
#define  ODBC_INSTALL_INQUIRY   1
#define  ODBC_INSTALL_COMPLETE  2

/* config driver flags */
#define  ODBC_INSTALL_DRIVER    1
#define  ODBC_REMOVE_DRIVER             2
#define  ODBC_CONFIG_DRIVER             3
#define  ODBC_CONFIG_DRIVER_MAX 100
#endif

/* SQLGetConfigMode and SQLSetConfigMode flags */
#if (ODBCVER >= 0x0300)
#define ODBC_BOTH_DSN           0
#define ODBC_USER_DSN           1
#define ODBC_SYSTEM_DSN         2
#endif  /* ODBCVER >= 0x0300 */

/* SQLInstallerError code */
#if (ODBCVER >= 0x0300)
#define ODBC_ERROR_GENERAL_ERR                   1
#define ODBC_ERROR_INVALID_BUFF_LEN              2
#define ODBC_ERROR_INVALID_HWND                  3
#define ODBC_ERROR_INVALID_STR                   4
#define ODBC_ERROR_INVALID_REQUEST_TYPE          5
#define ODBC_ERROR_COMPONENT_NOT_FOUND           6
#define ODBC_ERROR_INVALID_NAME                  7
#define ODBC_ERROR_INVALID_KEYWORD_VALUE         8
#define ODBC_ERROR_INVALID_DSN                   9
#define ODBC_ERROR_INVALID_INF                  10
#define ODBC_ERROR_REQUEST_FAILED               11
#define ODBC_ERROR_INVALID_PATH                 12
#define ODBC_ERROR_LOAD_LIB_FAILED              13
#define ODBC_ERROR_INVALID_PARAM_SEQUENCE       14
#define ODBC_ERROR_INVALID_LOG_FILE             15
#define ODBC_ERROR_USER_CANCELED                16
#define ODBC_ERROR_USAGE_UPDATE_FAILED          17
#define ODBC_ERROR_CREATE_DSN_FAILED            18
#define ODBC_ERROR_WRITING_SYSINFO_FAILED       19
#define ODBC_ERROR_REMOVE_DSN_FAILED            20
#define ODBC_ERROR_OUT_OF_MEM                   21
#define ODBC_ERROR_OUTPUT_STRING_TRUNCATED      22
#endif /* ODBCVER >= 0x0300 */

#ifndef EXPORT
#define EXPORT 
#endif

#ifndef RC_INVOKED
/* Prototypes -------------------------------------------------------------- */
#define INSTAPI __stdcall

BOOL INSTAPI SQLWritePrivateProfileString(LPCSTR lpszSection,
										 LPCSTR lpszEntry,
										 LPCSTR lpszString,
										 LPCSTR lpszFilename);

int  INSTAPI SQLGetPrivateProfileString( LPCSTR lpszSection,
										LPCSTR lpszEntry,
										LPCSTR lpszDefault,
										LPSTR  lpszRetBuffer,
										int    cbRetBuffer,
										LPCSTR lpszFilename);

BOOL INSTAPI SQLWriteDSNToIni( LPCSTR lpszDSN,
                                               LPCSTR lpszDriver);
BOOL SQLRemoveDSNFromIni(LPCSTR lpszDsn);
/*	Driver specific Setup APIs called by installer */
BOOL INSTAPI ConfigDSN (HWND	hwndParent,
						WORD	fRequest,
						LPCSTR	lpszDriver,
						LPCSTR	lpszAttributes);



BOOL INSTAPI SQLWriteFileDSN(LPCSTR lpszFileName,
					LPCSTR lpszAppName,
					LPCSTR lpszKeyName,
					LPCSTR lpszString);
RETCODE SQLInstallerError(WORD iError,
			DWORD * pfErrorCode,
			LPSTR lpszErrorMsg,
			WORD cbErrorMsgMax,
			WORD * pcbErrorMsgMax);

RETCODE SQLPostInstallerError(DWORD fErrorCode,
                        LPSTR szErrorMsg);
#endif /* RC_INVOKED*/

#ifdef __cplusplus
}                                    /* End of extern "C" { */
#endif	/* __cplusplus*/

#endif /* __ODBCINST_H*/
