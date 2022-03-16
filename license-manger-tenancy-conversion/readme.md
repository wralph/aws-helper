# AWS License Manager: Tenancy conversion

This script helps to move EC2 instances, initially deployed to shared tenancy using a custom - non AWS provided AMI, to a dedicated host, managed through a Host Resource Group.

*** 

## Variables

First, a set of variables need to be defined.

**Region:** The AWS region where the task is executed
**AccountId:** The AWS Account which has the License Configuration configured
**InstanceId:** References the EC2 instance to convert
**HostId:** This is referencing any Dedicated Host already provisioned. 
**LicensConfig:** This is the ARN of a License Configuration which is based on the "Cores" licensing model
**HRG:** This is referencing the Host Resource Group which is attached to the License Configuration

```shell
region=<eu-west-1>
accountid=<accountID>
instanceid=<i-EXAMPLE> 
hostid=<h-EXAMPLE>
licenseconfig=<arn:aws:license-manager:REGION:ACCOUNT:license-configuration:lic-EXAMPLE>
hrg=<arn:aws:resource-groups:REGION:ACCOUNT:group/SOME-HRG>
```

***

## Tenancy conversion

The tenancy conversion is happening through the AWS CLI. In order to assign the EC2 instance to the "Cores" based license configuration, it must be attached to a Dedicated Host intermittently. This instance will never run on this host though, except it is the target Dedicated Host already. Finally the instance is associate with the License Configuration an then placed within a Host Resource Group. Once started, it will be placed on a Dedicated Host managed by the Host Resoruce Group.

```shell
# stop the instance to migrate
aws ec2 stop-instances --instance-ids $instanceid

# wait for the instance to be stopped - status can be checked with this command
aws ec2 describe-instances --instance-ids $instanceid \
    --query 'Reservations[*].Instances[*].{State:State, Placement:Placement}'

# assign temporarily to any existing host to make the next command succeed
aws ec2 modify-instance-placement --instance-id $instanceid \
  --tenancy host --affinity host --host-id $hostid

# assign to a host base license configuration
aws license-manager update-license-specifications-for-resource \
    --resource-arn arn:aws:ec2:$region:$accountid:instance/$instanceid  \
    --add-license-specifications LicenseConfigurationArn=$licenseconfig

# assign to a HRG
aws ec2 modify-instance-placement --instance-id $instanceid  \
  --tenancy host --host-resource-group-arn $hrg

# start the instance
aws ec2 start-instances --instance-ids $instanceid

# check status
aws ec2 describe-instances --instance-ids $instanceid \
    --query 'Reservations[*].Instances[*].{State:State,Placement:Placement}'
```