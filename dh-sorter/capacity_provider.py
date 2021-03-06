import boto3
import json

pricing_client = boto3.client('pricing', region_name='us-east-1')
cache = {}

class CapacityProvider:    

    @staticmethod
    def getCapacity(region, instance_type):
        cacheKey = region + instance_type
        if cacheKey in cache:
            return cache[cacheKey]

        product_pager = pricing_client.get_paginator('get_products')    
        product_iterator = product_pager.paginate(
                ServiceCode='AmazonEC2', Filters=[
                {'Type' :'TERM_MATCH', 'Field':'operatingSystem', 'Value':'Linux'},
                {'Type' :'TERM_MATCH', 'Field':'instanceType', 'Value': instance_type},
                {'Type' :'TERM_MATCH', 'Field':'regioncode', 'Value': region},
                {'Type' :'TERM_MATCH', 'Field':'ProductFamily', 'Value': 'Dedicated Host'},
                {'Type' :'TERM_MATCH', 'Field':'tenancy', 'Value': 'Host'},
            ],
            MaxResults=1
        )

        for product_item in product_iterator:
            for offer_string in product_item.get('PriceList'):
                offer = json.loads(offer_string)
                product = offer.get('product')
                product_attributes = product.get('attributes')

                vCPU = int(product_attributes['vcpu'])
                cache[cacheKey] = vCPU
                return vCPU
        
        return -1

# get_ec2_pricing_info("r5", "eu-central-1", "Windows")