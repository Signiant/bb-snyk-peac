#!/bin/bash

session_name="bb-snyk-peak-deploy"
AWS_DEFAULT_REGION=us-east-1
SAM_CLI_TELEMETRY=0
sam validate
sam build
sam deploy --no-fail-on-empty-changeset --config-env live