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

    logging.error("retrieve RDS secrets for CSR-primary-serverless-db-1-tf")
    RDS_secret_return = aws_functions_for_lambda.get_aws_secret("CSR-primary-serverless-db-1-tf")
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

    #CREATE USERS TABLE
    create_users_table_query = """
    CREATE TABLE users(
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        identity_provider_sub_id VARCHAR(150),
        identity_provider VARCHAR(40),
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        email_address VARCHAR(320),
        email_verified VARCHAR(5),
        timezone VARCHAR(100),
        geo_location VARCHAR(100),
        last_login_epoch INT,
        time_created_epoch INT,
        brand_ambassador VARCHAR(5) DEFAULT 'False',
	    site_metrics_viewer VARCHAR(5) DEFAULT 'False',
	    site_admin_full VARCHAR(5) DEFAULT 'False',
        persona_user_id VARCHAR(40) DEFAULT NULL,
        persona_verification_status INT DEFAULT 1
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

    #CREATE pending_payments TABLE
    create_pending_payments_table_query = """
    CREATE TABLE pending_payments(
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        order_id VARCHAR(200),
        current_us_state VARCHAR(200),
        epoch_time_created INT,
        purchased_tier INT,
        purchased_months INT,
        payment_amount_in_usd INT
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
                cursor.execute(create_pending_payments_table_query)
                connection.commit()

    except Error as e:
        print(e)

    #CREATE USER PROFILE TABLE
    create_users_table_query = """
    CREATE TABLE users_profile(
        user_id INT PRIMARY KEY,
        time_created_epoch INT,
        time_zone VARCHAR(50),
        country_of_residence VARCHAR(100),
        state_of_residence VARCHAR(100),
        fiat_payment_gateway_customer_id VARCHAR(320),
        crypto_payment_gateway_customer_id VARCHAR(320),
        language_perf VARCHAR(50),
        dark_mode_light_mode VARCHAR(20)
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

    #CREATE USER PROFILE TABLE
    create_users_table_query = """
    CREATE TABLE brand_ambassador_referral_codes(
        user_id INT PRIMARY KEY,
        referral_code VARCHAR(200),
        revenue_share_percentage INT
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


    #CREATE users_subscription_status TABLE
    create_users_table_query = """
    CREATE TABLE users_subscription_status(
        user_id INT PRIMARY KEY,
        subscription_status VARCHAR(50),
        subscription_tier VARCHAR(50),
        number_of_transactions_this_month_exceeds_tier VARCHAR(5),
        dollar_amount_of_transactions_this_month_exceeds_tier VARCHAR(5),
        number_of_transactions_this_month INT,
        dollar_amount_of_transactions_this_month INT,
        tier_locked_by_admin VARCHAR(5)
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


    #CREATE users_payments TABLE
    create_users_table_query = """
    CREATE TABLE users_payments(
        user_id INT PRIMARY KEY,
        epoch_of_payment INT,
        payment_provider VARCHAR(50),
        payment_amount_in_usd INT,
        number_of_months_paid_for INT,
        tier_paid_for VARCHAR(10),
        sales_tax_jurisdiction VARCHAR(100)
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



    #CREATE user_behavior_logs TABLE
    create_users_table_query = """
    CREATE TABLE user_behavior_logs(
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        epoch_time INT,
        user_action VARCHAR(100),
        is_suspicious VARCHAR(5),
        is_error VARCHAR(5)
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


    #CREATE dca_schedule_ TABLE
    list_of_coins_to_schedule = ["btc", "eth", "ltc"]
    for coin in list_of_coins_to_schedule:
        create_dca_schedule_table_query = """
        CREATE TABLE dca_schedule_%s(
            user_id INT PRIMARY KEY,
            interval_time INT UNSIGNED,
            interval_denomination VARCHAR(200),
            interval_time_in_seconds INT UNSIGNED,
            fiat_amount INT UNSIGNED,
            fiat_denomination VARCHAR(5),
            date_schedule_created_epoch INT UNSIGNED,
            first_run_epoch INT UNSIGNED,
            last_run_epoch INT UNSIGNED,
            next_run_epoch INT UNSIGNED,
            high_availability_type VARCHAR(200),
            exchange_priority_1 VARCHAR(200),
            exchange_priority_2 VARCHAR(200),
            exchange_priority_3 VARCHAR(200),
            exchange_priority_4 VARCHAR(200),
            exchange_priority_5 VARCHAR(200),
            exchange_priority_6 VARCHAR(200),
            exchange_priority_7 VARCHAR(200),
            exchange_priority_8 VARCHAR(200),
            exchange_priority_9 VARCHAR(200),
            exchange_priority_10 VARCHAR(200),
            exchange_priority_11 VARCHAR(200),
            exchange_priority_12 VARCHAR(200),
            exchange_priority_13 VARCHAR(200),
            exchange_priority_14 VARCHAR(200),
            exchange_priority_15 VARCHAR(200),
            exchange_priority_16 VARCHAR(200),
            exchange_priority_17 VARCHAR(200),
            exchange_priority_18 VARCHAR(200),
            exchange_priority_19 VARCHAR(200),
            exchange_priority_20 VARCHAR(200),
            exchange_last_run VARCHAR(200)
        )
        """ % coin

        try:
            with connect(
                host=RDS_secret_host,
                user=RDS_secret_user,
                password=RDS_secret_pass,
                database="CSR",
            ) as connection:
                print(connection)

                with connection.cursor() as cursor:
                    cursor.execute(create_dca_schedule_table_query)
                    connection.commit()

        except Error as e:
            print(e)

    #CREATE general_event_log
    create_users_table_query = """
    CREATE TABLE general_event_log(
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        epoch_time INT,
        event VARCHAR(500),
        source VARCHAR(500)
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


    #CREATE dca_purchase_logs
    dca_purchase_logs_table_query = """
    CREATE TABLE dca_purchase_logs(
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        epoch_time INT,
        was_successful VARCHAR(5),
        coin_purchased VARCHAR(25),
        fiat_amount INT,
        fiat_denomination VARCHAR(25),
        exchange_used VARCHAR(40),
        interval_time_in_seconds INT,
        high_availability_type VARCHAR(20),
        exchange_order_id VARCHAR(300),
        failure_reason VARCHAR(100)
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
                cursor.execute(dca_purchase_logs_table_query)
                connection.commit()

    except Error as e:
        print(e)


    #CREATE user_subscription_status
    user_subscription_status = """
    CREATE TABLE user_subscription_status(
        user_id INT PRIMARY KEY,
        referral_code VARCHAR(200),
        subscription_tier INT DEFAULT 1,
        tier_locked_by_admin VARCHAR(5) DEFAULT 'False',
        number_of_transactions_this_month INT DEFAULT 0,
        dollar_amount_of_transactions_this_month INT DEFAULT 0,
        total_number_of_transactions INT DEFAULT 0,
        total_dollar_amount_of_transactions INT DEFAULT 0,
        fiat_payment_gateway_customer_id VARCHAR(400),
        fiat_payment_provider VARCHAR(400)
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
                cursor.execute(user_subscription_status)
                connection.commit()

    except Error as e:
        print(e)

    #CREATE failed_dca_counter
    create_table_query = """
    CREATE TABLE failed_dca_counter(
        user_id INT PRIMARY KEY,
        failed_dca_counter INT DEFAULT 0
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
                cursor.execute(create_table_query)
                connection.commit()

    except Error as e:
        print(e)

    #CREATE api_key_submission_counter
    create_table_query = """
    CREATE TABLE api_key_submission_counter(
        user_id INT PRIMARY KEY,
        api_key_submission_counter_hourly INT DEFAULT 0,
        api_key_submission_counter_all_time INT DEFAULT 0
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
                cursor.execute(create_table_query)
                connection.commit()

    except Error as e:
        print(e)

    #CREATE user_payments
    user_payments = """
    CREATE TABLE user_payments(
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        epoch_of_payment INT,
        payment_provider VARCHAR(200),
        crypto_or_fiat_gateway VARCHAR(200),
        order_id VARCHAR(1000),
        payment_amount_in_usd INT,
        number_of_months_paid_for INT,
        tier_paid_for INT,
        epoch_expiration INT,
        description VARCHAR(200),
        referral_code VARCHAR(200),
        account_created_epoch INT,
        current_us_state VARCHAR(200)
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
                cursor.execute(user_payments)
                connection.commit()

    except Error as e:
        print(e)


    #Create subscription_tier table
    create_users_table_query = """
    CREATE TABLE subscription_tier(
        subscription_tier INT,
        number_of_transactions INT,
        fiat_amount_of_transactions INT
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

    #Create pricing_tier_two table
    create_users_table_query = """
    CREATE TABLE pricing_tier(
        subscription_tier INT,
        months INT,
        due_at_purchase INT
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

    #Create newsletter_subscription table
    create_users_table_query = """
    CREATE TABLE newsletter_subscription(
        email_address VARCHAR(500) PRIMARY KEY,
        subscription_status VARCHAR(20),
        initial_signup_epoch INT,
        status_changed_epoch INT
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


    #Create giveaway_signup table
    create_users_table_query = """
    CREATE TABLE giveaway_signup(
        email_address VARCHAR(500),
        month_of_giveaway INT,
        year_of_giveaway INT,
        signup_epoch INT
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


    #Create coinbase_pro_api_keys_metadata table (metadata)
    create_users_table_query = """
    CREATE TABLE coinbase_pro_api_keys_metadata(
        user_id INT PRIMARY KEY,
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

    #Create kraken_api_keys table (metadata)
    create_users_table_query = """
    CREATE TABLE kraken_api_keys_metadata(
        user_id INT PRIMARY KEY,
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

    #Create bittrex_api_keys table (metadata)
    create_users_table_query = """
    CREATE TABLE bittrex_api_keys_metadata(
        user_id INT PRIMARY KEY,
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

    #Create gemini_api_keys table (metadata)
    create_users_table_query = """
    CREATE TABLE gemini_api_keys_metadata(
        user_id INT PRIMARY KEY,
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

    #Create binance_us_api_keys table (metadata)
    create_users_table_query = """
    CREATE TABLE binance_us_api_keys_metadata(
        user_id INT PRIMARY KEY,
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


    #Create crypto_com_api_keys table (metadata)
    create_users_table_query = """
    CREATE TABLE crypto_com_api_keys_metadata(
        user_id INT PRIMARY KEY,
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


    #Create ftx_us_api_keys table (metadata)
    create_users_table_query = """
    CREATE TABLE ftx_us_api_keys_metadata(
        user_id INT PRIMARY KEY,
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


    #Create daily_user_metrics table
    create_users_table_query = """
    CREATE TABLE daily_user_metrics(
        id INT AUTO_INCREMENT PRIMARY KEY,
        epoch_time INT,
        iso_date VARCHAR(200),
        total_users INT,
        user_subscription_status_users INT,
        verified_users INT,
        paying_users INT,
        payments_1_month INT,
        payments_3_month INT,
        payments_6_month INT,
        payments_12_month INT,
        payments_1200_month INT,
        payments_tier_2 INT,
        payments_tier_3 INT,
        users_logged_in_past_24_hours INT,
        users_logged_in_past_48_hours INT,
        users_logged_in_past_168_hours INT,
        users_logged_in_past_336_hours INT,
        users_logged_in_past_720_hours INT,
        active_schedules_btc INT,
        active_schedules_eth INT,
        active_schedules_ltc INT,
        active_schedules_ha_type_failover INT,
        active_schedules_ha_type_round_robin INT,
        active_schedules_ha_type_simultaneous INT,
        active_schedules_ha_type_single_exchange INT,
        active_schedules_dca_logs_past_30_days INT
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


    #Create daily_revenue_metrics table
    create_users_table_query = """
    CREATE TABLE daily_revenue_metrics(
        id INT AUTO_INCREMENT PRIMARY KEY,
        epoch_time INT,
        iso_date VARCHAR(200),
        gross_revenue_past_24_hours INT,
        gross_revenue_past_7_days INT,
        gross_revenue_past_rolling_30_days INT,
        gross_revenue_past_previous_month INT,
        gross_revenue_past_month_to_date INT,
        gross_revenue_past_previous_quarter INT,
        gross_revenue_past_quarter_to_date INT,
        gross_revenue_past_previous_year INT,
        gross_revenue_past_year_to_date INT,
        gross_revenue_past_rolling_1_year INT,
        gross_revenue_past_all_time INT
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

