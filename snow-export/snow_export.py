"""
- This code is provided at your own risk. 
- The author is not responsible for an actions that you do with this code. 
- The code is meant for proof-of-concept environments and is NOT production ready.
- This code is not optimized with regards to performance yet. Possible enhancements could be done using caching e.g. of the pricing API
"""

import boto3
import json
import snow_converter

# us-east-1 is where the pricing api is. Don't modify the following line
# This region does not align to the region where the target EC2 instance lives
pricing_client = boto3.client('pricing', region_name='us-east-1')
ssm_client = boto3.client('ssm')
ec2_client = boto3.resource('ec2')

def sanitize(input):
    return input.strip().lower()

PRODUCT_LINUX = "linux"
PRODUCT_WINDOWS = "windows"
PRODUCT_WINDOWSBYOL = "windowsbyol"
PRODUCT_ENTERPRISE = "enterprise"
PRODUCT_STANDARD = "standard"
PRODUCT_WEB = "web"

def interpretProductVersion(productVersion):
    switcher ={
        PRODUCT_LINUX: PRODUCT_LINUX,
        "l": PRODUCT_LINUX,
        "lin": PRODUCT_LINUX,
        PRODUCT_ENTERPRISE: PRODUCT_ENTERPRISE,
        "e": PRODUCT_ENTERPRISE,
        "ent": PRODUCT_ENTERPRISE,
        "standard": PRODUCT_STANDARD,
        "s": PRODUCT_STANDARD,
        "std": PRODUCT_STANDARD,
        PRODUCT_WINDOWS: PRODUCT_WINDOWS,
        "w": PRODUCT_WINDOWS,
        "win": PRODUCT_WINDOWS,
        PRODUCT_WINDOWSBYOL: PRODUCT_WINDOWSBYOL,
        "wb": PRODUCT_WINDOWSBYOL,
        "winBYOL": PRODUCT_WINDOWSBYOL,
        "BYOL": PRODUCT_WINDOWSBYOL,
        PRODUCT_WEB: PRODUCT_WEB,
        "wb": PRODUCT_WEB
    }
    return switcher.get(productVersion)

def getProductBillingCode(productVersion):
    productVersion = sanitize(productVersion)
    productVersion = interpretProductVersion(productVersion)
    switcher ={
        PRODUCT_LINUX: "RunInstances",
        PRODUCT_ENTERPRISE: "RunInstances:0102",
        PRODUCT_STANDARD: "RunInstances:0006",
        PRODUCT_WINDOWS: "RunInstances:0002",
        PRODUCT_WINDOWSBYOL: "RunInstances:0800",
        PRODUCT_WEB: "RunInstances:0202"
    }
    return switcher.get(productVersion)

