__author__ = "David Fernández González"
__license__ = "GPLv3+"
__version__ = "0.0.1"
__maintainer__ = "David Fernández González"
__email__ = "dfernandez.parking@gmail.com"
__status__ = "Development"
__credits__ = []

import json
from python.v30.WSClient import WSClient

ws = None

# **********************************************************************
# Update item.
#**********************************************************************
def update():
    item = ws.do_retrieve('9x000001')
    item['ticketstatus'] = 'Closed'
    print(ws.do_update(item))


#**********************************************************************
#Get related records.
#**********************************************************************
def get_related_records():
    print(ws.do_set_related('25x12368', json.dumps('17x114')))


#**********************************************************************
#Set related records.
#**********************************************************************
def set_related():
    params = json.dumps('9x257580')
    ws.do_set_related('31x266468', params)


#**********************************************************************
#Exec query.
#**********************************************************************
def query():
    result = ws.do_query("select * from helpdesk;")
    print(result)


#**********************************************************************
#Get list types
#**********************************************************************
def list_types():
    print(ws.do_listtypes)

#**********************************************************************
#Main
#**********************************************************************
if __name__ == "__main__":
    ws = WSClient("http://corebos.org/demos/corebos/")
    if ws.do_login('admin', '4qBtQX8s8RMqBgJQ'):
        print("Loggin OK")
        list_types()
        query()
        ws.logout()
