#!/bin/bash

set -eu

SCRIPTPATH=$( cd $(dirname $0) ; pwd -P )

SECRETS_FILE=$1

# Verify that the secrets file is provided to generate the manifest.
if [ -z $SECRETS_FILE ]; then
  echo >&2 "SECRETS_FILE argument not provided."
  exit 1
fi

spruce merge --prune meta --prune terraform_outputs \
  $SCRIPTPATH/shibboleth-deployment.yml \
  $ENVIRONMENT_FILE \
  terraform-yaml/state.yml \
  $SECRETS_FILE
