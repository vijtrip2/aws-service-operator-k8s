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

"""Stores the values used by each of the integration tests for replacing the
API Gateway v2 test variables.
"""

REPLACEMENT_VALUES = {
    "API_NAME": "ack-test-api",
    "API_TITLE": "ack-test-api",
    "API_ID": "api_id",
    "INTEGRATION_NAME": "ack-test-integration",
    "AUTHORIZER_NAME": "ack-test-authorizer",
    "IDENTITY_SOURCE": "$request.header.Authorization",
    "AUTHORIZER_URI": "authorizer_uri",
    "ROUTE_NAME": "ack-test-route",
    "ROUTE_KEY": "httpbin",
    "INTEGRATION_ID": "integration_id",
    "AUTHORIZER_ID": "authorizer_id",
    "STAGE_NAME": "test"
}
