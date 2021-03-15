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

"""Helper functions for apigatewayv2 tests
"""
from apigatewayv2 import CRD_GROUP, CRD_VERSION
from common import k8s

API_RESOURCE_PLURAL = 'apis'
INTEGRATION_RESOURCE_PLURAL = 'integrations'
AUTHORIZER_RESOURCE_PLURAL = 'authorizers'
ROUTE_RESOURCE_PLURAL = 'routes'
STAGE_RESOURCE_PLURAL = 'stages'


def get_api_ref(api_resource_name: str):
    return k8s.CustomResourceReference(
        CRD_GROUP, CRD_VERSION, API_RESOURCE_PLURAL,
        api_resource_name, namespace="default",
    )


def get_integration_ref(integration_resource_name: str):
    return k8s.CustomResourceReference(
        CRD_GROUP, CRD_VERSION, INTEGRATION_RESOURCE_PLURAL,
        integration_resource_name, namespace="default",
    )


def get_authorizer_ref(authorizer_resource_name: str):
    return k8s.CustomResourceReference(
        CRD_GROUP, CRD_VERSION, AUTHORIZER_RESOURCE_PLURAL,
        authorizer_resource_name, namespace="default",
    )


def get_route_ref(route_resource_name: str):
    return k8s.CustomResourceReference(
        CRD_GROUP, CRD_VERSION, ROUTE_RESOURCE_PLURAL,
        route_resource_name, namespace="default",
    )


def get_stage_ref(stage_resource_name: str):
    return k8s.CustomResourceReference(
        CRD_GROUP, CRD_VERSION, STAGE_RESOURCE_PLURAL,
        stage_resource_name, namespace="default",
    )


def get_api_endpoint(api_ref) -> str:
    cr = k8s.get_resource(api_ref)
    return cr['status']['apiEndpoint']


class ApiGatewayValidator:

    def __init__(self, apigatewayv2_client):
        self.apigatewayv2_client = apigatewayv2_client

    def assert_api_is_present(self, api_id: str):
        aws_res = self.apigatewayv2_client.get_api(ApiId=api_id)
        assert aws_res is not None

    def assert_integration_is_present(self, api_id: str, integration_id: str):
        aws_res = self.apigatewayv2_client.get_integration(ApiId=api_id, IntegrationId=integration_id)
        assert aws_res is not None

    def assert_authorizer_is_present(self, api_id: str, authorizer_id: str):
        aws_res = self.apigatewayv2_client.get_authorizer(ApiId=api_id, AuthorizerId=authorizer_id)
        assert aws_res is not None

    def assert_route_is_present(self, api_id: str, route_id: str):
        aws_res = self.apigatewayv2_client.get_route(ApiId=api_id, RouteId=route_id)
        assert aws_res is not None

    def assert_stage_is_present(self, api_id: str, stage_name: str):
        aws_res = self.apigatewayv2_client.get_stage(ApiId=api_id, StageName=stage_name)
        assert aws_res is not None

    def assert_api_is_deleted(self, api_id: str):
        res_found = False
        try:
            self.apigatewayv2_client.get_api(ApiId=api_id)
            res_found = True
        except self.apigatewayv2_client.exceptions.NotFoundException:
            pass

        assert res_found is False

    def assert_integration_is_deleted(self, api_id: str, integration_id: str):
        res_found = False
        try:
            self.apigatewayv2_client.get_integration(ApiId=api_id, IntegrationId=integration_id)
            res_found = True
        except self.apigatewayv2_client.exceptions.NotFoundException:
            pass

        assert res_found is False

    def assert_authorizer_is_deleted(self, api_id: str, authorizer_id: str):
        res_found = False
        try:
            self.apigatewayv2_client.get_authorizer(ApiId=api_id, AuthorizerId=authorizer_id)
            res_found = True
        except self.apigatewayv2_client.exceptions.NotFoundException:
            pass

        assert res_found is False

    def assert_route_is_deleted(self, api_id: str, route_id: str):
        res_found = False
        try:
            self.apigatewayv2_client.get_route(ApiId=api_id, RouteId=route_id)
            res_found = True
        except self.apigatewayv2_client.exceptions.NotFoundException:
            pass

        assert res_found is False

    def assert_stage_is_deleted(self, api_id: str, stage_name: str):
        res_found = False
        try:
            self.apigatewayv2_client.get_stage(ApiId=api_id, StageName=stage_name)
            res_found = True
        except self.apigatewayv2_client.exceptions.NotFoundException:
            pass

        assert res_found is False

    def assert_api_name(self, api_id, expected_api_name):
        aws_res = self.apigatewayv2_client.get_api(ApiId=api_id)
        assert aws_res is not None
        assert aws_res['Name'] == expected_api_name
