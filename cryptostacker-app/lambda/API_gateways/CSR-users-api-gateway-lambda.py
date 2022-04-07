#pip install mysql-connector-python
from mysql.connector import connect, Error
import logging
import aws_functions_for_lambda
import json
import datetime
import uuid
import CSR_service_mesh_map
import CSR_toolkit
#import pytz

def retrieve_identity_provider_sub_id_func(RDS_secret_host, RDS_secret_user, RDS_secret_pass, identity_provider_sub_id):
    logging.critical("retrieve_identity_provider_sub_id_func()")
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
            FROM users
            WHERE identity_provider_sub_id = %s
            """

            select_user_tuple = (identity_provider_sub_id, )

            with connection.cursor() as cursor:
                cursor.execute(select_user_query, select_user_tuple)
                sql_query_result = cursor.fetchone() 
                logging.error(sql_query_result) #debugging
        
        return sql_query_result

    except Error as e:
        print(e)

def retrieve_users_from_email_address(RDS_secret_host, RDS_secret_user, RDS_secret_pass, email_address):
    logging.critical("retrieve_users_from_email_address()")
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
            FROM users
            WHERE email_address = %s
            """

            select_user_tuple = (email_address, )

            with connection.cursor() as cursor:
                cursor.execute(select_user_query, select_user_tuple)
                sql_query_result = cursor.fetchmany(size=100)
                logging.error(sql_query_result) #debugging
        
        return sql_query_result

    except Error as e:
        print(e)

