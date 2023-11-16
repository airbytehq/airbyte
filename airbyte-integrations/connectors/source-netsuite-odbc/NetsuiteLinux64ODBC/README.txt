Installation Instructions
SuiteAnalytics Connect ODBC Driver for Linux
------------------------------

INSTALLATION
------------
These are instructions for installation of the NetSuite ODBC Driver for Linux after unpacking the provided NetSuiteODBCDrivers_Linux[32|64]bit.zip 


1. Read the EULA.txt file. Installing and using the NetSuite ODBC Driver for Linux signifies acceptance of this license.

2. Create a new installation directory of the following path /opt/netsuite/odbcclient. 

3. Copy the unpacked installation files to the installation directory created in the previous step.

4. Run 'source oaodbc[64].sh' or 'source oaodbc[64].csh' on the script files oaodbc[64].sh/oaodbc[64].csh. The selection should depend on your preferred shell.    


NOTE: You may also incorporate these script files into your custom .profile file.

NOTE: If you wish to install the driver into another location, please update files oaodbc[64].sh, oaodbc[64].csh, oaodbc[64].ini with the installation directory of your choice.

NOTE: If you wish to uninstall the NetSuite ODBC Driver for Linux, please remove the installation directory and if applicable update your .profile file accordingly.

NOTE: You may want to register the drivers into the system wide ODBC driver repository. In that case run 'odbcinst -i -d -f /opt/netsuite/odbcclient/odbcinst.ini'.  

NOTE: For more information please refer to NetSuite help pages.
