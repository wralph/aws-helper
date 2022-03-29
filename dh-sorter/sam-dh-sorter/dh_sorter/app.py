import json
from multiprocessing import process
from sorter import EC2Instance 
from sorter import HostSorter 
from capacity_provider import CapacityProvider


def lambda_handler(event, context):
    # print("entering function")
    # print(context)
    # print(event)

    data = json.loads(event["body"])
    print(data)
    region = data["region"]

    x = HostSorter(region)
    for instances in data["instances"]:
        t = instances["type"]
        c = int(instances["count"])
        for i in range(c):
            x.addInstance(EC2Instance(t, CapacityProvider.getEC2Capacity(region, t)))    
    x.placeInstances()

    # x.printUsage()

    # create a result which can be serialized
    processedData = []
    for hosts in x.hosts:
        for host in x.hosts[hosts]:            
            if host.type == "t3":
                rHost = {}
                rHost["type"] = host.type
                rHost["usage"] = host.hostUsage
                instanceCount = 0
                rHost["instances"] = []
                for block in host.blocks:              
                    instanceCount = instanceCount + len(block.instances)
                    for instance in block.instances:
                        rHost["instances"].append(instance.type)                                                                    

                rHost["instanceCount"] = instanceCount
                processedData.append(rHost)
            else:
                rHost = {}
                rHost["type"] = host.type
                rHost["usage"] = host.usage
                rHost["instanceCount"] = len(host.instances)
                rHost["instances"] = []
                for instance in host.instances:
                    rHost["instances"].append(instance.type)
                processedData.append(rHost)

    print(processedData)

    returnData = {
        "statusCode": 200,
        "body": json.dumps(processedData),
    }

    print(returnData)

    return returnData
