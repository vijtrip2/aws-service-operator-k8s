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

"""Integration tests for the API Gateway V2 ImportApi operation
"""

import boto3
import logging
import time

import pytest

from apigatewayv2 import SERVICE_NAME, service_marker, CRD_GROUP, CRD_VERSION
from apigatewayv2.replacement_values import REPLACEMENT_VALUES
from apigatewayv2.tests.helper import ApiGatewayValidator
from common.resources import load_resource_file
from common import k8s

RESOURCE_PLURAL = 'apis'

DELETE_WAIT_AFTER_SECONDS = 20
UPDATE_WAIT_AFTER_SECONDS = 10


@pytest.fixture(scope="module")
def apigw_validator():
    return ApiGatewayValidator(boto3.client('apigatewayv2'))


@pytest.fixture(scope="module")
def test_resource_values():
    return REPLACEMENT_VALUES.copy()


@service_marker
@pytest.mark.canary
class TestImportApi:
    def test_create_update_delete_api(self, apigw_validator, test_resource_values):
        resource_name = "import-ack-test-api"

        test_resource_values["API_NAME"] = resource_name
        test_resource_values["API_TITLE"] = resource_name

        resource_data = load_resource_file(
            SERVICE_NAME,
            "import_api",
            additional_replacements=test_resource_values,
        )
        logging.error(f"import api resource: {resource_data}")

        # Create the k8s resource
        ref = k8s.CustomResourceReference(
            CRD_GROUP, CRD_VERSION, RESOURCE_PLURAL,
            resource_name, namespace="default",
        )

        if k8s.get_resource_exists(ref):
            pytest.fail(f"expected {resource_name} to not exist. Did previous test cleanup?", False)

        k8s.create_custom_resource(ref, resource_data)
        cr = k8s.wait_resource_consumed_by_controller(ref)
        assert cr is not None
        assert k8s.get_resource_exists(ref)

        api_id = cr['status']['apiID']

        apigw_validator.assert_api_is_present(api_id=api_id)

        # Update the imported api's title
        updated_api_title = 'updated-import-ack-test-api'
        test_resource_values["API_TITLE"] = updated_api_title
        resource_data = load_resource_file(
            SERVICE_NAME,
            "import_api",
            additional_replacements=test_resource_values,
        )
        k8s.patch_custom_resource(ref, resource_data)
        time.sleep(UPDATE_WAIT_AFTER_SECONDS)
        assert k8s.get_resource_exists(ref)
        # Let's check that the Broker appears in AmazonMQ
        apigw_validator.assert_api_name(api_id=api_id, expected_api_name=updated_api_title)

        # Delete the k8s resource on teardown of the module
        k8s.delete_custom_resource(ref)
        time.sleep(DELETE_WAIT_AFTER_SECONDS)
        apigw_validator.assert_api_is_deleted(api_id=api_id)
