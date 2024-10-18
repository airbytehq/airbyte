if ($?LD_LIBRARY_PATH) then
  setenv LD_LIBRARY_PATH /opt/netsuite/odbcclient/lib64:$LD_LIBRARY_PATH
else
  setenv LD_LIBRARY_PATH /opt/netsuite/odbcclient/lib64
endif
setenv OASDK_ODBC_HOME /opt/netsuite/odbcclient/lib64
setenv ODBCINI /opt/netsuite/odbcclient/odbc64.ini

