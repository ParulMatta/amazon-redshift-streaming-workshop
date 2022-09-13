#!/usr/bin/env python3
import os
import constants

import aws_cdk as cdk

from redshift_streaming.ingestion_stack import IngestionStack
from redshift_streaming.sagemaker_stack import SagemakerStack
from redshift_streaming.redshift_stack import RedshiftStack

app = cdk.App(context=constants.context_constants)
#Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
environment = app.node.try_get_context("environment")
env=cdk.Environment(
        account=constants.context_constants[f'{environment}_global_config']['account_id'], 
        region=constants.context_constants[f'{environment}_global_config']['region'])

#add init  stack      
redshift_stack = RedshiftStack(app,  "RedshiftStack", env=env)
#add S3 in ingestion stack      
ingestion_stack = IngestionStack(app,  "IngestionStack", env=env, redshift_stack=redshift_stack)

#add ec2 in redshift stack
sagemaker_stack = SagemakerStack(app, "SagemakerStack", env=env)


app.synth()
