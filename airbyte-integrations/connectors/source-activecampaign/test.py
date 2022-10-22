import json


if __name__ == '__main__':

    a = '{ "owner": "1", "contact": "39", "organization": "20", "group": "1", "stage": "2", "title": "Able Hyena", "description": "Article do skill hope.", "percent": "0", "cdate": "2019-09-06T11:29:48-05:00", "mdate": "2019-09-06T11:29:48-05:00", "nextdate": null, "nexttaskid": null, "value": "1872151", "currency": "usd", "winProbability": 44, "winProbabilityMdate": "2019-10-05T12:27:22-05:00", "status": "0", "activitycount": "1", "nextdealid": "46", "edate": "2019-11-22 14:15:37", "links": { "dealActivities": "/api/3/deals/46/dealActivities", "contact": "/api/3/deals/46/contact", "contactDeals": "/api/3/deals/46/contactDeals", "group": "/api/3/deals/46/group", "nextTask": "/api/3/deals/46/nextTask", "notes": "/api/3/deals/46/notes", "account": "/api/3/deals/46/account", "customerAccount": "/api/3/deals/46/customerAccount", "organization": "/api/3/deals/46/organization", "owner": "/api/3/deals/46/owner", "scoreValues": "/api/3/deals/46/scoreValues", "stage": "/api/3/deals/46/stage", "tasks": "api/3/deals/46/tasks", "dealCustomFieldData": "/api/3/deals/46/dealCustomFieldData" }, "id": "46", "isDisabled": false, "account": "20", "customerAccount": "20" }'

    json_1 = json.loads(a)
    

    b = '{ "id": "2", "isDisabled": 1, "title": "Demo Requested" }'

    json_2 = json.loads(b)

    print("="*20)
    print(set(json_2.keys()).difference(json_1.keys()))