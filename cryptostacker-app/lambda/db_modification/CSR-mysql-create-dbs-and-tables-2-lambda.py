#todo: needs more DBs & tables
#todo: needs API db aka CSR-primary-serverless-db-2-tf

#pip install mysql-connector-python
from mysql.connector import connect, Error
import os
import logging
import aws_functions_for_lambda
import CSR_toolkit

def lambda_handler(event, context):
    #configure logging
    logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

    #Set creds for API db
    logging.error("retrieve RDS secrets for CSR-primary-serverless-db-2-tf")
    RDS_secret_return = aws_functions_for_lambda.get_aws_secret("CSR-primary-serverless-db-2-tf")
    RDS_secret_dict = eval(str(RDS_secret_return))
    RDS_secret_user = RDS_secret_dict["username"]
    RDS_secret_pass = RDS_secret_dict["password"]
    RDS_secret_host = RDS_secret_dict["host"]
    if RDS_secret_host: #debugging
        logging.error("RDS host set") #debugging
        logging.error(RDS_secret_host) #debugging

    #create "CSR" DATABASE
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
        ) as connection:
            print(connection)
            create_db_query = "CREATE DATABASE CSR"
            with connection.cursor() as cursor:
                cursor.execute(create_db_query)

    except Error as e:
        print(e)

    #CREATE API KEYS TABLES:
    #Create coinbase_pro_api_keys table
    create_users_table_query = """
    CREATE TABLE coinbase_pro_api_keys(
        user_id INT PRIMARY KEY,
        api_key_a VARCHAR(1000),
        api_secret_a VARCHAR(1000),
        api_passphrase_a VARCHAR(1000),
        api_key_a_version VARCHAR(20),
        api_key_b VARCHAR(1000),
        api_secret_b VARCHAR(1000),
        api_passphrase_b VARCHAR(1000),
        api_key_b_version VARCHAR(20),
        keys_created_time_epoch INT,
        keys_expiration_epoch INT
    )
    """

    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            print(connection)

            with connection.cursor() as cursor:
                cursor.execute(create_users_table_query)
                connection.commit()

    except Error as e:
        print(e)

    #Create coinbase_api_keys table
    create_users_table_query = """
    CREATE TABLE coinbase_api_keys(
        user_id INT PRIMARY KEY,
        api_key_a VARCHAR(1000),
        api_secret_a VARCHAR(1000),
        api_passphrase_a VARCHAR(1000),
        api_key_a_version VARCHAR(20),
        api_key_b VARCHAR(1000),
        api_secret_b VARCHAR(1000),
        api_passphrase_b VARCHAR(1000),
        api_key_b_version VARCHAR(20),
        keys_created_time_epoch INT,
        keys_expiration_epoch INT
    )
    """

    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            print(connection)

            with connection.cursor() as cursor:
                cursor.execute(create_users_table_query)
                connection.commit()

    except Error as e:
        print(e)

    #Create kraken_api_keys table
    create_users_table_query = """
    CREATE TABLE kraken_api_keys(
        user_id INT PRIMARY KEY,
        api_key_a VARCHAR(1000),
        api_secret_a VARCHAR(1000),
        api_key_a_version VARCHAR(20),
        api_key_b VARCHAR(1000),
        api_secret_b VARCHAR(1000),
        api_key_b_version VARCHAR(20),
        keys_created_time_epoch INT,
        keys_expiration_epoch INT
    )
    """

    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            print(connection)

            with connection.cursor() as cursor:
                cursor.execute(create_users_table_query)
                connection.commit()

    except Error as e:
        print(e)

    #Create bittrex_api_keys table
    create_users_table_query = """
    CREATE TABLE bittrex_api_keys(
        user_id INT PRIMARY KEY,
        api_key_a VARCHAR(1000),
        api_secret_a VARCHAR(1000),
        api_key_a_version VARCHAR(20),
        api_key_b VARCHAR(1000),
        api_secret_b VARCHAR(1000),
        api_key_b_version VARCHAR(20),
        keys_created_time_epoch INT,
        keys_expiration_epoch INT
    )
    """

    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            print(connection)

            with connection.cursor() as cursor:
                cursor.execute(create_users_table_query)
                connection.commit()

    except Error as e:
        print(e)

    #Create gemini_api_keys table
    create_users_table_query = """
    CREATE TABLE gemini_api_keys(
        user_id INT PRIMARY KEY,
        api_key_a VARCHAR(1000),
        api_secret_a VARCHAR(1000),
        api_key_a_version VARCHAR(20),
        api_key_b VARCHAR(1000),
        api_secret_b VARCHAR(1000),
        api_key_b_version VARCHAR(20),
        keys_created_time_epoch INT,
        keys_expiration_epoch INT
    )
    """

    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            print(connection)

            with connection.cursor() as cursor:
                cursor.execute(create_users_table_query)
                connection.commit()

    except Error as e:
        print(e)

    #Create binance_us_api_keys table
    create_users_table_query = """
    CREATE TABLE binance_us_api_keys(
        user_id INT PRIMARY KEY,
        api_key_a VARCHAR(1000),
        api_secret_a VARCHAR(1000),
        api_key_a_version VARCHAR(20),
        api_key_b VARCHAR(1000),
        api_secret_b VARCHAR(1000),
        api_key_b_version VARCHAR(20),
        keys_created_time_epoch INT,
        keys_expiration_epoch INT
    )
    """

    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            print(connection)

            with connection.cursor() as cursor:
                cursor.execute(create_users_table_query)
                connection.commit()

    except Error as e:
        print(e)


    #Create crypto_com_api_keys table
    create_users_table_query = """
    CREATE TABLE crypto_com_api_keys(
        user_id INT PRIMARY KEY,
        api_key_a VARCHAR(1000),
        api_secret_a VARCHAR(1000),
        api_key_a_version VARCHAR(20),
        api_key_b VARCHAR(1000),
        api_secret_b VARCHAR(1000),
        api_key_b_version VARCHAR(20),
        keys_created_time_epoch INT,
        keys_expiration_epoch INT
    )
    """

    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            print(connection)

            with connection.cursor() as cursor:
                cursor.execute(create_users_table_query)
                connection.commit()

    except Error as e:
        print(e)


    #Create ftx_us_api_keys table
    create_users_table_query = """
    CREATE TABLE ftx_us_api_keys(
        user_id INT PRIMARY KEY,
        api_key_a VARCHAR(1000),
        api_secret_a VARCHAR(1000),
        api_key_a_version VARCHAR(20),
        api_key_b VARCHAR(1000),
        api_secret_b VARCHAR(1000),
        api_key_b_version VARCHAR(20),
        keys_created_time_epoch INT,
        keys_expiration_epoch INT
    )
    """

    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            print(connection)

            with connection.cursor() as cursor:
                cursor.execute(create_users_table_query)
                connection.commit()

    except Error as e:
        print(e)
