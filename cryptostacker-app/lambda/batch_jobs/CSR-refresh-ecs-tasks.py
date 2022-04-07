#cron syntax:
# */15 * * * ? *


#standard library
import datetime
import logging
import json
import urllib.parse

#third party
import boto3
import requests

#iternal libraries
import aws_functions_for_lambda
import CSR_service_mesh_map
import CSR_toolkit


#configure logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

def lambda_handler(event, context):
    logging.error("lambda_handler begins") #debugging

    aws_ecs_client = boto3.client('ecs')

    ecs_cluster= "csr-flask-web-app-ecs-cluster-tf"
    ecs_service = "csr-flask-web-app-service-tf"
    
    logging.error("boto3 call to describe_services")
    describe_services_response = aws_ecs_client.describe_services(
    cluster=ecs_cluster,
    services=[
        ecs_service,
        ]
    )
    
    for service in describe_services_response["services"]:
        if service["serviceName"].lower() == ecs_service.lower():
            current_cluster_arn = service["clusterArn"]
            current_servicename = service["serviceName"]
            update_service_response = aws_ecs_client.update_service(
                cluster=current_cluster_arn,
                service=current_servicename,
                platformVersion='LATEST',
                forceNewDeployment=True,
            )

    logging.error("lambda_handler ends") #debugging