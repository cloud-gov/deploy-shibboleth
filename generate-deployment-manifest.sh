#!/bin/bash

set -e

SCRIPTPATH=$( cd $(dirname $0) ; pwd -P )

SECRETS_FILE=$1

# Verify that the secrets file is provided to generate the manifest.
if [ -z $SECRETS_FILE ]; then
  echo >&2 "SECRETS_FILE argument not provided."
  exit 1
fi

spruce merge --prune meta \
  $SCRIPTPATH/shibboleth-deployment.yml \
  $SCRIPTPATH/shibboleth-jobs.yml \
  $SCRIPTPATH/shibboleth-infrastructure.yml \
  $SECRETS_FILE
