#pip install mysql-connector-python
from mysql.connector import connect, Error
import logging
import aws_functions_for_lambda
import json
import CSR_service_mesh_map
import CSR_toolkit
#import threading

def get_multiple_metrics(RDS_secret_host, RDS_secret_user, RDS_secret_pass, limit):
    logging.critical("get_multiple_metrics() called") #debugging
    limit_max = 200
    limit = int(limit)
    if limit >= limit_max:
        limit = int(limit_max)
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_query = """
            SELECT *
            FROM daily_user_metrics
            ORDER BY id DESC
            LIMIT %s
            """

            select_tuple = (int(limit), )

            with connection.cursor() as cursor:
                cursor.execute(select_query, select_tuple)
                sql_query_result = cursor.fetchall()

        return sql_query_result

    except Error as e:
        print(e)


def create_metric_record(RDS_secret_host, RDS_secret_user, RDS_secret_pass, total_users, user_subscription_status_users, verified_users, paying_users,
    payments_1_month, payments_3_month, payments_6_month, payments_12_month, payments_1200_month, payments_tier_2, payments_tier_3, users_logged_in_past_24_hours,
    users_logged_in_past_48_hours, users_logged_in_past_168_hours, users_logged_in_past_336_hours, users_logged_in_past_720_hours, active_schedules_btc,
    active_schedules_eth, active_schedules_ltc, active_schedules_ha_type_failover, active_schedules_ha_type_round_robin, active_schedules_ha_type_simultaneous,
    active_schedules_ha_type_single_exchange, active_schedules_dca_logs_past_30_days):

    logging.critical("create_metric_record() called") #debugging
    epoch_time = CSR_toolkit.current_time_epoch()
    datetime_object = CSR_toolkit.epoch_to_datetime_object(epoch_time)
    iso_date = str(datetime_object.date())

    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            insert_query = """
            INSERT INTO daily_user_metrics
            (epoch_time,
            iso_date,
            total_users,
            user_subscription_status_users,
            verified_users,
            paying_users,
            payments_1_month,
            payments_3_month,
            payments_6_month,
            payments_12_month,
            payments_1200_month,
            payments_tier_2,
            payments_tier_3,
            users_logged_in_past_24_hours,
            users_logged_in_past_48_hours,
            users_logged_in_past_168_hours,
            users_logged_in_past_336_hours,
            users_logged_in_past_720_hours,
            active_schedules_btc,
            active_schedules_eth,
            active_schedules_ltc,
            active_schedules_ha_type_failover,
            active_schedules_ha_type_round_robin,
            active_schedules_ha_type_simultaneous,
            active_schedules_ha_type_single_exchange,
            active_schedules_dca_logs_past_30_days
            )
            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
            """

            insert_tuple = (int(epoch_time), str(iso_date), int(total_users), int(user_subscription_status_users), int(verified_users), 
            int(paying_users), int(payments_1_month), int(payments_3_month), int(payments_6_month), int(payments_12_month), int(payments_1200_month),
            int(payments_tier_2), int(payments_tier_3), int(users_logged_in_past_24_hours), int(users_logged_in_past_48_hours), 
            int(users_logged_in_past_168_hours), int(users_logged_in_past_336_hours), int(users_logged_in_past_720_hours), 
            int(active_schedules_btc), int(active_schedules_eth), int(active_schedules_ltc), int(active_schedules_ha_type_failover), 
            int(active_schedules_ha_type_round_robin), int(active_schedules_ha_type_simultaneous), int(active_schedules_ha_type_single_exchange), 
            int(active_schedules_dca_logs_past_30_days),
            )

            with connection.cursor() as cursor:
                cursor.execute(insert_query, insert_tuple)
                connection.commit()

        return "inserted metric row"

    except Error as e:
        print(e)

