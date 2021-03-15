# Copyright Amazon.com Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may
# not use this file except in compliance with the License. A copy of the
# License is located at
#
#	 http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

"""Cleans up the resources created by the bootstrapping process.
"""

import boto3
from common.aws import get_aws_region
from apigatewayv2.bootstrap_resources import (
    AUTHORIZER_IAM_ROLE_NAME,
    AUTHORIZER_POLICY_ARN,
    AUTHORIZER_FUNCTION_NAME
)


def service_cleanup(config: dict):
    detach_policy_and_delete_role()
    delete_authorizer_function()


def detach_policy_and_delete_role():
    region = get_aws_region()
    iam_client = boto3.client("iam", region_name=region)

    try:
        iam_client.detach_role_policy(RoleName=AUTHORIZER_IAM_ROLE_NAME, PolicyArn=AUTHORIZER_POLICY_ARN)
    except iam_client.exceptions.NoSuchEntityException:
        pass

    try:
        iam_client.delete_role(RoleName=AUTHORIZER_IAM_ROLE_NAME)
    except iam_client.exceptions.NoSuchEntityException:
        pass


def delete_authorizer_function():
    region = get_aws_region()
    lambda_client = boto3.client("lambda", region_name=region)

    try:
        lambda_client.delete_function(FunctionName=AUTHORIZER_FUNCTION_NAME)
    except lambda_client.exceptions.ResourceNotFoundException:
        pass
