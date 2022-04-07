#pip install mysql-connector-python
from mysql.connector import connect, Error
import logging
import aws_functions_for_lambda
import json
import CSR_service_mesh_map
import CSR_toolkit

def TopOfNextHour(datatimeobject):
    logging.critical("TopOfNextHour() called") #debugging
    """
    Pass a datatime object as an argument to return the top of the following hour.  
    If you want to run a particular function at or after the top of an/every hour this function will be useful for determining that time.
    """
    current_plus_one = (datatimeobject.hour + 1) % 24
    return datatimeobject.replace(hour=current_plus_one, minute=00, second=00, microsecond=00)

def delete_order_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, order_id):
    logging.critical("delete_order_id() called") #debugging
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
            FROM pending_payments
            WHERE order_id = %s
            """

            select_user_tuple = (order_id, )

            with connection.cursor() as cursor:
                cursor.execute(delete_row_query, select_user_tuple)
                connection.commit()
                logging.error("Row(s) Deleted") #debugging

        return "Row(s) Deleted"

    except Error as e:
        print(e)

def delete_user_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id):
    logging.critical("delete_user_id() called") #debugging
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
            FROM pending_payments
            WHERE user_id = %s
            """

            select_user_tuple = (int(user_id), )

            with connection.cursor() as cursor:
                cursor.execute(delete_row_query, select_user_tuple)
                connection.commit()
                logging.error("Row(s) Deleted") #debugging

        return "Row(s) Deleted"

    except Error as e:
        print(e)