def delete_row_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, row_id):
    logging.critical("delete_row_id() called") #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            delete_row_query = """
            Delete
            FROM daily_user_metrics
            WHERE id = %s
            """

            sql_tuple = (int(row_id), )

            with connection.cursor() as cursor:
                cursor.execute(delete_row_query, sql_tuple)
                connection.commit()
                logging.error("Row(s) Deleted") #debugging

        return "Row(s) Deleted"

    except Error as e:
        print(e)

def delete_epoch_time(RDS_secret_host, RDS_secret_user, RDS_secret_pass, epoch_time):
    logging.critical("delete_epoch_time() called") #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            delete_row_query = """
            Delete
            FROM daily_user_metrics
            WHERE epoch_time = %s
            """

            sql_tuple = (int(epoch_time), )

            with connection.cursor() as cursor:
                cursor.execute(delete_row_query, sql_tuple)
                connection.commit()
                logging.error("Row(s) Deleted") #debugging

        return "Row(s) Deleted"

    except Error as e:
        print(e)


def lambda_handler(event, context):
    #configure logging
    logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

    responseObject = {}
    responseObject["statusCode"] = 200
    responseObject["headers"] = {}
    responseObject["headers"]["Content-Type"] = "application/json" 
    #print(responseObject) #debugging

    logging.error("retrieve RDS secrets")
    RDS_secret_return = aws_functions_for_lambda.get_aws_secret("CSR-primary-serverless-db-1-tf")
    RDS_secret_dict = eval(RDS_secret_return)
    RDS_secret_user = RDS_secret_dict["username"]
    RDS_secret_pass = RDS_secret_dict["password"]
    RDS_secret_host = RDS_secret_dict["host"]
    if RDS_secret_host: #debugging
        logging.error("RDS host set") #debugging
        logging.error(RDS_secret_host) #debugging
    
    logging.error("retrieve service mesh secret for API calls")
    service_mesh_secret_1 = eval(aws_functions_for_lambda.get_aws_secret("CSR-Service-Mesh-Secret_1-TF"))
    
    #IF GET
    if event["httpMethod"] == "GET":
        logging.error("httpMethod: GET") #debugging
        if "scope" in event["queryStringParameters"]:
            logging.error("required scope set") #debugging
            
            if event["queryStringParameters"]["scope"] == "get_multiple_metrics":
                logging.error("scope: single_latest") #debugging
                if "limit" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                limit = event["queryStringParameters"]["limit"]
                sql_query_result = get_multiple_metrics(RDS_secret_host, RDS_secret_user, RDS_secret_pass, limit)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject

            elif event["queryStringParameters"]["scope"] == "single_active":
                responseObject["body"] = json.dumps("queryStringParameters missing")
                return responseObject
            
            else:
                logging.error("queryStringParameters missing") #debugging
                responseObject["statusCode"] = 400
                responseObject["body"] = json.dumps("queryStringParameters missing")
                return responseObject
            
        else:
            logging.error("queryStringParameters missing") #debugging
            responseObject["statusCode"] = 400
            responseObject["body"] = json.dumps("queryStringParameters missing")
            return responseObject

    #IF POST
    elif event["httpMethod"] == "POST":
        logging.error("httpMethod: POST") #debugging
    
        total_users = event["queryStringParameters"]["total_users"]
        user_subscription_status_users = event["queryStringParameters"]["user_subscription_status_users"]
        verified_users = event["queryStringParameters"]["verified_users"]
        paying_users = event["queryStringParameters"]["paying_users"]
        payments_1_month = event["queryStringParameters"]["payments_1_month"]
        payments_3_month = event["queryStringParameters"]["payments_3_month"]
        payments_6_month = event["queryStringParameters"]["payments_6_month"]
        payments_12_month = event["queryStringParameters"]["payments_12_month"]
        payments_1200_month = event["queryStringParameters"]["payments_1200_month"]
        payments_tier_2 = event["queryStringParameters"]["payments_tier_2"]
        payments_tier_3 = event["queryStringParameters"]["payments_tier_3"]
        users_logged_in_past_24_hours = event["queryStringParameters"]["users_logged_in_past_24_hours"]
        users_logged_in_past_48_hours = event["queryStringParameters"]["users_logged_in_past_48_hours"]
        users_logged_in_past_168_hours = event["queryStringParameters"]["users_logged_in_past_168_hours"]
        users_logged_in_past_336_hours = event["queryStringParameters"]["users_logged_in_past_336_hours"]
        users_logged_in_past_720_hours = event["queryStringParameters"]["users_logged_in_past_720_hours"]
        active_schedules_btc = event["queryStringParameters"]["active_schedules_btc"]
        active_schedules_eth = event["queryStringParameters"]["active_schedules_eth"]
        active_schedules_ltc = event["queryStringParameters"]["active_schedules_ltc"]
        active_schedules_ha_type_failover = event["queryStringParameters"]["active_schedules_ha_type_failover"]
        active_schedules_ha_type_round_robin = event["queryStringParameters"]["active_schedules_ha_type_round_robin"]
        active_schedules_ha_type_simultaneous = event["queryStringParameters"]["active_schedules_ha_type_simultaneous"]
        active_schedules_ha_type_single_exchange = event["queryStringParameters"]["active_schedules_ha_type_single_exchange"]
        active_schedules_dca_logs_past_30_days = event["queryStringParameters"]["active_schedules_dca_logs_past_30_days"]

        sql_query_result = create_metric_record(RDS_secret_host, RDS_secret_user, RDS_secret_pass, total_users, user_subscription_status_users, 
        verified_users, paying_users,
        payments_1_month, payments_3_month, payments_6_month, payments_12_month, payments_1200_month, payments_tier_2, payments_tier_3, users_logged_in_past_24_hours,
        users_logged_in_past_48_hours, users_logged_in_past_168_hours, users_logged_in_past_336_hours, users_logged_in_past_720_hours, active_schedules_btc,
        active_schedules_eth, active_schedules_ltc, active_schedules_ha_type_failover, active_schedules_ha_type_round_robin, active_schedules_ha_type_simultaneous,
        active_schedules_ha_type_single_exchange, active_schedules_dca_logs_past_30_days)
        
        if sql_query_result:
            responseObject["body"] = json.dumps(sql_query_result)
            return responseObject
        else:
            responseObject["body"] = json.dumps([])
            return responseObject

    #IF DELETE
    elif event["httpMethod"] == "DELETE":
        logging.error("httpMethod: DELETE") #debugging
        if "row_id" in event["queryStringParameters"]:
            row_id = event["queryStringParameters"]["row_id"]
            sql_query_result = delete_row_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, row_id)
            responseObject["body"] = json.dumps(sql_query_result)
            return responseObject
        
        elif "epoch_time" in event["queryStringParameters"]:
            epoch_time = event["queryStringParameters"]["epoch_time"]
            sql_query_result = delete_epoch_time(RDS_secret_host, RDS_secret_user, RDS_secret_pass, epoch_time)
            responseObject["body"] = json.dumps(sql_query_result)
            return responseObject
        
        else:
            logging.error("queryStringParameters missing") #debugging
            responseObject["body"] = json.dumps("queryStringParameters missing")
            responseObject["statusCode"] = 400
            return responseObject
    
    else:
        logging.error("queryStringParameters missing") #debugging
        responseObject["body"] = json.dumps("queryStringParameters missing")
        responseObject["statusCode"] = 400
        return responseObject


#########################
##### query params ######
#########################

#GET - multiple metrics - 
#?scope=get_multiple_metrics&limit=200

#POST - create metric row - 
#?total_users=1&user_subscription_status_users=1&verified_users=1&paying_users=1&payments_1_month=1&payments_3_month=1&payments_6_month=1&payments_12_month=1&payments_1200_month=1&payments_tier_2=1&payments_tier_3=1&users_logged_in_past_24_hours=1&users_logged_in_past_48_hours=1&users_logged_in_past_168_hours=1&users_logged_in_past_336_hours=1&users_logged_in_past_720_hours=1

#DELETE - delete single payment of row_id - 
#?row_id=1

#DELETE - delete all payments of user_id - 
#?epoch_time=1
