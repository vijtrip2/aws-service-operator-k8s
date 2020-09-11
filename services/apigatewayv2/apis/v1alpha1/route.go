// Copyright Amazon.com Inc. or its affiliates. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License"). You may
// not use this file except in compliance with the License. A copy of the
// License is located at
//
//     http://aws.amazon.com/apache2.0/
//
// or in the "license" file accompanying this file. This file is distributed
// on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
// express or implied. See the License for the specific language governing
// permissions and limitations under the License.

// Code generated by ack-generate. DO NOT EDIT.

package v1alpha1

import (
	ackv1alpha1 "github.com/aws/aws-controllers-k8s/apis/core/v1alpha1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// RouteSpec defines the desired state of Route
type RouteSpec struct {
	APIID                            *string                          `json:"apiID,omitempty"`
	APIKeyRequired                   *bool                            `json:"apiKeyRequired,omitempty"`
	AuthorizationScopes              []*string                        `json:"authorizationScopes,omitempty"`
	AuthorizationType                *string                          `json:"authorizationType,omitempty"`
	AuthorizerID                     *string                          `json:"authorizerID,omitempty"`
	ModelSelectionExpression         *string                          `json:"modelSelectionExpression,omitempty"`
	OperationName                    *string                          `json:"operationName,omitempty"`
	RequestModels                    map[string]*string               `json:"requestModels,omitempty"`
	RequestParameters                map[string]*ParameterConstraints `json:"requestParameters,omitempty"`
	RouteKey                         *string                          `json:"routeKey,omitempty"`
	RouteResponseSelectionExpression *string                          `json:"routeResponseSelectionExpression,omitempty"`
	Target                           *string                          `json:"target,omitempty"`
}

// RouteStatus defines the observed state of Route
type RouteStatus struct {
	// All CRs managed by ACK have a common `Status.ACKResourceMetadata` member
	// that is used to contain resource sync state, account ownership,
	// constructed ARN for the resource
	ACKResourceMetadata *ackv1alpha1.ResourceMetadata `json:"ackResourceMetadata"`
	// All CRS managed by ACK have a common `Status.Conditions` member that
	// contains a collection of `ackv1alpha1.Condition` objects that describe
	// the various terminal states of the CR and its backend AWS service API
	// resource
	Conditions        []*ackv1alpha1.Condition `json:"conditions"`
	APIGatewayManaged *bool                    `json:"apiGatewayManaged,omitempty"`
	RouteID           *string                  `json:"routeID,omitempty"`
}

// Route is the Schema for the Routes API
// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
type Route struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`
	Spec              RouteSpec   `json:"spec,omitempty"`
	Status            RouteStatus `json:"status,omitempty"`
}

// RouteList contains a list of Route
// +kubebuilder:object:root=true
type RouteList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []Route `json:"items"`
}

func init() {
	SchemeBuilder.Register(&Route{}, &RouteList{})
}