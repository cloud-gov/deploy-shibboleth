#!/bin/bash

set -e

template_prefix="shibboleth"
SECRETS_FILE=$1

# Verify that the secrets file is provided to generate the manifest.
if [ -z $SECRETS_FILE ]; then
  echo >&2 "SECRETS_FILE argument not provided."
  exit 1
fi

spruce merge --prune meta \
  $template_prefix-deployment.yml \
  $template_prefix-jobs.yml \
  $template_prefix-infrastructure.yml \
  $SECRETS_FILE
