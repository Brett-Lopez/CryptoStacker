#cron syntax:
#* * * * ? *

#standard library
import datetime
import logging
import time

#third party
import boto3
import requests

#iternal libraries
import aws_functions_for_lambda
import CSR_service_mesh_map
import CSR_toolkit

#configure logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

def parse_query_results_and_send_to_SQS_queue(paginated_query_response_json, base_digital_asset_symbol, price_quote):
    logging.critical("parse_query_results_and_send_to_SQS_queue() called") #debugging 
    if paginated_query_response_json:
        logging.error("paginated_query_response_json not null") #debugging
        sqs_client = boto3.client('sqs')
        
        for dca_schedule_row in paginated_query_response_json:
            #logging.error("inside for loop - for dca_schedule_row in paginated_query_response_json") #debugging
            #logging.error(dca_schedule_row) #debugging
            object_to_send = {
                "user_id": str(dca_schedule_row[0]),
                "interval_time_in_seconds": str(dca_schedule_row[3]),
                "dollar_amount": str(dca_schedule_row[4]),
                "fiat_denomination": str(dca_schedule_row[5]),
                "first_run_epoch": str(dca_schedule_row[7]),
                "next_run_epoch": str(dca_schedule_row[9]),
                "high_availability_type": str(dca_schedule_row[10]),
                "exchange_priority":{
                    "1": str(dca_schedule_row[11]),
                    "2": str(dca_schedule_row[12]),
                    "3": str(dca_schedule_row[13]),
                    "4": str(dca_schedule_row[14]),
                    "5": str(dca_schedule_row[15]),
                    "6": str(dca_schedule_row[16]),
                    "7": str(dca_schedule_row[17]),
                    "8": str(dca_schedule_row[18]),
                    "9": str(dca_schedule_row[19]),
                    "10": str(dca_schedule_row[20]),
                    "11": str(dca_schedule_row[21]),
                    "12": str(dca_schedule_row[22]),
                    "13": str(dca_schedule_row[23]),
                    "14": str(dca_schedule_row[24]),
                    "15": str(dca_schedule_row[25]),
                    "16": str(dca_schedule_row[26]),
                    "17": str(dca_schedule_row[27]),
                    "18": str(dca_schedule_row[28]),
                    "19": str(dca_schedule_row[29]),
                    "20": str(dca_schedule_row[30])
                    },
                "exchange_last_run": str(dca_schedule_row[31]),
                "currency_pair": str(base_digital_asset_symbol.upper()) + "-" + str(dca_schedule_row[5].upper()), #example: BTC-USD
                "digital_asset": str(base_digital_asset_symbol),
                "sleep_offset_for_nonce": "0",
                "price_quote": str(price_quote)
            }
            #logging.error("object_to_send: %s" % object_to_send) #debugging
            sqs_response = sqs_client.send_message(
                QueueUrl=CSR_service_mesh_map.cron_events_sqs_queue,
                MessageBody=str(object_to_send)
                #MessageBody='string',
                #DelaySeconds=123,
                #MessageDeduplicationId= #FIFO (first-in-first-out) queues only
                #MessageGroupId= FIFO (first-in-first-out) queues only
            )
            #logging.error(sqs_response) #debugging
            #logging.error("sent item to SQS queue") #debugging

def retrieve_price_data(base_digital_asset_symbol):
    logging.critical("retrieve_price_data() called")
    #retrieve from coinbase pro and fall back on ... ?
    headers = {"Accept": "application/json"}
    currency_pair = base_digital_asset_symbol.upper() + "-USD"
    bitcoin_price_quote_response = requests.get("https://api.exchange.coinbase.com/products/%s/ticker" % currency_pair)
    price_quote_last_run_epoch = int(datetime.datetime.now().strftime('%s')) #used to re-run this function after n seconds
    if bitcoin_price_quote_response.status_code == 200:
        if float(bitcoin_price_quote_response.json()["price"]) > 1:
            return price_quote_last_run_epoch, bitcoin_price_quote_response.json()["price"]
        else:
            #todo retrieve price from another source, different exchange?
            pass
    elif bitcoin_price_quote_response.status_code != 200:
        #todo retrieve price from another source, different exchange?
        pass

