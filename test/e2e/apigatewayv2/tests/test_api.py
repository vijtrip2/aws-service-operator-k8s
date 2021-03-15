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

"""Integration tests for the API Gateway V2
"""

import logging
import time

import boto3
import pytest
import requests

import apigatewayv2.tests.helper as helper
from apigatewayv2 import SERVICE_NAME, service_marker
from apigatewayv2.bootstrap_resources import get_bootstrap_resources, AUTHORIZER_FUNCTION_NAME
from apigatewayv2.replacement_values import REPLACEMENT_VALUES
from apigatewayv2.tests.helper import ApiGatewayValidator
from common import k8s
from common.aws import get_aws_region, get_aws_account_id
from common.resources import load_resource_file

DELETE_WAIT_AFTER_SECONDS = 10
UPDATE_WAIT_AFTER_SECONDS = 10
DEPLOYMENT_WAIT_AFTER_SECONDS = 10


@pytest.fixture(scope="module")
def apigw_validator():
    return ApiGatewayValidator(boto3.client('apigatewayv2'))

@pytest.fixture(scope="module")
def test_resource_values():
    return REPLACEMENT_VALUES.copy()


@service_marker
@pytest.mark.canary
class TestApiGatewayV2:

    @pytest.mark.run(order=1)
    def test_precheck_api_resource(self, test_resource_values):
        api_resource_name = test_resource_values['API_NAME']
        if k8s.get_resource_exists(helper.get_api_ref(api_resource_name)):
            pytest.fail(f"expected {api_resource_name} to not exist. Did previous test cleanup?", False)

    @pytest.mark.run(order=2)
    def test_precheck_integration_resource(self, test_resource_values):
        integration_resource_name = test_resource_values['INTEGRATION_NAME']
        if k8s.get_resource_exists(helper.get_api_ref(integration_resource_name)):
            pytest.fail(f"expected {integration_resource_name} to not exist. Did previous test cleanup?", False)

    @pytest.mark.run(order=3)
    def test_precheck_authorizer_resource(self, test_resource_values):
        authorizer_resource_name = test_resource_values['AUTHORIZER_NAME']
        if k8s.get_resource_exists(helper.get_api_ref(authorizer_resource_name)):
            pytest.fail(f"expected {authorizer_resource_name} to not exist. Did previous test cleanup?", False)

    @pytest.mark.run(order=4)
    def test_precheck_route_resource(self, test_resource_values):
        route_resource_name = test_resource_values['ROUTE_NAME']
        if k8s.get_resource_exists(helper.get_api_ref(route_resource_name)):
            pytest.fail(f"expected {route_resource_name} to not exist. Did previous test cleanup?", False)

    @pytest.mark.run(order=5)
    def test_create_http_api(self, apigw_validator, test_resource_values):
        api_resource_data = load_resource_file(
            SERVICE_NAME,
            "httpapi",
            additional_replacements=test_resource_values,
        )
        logging.error(f"http api resource: {api_resource_data}")

        # Create the k8s resource
        api_ref = helper.get_api_ref(test_resource_values['API_NAME'])
        k8s.create_custom_resource(api_ref, api_resource_data)
        cr = k8s.wait_resource_consumed_by_controller(api_ref)

        assert cr is not None
        assert k8s.get_resource_exists(api_ref)

        api_id = cr['status']['apiID']
        test_resource_values['API_ID'] = api_id

        # Let's check that the HTTP Api appears in Amazon API Gateway
        apigw_validator.assert_api_is_present(api_id=api_id)

    @pytest.mark.run(order=6)
    def test_update_http_api(self, apigw_validator, test_resource_values):
        updated_api_title = 'updated-ack-test-api'
        test_resource_values['API_TITLE'] = updated_api_title
        api_resource_data = load_resource_file(
            SERVICE_NAME,
            "httpapi",
            additional_replacements=test_resource_values,
        )
        logging.error(f"http api resource: {api_resource_data}")

        # Create the k8s resource
        api_ref = helper.get_api_ref(test_resource_values['API_NAME'])
        k8s.patch_custom_resource(api_ref, api_resource_data)
        time.sleep(UPDATE_WAIT_AFTER_SECONDS)

        assert k8s.get_resource_exists(api_ref)

        # Let's check that the HTTP Api appears in Amazon API Gateway
        apigw_validator.assert_api_name(
            api_id=test_resource_values['API_ID'],
            expected_api_name=updated_api_title
        )

    @pytest.mark.run(order=7)
    def test_create_integration(self, apigw_validator, test_resource_values):
        # Create an integration for the HTTP Api
        integration_ref = helper.get_integration_ref(integration_resource_name=test_resource_values['INTEGRATION_NAME'])
        integration_resource_data = load_resource_file(
            SERVICE_NAME,
            "integration",
            additional_replacements=test_resource_values
        )
        logging.error(f"integration resource: {integration_resource_data}")

        # Create the k8s integration resource
        k8s.create_custom_resource(integration_ref, integration_resource_data)
        cr = k8s.wait_resource_consumed_by_controller(integration_ref)
        assert cr is not None
        assert k8s.get_resource_exists(integration_ref)
        integration_id = cr['status']['integrationID']
        test_resource_values['INTEGRATION_ID'] = integration_id
        apigw_validator.assert_integration_is_present(
            api_id=test_resource_values['API_ID'],
            integration_id=integration_id
        )

    @pytest.mark.run(order=8)
    def test_create_authorizer(self, apigw_validator, test_resource_values):
        # Create an integration for the HTTP Api
        authorizer_ref = helper.get_authorizer_ref(authorizer_resource_name=test_resource_values['AUTHORIZER_NAME'])
        authorizer_uri = "arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{authorizer_function_arn}/invocations" \
                    .format(region=get_aws_region(), authorizer_function_arn=get_bootstrap_resources().AuthorizerFunctionArn)
        test_resource_values["AUTHORIZER_URI"] = authorizer_uri
        authorizer_resource_data = load_resource_file(
            SERVICE_NAME,
            "authorizer",
            additional_replacements=test_resource_values
        )
        logging.error(f"authorizer resource: {authorizer_resource_data}")

        # Create the k8s integration resource
        k8s.create_custom_resource(authorizer_ref, authorizer_resource_data)
        cr = k8s.wait_resource_consumed_by_controller(authorizer_ref)
        assert cr is not None
        assert k8s.get_resource_exists(authorizer_ref)
        authorizer_id = cr['status']['authorizerID']
        test_resource_values['AUTHORIZER_ID'] = authorizer_id
        apigw_validator.assert_authorizer_is_present(
            api_id=test_resource_values['API_ID'],
            authorizer_id=authorizer_id)

        # add permissions for apigateway to invoke authorizer lambda
        authorizer_arn = "arn:aws:execute-api:{region}:{account}:{api_id}/authorizers/{authorizer_id}".format(
            region=get_aws_region(),
            account=get_aws_account_id(),
            api_id=test_resource_values['API_ID'],
            authorizer_id=authorizer_id
        )
        lambda_client = boto3.client("lambda")
        lambda_client.add_permission(FunctionName=AUTHORIZER_FUNCTION_NAME,
                                     StatementId='apigatewayv2-authorizer-invoke-permissions',
                                     Action='lambda:InvokeFunction',
                                     Principal='apigateway.amazonaws.com',
                                     SourceArn=authorizer_arn)

    @pytest.mark.run(order=9)
    def test_create_route(self, apigw_validator, test_resource_values):
        # Create an integration for the HTTP Api
        route_ref = helper.get_route_ref(route_resource_name=test_resource_values['ROUTE_NAME'])
        route_resource_data = load_resource_file(
            SERVICE_NAME,
            "route",
            additional_replacements=test_resource_values
        )
        logging.error(f"route resource: {route_resource_data}")

        # Create the k8s integration resource
        k8s.create_custom_resource(route_ref, route_resource_data)
        cr = k8s.wait_resource_consumed_by_controller(route_ref)
        assert cr is not None
        assert k8s.get_resource_exists(route_ref)
        route_id = cr['status']['routeID']
        test_resource_values['ROUTE_ID'] = route_id
        apigw_validator.assert_route_is_present(api_id=test_resource_values['API_ID'], route_id=route_id)

    @pytest.mark.run(order=10)
    def test_create_stage(self, apigw_validator, test_resource_values):
        # Create an integration for the HTTP Api
        stage_ref = helper.get_stage_ref(stage_resource_name=test_resource_values['STAGE_NAME'])
        stage_resource_data = load_resource_file(
            SERVICE_NAME,
            "stage",
            additional_replacements=test_resource_values
        )
        logging.error(f"stage resource: {stage_resource_data}")

        # Create the k8s integration resource
        k8s.create_custom_resource(stage_ref, stage_resource_data)
        cr = k8s.wait_resource_consumed_by_controller(stage_ref)
        assert cr is not None
        assert k8s.get_resource_exists(stage_ref)
        apigw_validator.assert_stage_is_present(
            api_id=test_resource_values['API_ID'],
            stage_name=test_resource_values['STAGE_NAME']
        )

    @pytest.mark.run(order=11)
    def test_perform_invocation(self, apigw_validator, test_resource_values):
        time.sleep(DEPLOYMENT_WAIT_AFTER_SECONDS)
        api_ref = helper.get_api_ref(api_resource_name=test_resource_values['API_NAME'])
        api_endpoint = helper.get_api_endpoint(api_ref=api_ref)
        invoke_url = "{api_endpoint}/{stage_name}/{route_key}"\
            .format(api_endpoint=api_endpoint, stage_name=test_resource_values['STAGE_NAME'],
                    route_key=test_resource_values['ROUTE_KEY']
                    )
        response = requests.request(method='GET', url=invoke_url, headers={'Authorization': 'SecretToken'})
        assert 200 == response.status_code

    @pytest.mark.run(order=-5)
    def test_delete_stage(self, apigw_validator, test_resource_values):
        # Delete the k8s resource on teardown of the module
        stage_ref = helper.get_stage_ref(stage_resource_name=test_resource_values['STAGE_NAME'])
        k8s.delete_custom_resource(stage_ref)
        time.sleep(DELETE_WAIT_AFTER_SECONDS)
        # Stage should no longer appear in Amazon API Gateway
        apigw_validator.assert_stage_is_deleted(
            api_id=test_resource_values['API_ID'],
            stage_name=test_resource_values['STAGE_NAME']
        )

    @pytest.mark.run(order=-4)
    def test_delete_route(self, apigw_validator, test_resource_values):
        # Delete the k8s resource on teardown of the module
        route_ref = helper.get_route_ref(route_resource_name=test_resource_values['ROUTE_NAME'])
        k8s.delete_custom_resource(route_ref)
        time.sleep(DELETE_WAIT_AFTER_SECONDS)
        # Route should no longer appear in Amazon API Gateway
        apigw_validator.assert_route_is_deleted(
            api_id=test_resource_values['API_ID'],
            route_id=test_resource_values['ROUTE_ID']
        )

    @pytest.mark.run(order=-3)
    def test_delete_authorizer(self, apigw_validator, test_resource_values):
        # Delete the k8s resource on teardown of the module
        authorizer_ref = helper.get_authorizer_ref(authorizer_resource_name=test_resource_values['AUTHORIZER_NAME'])
        k8s.delete_custom_resource(authorizer_ref)
        time.sleep(DELETE_WAIT_AFTER_SECONDS)
        # Integration should no longer appear in Amazon API Gateway
        apigw_validator.assert_authorizer_is_deleted(
            api_id=test_resource_values['API_ID'],
            authorizer_id=test_resource_values['AUTHORIZER_ID']
        )

    @pytest.mark.run(order=-2)
    def test_delete_integration(self, apigw_validator, test_resource_values):
        # Delete the k8s resource on teardown of the module
        integration_ref = helper.get_integration_ref(integration_resource_name=test_resource_values['INTEGRATION_NAME'])
        k8s.delete_custom_resource(integration_ref)
        time.sleep(DELETE_WAIT_AFTER_SECONDS)
        # Integration should no longer appear in Amazon API Gateway
        apigw_validator.assert_integration_is_deleted(
            api_id=test_resource_values['API_ID'],
            integration_id=test_resource_values['INTEGRATION_ID']
        )

    @pytest.mark.run(order=-1)
    def test_delete_http_api(self, apigw_validator, test_resource_values):
        # Delete the k8s resource on teardown of the module
        api_ref = helper.get_api_ref(api_resource_name=test_resource_values['API_NAME'])
        k8s.delete_custom_resource(api_ref)
        time.sleep(DELETE_WAIT_AFTER_SECONDS)
        # HTTP Api should no longer appear in Amazon API Gateway
        apigw_validator.assert_api_is_deleted(api_id=test_resource_values['API_ID'])
