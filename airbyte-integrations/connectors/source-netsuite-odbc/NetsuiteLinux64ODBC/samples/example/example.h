/*
** (c) 2003-2008. Progress Software Corporation. All rights reserved
*/

/* example.h
** Contains #defines and structure definitions for the example.c program
*/

#define TRUE    1
#define FALSE   0

#define PWD_LEN         	32
#define UID_LEN         	32
#define OPT1_LEN        	255
#define OPT2_LEN        	255
#define TMPSTR_LEN      	255
#define SQL_STATEMENT_LEN 400
#define MAX_COLUMNS 		  255
#define COL_NAME_LEN    	255
#define MAX_DISPLAY_SIZE 	200
#define COLUMN_SEPERATOR_OFFSET 4
#define DSN_LEN         	32
#define PWD_MSG1 "Requested password exceeds compiled limit of %d.\n"
#define PWD_ERR1 "Password not found after keyword -pwd on command line.\n"
#define UID_MSG1 "Requested username exceeds compiled limit of %d.\n"
#define UID_ERR1 "Username not found after keyword -uid on command line.\n"
#define OPT1_ERR1 "Required value not found after keyword -opt1 on command line.\n"
#define OPT1_ERR2 "Option 1(-opt1) exceeds compiled limit of %d.\n"
#define OPT2_ERR1 "Required value not found after keyword -opt2 on command line.\n"
#define OPT2_ERR2 "Option 2(-opt2) exceeds compiled limit of %d.\n"
#define BANNER "%s Progress Software Corporation, Inc. ODBC Example Application.\n"

typedef struct 
{
	UCHAR  szColName [COL_NAME_LEN] ;
	SWORD cbColName ;
	SWORD fSqlType ;
	SQLULEN cbColDef ;
	SWORD ibScale ;
	SWORD fNullable ;
} ColInfoStruct ;

typedef struct 
{
	UCHAR charCol [255];
	SQLLEN length ;
}DataInfoStruct ;

DataInfoStruct dataStruct [MAX_COLUMNS] ;
ColInfoStruct  infoStruct [MAX_COLUMNS] ;

RETCODE BindColumns (SQLHSTMT hstmt, ColInfoStruct *colInfo, DataInfoStruct *dataInfo, SWORD icol) ;

RETCODE DisplayResults (SQLHSTMT hstmt, SWORD numCols) ;