def lambda_handler(event, context):
    base_digital_asset_symbol = "btc"
    base_digital_asset_name = "bitcoin"
    logging.critical("lambda_handler begins") #debugging
    
    #top of the current minute in epoch to retrieve next set of DCA events
    datetime_now_object = datetime.datetime.now()
    top_of_the_current_minute_build = datetime_now_object.replace(second=00, microsecond=00)
    top_of_the_current_minute_epoch = top_of_the_current_minute_build.strftime('%s')
    logging.error("top_of_the_current_minute_epoch") #debugging 
    logging.error(top_of_the_current_minute_epoch) #debugging 
    
    logging.error("retrieve service mesh secret for API calls") 
    service_mesh_secret_1 = eval(aws_functions_for_lambda.get_aws_secret("CSR-Service-Mesh-Secret_1-TF")) #{'CSR_Service_Mesh_Secret_1': 'test12345'}
    
    query_limit_size = 100
    price_data_rerun_threshold = 60
    while_loop_counter = 1

    logging.error("query_limit_size of: %s" % query_limit_size) #debugging
    while True:
        logging.error("start while loop") #debugging
        if while_loop_counter == 1:
            price_quote_last_run_epoch, price_quote = retrieve_price_data(base_digital_asset_symbol)
            logging.error("first loop query #%s" % while_loop_counter) #debugging 
            query_to_send = CSR_service_mesh_map.api_dca_schedule + "?digital_asset=" + str(base_digital_asset_symbol) + "&limit=" + str(query_limit_size) + "&after_id=" + str(0) + "&next_run_epoch=" + str(top_of_the_current_minute_epoch)
            logging.error("query to send: %s" % query_to_send) #debugging
            headers = {} 
            headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
            #paginated_query_response = requests.get(query_to_send, headers=headers)
            while True:
                paginated_query_response = requests.get(query_to_send, headers=headers)
                if paginated_query_response.status_code != 429:
                    break
                time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
            paginated_query_response_json = paginated_query_response.json()
            
            logging.error("paginated_query_response_json")
            logging.error(paginated_query_response_json)
            
            if isinstance(paginated_query_response_json, str): #if string then convert to python object with eval
                paginated_query_response_json = eval(paginated_query_response_json)
            parse_query_results_and_send_to_SQS_queue(paginated_query_response_json, base_digital_asset_symbol, price_quote)

        elif while_loop_counter > 1:
            logging.error("query #%s" % while_loop_counter) #debugging
            if int(datetime.datetime.now().strftime('%s')) - price_quote_last_run_epoch > price_data_rerun_threshold:
                price_quote_last_run_epoch, price_quote = retrieve_price_data(base_digital_asset_symbol)
            query_to_send = CSR_service_mesh_map.api_dca_schedule + "?digital_asset=" + str(base_digital_asset_symbol) + "&limit=" + str(query_limit_size) + "&after_id=" + str(paginated_query_response_json[query_limit_size-1][0]) + "&next_run_epoch=" + str(top_of_the_current_minute_epoch)
            logging.error("query to send: %s" % query_to_send) #debugging
            headers = {} 
            headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
            #paginated_query_response = requests.get(query_to_send, headers=headers)
            while True:
                paginated_query_response = requests.get(query_to_send, headers=headers)
                if paginated_query_response.status_code != 429:
                    break
                time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
            paginated_query_response_json = paginated_query_response.json()
            
            logging.error("paginated_query_response_json")
            logging.error(paginated_query_response_json)
            
            if isinstance(paginated_query_response_json, str): #if string then convert to python object with eval
                paginated_query_response_json = eval(paginated_query_response_json)
            parse_query_results_and_send_to_SQS_queue(paginated_query_response_json, base_digital_asset_symbol, price_quote)

        if len(paginated_query_response_json) < query_limit_size: #if API doesn't return at least as many rows as the query limit then then is the last loop
            logging.error("paginated_query_response_json length of: %s.  Breaking while loop." % len(paginated_query_response_json)) #debugging
            break
        
        while_loop_counter += 1
    
    time.sleep(65)
    logging.error("lambda_handler ends") #debugging