def retrieve_users_from_user_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id):
    logging.critical("retrieve_users_from_user_id()")
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
            FROM users
            WHERE user_id = %s
            """

            select_user_tuple = (int(user_id), )

            with connection.cursor() as cursor:
                cursor.execute(select_user_query, select_user_tuple)
                sql_query_result = cursor.fetchone() 
                logging.error(sql_query_result) #debugging
        
        return sql_query_result

    except Error as e:
        print(e)


def retrieve_users_by_verification_status_paginated(RDS_secret_host, RDS_secret_user, RDS_secret_pass, verification_status_threshold, user_id, limit):
    logging.critical("retrieve_users_from_by_verification_status_paginated()")
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

            select_user_query = """
            SELECT *
            FROM users
            WHERE persona_verification_status < %s AND user_id > %s
            LIMIT %s
            """

            select_user_tuple = (int(verification_status_threshold), int(user_id), int(limit), )

            with connection.cursor() as cursor:
                cursor.execute(select_user_query, select_user_tuple)
                sql_query_result = cursor.fetchall()
                logging.error(sql_query_result) #debugging
        
        return sql_query_result

    except Error as e:
        print(e)

def update_persona_verification_status(RDS_secret_host, RDS_secret_user, RDS_secret_pass, persona_verification_status, user_id):
    logging.critical("update_persona_verification_status()")
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            update_users_query = """
            UPDATE users
            SET persona_verification_status = %s
            WHERE user_id = %s
            """

            user_records = (int(persona_verification_status), int(user_id), )

            with connection.cursor() as cursor:
                cursor.execute(update_users_query, user_records)
                connection.commit()
                logging.error("record update") #debugging

        return "record updated"

    except Error as e:
        print(e)




def delete_user_sql_call(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id):
    logging.critical("delete_user_sql_call() called")
    logging.error("user_id: %s" % user_id) #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging
        
            delete_user_query = """
            Delete
            FROM users
            WHERE user_id = %s
            """

            user_tuple = (int(user_id), )

            with connection.cursor() as cursor:
                cursor.execute(delete_user_query, user_tuple)
                connection.commit()

            logging.error("returning: success")
            return "success"

    except Error as e:
        print(e)


def count_unique_users(RDS_secret_host, RDS_secret_user, RDS_secret_pass):
    logging.critical("count_unique_users()")
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_user_query = """
            SELECT COUNT(DISTINCT user_id) unique_users
            FROM users
            """

            with connection.cursor() as cursor:
                cursor.execute(select_user_query)
                sql_query_result = cursor.fetchone()
                logging.error(sql_query_result) #debugging
        
        if sql_query_result[0] == None: #if None return empty list
            sql_query_result = []
            return sql_query_result
        elif isinstance(sql_query_result[0], type(None)): #if None return empty list
            sql_query_result = []
            return sql_query_result
        else:
            try:
                return [int(float(sql_query_result[0]))]
            except:
                return sql_query_result

    except Error as e:
        print(e)

def count_verified_users(RDS_secret_host, RDS_secret_user, RDS_secret_pass):
    logging.critical("count_verified_users()")
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_user_query = """
            SELECT COUNT(DISTINCT user_id) unique_users
            FROM users
            WHERE persona_verification_status = 3
            """

            with connection.cursor() as cursor:
                cursor.execute(select_user_query)
                sql_query_result = cursor.fetchone()
                logging.error(sql_query_result) #debugging
        
        if sql_query_result[0] == None: #if None return empty list
            sql_query_result = []
            return sql_query_result
        elif isinstance(sql_query_result[0], type(None)): #if None return empty list
            sql_query_result = []
            return sql_query_result
        else:
            try:
                return [int(float(sql_query_result[0]))]
            except:
                return sql_query_result

    except Error as e:
        print(e)


def count_users_logged_in_last_n_hours(RDS_secret_host, RDS_secret_user, RDS_secret_pass, last_n_hours):
    logging.critical("count_users_logged_in_last_n_hours()")
    last_n_hours = int(last_n_hours) * -1
    epoch_last_login_n_hours_ago = CSR_toolkit.epoch_plus_hours_epoch(CSR_toolkit.current_time_epoch(), last_n_hours)

    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_user_query = """
            SELECT COUNT(DISTINCT user_id) unique_users
            FROM users
            WHERE last_login_epoch > %s
            """

            last_login_tuple = (int(epoch_last_login_n_hours_ago), )

            with connection.cursor() as cursor:
                cursor.execute(select_user_query, last_login_tuple)
                sql_query_result = cursor.fetchone()
                logging.error(sql_query_result) #debugging
        
        if sql_query_result[0] == None: #if None return empty list
            sql_query_result = []
            return sql_query_result
        elif isinstance(sql_query_result[0], type(None)): #if None return empty list
            sql_query_result = []
            return sql_query_result
        else:
            try:
                return [int(float(sql_query_result[0]))]
            except:
                return sql_query_result

    except Error as e:
        print(e)


def lambda_handler(event, context):
    #configure logging
    logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

    responseObject = {}
    responseObject["statusCode"] = 200
    responseObject["headers"] = {}
    responseObject["headers"]["Content-Type"] = "application/json" 

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
            logging.error("scope in event[queryStringParameters]") #debugging

            if event["queryStringParameters"]["scope"] == "retrieve_users_by_verification_status_paginated":
                verification_status_threshold = event["queryStringParameters"]["verification_status_threshold"]
                user_id = event["queryStringParameters"]["user_id"]
                limit = event["queryStringParameters"]["limit"]
                sql_query_result = retrieve_users_by_verification_status_paginated(RDS_secret_host, RDS_secret_user, RDS_secret_pass, verification_status_threshold, user_id, limit)
                
                if not sql_query_result:
                    responseObject["body"] = json.dumps([])
                    return responseObject

                responseObject["body"] = json.dumps(sql_query_result)
                return responseObject

            if event["queryStringParameters"]["scope"] == "count_unique_users":
                sql_query_result = count_unique_users(RDS_secret_host, RDS_secret_user, RDS_secret_pass)
                
                if not sql_query_result:
                    responseObject["body"] = json.dumps([0])
                    return responseObject

                responseObject["body"] = json.dumps(sql_query_result)
                return responseObject

            if event["queryStringParameters"]["scope"] == "count_verified_users":
                sql_query_result = count_verified_users(RDS_secret_host, RDS_secret_user, RDS_secret_pass)
                
                if not sql_query_result:
                    responseObject["body"] = json.dumps([0])
                    return responseObject

                responseObject["body"] = json.dumps(sql_query_result)
                return responseObject

            if event["queryStringParameters"]["scope"] == "count_users_logged_in_last_n_hours":
                last_n_hours = event["queryStringParameters"]["last_n_hours"]
                sql_query_result = count_users_logged_in_last_n_hours(RDS_secret_host, RDS_secret_user, RDS_secret_pass, last_n_hours)
                
                if not sql_query_result:
                    responseObject["body"] = json.dumps([0])
                    return responseObject

                responseObject["body"] = json.dumps(sql_query_result)
                return responseObject

        if "identity_provider_sub_id" in event["queryStringParameters"]:
            identity_provider_sub_id = event["queryStringParameters"]["identity_provider_sub_id"]
            sql_query_result = retrieve_identity_provider_sub_id_func(RDS_secret_host, RDS_secret_user, RDS_secret_pass, identity_provider_sub_id)
            if not sql_query_result:
                responseObject["body"] = json.dumps("None") #todo: this should be [] but that will be a breaking change downstream
                return responseObject

            responseObject["body"] = json.dumps(sql_query_result)
            return responseObject

        elif "email_address" in event["queryStringParameters"]:
            email_address = event["queryStringParameters"]["email_address"]
            sql_query_result = retrieve_users_from_email_address(RDS_secret_host, RDS_secret_user, RDS_secret_pass, email_address)
            if not sql_query_result:
                responseObject["body"] = json.dumps("[]") #todo: this should be [] but that will be a breaking change downstream
                return responseObject

            responseObject["body"] = json.dumps(sql_query_result)
            return responseObject

        elif "user_id" in event["queryStringParameters"]:
            user_id = event["queryStringParameters"]["user_id"]
            sql_query_result = retrieve_users_from_user_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id)
            if not sql_query_result:
                responseObject["body"] = json.dumps("[]") #todo: this should be [] but that will be a breaking change downstream
                return responseObject

            responseObject["body"] = json.dumps(sql_query_result)
            return responseObject
        
        else:
            logging.error("queryStringParameters missing - 1") #debugging
            responseObject["body"] = json.dumps("queryStringParameters missing")
            responseObject["statusCode"] = 400
            return responseObject


    #IF POST
    if event["httpMethod"] == "POST":
        logging.error("httpMethod: POST") #debugging
        if "identity_provider_sub_id" in event["queryStringParameters"] and "update" not in event["queryStringParameters"]:
            logging.error("all params provided") #debugging
            identity_provider_sub_id = event["queryStringParameters"]["identity_provider_sub_id"]
            first_name = event["queryStringParameters"]["first_name"]
            last_name = event["queryStringParameters"]["last_name"]
            email_address = event["queryStringParameters"]["email_address"]
            email_verified = event["queryStringParameters"]["email_verified"]
            timezone = "None"
            geo_location = "None"
            last_login_epoch = CSR_toolkit.current_time_epoch()
            identity_provider = "auth0" #hard coded for now since auth0 is the exclusive IDP at the moment
            
            #create result object to check to see if user already exists
            retrieve_identity_provider_sub_id_result = retrieve_identity_provider_sub_id_func(RDS_secret_host, RDS_secret_user, RDS_secret_pass, identity_provider_sub_id)

            if retrieve_identity_provider_sub_id_result:
                #if user already exists, update user
                try:
                    with connect(
                        host=RDS_secret_host,
                        user=RDS_secret_user,
                        password=RDS_secret_pass,
                        database="CSR",
                    ) as connection:
                        logging.error(connection) #debugging

                        update_users_query = """
                        UPDATE users
                        SET identity_provider = %s,
                        first_name = %s,
                        last_name = %s,
                        email_address = %s,
                        email_verified = %s,
                        timezone = %s,
                        geo_location = %s,
                        last_login_epoch = %s
                        WHERE identity_provider_sub_id = %s
                        """

                        user_records = (identity_provider, first_name, last_name, email_address, email_verified, timezone, geo_location, last_login_epoch, str(identity_provider_sub_id), )

                        with connection.cursor() as cursor:
                            cursor.execute(update_users_query, user_records)
                            connection.commit()
                            logging.error(cursor.rowcount, "record(s) affected") #debugging

                except Error as e:
                    print(e)

                responseObject["body"] = json.dumps("User already exists, user updated")
                return responseObject

            if not retrieve_identity_provider_sub_id_result:
                #if user doesn't already exist, create user
                time_created_epoch = datetime.datetime.now().strftime('%s') #set current epoch time
                persona_user_id = str(uuid.uuid4())

                try:
                    with connect(
                        host=RDS_secret_host,
                        user=RDS_secret_user,
                        password=RDS_secret_pass,
                        database="CSR",
                    ) as connection:
                        logging.error(connection) #debugging

                        insert_users_query = """
                        INSERT INTO users
                        (identity_provider_sub_id,
                        identity_provider,
                        first_name,
                        last_name, 
                        email_address,
                        email_verified,
                        timezone,
                        geo_location,
                        last_login_epoch,
                        time_created_epoch,
                        persona_user_id)
                        VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
                        """

                        user_records_tuple = (identity_provider_sub_id, identity_provider, first_name, last_name, email_address, email_verified, timezone, geo_location, last_login_epoch, time_created_epoch, str(persona_user_id), )

                        with connection.cursor() as cursor:
                            cursor.execute(insert_users_query, user_records_tuple)
                            connection.commit()

                    responseObject["body"] = json.dumps("User didn't already exist, user created")
                    return responseObject

                except Error as e:
                    print(e)
        
        elif "identity_provider_sub_id" in event["queryStringParameters"] and "update" in event["queryStringParameters"]:
            if event["queryStringParameters"]["update"] == "standard":
                logging.error("all params provided - update standard") #debugging
                identity_provider_sub_id = event["queryStringParameters"]["identity_provider_sub_id"]
                first_name = event["queryStringParameters"]["first_name"]
                last_name = event["queryStringParameters"]["last_name"]
                email_address = event["queryStringParameters"]["email_address"]
                email_verified = event["queryStringParameters"]["email_verified"]
                last_login_epoch = CSR_toolkit.current_time_epoch()
                identity_provider = "auth0" #hard coded for now since auth0 is the exclusive IDP at the moment
                
                #create result object to check to see if user already exists
                retrieve_identity_provider_sub_id_result = retrieve_identity_provider_sub_id_func(RDS_secret_host, RDS_secret_user, RDS_secret_pass, identity_provider_sub_id)

                if retrieve_identity_provider_sub_id_result:
                    #if user already exists, update user
                    try:
                        with connect(
                            host=RDS_secret_host,
                            user=RDS_secret_user,
                            password=RDS_secret_pass,
                            database="CSR",
                        ) as connection:
                            logging.error(connection) #debugging

                            update_users_query = """
                            UPDATE users
                            SET identity_provider = %s,
                            first_name = %s,
                            last_name = %s,
                            email_address = %s,
                            email_verified = %s,
                            last_login_epoch = %s
                            WHERE identity_provider_sub_id = %s
                            """

                            user_records = (identity_provider, first_name, last_name, email_address, email_verified, last_login_epoch, identity_provider_sub_id, )

                            with connection.cursor() as cursor:
                                cursor.execute(update_users_query, user_records)
                                connection.commit()
                                logging.error("record updated") #debugging

                    except Error as e:
                        print(e)

                    responseObject["body"] = json.dumps("User already exists, user updated - update standard")
                    return responseObject
            
            if event["queryStringParameters"]["update"] == "geolocation_and_timezone":
                logging.error("all params provided - update geolocation_and_timezone") #debugging
                identity_provider_sub_id = event["queryStringParameters"]["identity_provider_sub_id"]
                timezone = event["queryStringParameters"]["timezone"]
                geo_location = event["queryStringParameters"]["geo_location"]
                
                #create result object to check to see if user already exists
                retrieve_identity_provider_sub_id_result = retrieve_identity_provider_sub_id_func(RDS_secret_host, RDS_secret_user, RDS_secret_pass, identity_provider_sub_id)

                if retrieve_identity_provider_sub_id_result:
                    #if user already exists, update user
                    try:
                        with connect(
                            host=RDS_secret_host,
                            user=RDS_secret_user,
                            password=RDS_secret_pass,
                            database="CSR",
                        ) as connection:
                            logging.error(connection) #debugging

                            update_users_query = """
                            UPDATE users
                            SET timezone = %s,
                            geo_location = %s
                            WHERE identity_provider_sub_id = %s
                            """

                            user_records = (timezone, geo_location, str(identity_provider_sub_id), )

                            with connection.cursor() as cursor:
                                cursor.execute(update_users_query, user_records)
                                connection.commit()
                                logging.error("record update") #debugging

                    except Error as e:
                        print(e)

                    responseObject["body"] = json.dumps("User already exists, user updated - timezone & geo location")
                    return responseObject

            
            if event["queryStringParameters"]["update"] == "firstandlastname":
                logging.error("all params provided - update firstandlastname") #debugging
                identity_provider_sub_id = event["queryStringParameters"]["identity_provider_sub_id"]
                first_name = event["queryStringParameters"]["first_name"]
                last_name = event["queryStringParameters"]["last_name"]
                
                #create result object to check to see if user already exists
                retrieve_identity_provider_sub_id_result = retrieve_identity_provider_sub_id_func(RDS_secret_host, RDS_secret_user, RDS_secret_pass, identity_provider_sub_id)

                if retrieve_identity_provider_sub_id_result:
                    #if user already exists, update user
                    try:
                        with connect(
                            host=RDS_secret_host,
                            user=RDS_secret_user,
                            password=RDS_secret_pass,
                            database="CSR",
                        ) as connection:
                            logging.error(connection) #debugging

                            update_users_query = """
                            UPDATE users
                            SET first_name = %s,
                            last_name = %s
                            WHERE identity_provider_sub_id = %s
                            """

                            user_records = (str(first_name), str(last_name), str(identity_provider_sub_id), )

                            with connection.cursor() as cursor:
                                cursor.execute(update_users_query, user_records)
                                connection.commit()
                                logging.error("record update") #debugging

                    except Error as e:
                        print(e)

                    responseObject["body"] = json.dumps("User already exists, user updated - first & last name")
                    return responseObject

            
            if event["queryStringParameters"]["update"] == "userroles":
                logging.error("all params provided - update user roles") #debugging
                identity_provider_sub_id = event["queryStringParameters"]["identity_provider_sub_id"]
                brand_ambassador = event["queryStringParameters"]["brand_ambassador"]
                site_metrics_viewer = event["queryStringParameters"]["site_metrics_viewer"]
                site_admin_full = event["queryStringParameters"]["site_admin_full"]
                email_address = event["queryStringParameters"]["email_address"]

                #create result object to check to see if user already exists
                retrieve_identity_provider_sub_id_result = retrieve_identity_provider_sub_id_func(RDS_secret_host, RDS_secret_user, RDS_secret_pass, identity_provider_sub_id)

                if retrieve_identity_provider_sub_id_result:
                    #if user already exists, update user
                    try:
                        with connect(
                            host=RDS_secret_host,
                            user=RDS_secret_user,
                            password=RDS_secret_pass,
                            database="CSR",
                        ) as connection:
                            logging.error(connection) #debugging

                            update_users_query = """
                            UPDATE users
                            SET brand_ambassador = %s,
                            site_metrics_viewer = %s,
                            site_admin_full = %s
                            WHERE email_address = %s AND email_verified = 'True'
                            """

                            user_records = (str(brand_ambassador), str(site_metrics_viewer), str(site_admin_full), str(email_address), )

                            with connection.cursor() as cursor:
                                cursor.execute(update_users_query, user_records)
                                connection.commit()
                                logging.error("record update") #debugging

                    except Error as e:
                        print(e)

                    responseObject["body"] = json.dumps("User already exists, user updated - update user roles")
                    return responseObject

            #email_address, email_verified, last_login_epoch
            if event["queryStringParameters"]["update"] == "emailandlogin":
                logging.error("all params provided - emailandlogin") #debugging
                identity_provider_sub_id = event["queryStringParameters"]["identity_provider_sub_id"]
                email_address = event["queryStringParameters"]["email_address"]
                email_verified = event["queryStringParameters"]["email_verified"]
                last_login_epoch = CSR_toolkit.current_time_epoch()
                identity_provider = "auth0" #hard coded for now since auth0 is the exclusive IDP at the moment
                
                try:
                    with connect(
                        host=RDS_secret_host,
                        user=RDS_secret_user,
                        password=RDS_secret_pass,
                        database="CSR",
                    ) as connection:
                        logging.error(connection) #debugging

                        update_users_query = """
                        UPDATE users
                        SET identity_provider = %s,
                        email_address = %s,
                        email_verified = %s,
                        last_login_epoch = %s
                        WHERE identity_provider_sub_id = %s
                        """

                        user_records = (str(identity_provider), str(email_address), str(email_verified), int(last_login_epoch), str(identity_provider_sub_id), )

                        with connection.cursor() as cursor:
                            cursor.execute(update_users_query, user_records)
                            connection.commit()
                            logging.error("record update") #debugging

                except Error as e:
                    print(e)

                responseObject["body"] = json.dumps("User already exists, user updated - emailandlogin")
                return responseObject
        
        elif event["queryStringParameters"]["update"] == "userroles_by_user_id":
            logging.error("update scope: userroles_by_user_id") #debugging
            brand_ambassador = event["queryStringParameters"]["brand_ambassador"]
            site_metrics_viewer = event["queryStringParameters"]["site_metrics_viewer"]
            email_verified = event["queryStringParameters"]["email_verified"]
            user_id = event["queryStringParameters"]["user_id"]

            try:
                with connect(
                    host=RDS_secret_host,
                    user=RDS_secret_user,
                    password=RDS_secret_pass,
                    database="CSR",
                ) as connection:
                    logging.error(connection) #debugging

                    update_users_query = """
                    UPDATE users
                    SET brand_ambassador = %s,
                    site_metrics_viewer = %s,
                    email_verified = %s
                    WHERE user_id = %s
                    """

                    user_records = (str(brand_ambassador), str(site_metrics_viewer), str(email_verified), int(user_id), )

                    with connection.cursor() as cursor:
                        cursor.execute(update_users_query, user_records)
                        connection.commit()
                        logging.error("record update") #debugging

            except Error as e:
                print(e)

            responseObject["body"] = json.dumps("updated user roles")
            return responseObject

        elif event["queryStringParameters"]["update"] == "persona_verification_status":
            logging.error("update scope: persona_verification_status") #debugging
            persona_verification_status = event["queryStringParameters"]["persona_verification_status"]
            user_id = event["queryStringParameters"]["user_id"]

            update_persona_verification_status_response = update_persona_verification_status(RDS_secret_host, RDS_secret_user, RDS_secret_pass, persona_verification_status, user_id)
            responseObject["body"] = json.dumps(str(update_persona_verification_status_response))
            return responseObject
    

    #IF DELETE
    if event["httpMethod"] == "DELETE":
        if "user_id" in event["queryStringParameters"]:
            user_id = event["queryStringParameters"]["user_id"]
            delete_users_result = delete_user_sql_call(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id)
            if delete_users_result == "success":
                logging.error("returning: success")
                responseObject["body"] = json.dumps("success")
                return responseObject
        else:
            responseObject["body"] = json.dumps("queryStringParameters missing")
            logging.error("queryStringParameters missing")
            responseObject["statusCode"] = 400
            return responseObject

    else:
        responseObject["body"] = json.dumps("queryStringParameters missing")
        logging.error("queryStringParameters missing")
        responseObject["statusCode"] = 400
        return responseObject


#GET - scope=count_verified_users


#POST 
#set_brand_ambassador_site_metrics_viewer_email_verified 
#?user_id=1&brand_ambassador=True&site_metrics_viewer=True&email_verified=True&update=userroles_by_user_id
