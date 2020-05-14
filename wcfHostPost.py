from suds.client import Client
import json


def WcfPost(Machinecode, MachineData,host):
    # wcf地址
    # http: // localhost: 62970 / HostServices.svc
    client = Client(host)
    # print(client)
    # 查看可调用的wcf方法
    # print client  # 结果看图1
    # 调用wcf方法
    result = client.service.GetData()
    response = client.service.DasByImage(Machinecode, json.dumps(MachineData))
    return response

