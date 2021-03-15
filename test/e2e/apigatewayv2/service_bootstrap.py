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
"""Bootstraps the resources required to run the API Gateway v2 integration tests.
"""
import boto3
import logging
import time
from zipfile import ZipFile
import os


from common.aws import get_aws_account_id, get_aws_region, duplicate_s3_contents
from apigatewayv2.bootstrap_resources import (
    TestBootstrapResources,
    AUTHORIZER_IAM_ROLE_NAME,
    AUTHORIZER_ASSUME_ROLE_POLICY,
    AUTHORIZER_POLICY_ARN,
    AUTHORIZER_FUNCTION_NAME
)


def service_bootstrap() -> dict:
    logging.getLogger().setLevel(logging.INFO)
    authorizer_role_arn = create_authorizer_role()
    time.sleep(15)
    authorizer_function_arn = create_lambda_authorizer(authorizer_role_arn)

    return TestBootstrapResources(
        authorizer_role_arn,
        authorizer_function_arn
    ).__dict__


def create_authorizer_role() -> str:
    region = get_aws_region()
    iam_client = boto3.client("iam", region_name=region)

    logging.debug(f"Creating authorizer iam role {AUTHORIZER_IAM_ROLE_NAME}")

    try:
        iam_client.get_role(RoleName = AUTHORIZER_IAM_ROLE_NAME)
        raise RuntimeError(f"Expected {AUTHORIZER_IAM_ROLE_NAME} role to not exist. Did previous test cleanup successfully?")
    except iam_client.exceptions.NoSuchEntityException:
        pass

    resp = iam_client.create_role(RoleName=AUTHORIZER_IAM_ROLE_NAME, AssumeRolePolicyDocument=AUTHORIZER_ASSUME_ROLE_POLICY)
    iam_client.attach_role_policy(RoleName=AUTHORIZER_IAM_ROLE_NAME, PolicyArn=AUTHORIZER_POLICY_ARN)
    return resp['Role']['Arn']


def create_lambda_authorizer(authorizer_role_arn : str) -> str:
    region = get_aws_region()
    lambda_client = boto3.client("lambda", region)

    try:
        lambda_client.get_function(FunctionName = AUTHORIZER_FUNCTION_NAME)
        raise RuntimeError(f"Expected {AUTHORIZER_FUNCTION_NAME} function to not exist. Did previous test cleanup successfully?")
    except lambda_client.exceptions.ResourceNotFoundException:
        pass

    current_directory = os.path.dirname(os.path.realpath(__file__))
    index_zip = ZipFile(f'{current_directory}/resources/index.zip', 'w')
    index_zip.write(f'{current_directory}/resources/index.js', 'index.js')
    index_zip.close()

    with open(f'{current_directory}/resources/index.zip', 'rb') as f:
        b64_encoded_zip_file = f.read()

    response = lambda_client.create_function(FunctionName=AUTHORIZER_FUNCTION_NAME, Role=authorizer_role_arn, Handler='index.handler', Runtime='nodejs12.x', Code={'ZipFile': b64_encoded_zip_file})

    if os.path.exists(f'{current_directory}/resources/index.zip'):
        os.remove(f'{current_directory}/resources/index.zip')
    
    return response['FunctionArn']
