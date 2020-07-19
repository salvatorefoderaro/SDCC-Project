import json

def jsonDict():

    dict = {}
    jsonDict = {'list':[]}
    singleDict = {}

    dict['x'] = []
    dict['x'].append({'id':1, 'ip':2, 'status':3, 'name':'a', 'groupName':'b'})
    dict['x'].append({'id':3, 'ip':2, 'status':3, 'name':'a', 'groupName':'b'})



    dict['y'] = []
    dict['y'].append({'id':2, 'ip':3, 'status':4, 'name':'a', 'groupName':'b'})

    for i in dict:
        if i != 'list':
            singleDict = {'groupName':i, 'devicesList':dict[i]}
            jsonDict['list'].append(singleDict)
        
    json_data = json.dumps(jsonDict)
    print(json_data)

    data  = json.loads(json_data)
    print(data['list'])
    for i in range (0, len(data['list'])):
        print(data['list'][i]['groupName'])
        for j in range (0, len(data['list'][i]['devicesList'])):
            print(data['list'][i]['devicesList'][j])

    


if __name__ == "__main__":
    jsonDict()
