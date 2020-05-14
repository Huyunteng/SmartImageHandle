import requests
import json


def MesApiPost(MachineCode, MachineData):
    try:
        data = '{"ApiType": "EquipmentViewController","Parameters": [{"Value":"' + MachineCode + '"},{"Value":' + json.dumps(
            MachineData) + '}],"Method":"DasByImage","Context": {"InvOrgId": 321}}'
        jsondate = json.loads(data)
        response = requests.post(
            "http://localhost:8080/Server.svc/api/invoke", json=jsondate)
        print(response.text)
    except Exception as err:
        print(str(err))
    else:
        print('上传成功')
