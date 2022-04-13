## Snow Exporter

Using this tool, you can export AWS EC2 instance information an import it to the Snow software for license and asset management. For scaling purposes, it will be possible to use components of the AWS License Manager service, that will be able to gather information across an AWS Organization.

These scripts are using the Python boto3 APIs to create an .xml file to be imported to Snow software.


### Environment

This script can be executed in the scope of an AWS account which has the AWS Systems Manager (SSM) inventory gathering process enabled for EC2 instances. Based on the inventory & the AWS public pricing API the script gathers the necessary information to transform the collected data to an xml definition understood by Snow software.

### Usage

The script currently is self containing. To run the script in your AWS environment, modify the instanceId variable to obtain the relevant information.

Ensure you followed the [quickstart](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) to use the boto3 API.

#### Example 1
To see an example of the output execute it like this:
```bash
python.exe snow_export.py
```

#### Example 2
To store the output to a file execute it like this:
```bash
python.exe snow_export.py >> myexport.xml
```

### Disclaimer
This software is by no means production ready. Use this in a sandbox environment only! Any use is at your own risk. The contributors or AWS can not be held liable. The code is provided as-is without any warranty / guarantees or support. Verify the created datafiles for sensitive information which must not be exposed to other parties. Ensure the created data is not accesible from untrusted sources.

Latest version can be found [here](https://github.com/wralph/aws-helper/tree/main/snow-export).

TODO: Add information on supported Snow software versions or the tested one.

### Not included
- A definition how to setup the Snow software
- A definition how to roll out the solution within an AWS Organization. Ideas could be to leverage SSM Documents (can be executed or [shared](https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-how-to-share.html) within an AWS Organization) or AWS Lambda functions within participating accounts.
- An import mechanism from Snow software license configurations to AWS License Manager
- To store the output directly in a file, pipe it to a .xml filename that matches your specification.

### Contributors
- Ralph Waldenmaier (AWS)
- Rogier van Geest (AWS)
- Snow software