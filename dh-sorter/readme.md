# DH sorter

This project is about filling up dedicated hosts to a maximum with EC2 instances


The function to execute the code requires permissions to access the products API
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "pricing:GetProducts"
            ],
            "Resource": "*",
            "Effect": "Allow"
        }
    ]
}
```


Testdata for Postman
```json
{ "region": "eu-west-1", "instances": [{"type": "r5.xlarge", "count": 2}, {"type": "r5b.xlarge", "count": 3}, {"type": "t3.xlarge", "count": 2}, {"type": "t3.nano", "count": 22}]}
```