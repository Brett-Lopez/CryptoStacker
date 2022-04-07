#pip install mysql-connector-python
from mysql.connector import connect, Error
import logging
import aws_functions_for_lambda
import json
import CSR_service_mesh_map
import CSR_toolkit

def get_failed_dca_counter_row(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id):
    logging.critical("get_failed_dca_counter_row() called") #debugging
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
            FROM failed_dca_counter
            WHERE user_id = %s
            """

            select_user_tuple = (int(user_id), )

            with connection.cursor() as cursor:
                cursor.execute(select_user_query, select_user_tuple)
                sql_query_result = cursor.fetchone()
                #logging.error(sql_query_result) #debugging

        return sql_query_result

    except Error as e:
        print(e)

def insert_failed_count(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, failed_dca_counter):
    logging.critical("insert_failed_count() called") #debugging
   
    if not get_failed_dca_counter_row(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id):
        logging.error("attempting insert") #debugging
        try:
            with connect(
                host=RDS_secret_host,
                user=RDS_secret_user,
                password=RDS_secret_pass,
                database="CSR",
            ) as connection:
                print(connection) #debugging or replace with logging()

                insert_order_id_query = """
                INSERT INTO failed_dca_counter
                (user_id,
                failed_dca_counter)
                VALUES ( %s, %s )
                """
            
                order_id_tuple = (int(user_id), int(failed_dca_counter), )

                with connection.cursor() as cursor:
                    cursor.execute(insert_order_id_query, order_id_tuple)
                    connection.commit()

            return "inserted failed_dca_counter"

        except Error as e:
            print(e)
    else:
        logging.error("attempting update") #debugging
        try:
            with connect(
                host=RDS_secret_host,
                user=RDS_secret_user,
                password=RDS_secret_pass,
                database="CSR",
            ) as connection:
                print(connection) #debugging or replace with logging()

                insert_order_id_query = """
                UPDATE failed_dca_counter
                SET failed_dca_counter = %s
                WHERE user_id = %s
                """

                order_id_tuple = (int(failed_dca_counter), int(user_id), )

                with connection.cursor() as cursor:
                    cursor.execute(insert_order_id_query, order_id_tuple)
                    connection.commit()

            return "updated failed_dca_counter"

        except Error as e:
            print(e)

def count_rows(RDS_secret_host, RDS_secret_user, RDS_secret_pass):
    logging.critical("count_rows() called") #debugging
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
            from failed_dca_counter
            """

            with connection.cursor() as cursor:
                cursor.execute(select_user_query)
                sql_query_result = cursor.fetchone()

        return sql_query_result

    except Error as e:
        print(e)

def increment_counter_by_user_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id):
    logging.critical("increment_counter_by_user_id() called")

    counter_response = get_failed_dca_counter_row(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id)
    if not counter_response:
        logging.error("attempting insert")
        try:
            with connect(
                host=RDS_secret_host,
                user=RDS_secret_user,
                password=RDS_secret_pass,
                database="CSR",
            ) as connection:
                print(connection) #debugging or replace with logging()

                insert_order_id_query = """
                INSERT INTO failed_dca_counter
                (user_id,
                failed_dca_counter)
                VALUES ( %s, %s )
                """

                order_id_tuple = (int(user_id), int(1), )

                with connection.cursor() as cursor:
                    cursor.execute(insert_order_id_query, order_id_tuple)
                    connection.commit()

            return "inserted/incremented failed_dca_counter"

        except Error as e:
            print(e)
    else:
        new_counter_int = int(counter_response[1]) + 1
        try:
            with connect(
                host=RDS_secret_host,
                user=RDS_secret_user,
                password=RDS_secret_pass,
                database="CSR",
            ) as connection:
                print(connection) #debugging or replace with logging()

                update_query = """
                UPDATE failed_dca_counter
                SET failed_dca_counter = %s
                WHERE user_id = %s
                """

                param_tuple = (int(new_counter_int), int(user_id), )

                with connection.cursor() as cursor:
                    cursor.execute(update_query, param_tuple)
                    connection.commit()

            return "updated/incremented failed_dca_counter"

        except Error as e:
            print(e)

