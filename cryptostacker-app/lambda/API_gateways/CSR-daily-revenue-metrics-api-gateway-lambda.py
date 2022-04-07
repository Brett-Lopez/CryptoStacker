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
            FROM daily_revenue_metrics
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


def create_metric_record(RDS_secret_host, RDS_secret_user, RDS_secret_pass, gross_revenue_past_24_hours, gross_revenue_past_7_days, gross_revenue_past_rolling_30_days, gross_revenue_past_previous_month, gross_revenue_past_month_to_date, gross_revenue_past_previous_quarter, gross_revenue_past_quarter_to_date, gross_revenue_past_previous_year, gross_revenue_past_year_to_date, gross_revenue_past_rolling_1_year, gross_revenue_past_all_time):
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
            INSERT INTO daily_revenue_metrics
            (epoch_time,
            iso_date,
            gross_revenue_past_24_hours,
            gross_revenue_past_7_days,
            gross_revenue_past_rolling_30_days,
            gross_revenue_past_previous_month,
            gross_revenue_past_month_to_date,
            gross_revenue_past_previous_quarter,
            gross_revenue_past_quarter_to_date,
            gross_revenue_past_previous_year,
            gross_revenue_past_year_to_date,
            gross_revenue_past_rolling_1_year,
            gross_revenue_past_all_time
            )
            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
            """

            insert_tuple = (int(epoch_time), str(iso_date), int(gross_revenue_past_24_hours), int(gross_revenue_past_7_days), int(gross_revenue_past_rolling_30_days), 
            int(gross_revenue_past_previous_month), int(gross_revenue_past_month_to_date), int(gross_revenue_past_previous_quarter), int(gross_revenue_past_quarter_to_date), 
            int(gross_revenue_past_previous_year), int(gross_revenue_past_year_to_date), int(gross_revenue_past_rolling_1_year), int(gross_revenue_past_all_time) 
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
            FROM daily_revenue_metrics
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
            FROM daily_revenue_metrics
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
    
        gross_revenue_past_24_hours = event["queryStringParameters"]["gross_revenue_past_24_hours"]
        gross_revenue_past_7_days = event["queryStringParameters"]["gross_revenue_past_7_days"]
        gross_revenue_past_rolling_30_days = event["queryStringParameters"]["gross_revenue_past_rolling_30_days"]
        gross_revenue_past_previous_month = event["queryStringParameters"]["gross_revenue_past_previous_month"]
        gross_revenue_past_month_to_date = event["queryStringParameters"]["gross_revenue_past_month_to_date"]
        gross_revenue_past_previous_quarter = event["queryStringParameters"]["gross_revenue_past_previous_quarter"]
        gross_revenue_past_quarter_to_date = event["queryStringParameters"]["gross_revenue_past_quarter_to_date"]
        gross_revenue_past_previous_year = event["queryStringParameters"]["gross_revenue_past_previous_year"]
        gross_revenue_past_year_to_date = event["queryStringParameters"]["gross_revenue_past_year_to_date"]
        gross_revenue_past_rolling_1_year = event["queryStringParameters"]["gross_revenue_past_rolling_1_year"]
        gross_revenue_past_all_time = event["queryStringParameters"]["gross_revenue_past_all_time"]

        sql_query_result = create_metric_record(RDS_secret_host, RDS_secret_user, RDS_secret_pass, gross_revenue_past_24_hours, gross_revenue_past_7_days, 
        gross_revenue_past_rolling_30_days, gross_revenue_past_previous_month, gross_revenue_past_month_to_date, gross_revenue_past_previous_quarter, 
        gross_revenue_past_quarter_to_date, gross_revenue_past_previous_year, gross_revenue_past_year_to_date, gross_revenue_past_rolling_1_year, gross_revenue_past_all_time)
        
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
#?gross_revenue_past_24_hours=1&gross_revenue_past_7_days=1&gross_revenue_past_rolling_30_days=1&gross_revenue_past_previous_month=1&gross_revenue_past_month_to_date=1&gross_revenue_past_previous_quarter=1&gross_revenue_past_quarter_to_date=1&gross_revenue_past_previous_year=1&gross_revenue_past_year_to_date=1&gross_revenue_past_rolling_1_year=1&gross_revenue_past_all_time=1

#DELETE - delete single payment of row_id - 
#?row_id=1

#DELETE - delete all payments of user_id - 
#?epoch_time=1
