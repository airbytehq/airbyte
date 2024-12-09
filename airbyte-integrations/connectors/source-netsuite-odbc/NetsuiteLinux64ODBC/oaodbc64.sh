LD_LIBRARY_PATH=/opt/netsuite/odbcclient/lib64${LD_LIBRARY_PATH:+":"}${LD_LIBRARY_PATH:-""}
export LD_LIBRARY_PATH
OASDK_ODBC_HOME=/opt/netsuite/odbcclient/lib64; export OASDK_ODBC_HOME
ODBCINI=/opt/netsuite/odbcclient/odbc64.ini; export ODBCINI