def delete_orders_less_than_epoch(RDS_secret_host, RDS_secret_user, RDS_secret_pass, epoch_time_created):
    logging.critical("delete_orders_less_than_epoch() called") #debugging
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
            FROM pending_payments
            WHERE epoch_time_created < %s
            """

            select_user_tuple = (int(float(epoch_time_created)), )

            with connection.cursor() as cursor:
                cursor.execute(delete_row_query, select_user_tuple)
                connection.commit()
                logging.error("Row(s) Deleted") #debugging

        return "Row(s) Deleted"

    except Error as e:
        print(e)

def get_orders_for_user(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id):
    logging.critical("get_orders_for_user() called") #debugging
    limit_max = 200
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_user_query = """
            SELECT *
            FROM pending_payments
            WHERE user_id = %s
            """

            select_user_tuple = (int(user_id), )

            with connection.cursor() as cursor:
                cursor.execute(select_user_query, select_user_tuple)
                sql_query_result = cursor.fetchmany(size=limit_max)

        return sql_query_result

    except Error as e:
        print(e)

def get_user_ids_above_threshold(RDS_secret_host, RDS_secret_user, RDS_secret_pass, threshold):
    logging.critical("get_user_ids_above_threshold() called") #debugging
    limit_max = 200
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_user_query = """
            select user_id,COUNT(*) as count
            from pending_payments
            GROUP BY user_id
            HAVING count > %s
            order by count DESC;
            """

            select_user_tuple = (int(threshold), )

            with connection.cursor() as cursor:
                cursor.execute(select_user_query, select_user_tuple)
                sql_query_result = cursor.fetchmany(size=limit_max)

        return sql_query_result

    except Error as e:
        print(e)

def get_all_orders_paginated(RDS_secret_host, RDS_secret_user, RDS_secret_pass, after_id, limit):
    logging.critical("get_all_orders_paginated() called") #debugging
    limit_max = 200
    limit = int(limit)
    if limit >= limit_max:
        limit = int(limit_max)
    logging.error("limit: %s" % str(limit)) #debugging

    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_orders_query = """
            SELECT *
            FROM pending_payments
            WHERE id > %s
            LIMIT %s
            """

            select_orders_tuple = (int(after_id), int(limit), )

            with connection.cursor() as cursor:
                cursor.execute(select_orders_query, select_orders_tuple)
                sql_query_result = cursor.fetchall() 

        return sql_query_result

    except Error as e:
        print(e)

def get_all_orders_single_user_paginated(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, after_id, limit):
    logging.critical("get_all_orders_single_user_paginated() called") #debugging
    limit_max = 200
    limit = int(limit)
    if limit >= limit_max:
        limit = int(limit_max)
    logging.error("limit: %s" % str(limit)) #debugging

    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_orders_query = """
            SELECT *
            FROM pending_payments
            WHERE id > %s AND user_id = %s
            LIMIT %s
            """

            select_orders_tuple = (int(after_id), int(user_id), int(limit), )

            with connection.cursor() as cursor:
                cursor.execute(select_orders_query, select_orders_tuple)
                sql_query_result = cursor.fetchall() 

        return sql_query_result

    except Error as e:
        print(e)


def insert_order_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, current_us_state, order_id, purchased_tier, purchased_months, payment_amount_in_usd):
    logging.critical("insert_order_id() called") #debugging
    epoch_time_created = CSR_toolkit.current_time_epoch()
    
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            print(connection) #debugging

            insert_order_id_query = """
            INSERT INTO pending_payments
            (user_id,
            order_id,
            current_us_state,
            epoch_time_created,
            purchased_tier,
            purchased_months,
            payment_amount_in_usd
            )
            VALUES ( %s, %s, %s, %s, %s, %s, %s )
            """
        
            order_id_tuple = (int(user_id), order_id, current_us_state, int(epoch_time_created), int(purchased_tier), int(purchased_months), int(payment_amount_in_usd), )

            with connection.cursor() as cursor:
                cursor.execute(insert_order_id_query, order_id_tuple)
                connection.commit()

        return "inserted order_id"

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

    #IF GET
    if event["httpMethod"] == "GET":
        logging.error("httpMethod: GET") #debugging
        if "scope" in event["queryStringParameters"]:
            logging.error("required scope set") #debugging
            
            if event["queryStringParameters"]["scope"] == "singleuser":
                logging.error("scope: singleuser") #debugging
                if "user_id" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                user_id = event["queryStringParameters"]["user_id"]
                sql_query_result = get_orders_for_user(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
        
            elif event["queryStringParameters"]["scope"] == "alluserspaginated":
                logging.error("scope: alluserspaginated") #debugging
                if "after_id" in event["queryStringParameters"] and "limit" in event["queryStringParameters"]:
                    after_id = event["queryStringParameters"]["after_id"]
                    limit = event["queryStringParameters"]["limit"]
                else:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                
                sql_query_result = get_all_orders_paginated(RDS_secret_host, RDS_secret_user, RDS_secret_pass, after_id, limit)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "singleuserpaginated":
                logging.error("scope: singleuserpaginated") #debugging
                if "user_id" in event["queryStringParameters"] and "after_id" in event["queryStringParameters"] and "limit" in event["queryStringParameters"]:
                    user_id = event["queryStringParameters"]["user_id"]
                    after_id = event["queryStringParameters"]["after_id"]
                    limit = event["queryStringParameters"]["limit"]
                else:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                
                sql_query_result = get_all_orders_single_user_paginated(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, after_id, limit)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
                    
            elif event["queryStringParameters"]["scope"] == "ddos":
                logging.error("scope: ddos") #debugging
                if "threshold" in event["queryStringParameters"]:
                    threshold = event["queryStringParameters"]["threshold"]
                else:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                
                sql_query_result = get_user_ids_above_threshold(RDS_secret_host, RDS_secret_user, RDS_secret_pass, threshold)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
        
        else:          
            logging.error("queryStringParameters missing") #debugging
            responseObject["statusCode"] = 400
            responseObject["body"] = json.dumps("queryStringParameters missing")
            return responseObject

    #IF POST
    if event["httpMethod"] == "POST":
        logging.error("httpMethod: POST") #debugging
        if "user_id" in event["queryStringParameters"] and "order_id" in event["queryStringParameters"] and "current_us_state" in event["queryStringParameters"]:
            user_id = event["queryStringParameters"]["user_id"]
            order_id = event["queryStringParameters"]["order_id"]
            current_us_state = event["queryStringParameters"]["current_us_state"]
            purchased_tier = event["queryStringParameters"]["purchased_tier"]
            purchased_months = event["queryStringParameters"]["purchased_months"]
            payment_amount_in_usd = event["queryStringParameters"]["payment_amount_in_usd"]
            sql_query_result = insert_order_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, current_us_state, order_id, purchased_tier, purchased_months, payment_amount_in_usd)
            responseObject["body"] = json.dumps(sql_query_result)
            return responseObject

        else:
            logging.error("queryStringParameters missing") #debugging
            responseObject["body"] = json.dumps("queryStringParameters missing")
            responseObject["statusCode"] = 400
            return responseObject
    
    #IF DELETE
    if event["httpMethod"] == "DELETE":
        logging.error("httpMethod: DELETE") #debugging
        if "order_id" in event["queryStringParameters"]:
            order_id = event["queryStringParameters"]["order_id"]
            sql_query_result = delete_order_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, order_id)
            responseObject["body"] = json.dumps(sql_query_result)
            return responseObject
        elif "epoch_time_created" in event["queryStringParameters"]:
            epoch_time_created = event["queryStringParameters"]["epoch_time_created"]
            sql_query_result = delete_orders_less_than_epoch(RDS_secret_host, RDS_secret_user, RDS_secret_pass, epoch_time_created)
            responseObject["body"] = json.dumps(sql_query_result)
            return responseObject
        elif "user_id" in event["queryStringParameters"]:
            user_id = event["queryStringParameters"]["user_id"]
            sql_query_result = delete_user_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id)
            responseObject["body"] = json.dumps(sql_query_result)
            return responseObject
        else:
            logging.error("queryStringParameters missing") #debugging
            responseObject["body"] = json.dumps("queryStringParameters missing")
            responseObject["statusCode"] = 400
            return responseObject
                

#########################
##### query params ######
#########################

#GET - orders associated with a single user
#?user_id=user_id&scope=singleuser

#GET - all orders paginated
#?limit=200&after_id=0&scope=alluserspaginated

#GET - single user orders paginated
#?user_id=user_id&limit=200&after_id=0&scope=singleuserpaginated

#GET - get all user_ids above threshold
#?threshold=20&scope=ddos

#POST - insert order_id
#?user_id=50&current_us_state=Washington&order_id=order_id_string

#DELETE - delete single order
#?order_id=order_id_string

#DELETE - delete orders older than input epoch time (less than)
#?epoch_time_created=123456789

#DELETE - delete all orders associated with a specific user
#?user_id=1

