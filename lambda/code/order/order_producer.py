import logging
import os
import time

import boto3
import json
import random
import uuid
import datetime
from faker import Faker


def send_data(client, data, key, stream_name):
    resp = client.put_records(
        Records=[
            {
                "Data": json.dumps(data),
                "PartitionKey": key},
        ],
        StreamName=stream_name

    )
    LOGGER.info(f"Response:{resp}")


def lambda_handler(event, context):
    logging.basicConfig()
    global LOGGER
    LOGGER = logging.getLogger(__name__)
    resp = {"status": False, "resp": ""}
    LOGGER.setLevel(logging.DEBUG)
    table_name = 'latest_key'
    try:
        stream_name = os.environ.get('STREAM_NAME')
        region = os.environ.get('AWS_REGION')
        client_dynamodb = boto3.resource('dynamodb')
        table = client_dynamodb.Table(table_name)
        client_kinesis = boto3.client('kinesis', region)
        fake = Faker(['en-AU'])
        customer_key = 15521     
        orderkey = table.get_item(Key={'id':2})

        if "Item" in orderkey:
            order_key = int(orderkey['Item']['info']['latest'])
        else:
            table.put_item(Item={'id':2, 'info':{'latest':0}})
            order_key = 0

        with open('./product.json', 'r') as file:
            product_dict = json.loads(file.read())
            file.close()
            

        record_count = 0
        for i in range(random.randint(90,110)):
            now = datetime.datetime.now()
            prob = 0
            if now.hour < 12:
                prob = now.hour
            elif now.hour == 12:
                prob = now.hour + now.minute
            elif now.hour > 12:
                prob = now.hour + 60
            prob = prob/100
            product_id = random.randint(1, len(product_dict))
            profile_rec = {}
            profile_rec['consignmentid'] = order_key + record_count
            customer_address = fake.address()
            customer_state = customer_address.split(',')[-2]
            order_address = fake.address()
            order_state = customer_address.split(',')[-2]
            profile_rec['consignment_date'] = now.isoformat()
            profile_rec['destination_address'] = customer_address
            profile_rec['destination_state'] = customer_state
            profile_rec['destination_lat'] = random.uniform(-31.475, -37.643)
            profile_rec['destination_long'] = random.uniform(141.224, 149.581)
            profile_rec['origin_address'] = order_address
            profile_rec['origin_state'] = order_state
            profile_rec['origin_lat'] = random.uniform(-31.475, -37.643)
            profile_rec['origin_long'] = random.uniform(141.224, 149.581)
            profile_rec['userid'] = random.randint(0, customer_key)
            days_to_deliver = random.choice(range(2,7))
            profile_rec['delivery_date'] = (now + datetime.timedelta(days=days_to_deliver)).isoformat()
            #profile_rec['days_to_deliver'] = days_to_deliver
            mean_distance = 10 +  (days_to_deliver * 100)
            profile_rec['delivery_distance'] = random.gauss(mean_distance, mean_distance/5)
            profile_rec['revenue'] = random.gauss(mean_distance/6, mean_distance/18)
            profile_rec['cost'] =  profile_rec['revenue'] - (random.random() *  profile_rec['revenue'] /2)
            profile_rec['delay_probability'] = 'LOW'
            if random.random()  < 0.3:
                profile_rec['delay_probability'] = 'MEDIUM'
            if random.random()  < (0.05 + prob):
                profile_rec['delay_probability'] = 'HIGH'
            send_data(client_kinesis, profile_rec,
                        str(uuid.uuid4()), stream_name)
            record_count += 1
            time.sleep(0.5)
        resp["resp"] = record_count
        resp["status"] = True
        table.put_item(Item={'id':2, 'info':{'latest':int(order_key + record_count)}})

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": resp
            })
        }

    # catch connection exceptions
    except Exception as e:
        LOGGER.error(e)
        raise e
