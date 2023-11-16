/*****************************************************************
** SQLUNX.H - Mappings of Windows-style declarations and typedefs
**            for unix.
**
** Copyright: 1992-2012 Progress Software Corporation.
**                      All Rights Reserved.
** This software contains confidential and proprietary
** information of Progress Software Corporation.
*********************************************************************/

#ifndef __SQLUNX
#define __SQLUNX

/* Unix versions of Wintel declaration modifiers */

#define NEAR
#define FAR
#define EXPORT
#define PASCAL
#define VOID void
#define CALLBACK
#define _cdecl
#define __stdcall

/* Windows-style typedefs */

typedef VOID * HANDLE;
typedef unsigned short WORD;
typedef unsigned int UINT;
#if defined(ODBC64)
typedef unsigned int  DWORD;
#else
typedef unsigned long DWORD;
#endif
#ifdef BYTE
#undef BYTE
#endif
typedef unsigned char BYTE;
#ifdef BOOL
#undef BOOL
#endif
typedef int BOOL;
typedef VOID * LPVOID;
typedef VOID * PVOID;
typedef VOID * HMODULE;
typedef int GLOBALHANDLE;
typedef int (*FARPROC)();
typedef char *LPSTR;
typedef const char * LPCSTR;
typedef VOID * HINSTANCE;
typedef VOID * HWND;
typedef VOID * HKEY; 
typedef VOID * PHKEY;
typedef BYTE * LPBYTE;
typedef char CHAR;
typedef BOOL * LPBOOL;
typedef DWORD * LPDWORD;

#ifdef RETCODE
#undef RETCODE
#endif

#endif
