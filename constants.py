import os
import json
import urllib.request
import base64

from pathlib import Path

SH_FILE =str(Path(__file__).parent.joinpath("assets/scripts/startup.sh"))
with open(SH_FILE, 'r') as sh_file:
    startup_script = sh_file.read()

APP_NAME = "rs-qs"
context_constants = {
    "environment" : "dev",
    "dev_global_config": {
        "account_id": os.environ["CDK_DEFAULT_ACCOUNT"],
        "region": os.environ["CDK_DEFAULT_REGION"],
        "app_name": APP_NAME
    },
    # Kinesis Configuration,
    "dev_kinesis_config": {
        "stream_name": f"order-stream",
        "retention_period": 72,
    },
    # Redshift Configuration
    "dev_redshift_config": {
        "max_azs": 3,
        "nat_gateways": 1,
        "redshift_vpc_cidr": "10.1.0.0/16",
        "subnet_cidr_mask": 24,
        "namespace_name": f"{APP_NAME}-ns",
        "workgroup_name": f"{APP_NAME}-wg",
        "base_capacity": 32,
        "db_name": "dev",
        "cluster_type": "multi-node",
        "number_of_nodes": 2,
        "master_username": "admin",
        "node_type": "ra3.4xlarge",
    },
    "dev_sagemaker_config":{
        "content": base64.b64encode(startup_script.encode('utf-8')).decode("utf-8"),
        "platform_identifier": "notebook-al2-v2",
        "lifecycle_config_name": "pip-dependencies",
        "instance_type": "ml.t3.large",
        "notebook_instance_name": "redshift-sagemaker",
    }
}