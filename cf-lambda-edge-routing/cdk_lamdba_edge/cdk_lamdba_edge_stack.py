from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    CfnOutput,
    aws_iam as iam,
    aws_cloudfront as cloudfront,
    aws_s3 as s3,
    aws_lambda as _lambda
)


class CdkLamdbaEdgeStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # https://how.wtf/deploy-cloudfront-functions-to-add-security-headers-with-aws-cdk.html
        # https://aws.amazon.com/blogs/networking-and-content-delivery/dynamically-route-viewer-requests-to-any-origin-using-lambdaedge/
        # https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-event-structure.html
        # https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-examples.html#lambda-examples-general-examples
        
        
        # two buckets created for alternating access
        bucket = s3.Bucket(
            self,
            "bucket",
            website_index_document="index.html",
            public_read_access=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
        )

        second_bucket = s3.Bucket(
            self,
            "second_bucket",
            website_index_document="index.html",
            public_read_access=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # s3 origin lambda        
        with open("s3_origin_direction.js", encoding="utf8") as fp:
            handler_code = fp.read()

        s3_origin_lambda = _lambda.Function(self, "origin_direction",
            runtime=_lambda.Runtime.NODEJS_16_X,
            code=_lambda.Code.from_inline(handler_code),
            handler="index.handler"
        )

        ## custom origin lambda
        with open("custom_origin_direction.js", encoding="utf8") as fp:
            custom_handler_code = fp.read()

        custom_origin_lambda = _lambda.Function(self, "custom_origin_direction",
            runtime=_lambda.Runtime.NODEJS_16_X,
            code=_lambda.Code.from_inline(custom_handler_code),
            handler="index.handler"
        )

        # add an origin access identity to allow CF access the private bucket
        oia = cloudfront.OriginAccessIdentity(self, "BucketOIA", 
            comment="Created by CDK"
        )
        bucket.grant_read(oia)
        second_bucket.grant_read(oia)
        
        # create a CF distribution with two paths. Default leverages S3 as a source.
        # /custom redirects to public URIs
        distribution = cloudfront.CloudFrontWebDistribution(
            self,
            "cdn",
            origin_configs=[
                cloudfront.SourceConfiguration(
                    custom_origin_source=cloudfront.CustomOriginConfig(
                        domain_name="heise.de"
                    ),
                    behaviors=[
                        cloudfront.Behavior(
                            default_ttl=Duration.minutes(0),
                            path_pattern="custom",
                            lambda_function_associations=[
                                cloudfront.LambdaFunctionAssociation(
                                    event_type=cloudfront.LambdaEdgeEventType.ORIGIN_REQUEST,
                                    lambda_function=custom_origin_lambda.current_version,
                                ),
                            ],                            
                        )
                    ],
                ),
                cloudfront.SourceConfiguration(
                    s3_origin_source=cloudfront.S3OriginConfig(
                        s3_bucket_source=bucket,
                        origin_access_identity=oia
                    ),
                    behaviors=[
                        cloudfront.Behavior(is_default_behavior=True),
                        cloudfront.Behavior(
                            default_ttl=Duration.minutes(0),
                            path_pattern="*",
                            lambda_function_associations=[
                                cloudfront.LambdaFunctionAssociation(
                                    event_type=cloudfront.LambdaEdgeEventType.ORIGIN_REQUEST,
                                    lambda_function=s3_origin_lambda.current_version,
                                ),
                            ],
                        ),
                    ],
                )
            ],
        )

        CfnOutput(
            self,
            "distribution-domain-name",
            value=distribution.distribution_domain_name,
        )

        
