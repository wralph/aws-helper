#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_lamdba_edge.cdk_lamdba_edge_stack import CdkLamdbaEdgeStack

env_USA = cdk.Environment(account="0123456789", region="us-east-1")

app = cdk.App()
CdkLamdbaEdgeStack(app, "cdk-lamdba-edge", env=env_USA)

app.synth()