def reset_counter_by_user_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id):
    logging.critical("reset_counter_by_user_id() called")
    
    if not get_failed_dca_counter_row(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id):
        logging.error("attempting insert")
        try:
            with connect(
                host=RDS_secret_host,
                user=RDS_secret_user,
                password=RDS_secret_pass,
                database="CSR",
            ) as connection:
                print(connection) #debugging or replace with logging()

                insert_order_id_query = """
                INSERT INTO failed_dca_counter
                (user_id,
                failed_dca_counter)
                VALUES ( %s, %s )
                """

                order_id_tuple = (int(user_id), int(0), )

                with connection.cursor() as cursor:
                    cursor.execute(insert_order_id_query, order_id_tuple)
                    connection.commit()

            return "inserted/reset failed_dca_counter"

        except Error as e:
            print(e)
    else:
        try:
            with connect(
                host=RDS_secret_host,
                user=RDS_secret_user,
                password=RDS_secret_pass,
                database="CSR",
            ) as connection:
                print(connection) #debugging or replace with logging()

                update_query = """
                UPDATE failed_dca_counter
                SET failed_dca_counter = 0
                WHERE user_id = %s
                """

                param_tuple = (int(user_id), )

                with connection.cursor() as cursor:
                    cursor.execute(update_query, param_tuple)
                    connection.commit()

            return "updated/reset failed_dca_counter"

        except Error as e:
            print(e)

def delete_row_by_user_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id):
    logging.critical("delete_row_by_user_id() called") #debugging
    limit_max = 200
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            sql_query = """
            Delete
            FROM failed_dca_counter
            WHERE user_id = %s
            """

            sql_tuple = (int(user_id), )

            with connection.cursor() as cursor:
                cursor.execute(sql_query, sql_tuple)
                connection.commit()

        return "row deleted"

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

    #IF GET
    if event["httpMethod"] == "GET":
        logging.error("httpMethod: GET") #debugging
        if "scope" in event["queryStringParameters"]:
            logging.error("required scope set") #debugging
            if event["queryStringParameters"]["scope"] == "get_failed_dca_counter_row":
                logging.error("scope: get_failed_dca_counter_row") #debugging
                if "user_id" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                user_id = event["queryStringParameters"]["user_id"]
                sql_query_result = get_failed_dca_counter_row(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            elif event["queryStringParameters"]["scope"] == "count_rows":
                logging.error("scope: count_rows") #debugging
                sql_query_result = count_rows(RDS_secret_host, RDS_secret_user, RDS_secret_pass)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            else:
                logging.error("queryStringParameters missing 1") #debugging
                responseObject["statusCode"] = 400
                responseObject["body"] = json.dumps("queryStringParameters missing")
                return responseObject
        else:
            logging.error("queryStringParameters missing 2") #debugging
            responseObject["statusCode"] = 400
            responseObject["body"] = json.dumps("queryStringParameters missing")
            return responseObject

    #IF POST
    if event["httpMethod"] == "POST":
        logging.error("httpMethod: POST") #debugging
        if "user_id" in event["queryStringParameters"] and "scope" in event["queryStringParameters"]:
            if event["queryStringParameters"]["scope"] == "insert_failed_count":
                logging.error("scope: insert_failed_count") #debugging
                user_id = event["queryStringParameters"]["user_id"]
                failed_dca_counter = event["queryStringParameters"]["failed_dca_counter"]
                sql_query_result = insert_failed_count(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, failed_dca_counter)
                responseObject["body"] = json.dumps(sql_query_result)
                return responseObject
            elif event["queryStringParameters"]["scope"] == "reset_counter_by_user_id":
                logging.error("scope: reset_counter_by_user_id") #debugging
                user_id = event["queryStringParameters"]["user_id"]
                sql_query_result = reset_counter_by_user_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id)
                responseObject["body"] = json.dumps(sql_query_result)
                return responseObject
            elif event["queryStringParameters"]["scope"] == "increment_counter_by_user_id":
                logging.error("scope: increment_counter_by_user_id") #debugging
                user_id = event["queryStringParameters"]["user_id"]
                sql_query_result = increment_counter_by_user_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id)
                responseObject["body"] = json.dumps(sql_query_result)
                return responseObject
            else:
                logging.error("queryStringParameters missing 1") #debugging
                responseObject["body"] = json.dumps("queryStringParameters missing")
                responseObject["statusCode"] = 400
                return responseObject
        else:
            logging.error("queryStringParameters missing 2") #debugging
            responseObject["body"] = json.dumps("queryStringParameters missing")
            responseObject["statusCode"] = 400
            return responseObject
    
    #IF DELETE
    if event["httpMethod"] == "DELETE":
        logging.error("httpMethod: DELETE") #debugging
        if "user_id" in event["queryStringParameters"]:
            user_id = event["queryStringParameters"]["user_id"]
            sql_query_result = delete_row_by_user_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id)
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

#GET - retrieve entire row by user_id (single row) - working
#?user_id=1&scope=get_failed_dca_counter_row

#GET - count rows - working
#?scope=count_rows

#POST - insert/update insert_failed_count - working
#?user_id=1&failed_dca_counter=5&scope=insert_failed_count

#POST - increment failed count - 
#?user_id=1&scope=increment_counter_by_user_id

#POST - reset counter by user id - 
#?user_id=1&scope=reset_counter_by_user_id

#DELETE - entire row by user_id - working
#?user_id=1

#=================================================================