def get_ec2_pricing_info(instance_type, platformType):    
    billingCode = getProductBillingCode(platformType)
    product_pager = pricing_client.get_paginator('get_products')    
    product_iterator = product_pager.paginate(
            ServiceCode='AmazonEC2', Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'capacityStatus', 'Value': 'Used'},
            {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': "EU (Ireland)"},
            {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
            {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
            {'Type': 'TERM_MATCH', 'Field': 'operation', 'Value': billingCode}, 
        ]
    )

    for product_item in product_iterator:
        for offer_string in product_item.get('PriceList'):
            offer = json.loads(offer_string)
            product = offer.get('product')
            product_attributes = product.get('attributes')

            ec2data = {}
            ec2data["sku"] = product['sku']
            ec2data["memory"] = product_attributes['memory']
            ec2data["vcpu"] = product_attributes['vcpu']
            ec2data["operatingSystem"] = product_attributes['operatingSystem']
            ec2data["regionCode"] = product_attributes['regionCode']
            ec2data["physicalProcessor"] = product_attributes['physicalProcessor']
            ec2data["clockSpeed"] = product_attributes['clockSpeed']
            ec2data["tenancy"] = product_attributes['tenancy']
            ec2data["processorFeatures"] = product_attributes['processorFeatures']
            ec2data["processorArchitecture"] = product_attributes['processorArchitecture']

            return ec2data

def get_ec2_instances():
    instances = []
    pager = ssm_client.get_paginator('describe_instance_information')
    iterator = pager.paginate()
    for item in iterator:
        instanceInfoList = item['InstanceInformationList']
        for info in instanceInfoList:
            instancedata = {} 
            instancedata["InstanceId"] = info['InstanceId']
            instancedata["AgentVersion"] = info['AgentVersion']
            instancedata["PlatformType"] = info['PlatformType']
            instancedata["PlatformName"] = info['PlatformName']
            instancedata["PlatformVersion"] = info['PlatformVersion']
            instancedata["IPAddress"] = info['IPAddress']
            instances.append(instancedata)

    return instances

def get_ec2_inventory(instanceIds):
    inventory = []
    pager = ssm_client.get_paginator('get_inventory')
    iterator = pager.paginate(Filters=[
            {'Type': 'Equal', 'Key': 'AWS:InstanceInformation.InstanceId', 'Values': instanceIds}            
        ], ResultAttributes = [{'TypeName': 'AWS:InstanceInformation'}])

    for item in iterator:
        print(item)
    return inventory

def get_ec2_inventory_entries(instanceId, typeName):
    inventory = []
    response = ssm_client.list_inventory_entries( InstanceId=instanceId, TypeName=typeName)
    entries = response['Entries']
    captureTime = response['CaptureTime']
    for item in entries:
        inventory.append(item)
    return inventory

def get_ec2_instance_details(instanceId):
    instance = ec2_client.Instance(instanceId)
    instancedata = {}
    instancedata['instance_type'] = instance.instance_type
    instancedata['image_id'] = instance.image_id
    instancedata['architecture'] = instance.architecture
    return instancedata

def getOSManufacturer(productVersion):
    productVersion = sanitize(productVersion)

    # This part needs to be adjusted to support other vendors 
    switcher ={
        PRODUCT_LINUX: "Amazon Inc.",
        PRODUCT_WINDOWS: "Microsoft Corporation"
    }
    return switcher.get(productVersion)    

def convertGiB2MB(memory):
    memory = memory.replace(' GiB','')    
    return int(memory) * 1024 * 1024 * 1024

instanceId = 'i-0ce10EXAMPLE'

instancedata = get_ec2_instance_details(instanceId)
ec2_instances = get_ec2_instances()
ec2_pricing_data = get_ec2_pricing_info(instancedata['instance_type'], ec2_instances[0]['PlatformType'])

# https://github.com/awsdocs/aws-systems-manager-user-guide/blob/main/doc_source/sysman-inventory-schema.md
inventoryDetailedInfo = get_ec2_inventory_entries(instanceId, 'AWS:InstanceDetailedInformation')
inventoryNetworking = get_ec2_inventory_entries(instanceId, 'AWS:Network')
inventory = get_ec2_inventory_entries(instanceId, 'AWS:Application')

snowdata={}
snowdata['hostname'] = ec2_instances[0]['InstanceId']
snowdata['clientidentifier'] = snowdata['hostname']
snowdata['site'] = "SITEIDENTIFIER" # To be aligned within Snow Software
snowdata['manufacturer'] = 'AWS'
snowdata['biosserialnumber'] = snowdata['site'] + snowdata['hostname']
snowdata['model'] = instancedata['instance_type']
snowdata['clienttype'] = ec2_pricing_data['operatingSystem'] # Types allowed = Windows, Mac OS X, Red Hat Linux, Linux, HP-UX, Solaris, AIX, ESX
snowdata['isvirtual'] = True
snowdata['hypervisorname'] = 'xen' # Use the proper hypervisor
snowdata['notebook'] = False
snowdata['ismobiledevice'] = False

snowdata['processors'] = inventoryDetailedInfo[0]['CPUCores']
snowdata['processorname'] = inventoryDetailedInfo[0]['CPUModel']
snowdata['coresperprocessor'] = inventoryDetailedInfo[0]['CPUs'] 
snowdata['processorspeed'] = inventoryDetailedInfo[0]['CPUSpeedMHz']
snowdata['processormodel'] = inventoryDetailedInfo[0]['CPUModel']
snowdata['memory'] = convertGiB2MB(ec2_pricing_data['memory'])
snowdata['ipaddress'] = inventoryNetworking[0]['IPV4']
snowdata['macaddress'] = inventoryNetworking[0]['MacAddress']
snowdata['osname'] = ec2_instances[0]['PlatformName']
snowdata['osversion'] = ec2_instances[0]['PlatformVersion']
snowdata['osbuild'] = ec2_instances[0]['PlatformVersion']
snowdata['osmanufacturer'] = getOSManufacturer(ec2_instances[0]['PlatformType']) 

inv=[]
for item in inventory:
    inv.append({'Manufacturer': item['Publisher'], 'Application': item['Name'], 'Version': item['Version']})

snowdata['software'] = inv

# the gathered details can be converted to a special Snow format
xml = snow_converter.toXML(snowdata)
print(xml)