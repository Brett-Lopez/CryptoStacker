# Python standard libraries
import json
import os
import time
import datetime
import logging
import base64
import binascii
import math
import urllib.parse
import threading
import csv

# Third-party libraries
from flask import Flask, redirect, request, url_for, render_template, session, send_file, send_from_directory, abort
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests
import wtforms
import flask_wtf
import wtforms.validators
import flask_session
import redis
import bleach
import pytz
from flask_talisman import Talisman
#from flask_seasurf import SeaSurf

# Internal imports
from user import User
import CSR_toolkit
import CSR_service_mesh_map
import exchange_api_key_validation
import aws_functions
import auth0_lib
import opennode_lib
from crypto_exchange_lib import coinbase_pro_functions


logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

#retrieve secrets from secrets manager
auth0_secret = eval(aws_functions.get_aws_secret("CSR-auth0-api-keys-tf"))
redis_secret = eval(aws_functions.get_aws_secret("CSR-ECS-TASKS-WWW-WEBAPP-REDIS-TF"))
service_mesh_secret_1 = eval(aws_functions.get_aws_secret("CSR-Service-Mesh-Secret_1-TF")) #{'CSR_Service_Mesh_Secret_1': 'test12345'}
app_secret_secret = eval(aws_functions.get_aws_secret("CSR-ECS-TASKS-WWW-WEBAPP-app_secret_key-TF"))
logging.error("testing new version 1") #debugging, used for A/B testing

# AUTH0 oauth2.0 Configuration
AUTH0_CLIENT_ID = auth0_secret["AUTH0_CLIENT_ID"]
AUTH0_DISCOVERY_URL = auth0_secret["AUTH0_DISCOVERY_URL"]

#Price & tier limit maps
csr_price_map = CSR_toolkit.create_csr_price_map(service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]) #example: [[2, 1, 10], [2, 3, 24], [2, 6, 42], [2, 12, 72], [2, 1200, 200], [3, 1, 50], [3, 3, 120], [3, 6, 180], [3, 12, 240], [3, 1200, 650]]
csr_tier_limits_map = CSR_toolkit.create_csr_tier_limits_map(service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]) #example: {'tier1': {'transaction_limit': 10, 'dollar_limit': 100}, 'tier2': {'transaction_limit': 1000, 'dollar_limit': 10000}, 'tier3': {'transaction_limit': 500000000, 'dollar_limit': 500000000}}
csr_price_and_per_month_map_dict = CSR_toolkit.create_csr_price_and_per_month_map_dict(service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]) #example: {'tier2': {'1months': {'total_price': 10, 'price_per_month': 10}, '3months': {'total_price': 24, 'price_per_month': 8}, '6months': {'total_price': 42, 'price_per_month': 7}, '12months': {'total_price': 72, 'price_per_month': 6}, '1200months': {'total_price': 200, 'price_per_month': 0}}, 'tier3': {'1months': {'total_price': 50, 'price_per_month': 50}, '3months': {'total_price': 120, 'price_per_month': 40}, '6months': {'total_price': 180, 'price_per_month': 30}, '12months': {'total_price': 240, 'price_per_month': 20}, '1200months': {'total_price': 650, 'price_per_month': 0}}}

logging.error(csr_price_map)
logging.error(csr_tier_limits_map)
logging.error(csr_price_and_per_month_map_dict)

user_session_datetime_delta = datetime.timedelta(minutes=30) #permanent timeout
#user_session_datetime_delta_inactive_timeout = datetime.timedelta(minutes=30) #inactive_timeout

# Flask app setup
app = Flask(__name__)
#app.secret_key = "SUPER_SECRET_PASSWORD_NOT_FOR_PROD" #local use only
app.secret_key = app_secret_secret["app_secret_key"]
app.config["REMEMBER_COOKIE_DURATION"] = user_session_datetime_delta 
app.config["REMEMBER_COOKIE_HTTPONLY"] = True 
app.config["REMEMBER_COOKIE_REFRESH_EACH_REQUEST"] = False 
app.permanent_session_lifetime = user_session_datetime_delta

content_security_policy = {
        'default-src': [
            '\'self\'',
            'cryptostacker.io',
            '*.cryptostacker.io',
            'unpkg.com',
            'www.googletagmanager.com',
            'www.google-analytics.com'
        ],
        'connect-src': [
            '\'self\'',
            'cryptostacker.io',
            '*.cryptostacker.io',
            'unpkg.com',
            'www.googletagmanager.com',
            'www.google-analytics.com'
        ],
        'img-src': [
            '\'self\'',
            'cryptostacker.io',
            '*.cryptostacker.io',
            'unpkg.com',
            'www.google-analytics.com'
        ],
        'script-src': [
            '\'self\'',
            'cryptostacker.io',
            '*.cryptostacker.io',
            'code.jquery.com',
            'cdn.jsdelivr.net',
            'w3.org',
            'unpkg.com',
            'www.googletagmanager.com'
        ],
        'style-src': [
            '\'self\'',
            'cryptostacker.io',
            '*.cryptostacker.io',
            'code.jquery.com',
            'cdn.jsdelivr.net',
            'fonts.googleapis.com',
            'fonts.gstatic.com',
            'w3.org',
            'unpkg.com'
        ],
        'font-src': [
            '\'self\'',
            'cryptostacker.io',
            '*.cryptostacker.io',
            'fonts.googleapis.com',
            'fonts.gstatic.com'
        ]
}

Talisman(app, force_https=True, content_security_policy=content_security_policy, force_file_save=True)

# User session management setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth0_login"
login_manager.session_protection = "strong"

#setup flask-session for redis server session management
app.config['SESSION_TYPE'] = "redis"
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.from_url("redis://" + redis_secret["primary_endpoint_address"])
session = flask_session.Session(app)

# OAuth 2 client setup for each identity provider
auth0_client = WebApplicationClient(AUTH0_CLIENT_ID)

# Endpoint discovery
def get_auth0_provider_cfg():
    return requests.get(AUTH0_DISCOVERY_URL).json()

def is_float_number(string):
    logging.critical("is_float_number() called")
    try:
        float(string)
        return True
    except ValueError:
        return False

def seconds_to_human_readable(seconds, granularity=4):
    logging.critical("seconds_to_human_readable() called")
    intervals = (
        ('weeks', 604800),  # 60 * 60 * 24 * 7
        ('days', 86400),    # 60 * 60 * 24
        ('hours', 3600),    # 60 * 60
        ('minutes', 60),
        ('seconds', 1),
        )
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])

def trim_sanitize_strip(trim_length, input_string):
    logging.critical("trim_sanitize_strip() called")
    try:
        trimmed_string = str(input_string)[:trim_length]
        trimmed_sanitized = bleach.clean(trimmed_string, strip=True)
        trimmed_sanitized_stripped = trimmed_sanitized.strip()
        return trimmed_sanitized_stripped
    except:
        return ""

def python_sanitize_aggressive(input_string):
    logging.critical("python_sanitize_aggressive() called")
    try:
        python_sanitize_string = input_string.replace("(", "|||")
        python_sanitize_string = python_sanitize_string.replace(")", "&&&")
        python_sanitize_string = python_sanitize_string.replace(",", "^^^")
        python_sanitize_string = python_sanitize_string.replace(";", "***")
        python_sanitize_string = python_sanitize_string.replace("import", "###")
        python_sanitize_string = python_sanitize_string.replace("base64", "###")
        return python_sanitize_string
    except:
        return ""

def python_sanitize_clean(input_string):
    logging.critical("python_sanitize_clean() called")
    try:
        python_sanitize_string = input_string.replace("import", "")
        python_sanitize_string = python_sanitize_string.replace("base64", "")
        return python_sanitize_string
    except:
        return ""

def sanitize_special_chars_and_nums(input_string):
    logging.critical("sanitize_special_chars_and_nums() called")
    try:
        sanitize_string = input_string.replace("!", "")
        sanitize_string = sanitize_string.replace("@", "")
        sanitize_string = sanitize_string.replace("#", "")
        sanitize_string = sanitize_string.replace("$", "")
        sanitize_string = sanitize_string.replace("%", "")
        sanitize_string = sanitize_string.replace("^", "")
        sanitize_string = sanitize_string.replace("&", "")
        sanitize_string = sanitize_string.replace("*", "")
        sanitize_string = sanitize_string.replace("(", "")
        sanitize_string = sanitize_string.replace(")", "")
        sanitize_string = sanitize_string.replace("_", "")
        sanitize_string = sanitize_string.replace("-", "")
        sanitize_string = sanitize_string.replace("+", "")
        sanitize_string = sanitize_string.replace("=", "")
        sanitize_string = sanitize_string.replace("[", "")
        sanitize_string = sanitize_string.replace("{", "")
        sanitize_string = sanitize_string.replace("]", "")
        sanitize_string = sanitize_string.replace("}", "")
        sanitize_string = sanitize_string.replace("\\", "")
        sanitize_string = sanitize_string.replace("|", "")
        sanitize_string = sanitize_string.replace(";", "")
        sanitize_string = sanitize_string.replace(":", "")
        sanitize_string = sanitize_string.replace("'", "")
        sanitize_string = sanitize_string.replace("\"", "")
        sanitize_string = sanitize_string.replace("`", "")
        sanitize_string = sanitize_string.replace("~", "")
        sanitize_string = sanitize_string.replace(".", "")
        sanitize_string = sanitize_string.replace(">", "")
        sanitize_string = sanitize_string.replace("<", "")
        sanitize_string = sanitize_string.replace(",", "")
        sanitize_string = sanitize_string.replace("?", "")
        sanitize_string = sanitize_string.replace("/", "")
        sanitize_string = sanitize_string.replace("1", "")
        sanitize_string = sanitize_string.replace("2", "")
        sanitize_string = sanitize_string.replace("3", "")
        sanitize_string = sanitize_string.replace("4", "")
        sanitize_string = sanitize_string.replace("5", "")
        sanitize_string = sanitize_string.replace("6", "")
        sanitize_string = sanitize_string.replace("7", "")
        sanitize_string = sanitize_string.replace("8", "")
        sanitize_string = sanitize_string.replace("9", "")
        sanitize_string = sanitize_string.replace("0", "")
        sanitize_string = sanitize_string.replace(" ", "")

        return sanitize_string
    except:
        return ""


class ApiKeyFormCoinbase(flask_wtf.FlaskForm):
    form_entered_api_key_plaintext = wtforms.PasswordField('API Key:',validators=[wtforms.validators.DataRequired()])
    form_entered_api_secret_plaintext = wtforms.PasswordField('API Secret:',validators=[wtforms.validators.DataRequired()])
    form_entered_api_passphrase_plaintext = wtforms.PasswordField('API Passphrase:',validators=[wtforms.validators.DataRequired()])
    form_entered_api_key_expires_length = wtforms.SelectField(u'Set key expiration length to automatically delete your key.',
                          choices=[('never', 'never'), ('1month', 'one month from now'), 
                          ('6months', 'six months from now'),
                          ('1year', 'one year from now'), ('3year', 'three years from now')
                          ])
    submit = wtforms.SubmitField('Submit')

class ApiKeyFormStandard(flask_wtf.FlaskForm):
    form_entered_api_key_plaintext = wtforms.PasswordField('API Key:',validators=[wtforms.validators.DataRequired()])
    form_entered_api_secret_plaintext = wtforms.PasswordField('API Secret:',validators=[wtforms.validators.DataRequired()])
    form_entered_api_key_expires_length = wtforms.SelectField(u'Set key expiration length to automatically delete your key.',
                          choices=[('never', 'never'), ('1month', 'one month from now'), 
                          ('6months', 'six months from now'),
                          ('1year', 'one year from now'), ('3year', 'three years from now')
                          ])

    submit = wtforms.SubmitField('Submit')

class DcaSchedulerForm(flask_wtf.FlaskForm):
    form_entered_dollar_amount = wtforms.StringField('Dollars:',validators=[wtforms.validators.DataRequired()])
    form_entered_time_interval = wtforms.StringField('every:',validators=[wtforms.validators.DataRequired()])
    form_entered_time_denomination = wtforms.SelectField(u'',
                          choices=[('minutes', 'Minutes'), ('hours', 'Hours')])

    form_entered_high_availability_type = wtforms.SelectField(u'Choose high availability type:',
                          choices=[('failover', 'Failover'), ('round_robin', 'Round Robin'), 
                          ('simultaneous', 'Simultaneous'), ('single_exchange', 'Single Exchange')])

    form_entered_fiat_denomination = wtforms.SelectField(u'Choose funding source:',
                          choices=[('USD', 'USD on exchange')])

    form_entered_exchange_priority_1 = wtforms.SelectField(u'Set exchange of priority 1',
                          choices=[('not_set', 'Set exchange of priority 1'),
                                   ('coinbase_pro', 'Coinbase Pro'), ('kraken', 'Kraken'),
                                   ('binance_us', 'Binance US'), ('gemini', 'Gemini'),
                                   ('ftx_us', 'FTX US'), ('bittrex', 'Bittrex'),
                                   ('not_set', 'None')
                                   ])

    form_entered_exchange_priority_2 = wtforms.SelectField(u'Set exchange of priority 2',
                          choices=[('not_set', 'Set exchange of priority 2'),
                                   ('coinbase_pro', 'Coinbase Pro'), ('kraken', 'Kraken'),
                                   ('binance_us', 'Binance US'), ('gemini', 'Gemini'),
                                   ('ftx_us', 'FTX US'), ('bittrex', 'Bittrex'),
                                   ('not_set', 'None')
                                   ])

    form_entered_exchange_priority_3 = wtforms.SelectField(u'Set exchange of priority 3',
                          choices=[('not_set', 'Set exchange of priority 3'),
                                   ('coinbase_pro', 'Coinbase Pro'), ('kraken', 'Kraken'),
                                   ('binance_us', 'Binance US'), ('gemini', 'Gemini'),
                                   ('ftx_us', 'FTX US'), ('bittrex', 'Bittrex'),
                                   ('not_set', 'None')
                                   ])

    form_entered_exchange_priority_4 = wtforms.SelectField(u'Set exchange of priority 4',
                          choices=[('not_set', 'Set exchange of priority 4'),
                                   ('coinbase_pro', 'Coinbase Pro'), ('kraken', 'Kraken'),
                                   ('binance_us', 'Binance US'), ('gemini', 'Gemini'),
                                   ('ftx_us', 'FTX US'), ('bittrex', 'Bittrex'),
                                   ('not_set', 'None')
                                   ])

    form_entered_exchange_priority_5 = wtforms.SelectField(u'Set exchange of priority 5',
                          choices=[('not_set', 'Set exchange of priority 5'),
                                   ('coinbase_pro', 'Coinbase Pro'), ('kraken', 'Kraken'),
                                   ('binance_us', 'Binance US'), ('gemini', 'Gemini'),
                                   ('ftx_us', 'FTX US'), ('bittrex', 'Bittrex'),
                                   ('not_set', 'None')
                                   ])

    form_entered_exchange_priority_6 = wtforms.SelectField(u'Set exchange of priority 6',
                          choices=[('not_set', 'Set exchange of priority 6'),
                                   ('coinbase_pro', 'Coinbase Pro'), ('kraken', 'Kraken'),
                                   ('binance_us', 'Binance US'), ('gemini', 'Gemini'),
                                   ('ftx_us', 'FTX US'), ('bittrex', 'Bittrex'),
                                   ('not_set', 'None')
                                   ])

    submit = wtforms.SubmitField('Submit')

class LogViewForm(flask_wtf.FlaskForm):
    form_entered_number_of_log_events = wtforms.SelectField(u'Number of events to view',
                          choices=[('1', 'One'), ('5', 'Five'), 
                          ('10', 'Ten'), ('50', 'Fifty'), ('100', 'One hundred')
                          ])
    form_entered_log_status_events = wtforms.SelectField(u'Status',
                          choices=[('all', 'All'), ('success', 'Success'), ('failed', 'Failed')
                          ])
    form_entered_coin_type_events = wtforms.SelectField(u'Coin',
                          choices=[('all', 'All'), ('btc', 'BTC'), ('eth', 'ETH'), ('ltc', 'LTC')
                          ])
    form_entered_exchange_events = wtforms.SelectField(u'Exchange',
                          choices=[('all', 'All'), ('coinbase_pro', 'Coinbase Pro'), ('bittrex', 'Bittrex'),
                                   ('kraken', 'Kraken'), ('binance_us', 'Binance US'),
                                   ('gemini', 'Gemini'), ('ftx_us', 'FTX US')
                          ])
    submit = wtforms.SubmitField('View events')

class FirstTimeLogin(flask_wtf.FlaskForm):
    form_entered_timezone = wtforms.SelectField(u'Preferred timezone',
                          choices=[('pacific', 'Pacific'), ('mountain', 'Mountain'),
                          ('central', 'Central'), ('eastern', 'Eastern'), 
                          ('alaska', 'Alaska'), ('hawaii', 'Hawaii'), ('arizona', 'Arizona')
                          ])
    form_entered_geo_location = wtforms.SelectField(u'Are you a US resident?',
                          choices=[('yes', 'Yes'), ('no', 'No')
                          ])
    form_entered_referral_code = wtforms.StringField('Enter your referral code:', validators=[wtforms.validators.optional(), wtforms.validators.length(max=200)])
    form_entered_terms_of_service_checkbox = wtforms.BooleanField("Do you agree to the terms of service?")
    form_entered_age_restriction_checkbox = wtforms.BooleanField("Are you at least 18 years old?")
    submit = wtforms.SubmitField('Submit')

class SetTimezoneForm(flask_wtf.FlaskForm):
    form_entered_timezone = wtforms.SelectField(u'Preferred timezone',
                          choices=[('pacific', 'Pacific'), ('mountain', 'Mountain'),
                          ('central', 'Central'), ('eastern', 'Eastern'), 
                          ('alaska', 'Alaska'), ('hawaii', 'Hawaii'), ('arizona', 'Arizona')
                          ])
    submit = wtforms.SubmitField('Submit')

class SelectUsState(flask_wtf.FlaskForm):
    form_entered_us_state = wtforms.SelectField(u'Select state:',
                          choices=[('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming'), ('DC', 'District of Columbia'), ('AS', 'American Samoa'), ('GU', 'Guam'), ('MP', 'Northern Mariana Islands'), ('PR', 'Puerto Rico'), ('VI', 'U.S. Virgin Islands')])
    submit = wtforms.SubmitField('Submit')

class FirstNameLastNameForm(flask_wtf.FlaskForm):
    form_entered_first_name = wtforms.StringField('First name:',validators=[wtforms.validators.DataRequired()])
    form_entered_last_name = wtforms.StringField('Last name:',validators=[wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField('Submit')

class DcaCalculatorForm(flask_wtf.FlaskForm):
    form_entered_periodic_buy_amount = wtforms.StringField('Amount to purchase per DCA:',validators=[wtforms.validators.DataRequired()])
    form_entered_number_of_days_per_purchase_period = wtforms.StringField('Number of days in a purchase period (eg pay check cycle):',validators=[wtforms.validators.DataRequired()])
    form_entered_amount_of_fiat_per_purchase_period = wtforms.StringField('Total dollar amount to DCA per purchase period:',validators=[wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField('Submit')

class AdminCheck_ba_ReferralCodeExists(flask_wtf.FlaskForm):
    form_entered_referral_code = wtforms.StringField('Referral code:',validators=[wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField('Submit')

class AdminSet_ba_ReferralCode(flask_wtf.FlaskForm):
    form_entered_user_id = wtforms.StringField('User ID:',validators=[wtforms.validators.DataRequired()])
    form_entered_referral_code = wtforms.StringField('Referral code:',validators=[wtforms.validators.DataRequired()])
    form_entered_revenue_share_percentage = wtforms.StringField('Revenue Share Percentage (whole number int):',validators=[wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField('Submit')

class AdminDelete_ba_ReferralCode(flask_wtf.FlaskForm):
    form_entered_user_id = wtforms.StringField('User ID:',validators=[wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField('Submit')

class Admin_set_ba_smv_ev(flask_wtf.FlaskForm):
    form_entered_user_id = wtforms.StringField('User ID:', validators=[wtforms.validators.optional(), wtforms.validators.length(max=200)])
    form_entered_brand_ambassador_bool = wtforms.SelectField(u'Brand Ambassador',
                          choices=[('False', 'False'), ('True', 'True')])
    form_entered_site_metrics_viewer_bool = wtforms.SelectField(u'Site Metrics Viewer',
                          choices=[('False', 'False'), ('True', 'True')])
    form_entered_email_verified_bool = wtforms.SelectField(u'Email Verified',
                          choices=[('True', 'True'), ('False', 'False')])
    submit = wtforms.SubmitField('Submit')

class AdminSetSubTierAndLock(flask_wtf.FlaskForm):
    form_entered_user_id = wtforms.StringField('User ID:', validators=[wtforms.validators.optional(), wtforms.validators.length(max=200)])
    form_entered_tier = wtforms.StringField('Tier (1-3):', validators=[wtforms.validators.optional(), wtforms.validators.length(max=200)])
    form_entered_admin_tier_lock_bool = wtforms.SelectField(u'Admin Tier Lock',
                          choices=[('False', 'False'), ('True', 'True')])
    submit = wtforms.SubmitField('Submit')

class AdminUserCognitoVerificationStatus(flask_wtf.FlaskForm):
    form_entered_user_id = wtforms.StringField('User ID:', validators=[wtforms.validators.optional(), wtforms.validators.length(max=200)])
    form_entered_verification_status = wtforms.StringField('Verification Status (int: 1-10):', validators=[wtforms.validators.optional(), wtforms.validators.length(max=200)])
    submit = wtforms.SubmitField('Submit')

class AdminEnterEmailAddress(flask_wtf.FlaskForm):
    form_entered_email_address = wtforms.StringField('Email Address:', validators=[wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField('Submit')

class AdminEnterUserID(flask_wtf.FlaskForm):
    form_entered_user_id = wtforms.StringField('User ID:', validators=[wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField('Submit')

class AdminDeleteDcaSchedule(flask_wtf.FlaskForm):
    form_entered_user_id = wtforms.StringField('User ID:', validators=[wtforms.validators.DataRequired()])
    form_entered_coin_schedule = wtforms.SelectField(u'Coin/schedule to delete:',
                          choices=[('btc', 'BTC'), ('eth', 'ETH'), ('ltc', 'LTC')])
    submit = wtforms.SubmitField('Submit')

class AdminDeleteApiKeys(flask_wtf.FlaskForm):
    form_entered_user_id = wtforms.StringField('User ID:', validators=[wtforms.validators.DataRequired()])
    form_entered_exchange = wtforms.SelectField(u'Delete API key on exchange:',
                          choices=[('coinbase_pro', 'Coinbase Pro'), ('bittrex', 'Bittrex'),
                                   ('kraken', 'Kraken'), ('binance_us', 'Binance US'),
                                   ('gemini', 'Gemini'), ('ftx_us', 'FTX US')])
    submit = wtforms.SubmitField('Submit')

class AdminLogViewUserIdForm(flask_wtf.FlaskForm):
    form_entered_user_id = wtforms.StringField('User ID:', validators=[wtforms.validators.DataRequired()])
    form_entered_number_of_log_events = wtforms.SelectField(u'Number of events to view',
                          choices=[('1', 'One'), ('5', 'Five'), 
                          ('10', 'Ten'), ('50', 'Fifty'), ('100', 'One hundred')
                          ])
    form_entered_log_status_events = wtforms.SelectField(u'Status',
                          choices=[('all', 'All'), ('success', 'Success'), ('failed', 'Failed')
                          ])
    form_entered_coin_type_events = wtforms.SelectField(u'Coin',
                          choices=[('all', 'All'), ('btc', 'BTC'), ('eth', 'ETH'), ('ltc', 'LTC')
                          ])
    form_entered_exchange_events = wtforms.SelectField(u'Exchange',
                          choices=[('all', 'All'), ('coinbase_pro', 'Coinbase Pro'), ('bittrex', 'Bittrex'),
                                   ('kraken', 'Kraken'), ('binance_us', 'Binance US'),
                                   ('gemini', 'Gemini'), ('ftx_us', 'FTX US')
                          ])
    submit = wtforms.SubmitField('View events')

class MetricsUserMetricsTable(flask_wtf.FlaskForm):
    form_entered_number_of_rows = wtforms.StringField('Number of rows (1-200):', validators=[wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField('Submit')


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    logging.error("user loader called")
    return User.get(user_id, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])

@app.route("/")
def index():
    logging.critical("index / route called")
    return render_template("index.html")
    
@app.route("/login")
def auth0_login():
    logging.critical("/login route called")
    # Find out what URL to hit for auth0 login
    auth0_provider_cfg = get_auth0_provider_cfg()
    authorization_endpoint = auth0_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for auth0 login and provide
    # scopes that let you retrieve user's profile from auth0
    request_uri = auth0_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )

    logging.error(request_uri)
    return redirect(request_uri)

@app.route("/login/callback")
def auth0_callback():
    logging.critical("/login/callback route called")


    code = request.args.get("code")
    auth0_provider_cfg = get_auth0_provider_cfg()
    token_endpoint = auth0_provider_cfg["token_endpoint"]
    
    ############################################################################
    #api call to CSR-auth0-token-response service
    csr_service_headers = {}
    csr_service_headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
    query_url = CSR_service_mesh_map.api_auth0_token_response + "?scope=token_response" + "&request_url=" + urllib.parse.quote_plus(str(request.url)) + "&request_base_url=" + urllib.parse.quote_plus(str(request.base_url)) + "&code_auth0=" + urllib.parse.quote_plus(str(code))
    userinfo_response = requests.post(query_url, headers=csr_service_headers)
    if userinfo_response.status_code == 429:
        abort(429)
    logging.error(userinfo_response.json())
    ############################################################################

    unique_id = userinfo_response.json()["sub"]
    unique_id = bleach.clean(str(unique_id), strip=True) #strip of XSS
    users_email = userinfo_response.json()["email"]
    users_email = bleach.clean(str(users_email), strip=True) #strip of XSS
    email_verified = userinfo_response.json().get("email_verified")

    if "given_name" in userinfo_response.json():
        logging.error(userinfo_response.json()["given_name"])
        first_name_stripped = bleach.clean(str(userinfo_response.json()["given_name"]), strip=True) #strip of XSS
    else:
        logging.error("no first name")
        first_name_stripped = "None"
    
    if "family_name" in userinfo_response.json():
        logging.error(userinfo_response.json()["family_name"])
        last_name_stripped = bleach.clean(str(userinfo_response.json()["family_name"]), strip=True) #strip of XSS
    else:
        logging.error("no last name")
        last_name_stripped = "None"
    
    if not User.get(unique_id, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]):
        User.create(identity_provider_sub_id=unique_id, first_name=first_name_stripped, 
        last_name=last_name_stripped, email=users_email, email_verified=email_verified,
        api_gateway_api_key=service_mesh_secret_1["CSR_Service_Mesh_Secret_1"],
        provider_name="auth0")
    else:
        if unique_id[:6] == "auth0|":
            logging.error("unique_id[:6] == auth0|") #debugging
            User.update_without_names(identity_provider_sub_id=unique_id, email=users_email, email_verified=email_verified,
            api_gateway_api_key=service_mesh_secret_1["CSR_Service_Mesh_Secret_1"],
            provider_name="auth0")
        else:
            User.update(identity_provider_sub_id=unique_id, first_name=first_name_stripped, 
            last_name=last_name_stripped, email=users_email, email_verified=email_verified,
            api_gateway_api_key=service_mesh_secret_1["CSR_Service_Mesh_Secret_1"],
            provider_name="auth0")

    # create user object (login_user)
    user = User.get(unique_id, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])

    # begin user session
    login_user(user, remember=False, duration=user_session_datetime_delta)

    # send user to correct landing page
    if int(current_user.persona_verification_status) == 3 and str(current_user.email_verified) == "True":
        logging.error("current_user.persona_verification_status is 3 AND email_verified is true.  Redirecting to scheduler")
        return redirect(url_for('scheduler'))
    elif int(current_user.persona_verification_status) != 3 and str(current_user.email_verified) == "True":
        logging.error("current_user.persona_verification_status is NOT 3 AND email_verified is true.  Redirecting to scheduler | scheduler will redirect depending upon persona verification status")
        return redirect(url_for('scheduler'))
    else:
        logging.error("current_user.persona_verification_status is NOT 3 or email_verified is NOT True.  Redirecting to utilities_user_settings")
        return redirect(url_for('utilities_user_settings'))

@app.route("/logout")
@login_required
def logout():
    logging.critical("/logout route called")
    logout_user()
    logout_url_encoded = urllib.parse.quote_plus(CSR_service_mesh_map.cryptostacker_logout_url)
    logging.error(CSR_service_mesh_map.auth0_base_logout_url_cname + logout_url_encoded + "&client_id=%s" % AUTH0_CLIENT_ID) #debugging
    return redirect(CSR_service_mesh_map.auth0_base_logout_url_cname + logout_url_encoded + "&client_id=%s" % AUTH0_CLIENT_ID)

@app.route("/logged_out")
def logged_out():
    logging.critical("/logged_out route called")
    return render_template("logged_out.html")

@app.route("/logged_out_verify_email")
def logged_out_verify_email():
    logging.critical("/logged_out_verify_email route called")
    return render_template("logged_out_verify_email.html")

@app.route("/pricing")
def pricing():
    logging.critical("/pricing route called")
    return render_template("pricing.html", csr_tier_limits_map=csr_tier_limits_map, csr_price_and_per_month_map_dict=csr_price_and_per_month_map_dict)

@app.route("/pricing-tier-2")
def pricing_tier_2():
    logging.critical("/pricing-tier-2 route called")
    return render_template("pricing-tier-2.html", csr_tier_limits_map=csr_tier_limits_map, csr_price_and_per_month_map_dict=csr_price_and_per_month_map_dict)

@app.route("/pricing-tier-3")
def pricing_tier_3():
    logging.critical("/pricing-tier-3 route called")
    return render_template("pricing-tier-3.html", csr_tier_limits_map=csr_tier_limits_map, csr_price_and_per_month_map_dict=csr_price_and_per_month_map_dict)

@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route("/loaderio-841cbfcfa2d708e7df698cf72bd8817f/")
def loaderio():
    logging.critical("/loaderio-841cbfcfa2d708e7df698cf72bd8817f route called")
    return render_template("loaderio-841cbfcfa2d708e7df698cf72bd8817f.txt", current_user=current_user)

@app.route("/legal")
def legal():
    logging.error("/legal route called")
    return render_template("legal/legal.html", current_user=current_user)

@app.route("/legal/terms_of_service")
def terms_of_service():
    logging.error("/legal/terms_of_service route called")
    return redirect("https://app.termly.io/document/terms-of-use-for-saas/e6f89f73-0ea4-4451-b5a1-f4c1b30376da")

@app.route("/legal/privacy_policy")
def privacy_policy():
    logging.error("/legal/privacy_policy route called")
    return redirect("https://app.termly.io/document/privacy-policy/bfc62e02-9506-4e26-b750-63aee8d4e611")

@app.route("/legal/cookie_policy")
def cookie_policy():
    logging.error("/legal/cookie_policy route called")
    return redirect("https://app.termly.io/document/cookie-policy/028b7bf5-2089-4104-9806-8aabd0c06b54")

@app.route("/legal/return_policy")
def return_policy():
    logging.error("/legal/return_policy route called")
    return render_template("legal/return_policy.html")

@app.route("/about_us")
def about_us():
    logging.error("/about_us route called")
    return render_template("about_us.html")

@app.errorhandler(403)
def page_not_allowed(e):
    logging.critical("403 error handler called")
    return render_template("error_handlers/403.html"), 403

@app.errorhandler(404)
def page_not_found(e):
    logging.critical("404 error handler called")
    return render_template("error_handlers/404.html"), 404

@app.errorhandler(429)
def too_many_requests(e):
    logging.critical("429 error handler called")
    return render_template("error_handlers/429.html"), 429

@app.errorhandler(500)
def too_many_requests(e):
    logging.critical("500 error handler called")
    return render_template("error_handlers/500.html"), 500

@app.route("/test_404")
def test_404():
    logging.critical("/test_404 route called")
    abort(404)

@app.route("/test_429")
def test_429():
    logging.critical("/test_429 route called")
    abort(429)



@app.route("/scheduler")
@login_required
def scheduler():
    logging.critical("/scheduler route called")

    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    if current_user.email_verified != "True":
        logging.error("email_verified is not True - redirecting to utilities_verify_email")
        return redirect(url_for('utilities_verify_email'))

    ###############################################################
    ### persona verification enforcement - begins ####
    if not hasattr(current_user, 'persona_verification_status'):
        logging.error("persona_verification_status not found returning 404")
        abort(404)
    
    if int(current_user.persona_verification_status) < 2:
        logging.error("current_user.persona_verification_status is less than 2")
        return redirect(url_for('persona_verification'))
    
    if int(current_user.persona_verification_status) == 2:
        logging.error("current_user.persona_verification_status is 2")
        return redirect(url_for('persona_verification_status'))

    if int(current_user.persona_verification_status) == 9:
        logging.error("current_user.persona_verification_status is 9")
        return redirect(url_for('persona_verification_status'))
    
    if int(current_user.persona_verification_status) == 3: #no action required because the user is validated
        logging.error("current_user.persona_verification_status is 3")
    ### persona verification enforcement - ends ####
    ###############################################################

    return render_template("scheduler.html")

@app.route("/set_api_keys")
@login_required
def set_api_keys():
    logging.critical("/set_api_keys route called")

    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    if current_user.email_verified != "True":
        logging.error("email_verified is not True - redirecting to utilities_verify_email")
        return redirect(url_for('utilities_verify_email'))

    ###############################################################
    ### persona verification enforcement - begins ####
    if not hasattr(current_user, 'persona_verification_status'):
        logging.error("persona_verification_status not found returning 404")
        abort(404)
    
    if int(current_user.persona_verification_status) < 2:
        logging.error("current_user.persona_verification_status is less than 2")
        return redirect(url_for('persona_verification'))
    
    if int(current_user.persona_verification_status) == 2:
        logging.error("current_user.persona_verification_status is 2")
        return redirect(url_for('persona_verification_status'))

    if int(current_user.persona_verification_status) == 9:
        logging.error("current_user.persona_verification_status is 9")
        return redirect(url_for('persona_verification_status'))
    
    if int(current_user.persona_verification_status) == 3: #no action required because the user is validated
        logging.error("current_user.persona_verification_status is 3")
    ### persona verification enforcement - ends ####
    ###############################################################

    return render_template("set_api_keys.html")

@app.route("/set_api_keys/coinbase/<coinbase_exchange_endpoint>", methods=['GET', 'POST'])
@login_required
def set_api_keys_coinbase(coinbase_exchange_endpoint):
    logging.critical("/set_api_keys/coinbase/<coinbase_exchange_endpoint> route called")
    
    coinbase_exchange_endpoint_sanitized = trim_sanitize_strip(20, coinbase_exchange_endpoint)

    if coinbase_exchange_endpoint_sanitized not in ["coinbase_pro"]:
        logging.error("/set_api_keys/coinbase/<coinbase_exchange_endpoint> route called and not found, returning 404")
        abort(404)
    
    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    if current_user.email_verified != "True":
        logging.error("email_verified is not True - redirecting to utilities_verify_email")
        return redirect(url_for('utilities_verify_email'))

    ###############################################################
    ### persona verification enforcement - begins ####
    if not hasattr(current_user, 'persona_verification_status'):
        logging.error("persona_verification_status not found returning 404")
        abort(404)
    
    if int(current_user.persona_verification_status) < 2:
        logging.error("current_user.persona_verification_status is less than 2")
        return redirect(url_for('persona_verification'))
    
    if int(current_user.persona_verification_status) == 2:
        logging.error("current_user.persona_verification_status is 2")
        return redirect(url_for('persona_verification_status'))

    if int(current_user.persona_verification_status) == 9:
        logging.error("current_user.persona_verification_status is 9")
        return redirect(url_for('persona_verification_status'))
    
    if int(current_user.persona_verification_status) == 3: #no action required because the user is validated
        logging.error("current_user.persona_verification_status is 3")
    ### persona verification enforcement - ends ####
    ###############################################################

    if coinbase_exchange_endpoint_sanitized == "coinbase":
        coinbase_exchange_endpoint_jinja_template = "Coinbase"
    if coinbase_exchange_endpoint_sanitized == "coinbase_pro":
        coinbase_exchange_endpoint_jinja_template = "Coinbase Pro"
    
    #retrieve api key metadata
    meta_data_to_return_to_user = CSR_toolkit.build_api_key_metadata_list(current_user.user_id, coinbase_exchange_endpoint_sanitized, current_user.timezone, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
    
    # Create instance of the form.
    form = ApiKeyFormCoinbase()
    
    if form.validate_on_submit():
        #session['breed'] = form.breed.data
        #sanitize and verify user strings
        if form.form_entered_api_key_expires_length.data not in ["never", "1month", "6months", "1year", "3year"]:
            logging.error("api expires length entered incorrectly")
            message_to_return_to_user = "api expires length entered incorrectly"
            return render_template("set_api_keys/coinbase.html", form=form, message_to_return_to_user=message_to_return_to_user, friendly_exchange_name=coinbase_exchange_endpoint_jinja_template, exchange_name=coinbase_exchange_endpoint_sanitized)

        greater_than_int = 200
        if len(form.form_entered_api_key_plaintext.data) > greater_than_int or len(form.form_entered_api_secret_plaintext.data) > greater_than_int or len(form.form_entered_api_passphrase_plaintext.data) > greater_than_int:
            logging.error("key length greater than %s" % greater_than_int)
            message_to_return_to_user = "Your API key was entered incorrectly"
            return render_template("set_api_keys/coinbase.html", form=form, message_to_return_to_user=message_to_return_to_user, friendly_exchange_name=coinbase_exchange_endpoint_jinja_template, exchange_name=coinbase_exchange_endpoint_sanitized)
        
        #create epoch object to be used for api key expiration
        datetime_now_object = datetime.datetime.now()
        datetime_now_object_epoch = datetime_now_object.strftime('%s')
        datetime_now_object_epoch = int(datetime_now_object_epoch)
        #determine epoch length based on user input
        if form.form_entered_api_key_expires_length.data == "never":
            api_key_expires_length_epoch = 0
        elif form.form_entered_api_key_expires_length.data == "1month":
            api_key_expires_length_epoch = CSR_toolkit.epoch_plus_months_epoch(datetime_now_object_epoch, 1)
        elif form.form_entered_api_key_expires_length.data == "6months":
            api_key_expires_length_epoch = CSR_toolkit.epoch_plus_months_epoch(datetime_now_object_epoch, 6)
        elif form.form_entered_api_key_expires_length.data == "1year":
            api_key_expires_length_epoch = CSR_toolkit.epoch_plus_months_epoch(datetime_now_object_epoch, 12)
        elif form.form_entered_api_key_expires_length.data == "3year":
            api_key_expires_length_epoch = CSR_toolkit.epoch_plus_months_epoch(datetime_now_object_epoch, 36)
        else:
            logging.error("api_key_expires_length_epoch = 0 - unexpected form.form_entered_api_key_expires_length")
            api_key_expires_length_epoch = "0"

        #markup removed for XXS - example: #bleach.clean('<span>is not allowed</span>', strip=True)
        logging.error("keys stripped of markup")
        api_key_plaintext_sanitized = trim_sanitize_strip(200, form.form_entered_api_key_plaintext.data)
        api_secret_plaintext_sanitized = trim_sanitize_strip(200, form.form_entered_api_secret_plaintext.data)
        api_passphrase_plaintext_sanitized = trim_sanitize_strip(200, form.form_entered_api_passphrase_plaintext.data)
        api_key_plaintext_sanitized = python_sanitize_aggressive(api_key_plaintext_sanitized)
        api_secret_plaintext_sanitized = python_sanitize_aggressive(api_secret_plaintext_sanitized)
        api_passphrase_plaintext_sanitized = python_sanitize_aggressive(api_passphrase_plaintext_sanitized)

        try:
            logging.error("checking whether api_secret_plaintext_sanitized is properly base64 encoded or not")
            base64.b64decode(api_secret_plaintext_sanitized)
        except binascii.Error:
            logging.error("not base64 string")
            message_to_return_to_user = "Your API key is invalid, you may have entered the key incorrectly."
            return render_template("set_api_keys/coinbase.html", form=form, message_to_return_to_user=message_to_return_to_user, friendly_exchange_name=coinbase_exchange_endpoint_jinja_template, exchange_name=coinbase_exchange_endpoint_sanitized)
        
        #check & increment api_key_submission_counter
        CSR_toolkit.increment_api_key_submission_counter(current_user.user_id, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
        api_key_submission_counter_return_bool = CSR_toolkit.api_key_submission_counter_return_bool(current_user.user_id, 20, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
        if api_key_submission_counter_return_bool:
            message_to_return_to_user = "You're submitting API keys too quickly, for security reasons you'll have to wait 60 minutes to enter API keys again"
            return render_template("set_api_keys/coinbase.html", form=form, message_to_return_to_user=message_to_return_to_user, friendly_exchange_name=coinbase_exchange_endpoint_jinja_template, exchange_name=coinbase_exchange_endpoint_sanitized)

        #api key validation
        logging.error("validating key with exchange API")
        validation_return = exchange_api_key_validation.validate_api_key(coinbase_exchange_endpoint_sanitized, api_key_plaintext_sanitized, api_secret_plaintext_sanitized, api_passphrase=api_passphrase_plaintext_sanitized)
        if validation_return == "invalid":
            logging.error("key is invalid")
            message_to_return_to_user = "Your API key is invalid, you may have entered the key incorrectly or the key is expired or the key does not have the proper permissions."
            return render_template("set_api_keys/coinbase.html", form=form, message_to_return_to_user=message_to_return_to_user, friendly_exchange_name=coinbase_exchange_endpoint_jinja_template, exchange_name=coinbase_exchange_endpoint_sanitized)
        
        logging.error("Key validation passed, posting API keys to service")

        api_key_plaintext_sanitized_url_encoded = urllib.parse.quote_plus(api_key_plaintext_sanitized)
        api_secret_plaintext_sanitized_url_encoded = urllib.parse.quote_plus(api_secret_plaintext_sanitized)
        api_passphrase_plaintext_sanitized_url_encoded = urllib.parse.quote_plus(api_passphrase_plaintext_sanitized)

        query_string = CSR_service_mesh_map.api_keys_write + "?" + "user_id=" + str(current_user.user_id) + "&" + "exchange=" + str(coinbase_exchange_endpoint_sanitized) + "&" + "api_key=" + str(api_key_plaintext_sanitized_url_encoded) + "&" + "api_secret=" + str(api_secret_plaintext_sanitized_url_encoded) + "&" + "api_passphrase=" + str(api_passphrase_plaintext_sanitized_url_encoded) + "&" + "keys_expiration_epoch=" + str(api_key_expires_length_epoch)
        headers = {}
        headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
        api_keys_post_response = requests.post(query_string, headers=headers)
        if api_keys_post_response.status_code == 429:
            abort(429)
        message_to_return_to_user = "%s API Key set successfully!" % coinbase_exchange_endpoint_jinja_template
        
        #clears the form data for the user
        form.form_entered_api_key_plaintext.data = ""
        form.form_entered_api_secret_plaintext.data = ""
        form.form_entered_api_passphrase_plaintext.data = ""
        #API Key set successfully

        #retrieve metadata
        meta_data_to_return_to_user = CSR_toolkit.build_api_key_metadata_list(current_user.user_id, coinbase_exchange_endpoint_sanitized, current_user.timezone, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
        return render_template("set_api_keys/coinbase.html", form=form, message_to_return_to_user=message_to_return_to_user, friendly_exchange_name=coinbase_exchange_endpoint_jinja_template, exchange_name=coinbase_exchange_endpoint_sanitized, meta_data_to_return_to_user=meta_data_to_return_to_user)
    return render_template("set_api_keys/coinbase.html", form=form, message_to_return_to_user=None, friendly_exchange_name=coinbase_exchange_endpoint_jinja_template, exchange_name=coinbase_exchange_endpoint_sanitized, meta_data_to_return_to_user=meta_data_to_return_to_user)

@app.route("/set_api_keys/standard/<crypto_exchange_endpoint>", methods=['GET', 'POST'])
@login_required
def set_api_keys_standard(crypto_exchange_endpoint):
    logging.critical("/set_api_keys/standard/<crypto_exchange_endpoint> route called")
    
    crypto_exchange_endpoint_sanitized = trim_sanitize_strip(20, crypto_exchange_endpoint)

    if crypto_exchange_endpoint_sanitized not in ['bittrex', 'kraken', 'binance_us', 'gemini', 'ftx_us']:
            logging.error("/set_api_keys/standard/<crypto_exchange_endpoint> route called and not found, returning 404")
            abort(404)

    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    if current_user.email_verified != "True":
        logging.error("email_verified is not True - redirecting to utilities_verify_email")
        return redirect(url_for('utilities_verify_email'))

    ###############################################################
    ### persona verification enforcement - begins ####
    if not hasattr(current_user, 'persona_verification_status'):
        logging.error("persona_verification_status not found returning 404")
        abort(404)
    
    if int(current_user.persona_verification_status) < 2:
        logging.error("current_user.persona_verification_status is less than 2")
        return redirect(url_for('persona_verification'))
    
    if int(current_user.persona_verification_status) == 2:
        logging.error("current_user.persona_verification_status is 2")
        return redirect(url_for('persona_verification_status'))

    if int(current_user.persona_verification_status) == 9:
        logging.error("current_user.persona_verification_status is 9")
        return redirect(url_for('persona_verification_status'))
    
    if int(current_user.persona_verification_status) == 3: #no action required because the user is validated
        logging.error("current_user.persona_verification_status is 3")
    ### persona verification enforcement - ends ####
    ###############################################################

    if crypto_exchange_endpoint_sanitized == "binance_us":
        crypto_exchange_endpoint_jinja_template = "Binance US"
    if crypto_exchange_endpoint_sanitized == "bittrex":
        crypto_exchange_endpoint_jinja_template = "Bittrex"
    if crypto_exchange_endpoint_sanitized == "kraken":
        crypto_exchange_endpoint_jinja_template = "Kraken"
    if crypto_exchange_endpoint_sanitized == "gemini":
        crypto_exchange_endpoint_jinja_template = "Gemini"
    if crypto_exchange_endpoint_sanitized == "ftx_us":
        crypto_exchange_endpoint_jinja_template = "FTX US"

    meta_data_to_return_to_user = CSR_toolkit.build_api_key_metadata_list(current_user.user_id, crypto_exchange_endpoint_sanitized, current_user.timezone, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])

    # Create instance of the form.
    form = ApiKeyFormStandard()
    
    if form.validate_on_submit():
        #session['breed'] = form.breed.data
        #sanitize and verify user strings
        if form.form_entered_api_key_expires_length.data not in ["never", "1month", "6months", "1year", "3year"]:
            logging.error("api expires length entered incorrectly")
            message_to_return_to_user = "api expires length entered incorrectly"
            return render_template("set_api_keys/coinbase.html", form=form, message_to_return_to_user=message_to_return_to_user, friendly_exchange_name=crypto_exchange_endpoint_jinja_template, exchange_name=crypto_exchange_endpoint_sanitized) 

        greater_than_int = 200
        if len(form.form_entered_api_key_plaintext.data) > greater_than_int or len(form.form_entered_api_secret_plaintext.data) > greater_than_int:
            logging.error("key length greater than %s" % greater_than_int)
            message_to_return_to_user = "Your API key was entered incorrectly"
            return render_template("set_api_keys/coinbase.html", form=form, message_to_return_to_user=message_to_return_to_user, friendly_exchange_name=crypto_exchange_endpoint_jinja_template, exchange_name=crypto_exchange_endpoint_sanitized) 
        
        #create epoch object to be used for api key expiration
        datetime_now_object = datetime.datetime.now()
        datetime_now_object_epoch = datetime_now_object.strftime('%s')
        datetime_now_object_epoch = int(datetime_now_object_epoch)
        #determine epoch length based on user input
        if form.form_entered_api_key_expires_length.data == "never":
            api_key_expires_length_epoch = 0
        elif form.form_entered_api_key_expires_length.data == "1month":
            api_key_expires_length_epoch = CSR_toolkit.epoch_plus_months_epoch(datetime_now_object_epoch, 1)
        elif form.form_entered_api_key_expires_length.data == "6months":
            api_key_expires_length_epoch = CSR_toolkit.epoch_plus_months_epoch(datetime_now_object_epoch, 6)
        elif form.form_entered_api_key_expires_length.data == "1year":
            api_key_expires_length_epoch = CSR_toolkit.epoch_plus_months_epoch(datetime_now_object_epoch, 12)
        elif form.form_entered_api_key_expires_length.data == "3year":
            api_key_expires_length_epoch = CSR_toolkit.epoch_plus_months_epoch(datetime_now_object_epoch, 36)
        else:
            logging.error("api_key_expires_length_epoch = 0 - unexpected form.form_entered_api_key_expires_length")
            api_key_expires_length_epoch = "0"

        logging.error("keys stripped of markup")
        api_key_plaintext_sanitized = trim_sanitize_strip(200, form.form_entered_api_key_plaintext.data)
        api_secret_plaintext_sanitized = trim_sanitize_strip(200, form.form_entered_api_secret_plaintext.data)
        api_key_plaintext_sanitized = python_sanitize_aggressive(api_key_plaintext_sanitized)
        api_secret_plaintext_sanitized = python_sanitize_aggressive(api_secret_plaintext_sanitized)

        #check & increment api_key_submission_counter
        CSR_toolkit.increment_api_key_submission_counter(current_user.user_id, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
        api_key_submission_counter_return_bool = CSR_toolkit.api_key_submission_counter_return_bool(current_user.user_id, 20, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
        if api_key_submission_counter_return_bool:
            message_to_return_to_user = "You're submitting API keys too quickly, for security reasons you'll have to wait 60 minutes to enter API keys again"
            return render_template("set_api_keys/standard.html", form=form, message_to_return_to_user=message_to_return_to_user, friendly_exchange_name=crypto_exchange_endpoint_jinja_template, exchange_name=crypto_exchange_endpoint_sanitized)

        #if crypto_exchange_endpoint is kraken then validate that secret is base64
        if crypto_exchange_endpoint_sanitized == "kraken":
            try:
                logging.error("checking whether api_secret_plaintext_sanitized is properly base64 encoded or not")
                base64.b64decode(api_secret_plaintext_sanitized)
            except binascii.Error:
                logging.error("not base64 string")
                message_to_return_to_user = "Your API key is invalid, you may have entered the key incorrectly."
                return render_template("set_api_keys/standard.html", form=form, message_to_return_to_user=message_to_return_to_user, friendly_exchange_name=crypto_exchange_endpoint_jinja_template, exchange_name=crypto_exchange_endpoint_sanitized) 
        
        #api key validation
        logging.error("validating key with exchange API")
        validation_return = exchange_api_key_validation.validate_api_key(crypto_exchange_endpoint_sanitized, api_key_plaintext_sanitized, api_secret_plaintext_sanitized)
        if validation_return == "invalid":
            logging.error("key is invalid")
            message_to_return_to_user = "Your API key is invalid, you may have entered the key incorrectly or the key is expired or the key does not have the proper permissions."
            return render_template("set_api_keys/standard.html", form=form, message_to_return_to_user=message_to_return_to_user, friendly_exchange_name=crypto_exchange_endpoint_jinja_template, exchange_name=crypto_exchange_endpoint_sanitized)
        
        logging.error("Key validations passed, posting API keys to service")

        api_key_plaintext_sanitized_url_encoded = urllib.parse.quote_plus(api_key_plaintext_sanitized) 
        api_secret_plaintext_sanitized_url_encoded = urllib.parse.quote_plus(api_secret_plaintext_sanitized) 

        query_string = CSR_service_mesh_map.api_keys_write + "?" + "user_id=" + str(current_user.user_id) + "&" + "exchange=" + str(crypto_exchange_endpoint_sanitized) + "&" + "api_key=" + str(api_key_plaintext_sanitized_url_encoded) + "&" + "api_secret=" + str(api_secret_plaintext_sanitized_url_encoded) + "&" + "keys_expiration_epoch=" + str(api_key_expires_length_epoch)
        headers = {}
        headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
        api_keys_post_response = requests.post(query_string, headers=headers)
        if api_keys_post_response.status_code == 429:
            abort(429)
        message_to_return_to_user = "%s API Key set successfully!" % crypto_exchange_endpoint_jinja_template
        
        #clears the form data for the user
        form.form_entered_api_key_plaintext.data = ""
        form.form_entered_api_secret_plaintext.data = ""
        #API Key set successfully

        meta_data_to_return_to_user = CSR_toolkit.build_api_key_metadata_list(current_user.user_id, crypto_exchange_endpoint_sanitized, current_user.timezone, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
        return render_template("set_api_keys/standard.html", form=form, message_to_return_to_user=message_to_return_to_user, friendly_exchange_name=crypto_exchange_endpoint_jinja_template, exchange_name=crypto_exchange_endpoint_sanitized, meta_data_to_return_to_user=meta_data_to_return_to_user)
    return render_template("set_api_keys/standard.html", form=form, message_to_return_to_user=None, friendly_exchange_name=crypto_exchange_endpoint_jinja_template, exchange_name=crypto_exchange_endpoint_sanitized, meta_data_to_return_to_user=meta_data_to_return_to_user)

@app.route("/set_api_keys/<exchange_type>/delete/<crypto_exchange_endpoint>", methods=['GET', 'POST'])
@login_required
def delete_api_keys(exchange_type, crypto_exchange_endpoint):
    #delete
    #/set_api_keys/coinbase/delete/<crypto_exchange_endpoint>
    #/set_api_keys/standard/delete/<crypto_exchange_endpoint>
    #/set_api_keys/coinbase/delete/coinbase_pro
    #/set_api_keys/standard/delete/kraken
    logging.critical("/set_api_keys/<exchange_type>/delete/<crypto_exchange_endpoint>")
    
    if exchange_type [:20] not in ["coinbase", "standard"]:
        logging.error("/set_api_keys/<exchange_type>/delete/<crypto_exchange_endpoint> called and exchange_type not found, returning 404")
        abort(404)
    if crypto_exchange_endpoint[:20] not in CSR_toolkit.supported_exchanges_list:
        logging.error("/set_api_keys/<exchange_type>/delete/<crypto_exchange_endpoint> called and crypto_exchange_endpoint not found, returning 404")
        abort(404)
    if exchange_type [:20] in ["coinbase"] and crypto_exchange_endpoint[:20] not in ["coinbase_pro"]:
        logging.error("/set_api_keys/<exchange_type>/delete/<crypto_exchange_endpoint> called and not found, returning 404")
        abort(404)
    if exchange_type [:20] in ["standard"] and crypto_exchange_endpoint[:20] not in ['bittrex', 'kraken', 'binance_us', 'gemini', 'ftx_us']:
        logging.error("/set_api_keys/<exchange_type>/delete/<crypto_exchange_endpoint> called and not found, returning 404")
        abort(404)

    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    if current_user.email_verified != "True":
        logging.error("email_verified is not True - redirecting to utilities_verify_email")
        return redirect(url_for('utilities_verify_email'))

    ###############################################################
    ### persona verification enforcement - begins ####
    if not hasattr(current_user, 'persona_verification_status'):
        logging.error("persona_verification_status not found returning 404")
        abort(404)
    
    if int(current_user.persona_verification_status) < 2:
        logging.error("current_user.persona_verification_status is less than 2")
        return redirect(url_for('persona_verification'))
    
    if int(current_user.persona_verification_status) == 2:
        logging.error("current_user.persona_verification_status is 2")
        return redirect(url_for('persona_verification_status'))

    if int(current_user.persona_verification_status) == 9:
        logging.error("current_user.persona_verification_status is 9")
        return redirect(url_for('persona_verification_status'))
    
    if int(current_user.persona_verification_status) == 3: #no action required because the user is validated
        logging.error("current_user.persona_verification_status is 3")
    ### persona verification enforcement - ends ####
    ###############################################################

    CSR_toolkit.delete_users_exchange_api_key_write_only(str(current_user.user_id), crypto_exchange_endpoint.lower(), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
    message_to_return_to_user = "Deleted API key successfully"
    #return render_template("set_api_keys.html", message_to_return_to_user=message_to_return_to_user)
    return redirect("/set_api_keys")

@app.route("/dca_scheduler")
@login_required
def dca_scheduler():
    logging.critical("/dca_scheduler route called")

    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    if current_user.email_verified != "True":
        logging.error("email_verified is not True - redirecting to utilities_verify_email")
        return redirect(url_for('utilities_verify_email'))

    ###############################################################
    ### persona verification enforcement - begins ####
    if not hasattr(current_user, 'persona_verification_status'):
        logging.error("persona_verification_status not found returning 404")
        abort(404)
    
    if int(current_user.persona_verification_status) < 2:
        logging.error("current_user.persona_verification_status is less than 2")
        return redirect(url_for('persona_verification'))
    
    if int(current_user.persona_verification_status) == 2:
        logging.error("current_user.persona_verification_status is 2")
        return redirect(url_for('persona_verification_status'))

    if int(current_user.persona_verification_status) == 9:
        logging.error("current_user.persona_verification_status is 9")
        return redirect(url_for('persona_verification_status'))
    
    if int(current_user.persona_verification_status) == 3: #no action required because the user is validated
        logging.error("current_user.persona_verification_status is 3")
    ### persona verification enforcement - ends ####
    ###############################################################

    return render_template("dca_schedule/dca_scheduler.html")

@app.route("/dca_scheduler/set/<digital_asset_endpoint>", methods=['GET', 'POST'])
@login_required
def dca_scheduler_set(digital_asset_endpoint):
    logging.critical("/dca_scheduler/set/<digital_asset_endpoint> route called")
    
    digital_asset_endpoint_sanitized = trim_sanitize_strip(10, digital_asset_endpoint)

    if digital_asset_endpoint_sanitized not in CSR_toolkit.supported_coins_list:
        logging.error("/dca_scheduler/set/<digital_asset_endpoint> called and not found, returning 404")
        abort(404)

    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    if current_user.email_verified != "True":
        logging.error("email_verified is not True - redirecting to utilities_verify_email")
        return redirect(url_for('utilities_verify_email'))

    ###############################################################
    ### persona verification enforcement - begins ####
    if not hasattr(current_user, 'persona_verification_status'):
        logging.error("persona_verification_status not found returning 404")
        abort(404)
    
    if int(current_user.persona_verification_status) < 2:
        logging.error("current_user.persona_verification_status is less than 2")
        return redirect(url_for('persona_verification'))
    
    if int(current_user.persona_verification_status) == 2:
        logging.error("current_user.persona_verification_status is 2")
        return redirect(url_for('persona_verification_status'))

    if int(current_user.persona_verification_status) == 9:
        logging.error("current_user.persona_verification_status is 9")
        return redirect(url_for('persona_verification_status'))
    
    if int(current_user.persona_verification_status) == 3: #no action required because the user is validated
        logging.error("current_user.persona_verification_status is 3")
    ### persona verification enforcement - ends ####
    ###############################################################

    message_to_return_to_user = None
    form = DcaSchedulerForm()

    if not form.validate_on_submit():
        logging.error("/dca_scheduler/%s POST form NOT validate on submit!" % digital_asset_endpoint_sanitized)
    if form.validate_on_submit():
        #session['breed'] = form.breed.data
        logging.error("/dca_scheduler/%s POST form validate on submit" % digital_asset_endpoint_sanitized)

        form_entered_exchange_priority_1_sanitized = trim_sanitize_strip(20, form.form_entered_exchange_priority_1.data) #allow listed
        form_entered_exchange_priority_1_sanitized = python_sanitize_aggressive(form_entered_exchange_priority_1_sanitized)
        form_entered_exchange_priority_2_sanitized = trim_sanitize_strip(20, form.form_entered_exchange_priority_2.data) #allow listed
        form_entered_exchange_priority_2_sanitized = python_sanitize_aggressive(form_entered_exchange_priority_2_sanitized)
        form_entered_exchange_priority_3_sanitized = trim_sanitize_strip(20, form.form_entered_exchange_priority_3.data) #allow listed
        form_entered_exchange_priority_3_sanitized = python_sanitize_aggressive(form_entered_exchange_priority_3_sanitized)
        form_entered_exchange_priority_4_sanitized = trim_sanitize_strip(20, form.form_entered_exchange_priority_4.data) #allow listed
        form_entered_exchange_priority_4_sanitized = python_sanitize_aggressive(form_entered_exchange_priority_4_sanitized)
        form_entered_exchange_priority_5_sanitized = trim_sanitize_strip(20, form.form_entered_exchange_priority_5.data) #allow listed
        form_entered_exchange_priority_5_sanitized = python_sanitize_aggressive(form_entered_exchange_priority_5_sanitized)
        form_entered_exchange_priority_6_sanitized = trim_sanitize_strip(20, form.form_entered_exchange_priority_6.data) #allow listed
        form_entered_exchange_priority_6_sanitized = python_sanitize_aggressive(form_entered_exchange_priority_6_sanitized)
        
        form_entered_high_availability_type_sanitized = trim_sanitize_strip(20, form.form_entered_high_availability_type.data) #allow listed
        form_entered_high_availability_type_sanitized = python_sanitize_aggressive(form_entered_high_availability_type_sanitized)

        form_entered_time_denomination_sanitized = trim_sanitize_strip(20, form.form_entered_time_denomination.data) #allow listed
        form_entered_time_denomination_sanitized = python_sanitize_aggressive(form_entered_time_denomination_sanitized)

        form_entered_time_interval_sanitized = trim_sanitize_strip(10, form.form_entered_time_interval.data) #checks for whole number
        form_entered_time_interval_sanitized = python_sanitize_aggressive(form_entered_time_interval_sanitized)
        
        form_entered_dollar_amount_sanitized = trim_sanitize_strip(10, form.form_entered_dollar_amount.data) #checks for whole number
        form_entered_dollar_amount_sanitized = python_sanitize_aggressive(form_entered_dollar_amount_sanitized)
        
        form_entered_fiat_denomination_sanitized = trim_sanitize_strip(10, form.form_entered_fiat_denomination.data) #not currently used
        form_entered_fiat_denomination_sanitized = python_sanitize_aggressive(form_entered_fiat_denomination_sanitized)
        
        if form_entered_exchange_priority_1_sanitized not in CSR_toolkit.supported_exchanges_list: 
            logging.error("user sent exchange that is not supported")
            #do not set DCA schedule, do not return error to user.
            #todo #write log in suspicious behavior DB
            return render_template("dca_schedule/set_dca.html", form=form, digital_asset=digital_asset_endpoint_sanitized, message_to_return_to_user=message_to_return_to_user)
        if form_entered_exchange_priority_2_sanitized not in CSR_toolkit.supported_exchanges_list: 
            logging.error("user sent exchange that is not supported")
            #do not set DCA schedule, do not return error to user.
            #todo #write log in suspicious behavior DB
            return render_template("dca_schedule/set_dca.html", form=form, digital_asset=digital_asset_endpoint_sanitized, message_to_return_to_user=message_to_return_to_user)
        if form_entered_exchange_priority_3_sanitized not in CSR_toolkit.supported_exchanges_list: 
            logging.error("user sent exchange that is not supported")
            #do not set DCA schedule, do not return error to user.
            #todo #write log in suspicious behavior DB
            return render_template("dca_schedule/set_dca.html", form=form, digital_asset=digital_asset_endpoint_sanitized, message_to_return_to_user=message_to_return_to_user)
        if form_entered_exchange_priority_4_sanitized not in CSR_toolkit.supported_exchanges_list: 
            logging.error("user sent exchange that is not supported")
            #do not set DCA schedule, do not return error to user.
            #todo #write log in suspicious behavior DB
            return render_template("dca_schedule/set_dca.html", form=form, digital_asset=digital_asset_endpoint_sanitized, message_to_return_to_user=message_to_return_to_user)
        if form_entered_exchange_priority_5_sanitized not in CSR_toolkit.supported_exchanges_list: 
            logging.error("user sent exchange that is not supported")
            #do not set DCA schedule, do not return error to user.
            #todo #write log in suspicious behavior DB
            return render_template("dca_schedule/set_dca.html", form=form, digital_asset=digital_asset_endpoint_sanitized, message_to_return_to_user=message_to_return_to_user)
        if form_entered_exchange_priority_6_sanitized not in CSR_toolkit.supported_exchanges_list: 
            logging.error("user sent exchange that is not supported")
            #do not set DCA schedule, do not return error to user.
            #todo #write log in suspicious behavior DB
            return render_template("dca_schedule/set_dca.html", form=form, digital_asset=digital_asset_endpoint_sanitized, message_to_return_to_user=message_to_return_to_user)

        if form_entered_exchange_priority_1_sanitized == form_entered_exchange_priority_2_sanitized == form_entered_exchange_priority_3_sanitized == form_entered_exchange_priority_4_sanitized == form_entered_exchange_priority_5_sanitized == form_entered_exchange_priority_6_sanitized == "not_set":
            logging.error("user set every form_entered_exchange_priority to not set, returning message to user")
            message_to_return_to_user = "Must set at least one exchange"
            return render_template("dca_schedule/set_dca.html", form=form, digital_asset=digital_asset_endpoint_sanitized, message_to_return_to_user=message_to_return_to_user)

        if form_entered_high_availability_type_sanitized not in CSR_toolkit.supported_high_availability_type_list: 
            logging.error("user sent high_availability_type that is not supported")
            #do not set DCA schedule, do not return error to user.
            #todo #write log in suspicious behavior DB
            return render_template("dca_schedule/set_dca.html", form=form, digital_asset=digital_asset_endpoint_sanitized, message_to_return_to_user=message_to_return_to_user)

        if form_entered_time_denomination_sanitized not in ["minutes", "hours"]:
            logging.error("user sent time_denomination that is not supported")
            #do not set DCA schedule, do not return error to user.
            #todo #write log in suspicious behavior DB
            return render_template("dca_schedule/set_dca.html", form=form, digital_asset=digital_asset_endpoint_sanitized, message_to_return_to_user=message_to_return_to_user)

        if not form_entered_time_interval_sanitized.isnumeric(): #checks for whole number
            logging.error("user sent time_interval that is not a numeric or not a whole number")
            message_to_return_to_user = "Time interval must be a whole number of at least 10 minutes, or at least 1 hour"
            return render_template("dca_schedule/set_dca.html", form=form, digital_asset=digital_asset_endpoint_sanitized, message_to_return_to_user=message_to_return_to_user)

        if not form_entered_dollar_amount_sanitized.isnumeric(): #checks for whole number
            logging.error("user sent time_interval that is not a numeric or not a whole number")
            message_to_return_to_user = "Dollar amount must be a whole number of at least $10"
            return render_template("dca_schedule/set_dca.html", form=form, digital_asset=digital_asset_endpoint_sanitized, message_to_return_to_user=message_to_return_to_user)

        if float(form_entered_dollar_amount_sanitized) < 10 or float(form_entered_dollar_amount_sanitized) > 10000: #must be greater than 10
            logging.error("form_entered_dollar_amount less than 10 or greater than 100k")
            message_to_return_to_user = "Dollar amount must be a whole number greater than or equal to $10 and less than $10,000"
            return render_template("dca_schedule/set_dca.html", form=form, digital_asset=digital_asset_endpoint_sanitized, message_to_return_to_user=message_to_return_to_user)
        
        if float(form_entered_time_interval_sanitized) < 10 and form_entered_time_denomination_sanitized == "minutes":
            logging.error("user entered time less than 10 minutes")
            message_to_return_to_user = "Time interval must be a whole number of at least 10 minutes"
            return render_template("dca_schedule/set_dca.html", form=form, digital_asset=digital_asset_endpoint_sanitized, message_to_return_to_user=message_to_return_to_user)
        
        if float(form_entered_time_interval_sanitized) > 50000 and form_entered_time_denomination_sanitized == "minutes":
            logging.error("user entered time greater than 50000 minutes")
            message_to_return_to_user = "Time interval must be a whole number of less than 50000 minutes"
            return render_template("dca_schedule/set_dca.html", form=form, digital_asset=digital_asset_endpoint_sanitized, message_to_return_to_user=message_to_return_to_user)
        
        if float(form_entered_time_interval_sanitized) < 1 and form_entered_time_denomination_sanitized == "hours":
            logging.error("user entered time less than 1 hours")
            message_to_return_to_user = "Time interval must be a whole number of at least 1 hour"
            return render_template("dca_schedule/set_dca.html", form=form, digital_asset=digital_asset_endpoint_sanitized, message_to_return_to_user=message_to_return_to_user)
        
        if float(form_entered_time_interval_sanitized) > 1000 and form_entered_time_denomination_sanitized == "hours":
            logging.error("user entered time greater than 1000 hours")
            message_to_return_to_user = "Time interval must be a whole number of less than 1000 hours"
            return render_template("dca_schedule/set_dca.html", form=form, digital_asset=digital_asset_endpoint_sanitized, message_to_return_to_user=message_to_return_to_user)

        logging.error("setting schedule in DB")
        #exchange_priority_1 through exchange_priority_20 now in tables
        query_string = CSR_service_mesh_map.api_dca_schedule + "?" + "user_id=" + str(current_user.user_id) + "&" + "digital_asset=" + str(digital_asset_endpoint_sanitized) + "&" + "interval_time=" + str(int(form_entered_time_interval_sanitized)) + "&" + "interval_denomination=" + str(form_entered_time_denomination_sanitized) + "&" + "fiat_amount=" + str(int(form_entered_dollar_amount_sanitized)) + "&" + "fiat_denomination=USD" + "&" + "high_availability_type=" + str(form_entered_high_availability_type_sanitized) + "&" + "exchange_priority_1=" + str(form_entered_exchange_priority_1_sanitized) + "&" + "exchange_priority_2=" + str(form_entered_exchange_priority_2_sanitized) + "&" + "exchange_priority_3=" + str(form_entered_exchange_priority_3_sanitized) + "&" + "exchange_priority_4=" + str(form_entered_exchange_priority_4_sanitized) + "&" + "exchange_priority_5=" + str(form_entered_exchange_priority_5_sanitized) + "&" + "exchange_priority_6=" + str(form_entered_exchange_priority_6_sanitized) + "&exchange_priority_7=not_set&exchange_priority_8=not_set&exchange_priority_9=not_set&exchange_priority_10=not_set&exchange_priority_11=not_set&exchange_priority_12=not_set&exchange_priority_13=not_set&exchange_priority_14=not_set&exchange_priority_15=not_set&exchange_priority_16=not_set&exchange_priority_17=not_set&exchange_priority_18=not_set&exchange_priority_19=not_set&exchange_priority_20=not_set"
        headers = {}
        headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
        dca_create_update_response = requests.post(query_string, headers=headers)
        if dca_create_update_response.status_code == 429:
            abort(429)
        return redirect("/dca_scheduler/view_delete/" + digital_asset_endpoint_sanitized) #better to return to set_api_keys with a flask that key setting was successful
    return render_template("dca_schedule/set_dca.html", form=form, digital_asset=digital_asset_endpoint_sanitized, message_to_return_to_user=message_to_return_to_user)


@app.route("/dca_scheduler/view_delete/<digital_asset_endpoint>", methods=['GET', 'POST'])
@login_required
def dca_scheduler_view_delete(digital_asset_endpoint):
    logging.critical("/dca_scheduler/view_delete/<digital_asset_endpoint> route called")
    
    digital_asset_endpoint_sanitized = trim_sanitize_strip(10, digital_asset_endpoint)

    if digital_asset_endpoint_sanitized not in CSR_toolkit.supported_coins_list:
        logging.error("/dca_scheduler/view_delete/<digital_asset_endpoint> called and not found, returning 404")
        abort(404)
    
    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    if current_user.email_verified != "True":
        logging.error("email_verified is not True - redirecting to utilities_verify_email")
        return redirect(url_for('utilities_verify_email'))

    ###############################################################
    ### persona verification enforcement - begins ####
    if not hasattr(current_user, 'persona_verification_status'):
        logging.error("persona_verification_status not found returning 404")
        abort(404)
    
    if int(current_user.persona_verification_status) < 2:
        logging.error("current_user.persona_verification_status is less than 2")
        return redirect(url_for('persona_verification'))
    
    if int(current_user.persona_verification_status) == 2:
        logging.error("current_user.persona_verification_status is 2")
        return redirect(url_for('persona_verification_status'))

    if int(current_user.persona_verification_status) == 9:
        logging.error("current_user.persona_verification_status is 9")
        return redirect(url_for('persona_verification_status'))
    
    if int(current_user.persona_verification_status) == 3: #no action required because the user is validated
        logging.error("current_user.persona_verification_status is 3")
    ### persona verification enforcement - ends ####
    ###############################################################

    query_to_send = CSR_service_mesh_map.api_dca_schedule + "?user_id=" + str(current_user.user_id) + "&digital_asset=" + str(digital_asset_endpoint_sanitized)
    logging.error("query to send: %s" % query_to_send) #debugging
    headers = {}
    headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
    query_response = requests.get(query_to_send, headers=headers)
    if query_response.status_code == 429:
        abort(429)
    logging.error(query_response.status_code) #debugging
    logging.error(query_response.json()) #debugging
    logging.error(len(query_response.json())) #debugging

    query_response_object = query_response.json()
    logging.error(query_response_object) #debugging
    if isinstance(query_response_object, str):
        logging.error("is string") #debugging
        query_response_object = eval(query_response.json())
        logging.error(query_response_object) #debugging
        logging.error(type(query_response_object)) #debugging
        logging.error(len(query_response_object)) #debugging

    if query_response_object:
        logging.error("list not empty") #debugging
        list_of_schedule_info_to_display_to_user = []

        ###### Schedule next run:
        utc_datetime_from_epoch = pytz.utc.localize(datetime.datetime.fromtimestamp(int(query_response.json()[9])))
        timezone_adjusted_now = utc_datetime_from_epoch.astimezone(pytz.timezone(current_user.timezone))
        temp_time_stamp = timezone_adjusted_now.strftime('%Y-%m-%d %H:%M:%S')
        #temp_time_stamp = datetime.datetime.fromtimestamp(int(query_response.json()[9])).strftime('%Y-%m-%d %H:%M:%S')
        list_of_schedule_info_to_display_to_user.append("Schedule next run: %s" % (str(temp_time_stamp)))
        ######

        ###### Schedule last ran:
        if int(query_response.json()[8]) == 0:
            temp_time_stamp = "n/a"
        else:
            utc_datetime_from_epoch = pytz.utc.localize(datetime.datetime.fromtimestamp(int(query_response.json()[8])))
            timezone_adjusted_now = utc_datetime_from_epoch.astimezone(pytz.timezone(current_user.timezone))
            temp_time_stamp = timezone_adjusted_now.strftime('%Y-%m-%d %H:%M:%S')
            #temp_time_stamp = datetime.datetime.fromtimestamp(int(query_response.json()[8])).strftime('%Y-%m-%d %H:%M:%S')
        list_of_schedule_info_to_display_to_user.append("Schedule last ran: %s" % (str(temp_time_stamp)))
        ######

        ###### Schedule first ran:
        if int(query_response.json()[7]) == 0:
            temp_time_stamp = "n/a"
        else:
            utc_datetime_from_epoch = pytz.utc.localize(datetime.datetime.fromtimestamp(int(query_response.json()[7])))
            timezone_adjusted_now = utc_datetime_from_epoch.astimezone(pytz.timezone(current_user.timezone))
            temp_time_stamp = timezone_adjusted_now.strftime('%Y-%m-%d %H:%M:%S')
        list_of_schedule_info_to_display_to_user.append("Schedule first ran: %s" % (str(temp_time_stamp)))
        ######

        ###### Schedule created at:
        utc_datetime_from_epoch = pytz.utc.localize(datetime.datetime.fromtimestamp(int(query_response.json()[6])))
        timezone_adjusted_now = utc_datetime_from_epoch.astimezone(pytz.timezone(current_user.timezone))
        temp_time_stamp = timezone_adjusted_now.strftime('%Y-%m-%d %H:%M:%S')
        #temp_time_stamp = datetime.datetime.fromtimestamp(int(query_response.json()[6])).strftime('%Y-%m-%d %H:%M:%S')
        list_of_schedule_info_to_display_to_user.append("Schedule created at: %s" % (str(temp_time_stamp)))
        ######

        list_of_schedule_info_to_display_to_user.append(f"Schedule purchases: ${query_response.json()[4]} {query_response.json()[5]}")
        human_readable_time = seconds_to_human_readable(int(query_response.json()[3]), granularity=4)
        list_of_schedule_info_to_display_to_user.append("Schedule runs every: %s (%s minutes)" % (str(human_readable_time), str(int(query_response.json()[3]) / 60)))

        ######
        list_of_schedule_info_to_display_to_user.append("High Availability Type: %s" % (CSR_toolkit.supported_high_availability_type_human_friendly_map[str(query_response.json()[10])]))
        list_of_schedule_info_to_display_to_user.append("Funding Source: USD balance on exchange")
        list_of_schedule_info_to_display_to_user.append("Exchange priority #1: %s" % (CSR_toolkit.map_of_exchange_names_computer_to_human[str(query_response.json()[11])]))
        list_of_schedule_info_to_display_to_user.append("Exchange priority #2: %s" % (CSR_toolkit.map_of_exchange_names_computer_to_human[str(query_response.json()[12])]))
        list_of_schedule_info_to_display_to_user.append("Exchange priority #3: %s" % (CSR_toolkit.map_of_exchange_names_computer_to_human[str(query_response.json()[13])]))
        list_of_schedule_info_to_display_to_user.append("Exchange priority #4: %s" % (CSR_toolkit.map_of_exchange_names_computer_to_human[str(query_response.json()[14])]))
        list_of_schedule_info_to_display_to_user.append("Exchange priority #5: %s" % (CSR_toolkit.map_of_exchange_names_computer_to_human[str(query_response.json()[15])]))
        list_of_schedule_info_to_display_to_user.append("Exchange priority #6: %s" % (CSR_toolkit.map_of_exchange_names_computer_to_human[str(query_response.json()[16])]))
        
    elif not query_response_object:
        logging.error("list empty - elif") #debugging
        list_of_schedule_info_to_display_to_user = None

    else:
        logging.error("list empty - else") #debugging
        list_of_schedule_info_to_display_to_user = None

    #logging.error(list_of_schedule_info_to_display_to_user) #debugging
    ##user_id	interval_time	interval_denomination	interval_time_in_seconds	fiat_amount	fiat_denomination	date_schedule_created_epoch	first_run_epoch	last_run_epoch	next_run_epoch	high_availability_type	exchange_priority_1	exchange_priority_2	exchange_priority_3	exchange_priority_4	exchange_priority_5	exchange_priority_6	exchange_priority_7	exchange_priority_8	exchange_priority_9	exchange_priority_10	exchange_priority_11	exchange_priority_12	exchange_priority_13	exchange_priority_14	exchange_priority_15	exchange_priority_16	exchange_priority_17	exchange_priority_18	exchange_priority_19	exchange_priority_20	exchange_last_run
    ##[1, 80, 'minutes', 4800, 10, 'USD', 1638394085, 1638394440, 1638452280, 1638457080, 'failover', 'bittrex', 'kraken', 'binance_us', 'gemini', 'ftx_us', 'coinbase_pro', 'not_set', 'not_set', 'not_set', 'not_set', 'not_set', 'not_set', 'not_set', 'not_set', 'not_set', 'not_set', 'not_set', 'not_set', 'not_set', 'not_set', 'coinbase_pro']
    return render_template("dca_schedule/view_delete.html", digital_asset=digital_asset_endpoint_sanitized, list_of_schedule_info_to_display_to_user=list_of_schedule_info_to_display_to_user)

@app.route("/dca_scheduler/delete/<digital_asset_endpoint>", methods=['GET', 'POST'])
@login_required
def dca_scheduler_delete(digital_asset_endpoint):
    logging.critical("/dca_scheduler/delete/<digital_asset_endpoint> route called")
    
    digital_asset_endpoint_sanitized = trim_sanitize_strip(10, digital_asset_endpoint)
    
    if digital_asset_endpoint_sanitized not in CSR_toolkit.supported_coins_list:
        logging.error("/dca_scheduler/view_delete/<digital_asset_endpoint> called and not found, returning 404")
        abort(404)
    
    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    if current_user.email_verified != "True":
        logging.error("email_verified is not True - redirecting to utilities_verify_email")
        return redirect(url_for('utilities_verify_email'))

    ###############################################################
    ### persona verification enforcement - begins ####
    if not hasattr(current_user, 'persona_verification_status'):
        logging.error("persona_verification_status not found returning 404")
        abort(404)
    
    if int(current_user.persona_verification_status) < 2:
        logging.error("current_user.persona_verification_status is less than 2")
        return redirect(url_for('persona_verification'))
    
    if int(current_user.persona_verification_status) == 2:
        logging.error("current_user.persona_verification_status is 2")
        return redirect(url_for('persona_verification_status'))

    if int(current_user.persona_verification_status) == 9:
        logging.error("current_user.persona_verification_status is 9")
        return redirect(url_for('persona_verification_status'))
    
    if int(current_user.persona_verification_status) == 3: #no action required because the user is validated
        logging.error("current_user.persona_verification_status is 3")
    ### persona verification enforcement - ends ####
    ###############################################################

    CSR_toolkit.delete_dca_schedule(str(current_user.user_id), digital_asset_endpoint_sanitized.lower(), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
    return redirect("/dca_scheduler/view_delete/" + digital_asset_endpoint_sanitized)

@app.route("/utilities/user_settings/resend_verification_email")
@login_required
def utilities_resend_verification_email():
    logging.critical("/utilities/user_settings/resend_verification_email route called")

    headers = {}
    headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
    query_string = CSR_service_mesh_map.api_resend_verification_email + "?email_address=" + str(current_user.email) + "&identity_provider_sub_id=" + str(current_user.id)
    logging.error(query_string)
    query_response = requests.post(query_string, headers=headers)
    if query_response.status_code == 429:
        abort(429)
    query_response_json = query_response.json()
    logging.error(query_response_json) #debugging
    
    logout_user()
    logout_url_encoded = urllib.parse.quote_plus(CSR_service_mesh_map.cryptostacker_logged_out_verify_email)
    logging.error(CSR_service_mesh_map.auth0_base_logout_url_cname + logout_url_encoded + "&client_id=%s" % AUTH0_CLIENT_ID) #debugging
    return redirect(CSR_service_mesh_map.auth0_base_logout_url_cname + logout_url_encoded + "&client_id=%s" % AUTH0_CLIENT_ID)

@app.route("/utilities/verify_email")
@login_required
def utilities_verify_email():
    logging.critical("/utilities/verify_email route called")
    #this route will be called whenever a user hasn't verified their email address
    logout_user()
    logout_url_encoded = urllib.parse.quote_plus(CSR_service_mesh_map.cryptostacker_logged_out_verify_email)
    logging.error(CSR_service_mesh_map.auth0_base_logout_url_cname + logout_url_encoded + "&client_id=%s" % AUTH0_CLIENT_ID) #debugging
    return redirect(CSR_service_mesh_map.auth0_base_logout_url_cname + logout_url_encoded + "&client_id=%s" % AUTH0_CLIENT_ID)

@app.route("/utilities/first_time_login_landing_page", methods=['GET', 'POST'])
@login_required
def utilities_firsttimeloginlandingpage():
    logging.critical("/utilities/first_time_login_landing_page route called")

    if current_user.timezone != "None" and current_user.geo_location != "None":
        logging.error("timezone and geo_location already set - user settings page")
        return redirect(url_for('utilities_user_settings'))

    form = FirstTimeLogin()
    if form.validate_on_submit():
        message_to_return_to_user = None
        if form.form_entered_timezone.data not in ["pacific", "mountain", "central", "eastern", "alaska", "hawaii", "arizona"]:
            return render_template("utilities/first_time_login_landing_page.html", form=form, message_to_return_to_user=message_to_return_to_user)
        if form.form_entered_geo_location.data not in ["yes", "no"]:
            return render_template("utilities/first_time_login_landing_page.html", form=form, message_to_return_to_user=message_to_return_to_user)

        if form.form_entered_geo_location.data == "no":
            message_to_return_to_user = "Sorry, at this time our site only supports US residents."
            return render_template("utilities/first_time_login_landing_page.html", form=form, message_to_return_to_user=message_to_return_to_user)

        if not isinstance(form.form_entered_terms_of_service_checkbox.data, type(True)): #if type isn't <class 'bool'> then return 404
            abort(404)

        if form.form_entered_terms_of_service_checkbox.data == False:
            message_to_return_to_user = "You must agree to the terms of service before using CryptoStacker."
            return render_template("utilities/first_time_login_landing_page.html", form=form, message_to_return_to_user=message_to_return_to_user)

        if not isinstance(form.form_entered_age_restriction_checkbox.data, type(True)): #if type isn't <class 'bool'> then return 404
            abort(404)

        if form.form_entered_age_restriction_checkbox.data == False:
            message_to_return_to_user = "You must be at least 18 years old to use CryptoStacker."
            return render_template("utilities/first_time_login_landing_page.html", form=form, message_to_return_to_user=message_to_return_to_user)

        form_entered_referral_code_sanitized = trim_sanitize_strip(200, form.form_entered_referral_code.data)
        form_entered_referral_code_sanitized = python_sanitize_aggressive(form_entered_referral_code_sanitized)

        brand_ambassador_referral_code_row_response = CSR_toolkit.get_brand_ambassador_referral_code_row_from_referral_code(form_entered_referral_code_sanitized, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
        if not brand_ambassador_referral_code_row_response:
            message_to_return_to_user = "Invalid referral code, if you don't have a valid referral code leave the box blank"
            return render_template("utilities/first_time_login_landing_page.html", form=form, message_to_return_to_user=message_to_return_to_user)

        form_entered_timezone_sanitized = trim_sanitize_strip(20, form.form_entered_timezone.data)

        if form_entered_timezone_sanitized in CSR_toolkit.timezones_from_lower_case_human_friendly_to_computer_map:
            timezone = CSR_toolkit.timezones_from_lower_case_human_friendly_to_computer_map[form_entered_timezone_sanitized]
        else:
            timezone = "America/Los_Angeles"
        
        if form.form_entered_geo_location.data == "yes":
            geo_location = "US"

        #set timezone and geo location
        thread1 = threading.Thread(target=CSR_toolkit.set_timezone_and_geo_location_service_mesh(current_user.id, timezone, geo_location, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]))
        
        #set referral code - form_entered_referral_code_sanitized
        thread2 = threading.Thread(target=CSR_toolkit.set_referral_code_service_mesh(current_user.user_id, form_entered_referral_code_sanitized, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]))

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        return redirect(url_for('scheduler'))

    message_to_return_to_user = None
    return render_template("utilities/first_time_login_landing_page.html", form=form, message_to_return_to_user=message_to_return_to_user)


@app.route("/utilities/dca_logs", methods=['GET', 'POST'])
@login_required
def utilities_dca_logs():
    logging.critical("/utilities/dca_logs route called")

    if hasattr(current_user, 'attribute_doesnt_exist'):
        logging.error("found attribute_doesnt_exist")
    else:
        logging.error("attribute_doesnt_exist not found")
    if not hasattr(current_user, 'attribute_doesnt_exist'):
        logging.error("attribute_doesnt_exist not found")

    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    if current_user.email_verified != "True":
        logging.error("email_verified is not True - redirecting to utilities_verify_email")
        return redirect(url_for('utilities_verify_email'))

    ###############################################################
    ### persona verification enforcement - begins ####
    if not hasattr(current_user, 'persona_verification_status'):
        logging.error("persona_verification_status not found returning 404")
        abort(404)
    
    if int(current_user.persona_verification_status) < 2:
        logging.error("current_user.persona_verification_status is less than 2")
        return redirect(url_for('persona_verification'))
    
    if int(current_user.persona_verification_status) == 2:
        logging.error("current_user.persona_verification_status is 2")
        return redirect(url_for('persona_verification_status'))

    if int(current_user.persona_verification_status) == 9:
        logging.error("current_user.persona_verification_status is 9")
        return redirect(url_for('persona_verification_status'))
    
    if int(current_user.persona_verification_status) == 3: #no action required because the user is validated
        logging.error("current_user.persona_verification_status is 3")
    ### persona verification enforcement - ends ####
    ###############################################################

    form = LogViewForm()
    if form.validate_on_submit():
        
        if form.form_entered_number_of_log_events.data not in ["1", "5", "10", "50", "100"]:
            abort(404)
        if form.form_entered_log_status_events.data not in ["all", "success", "failed"]:
            abort(404)
        if form.form_entered_coin_type_events.data not in ["all", "btc", "eth", "ltc"]:
            abort(404)
        if form.form_entered_exchange_events.data not in CSR_toolkit.supported_exchanges_list_without_notset_with_all:
            abort(404)
        
        headers = {}
        headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
        query_string = CSR_service_mesh_map.api_dca_purchase_logs + "?" + "user_id=" + str(current_user.user_id) + "&limit=" + str(form.form_entered_number_of_log_events.data) + "&was_successful=" + str(form.form_entered_log_status_events.data) + "&coin_purchased=" + str(form.form_entered_coin_type_events.data) + "&exchange_used=" + str(form.form_entered_exchange_events.data)
        logging.error(query_string)
        query_response = requests.get(query_string, headers=headers)
        if query_response.status_code == 429:
            abort(429)
        query_response_json = query_response.json()
        logging.error(query_response_json) #debugging

        if isinstance(query_response_json, str):
            query_response_json = eval(query_response_json)
        if not isinstance(query_response_json, type([])):
            logging.error("error: response from api is not a list")
            return render_template("utilities/dca_logs.html", form=form, list_of_log_events=None, stage_indicator="blank")

        if len(query_response_json) < 1:
            logging.error("no DCA events, empty list")
            return render_template("utilities/dca_logs.html", form=form, list_of_log_events=None, stage_indicator="response")
        
        logging.error(query_response_json) #debugging
        query_response_json_removed_primary_key = []
        query_response_json_list_of_dictionaries = []
        for list in query_response_json:
            del list[0]
            del list[0]
            query_response_json_removed_primary_key.append(list)
        for list in query_response_json_removed_primary_key:
            temp_dict = {}
            
            utc_datetime_from_epoch = pytz.utc.localize(datetime.datetime.fromtimestamp(int(list[0])))
            timezone_adjusted_now = utc_datetime_from_epoch.astimezone(pytz.timezone(current_user.timezone))
            temp_dict["datetime"] = timezone_adjusted_now.strftime('%Y-%m-%d %H:%M:%S')

            if list[1] == "True":
                temp_status = "Success"
            elif list[1] == "False":
                temp_status = "Failed"
            else:
                temp_status = list[1]
            temp_dict["status"] = temp_status
            temp_dict["coin"] = list[2].upper()
            temp_dict["fiatamount"] = list[3]
            temp_dict["fiatdenomination"] = list[4]
            temp_dict["exchange"] = CSR_toolkit.map_of_exchange_names_computer_to_human[list[5]]
            human_readable_time = seconds_to_human_readable(int(list[6]), granularity=4)
            temp_dict["timeinterval"] = human_readable_time
            temp_dict["highavailabilitytype"] = CSR_toolkit.supported_high_availability_type_human_friendly_map[str(list[7])]
            temp_dict["exchangeorderid"] = bleach.clean(str(list[8]), strip=True)
            temp_dict["additionalinfo"] = list[9]
            query_response_json_list_of_dictionaries.append(temp_dict)
        
        return render_template("utilities/dca_logs.html", form=form, list_of_log_events=query_response_json_list_of_dictionaries, stage_indicator="response")
    return render_template("utilities/dca_logs.html", form=form, list_of_log_events=None, stage_indicator="blank")


@app.route("/utilities/dca_calculator", methods=['GET', 'POST'])
@login_required
def utilities_dca_calculator():
    logging.critical("/utilities/dca_calculator route called")

    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    if current_user.email_verified != "True":
        logging.error("email_verified is not True - redirecting to utilities_verify_email")
        return redirect(url_for('utilities_verify_email'))

    ###############################################################
    ### persona verification enforcement - begins ####
    if not hasattr(current_user, 'persona_verification_status'):
        logging.error("persona_verification_status not found returning 404")
        abort(404)
    
    if int(current_user.persona_verification_status) < 2:
        logging.error("current_user.persona_verification_status is less than 2")
        return redirect(url_for('persona_verification'))
    
    if int(current_user.persona_verification_status) == 2:
        logging.error("current_user.persona_verification_status is 2")
        return redirect(url_for('persona_verification_status'))

    if int(current_user.persona_verification_status) == 9:
        logging.error("current_user.persona_verification_status is 9")
        return redirect(url_for('persona_verification_status'))
    
    if int(current_user.persona_verification_status) == 3: #no action required because the user is validated
        logging.error("current_user.persona_verification_status is 3")
    ### persona verification enforcement - ends ####
    ###############################################################

    form = DcaCalculatorForm()
    message_to_user = None
    if form.validate_on_submit():
        form_entered_periodic_buy_amount_sanitized = trim_sanitize_strip(20, form.form_entered_periodic_buy_amount.data) #6 characters max, 101000 max
        form_entered_number_of_days_per_purchase_period_sanitized = trim_sanitize_strip(20, form.form_entered_number_of_days_per_purchase_period.data) #3 chars max, 999 max
        form_entered_amount_of_fiat_per_purchase_period_sanitized = trim_sanitize_strip(20, form.form_entered_amount_of_fiat_per_purchase_period.data) #8 chars max, 36864636 max
        form_entered_periodic_buy_amount_sanitized = python_sanitize_aggressive(form_entered_periodic_buy_amount_sanitized)
        form_entered_number_of_days_per_purchase_period_sanitized = python_sanitize_aggressive(form_entered_number_of_days_per_purchase_period_sanitized)
        form_entered_amount_of_fiat_per_purchase_period_sanitized = python_sanitize_aggressive(form_entered_amount_of_fiat_per_purchase_period_sanitized)
        try:
            form_entered_periodic_buy_amount_sanitized = format(float(form_entered_periodic_buy_amount_sanitized), '.2f')
            form_entered_number_of_days_per_purchase_period_sanitized = form_entered_number_of_days_per_purchase_period_sanitized[:5]
            form_entered_amount_of_fiat_per_purchase_period_sanitized = form_entered_amount_of_fiat_per_purchase_period_sanitized[:10]
            
            form_entered_periodic_buy_amount_sanitized = float(form_entered_periodic_buy_amount_sanitized)
            form_entered_number_of_days_per_purchase_period_sanitized = float(form_entered_number_of_days_per_purchase_period_sanitized)
            form_entered_amount_of_fiat_per_purchase_period_sanitized = float(form_entered_amount_of_fiat_per_purchase_period_sanitized)
        except ValueError:
            return render_template("utilities/dca_calculator.html", form=form)

        if form_entered_periodic_buy_amount_sanitized > 101000: #6 characters max, 101000 max
            message_to_user = "Amount to purchase per DCA must be less than 101000"
            return render_template("utilities/dca_calculator.html", form=form, message_to_user=message_to_user)
        if form_entered_number_of_days_per_purchase_period_sanitized > 999:
            message_to_user = "Number of days in a purchase period must be less than 1000"
            return render_template("utilities/dca_calculator.html", form=form, message_to_user=message_to_user)
        if form_entered_amount_of_fiat_per_purchase_period_sanitized > 36864636:
            message_to_user = "Total dollar amount to DCA per purchase period must be less than 36864636"
            return render_template("utilities/dca_calculator.html", form=form, message_to_user=message_to_user)

        if form_entered_periodic_buy_amount_sanitized < 10: #6 characters max, 101000 max
            message_to_user = "Amount to purchase per DCA must be at least 10"
            return render_template("utilities/dca_calculator.html", form=form, message_to_user=message_to_user)
        if form_entered_number_of_days_per_purchase_period_sanitized < 1:
            message_to_user = "Number of days in a purchase period must be at least 1"
            return render_template("utilities/dca_calculator.html", form=form, message_to_user=message_to_user)
        if form_entered_amount_of_fiat_per_purchase_period_sanitized < 10:
            message_to_user = "Total dollar amount to DCA per purchase period must be at least 10"
            return render_template("utilities/dca_calculator.html", form=form, message_to_user=message_to_user)

        def CalcMinuteIntervalForBTCPurchases(number_of_days_per_pay_period_int, amount_of_fiat_per_pay_period_int, minimum_fiat_purchase_amount_int):
            minutes_per_day_int = 1440
            total_minutes_per_pay_period_int = minutes_per_day_int * number_of_days_per_pay_period_int
            number_of_transactions_per_pay_period_int = amount_of_fiat_per_pay_period_int / minimum_fiat_purchase_amount_int
            minute_interval_during_pay_period_int = total_minutes_per_pay_period_int / number_of_transactions_per_pay_period_int
            return minute_interval_during_pay_period_int
        
        minutes_result = CalcMinuteIntervalForBTCPurchases(form_entered_number_of_days_per_purchase_period_sanitized, form_entered_amount_of_fiat_per_purchase_period_sanitized, form_entered_periodic_buy_amount_sanitized)
        
        message_to_user = "Purchase $%s every %s minutes" % (str(form_entered_periodic_buy_amount_sanitized), str(int(float(minutes_result))))

        return render_template("utilities/dca_calculator.html", form=form, message_to_user=message_to_user)
    
    form.form_entered_periodic_buy_amount.data = "10"
    form.form_entered_number_of_days_per_purchase_period.data = "30"
    form.form_entered_amount_of_fiat_per_purchase_period.data = "300"
    
    return render_template("utilities/dca_calculator.html", form=form, message_to_user=message_to_user)

@app.route("/utilities/user_settings", methods=['GET', 'POST'])
@login_required
def utilities_user_settings():
    logging.critical("/utilities/user_settings called")

    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    form = SetTimezoneForm()

    if form.validate_on_submit():
        logging.error("from validate_on_submit") #debugging
        #message_to_return_to_user = None

        form_entered_timezone_sanitized = trim_sanitize_strip(20, form.form_entered_timezone.data)

        if form_entered_timezone_sanitized not in CSR_toolkit.timezones_from_lower_case_human_friendly_to_computer_map:
            return render_template("utilities/user_settings.html", form=form)

        if form_entered_timezone_sanitized in CSR_toolkit.timezones_from_lower_case_human_friendly_to_computer_map:
            timezone = CSR_toolkit.timezones_from_lower_case_human_friendly_to_computer_map[form_entered_timezone_sanitized]
        else:
            timezone = "America/Los_Angeles"

        logging.error("timezone set to: %s" % timezone) #debugging

        geo_location = "US"

        headers = {}
        headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
        query_string = CSR_service_mesh_map.users_api + "?identity_provider_sub_id=" + str(current_user.id) + "&timezone=" + str(timezone) + "&geo_location=" + str(geo_location) + "&update=geolocation_and_timezone"
        logging.error("query_string set to: %s" % query_string) #debugging
        api_response = requests.post(query_string, headers=headers)
        if api_response.status_code == 429:
            abort(429)
        logging.error(api_response.json()) #debugging
        
        return redirect("/utilities/user_settings")
    
    return render_template("utilities/user_settings.html", form=form, usertimezone=CSR_toolkit.timezones_from_computer_to_human_friendly_map[str(current_user.timezone)])

@app.route("/utilities/persona_verification")
@login_required
def persona_verification():
    logging.error("/utilities/persona_verification route called")

    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    if current_user.email_verified != "True":
        logging.error("email_verified is not True - redirecting to utilities_verify_email")
        return redirect(url_for('utilities_verify_email'))

    #persona verification enforcement
    if not hasattr(current_user, 'persona_verification_status'):
        logging.error("persona_verification_status not found returning 404")
        abort(404)
    
    #if user is already verified then send them to user settings
    if int(current_user.persona_verification_status) == 3:
        logging.error("current_user.persona_verification_status is 3")
        return redirect(url_for('utilities_user_settings'))

    return render_template("utilities/persona_verification.html")

@app.route("/utilities/persona_verification/begin")
@login_required
def persona_verification_begin():
    logging.error("/utilities/persona_verification/begin route called")
    
    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    if current_user.email_verified != "True":
        logging.error("email_verified is not True - redirecting to utilities_verify_email")
        return redirect(url_for('utilities_verify_email'))

    #persona verification enforcement
    if not hasattr(current_user, 'persona_verification_status'):
        logging.error("persona_verification_status not found returning 404")
        abort(404)
    
    #if user is already verified then send them to status page
    if int(current_user.persona_verification_status) == 3:
        logging.error("current_user.persona_verification_status is 3")
        return redirect(url_for('persona_verification_status'))

    headers = {}
    headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
    query_string = CSR_service_mesh_map.users_api + "?update=persona_verification_status&user_id=" + str(current_user.user_id) + "&persona_verification_status=" + str(2)
    logging.error(query_string)
    query_response = requests.post(query_string, headers=headers)
    if query_response.status_code == 429:
        abort(429)
    verification_url = CSR_service_mesh_map.persona_base_url + "/verify?inquiry-template-id=" + CSR_service_mesh_map.persona_template_id + "&reference-id=" + str(current_user.persona_user_id) \
        + "&redirect-uri=" + "https://www.cryptostacker.io/utilities/persona_verification/redirecting_on_complete" \
        + "&environment=" + CSR_service_mesh_map.persona_environment
    logging.error(verification_url)
    return redirect(verification_url)

@app.route("/utilities/persona_verification/status")
@login_required
def persona_verification_status():
    logging.error("/utilities/persona_verification/status route called")
    
    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    if current_user.email_verified != "True":
        logging.error("email_verified is not True - redirecting to utilities_verify_email")
        return redirect(url_for('utilities_verify_email'))

    #persona verification enforcement
    if not hasattr(current_user, 'persona_verification_status'):
        logging.error("persona_verification_status not found returning 404")
        abort(404)
    
    #if the user is already verified
    if int(current_user.persona_verification_status) == 3:
        logging.error("current_user.persona_verification_status is 3")
        message_to_user_1 = "Your verification has completed, you are ready to begin using CryptoStacker!"
        message_to_user_2 = "Use the link below to get started!"
        link_below = "/scheduler"
        return render_template("utilities/persona_status.html", message_to_user_1=message_to_user_1, message_to_user_2=message_to_user_2, link_below=link_below)

    #api call to refresh status of a single user
    logging.error("api call to refresh status of a single user")
    headers = {}
    headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
    query_url = CSR_service_mesh_map.api_refresh_kyc_verification_status_single_user + "?scope=get_latest_kyc_status&user_id=" + str(current_user.user_id)
    refresh_kyc_verification_status_response = requests.get(query_url, headers=headers)
    if refresh_kyc_verification_status_response.status_code == 429:
        abort(429)
    logging.error(refresh_kyc_verification_status_response.json())

    if int(current_user.persona_verification_status) < 3:
        logging.error("current_user.persona_verification_status is less than 3")
        message_to_user_1 = "Your verification is still being processed, please wait 10-15 minutes for our system to update your verification status before you can begin using CryptoStacker.  Refresh this page to get the latest status."
        message_to_user_2 = "If you did not finish entering your verification information you may use the link below to start over."
        link_below = "/utilities/persona_verification/begin"
        return render_template("utilities/persona_status.html", message_to_user_1=message_to_user_1, message_to_user_2=message_to_user_2, link_below=link_below)

    elif int(current_user.persona_verification_status) == 9:
        logging.error("current_user.persona_verification_status is 9")
        message_to_user_1 = "Your verification is still being processed, please wait 10-15 minutes for our system to update your verification status before you can begin using CryptoStacker.  Refresh this page to get the latest status."
        message_to_user_2 = "If you did not finish entering your verification information you may use the link below to start over."
        link_below = "/utilities/persona_verification/begin"
        return render_template("utilities/persona_status.html", message_to_user_1=message_to_user_1, message_to_user_2=message_to_user_2, link_below=link_below)

    else:
        logging.error("current_user.persona_verification_status is unknown")
        message_to_user_1 = "Your verification is still being processed, please wait 10-15 minutes for our system to update your verification status before you can begin using CryptoStacker.  Refresh this page to get the latest status."
        message_to_user_2 = "If you did not finish entering your verification information you may use the link below to start over."
        link_below = "/utilities/persona_verification/begin"
        return render_template("utilities/persona_status.html", message_to_user_1=message_to_user_1, message_to_user_2=message_to_user_2, link_below=link_below)


@app.route("/utilities/persona_verification/redirecting_on_complete")
@login_required
def persona_verification_redirecting_on_complete():
    logging.error("/utilities/persona_verification/redirecting_on_complete route called")
    
    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    if current_user.email_verified != "True":
        logging.error("email_verified is not True - redirecting to utilities_verify_email")
        return redirect(url_for('utilities_verify_email'))

    #if the user is already verified
    if int(current_user.persona_verification_status) == 3:
        logging.error("current_user.persona_verification_status is 3")
        return redirect(url_for('persona_verification_status'))

    #api call to refresh status of a single user
    logging.error("api call to refresh status of a single user")
    headers = {}
    headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
    query_url = CSR_service_mesh_map.api_refresh_kyc_verification_status_single_user + "?scope=get_latest_kyc_status&user_id=" + str(current_user.user_id)
    refresh_kyc_verification_status_response = requests.get(query_url, headers=headers)
    if refresh_kyc_verification_status_response.status_code == 429:
        abort(429)
    logging.error(refresh_kyc_verification_status_response.json())
    return redirect(url_for('persona_verification_status'))


@app.route("/utilities/user_settings/delete_user/confirmation")
@login_required
def utilities_user_settings_delete_user_confirmation():
    logging.critical("/utilities/user_settings/delete_user/confirmation called")

    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    return render_template("utilities/delete_user_confirmation.html", email_address=current_user.email)


@app.route("/utilities/user_settings/delete_user")
@login_required
def utilities_user_settings_delete_user():
    logging.critical("/utilities/user_settings/delete_user called")
    headers = {}
    headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
    query_string = CSR_service_mesh_map.api_delete_users_everywhere + "?user_id=" + str(current_user.user_id) + "&deleteoptions=deleteauth0"
    logging.error(query_string)
    logout_user()
    try:
        delete_response = requests.delete(query_string, headers=headers, timeout=5)
        if delete_response.status_code == 429:
            abort(429)
    except:
        pass
    return redirect(url_for("index"))

@app.route("/utilities/user_settings/reset_mfa")
@login_required
def utilities_user_settings_reset_mfa():
    logging.critical("/utilities/user_settings/reset_mfa called")

    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    if current_user.email_verified != "True":
        logging.error("email_verified is not True - redirecting to utilities_verify_email")
        return redirect(url_for('utilities_verify_email'))

    ###############################################################
    ### persona verification enforcement - begins ####
    if not hasattr(current_user, 'persona_verification_status'):
        logging.error("persona_verification_status not found returning 404")
        abort(404)
    
    if int(current_user.persona_verification_status) < 2:
        logging.error("current_user.persona_verification_status is less than 2")
        return redirect(url_for('persona_verification'))
    
    if int(current_user.persona_verification_status) == 2:
        logging.error("current_user.persona_verification_status is 2")
        return redirect(url_for('persona_verification_status'))

    if int(current_user.persona_verification_status) == 9:
        logging.error("current_user.persona_verification_status is 9")
        return redirect(url_for('persona_verification_status'))
    
    if int(current_user.persona_verification_status) == 3: #no action required because the user is validated
        logging.error("current_user.persona_verification_status is 3")
    ### persona verification enforcement - ends ####
    ###############################################################

    #access_token = auth0_lib.get_bearer_token(AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET)
    #auth0_lib.reset_google_mfa(current_user.id, access_token)
    headers = {}
    headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
    query_string = CSR_service_mesh_map.api_auth0 + "?scope=reset_mfa&identity_provider_sub_id=" + urllib.parse.quote(current_user.id)
    logging.error(query_string)
    query_response = requests.post(query_string, headers=headers)
    if query_response.status_code == 429:
        abort(429)

    return redirect(url_for("logout"))


@app.route("/subscribe/manage_subscription")
@login_required
def manage_subscription():
    logging.critical("/subscribe/manage_subscription called")

    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    if current_user.email_verified != "True":
        logging.error("email_verified is not True - redirecting to utilities_verify_email")
        return redirect(url_for('utilities_verify_email'))

    ###############################################################
    ### persona verification enforcement - begins ####
    if not hasattr(current_user, 'persona_verification_status'):
        logging.error("persona_verification_status not found returning 404")
        abort(404)
    
    if int(current_user.persona_verification_status) < 2:
        logging.error("current_user.persona_verification_status is less than 2")
        return redirect(url_for('persona_verification'))
    
    if int(current_user.persona_verification_status) == 2:
        logging.error("current_user.persona_verification_status is 2")
        return redirect(url_for('persona_verification_status'))

    if int(current_user.persona_verification_status) == 9:
        logging.error("current_user.persona_verification_status is 9")
        return redirect(url_for('persona_verification_status'))
    
    if int(current_user.persona_verification_status) == 3: #no action required because the user is validated
        logging.error("current_user.persona_verification_status is 3")
    ### persona verification enforcement - ends ####
    ###############################################################

    #threading will make this fucntion faster
    response_tuple = CSR_toolkit.get_active_subscription_tier_transaction_stats_exceeded_bool(current_user.user_id, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
    logging.error(response_tuple) #debugging
    exceeded_tier_limit = response_tuple[0]
    active_tier = response_tuple[1]
    number_of_transactions_this_month = response_tuple[2]
    dollar_amount_of_transactions_this_month = response_tuple[3]
    total_number_of_transactions = response_tuple[4]
    total_dollar_amount_of_transactions = response_tuple[5]
    user_payments = response_tuple[6]
    user_subscription_status = response_tuple[7]
    pending_payments_many = response_tuple[8] #[[265, 1, '2d42a0dc-235e-4405-8e22-eaca8aa7072f', 'WV', 1640716663]]
    logging.error(pending_payments_many) #debugging
    
    #####
    #build subscription stats/info lists & dicts for the jinja2 table - begins
    #####
    list_of_subscription_tier_data = []
    subscription_tier_data_list_of_dictionaries = []
    exceeded_tier_limit_string = "No"
    if exceeded_tier_limit:
        exceeded_tier_limit_string = "Yes"
    
    temp_dict = {}
    temp_dict["active_tier"] = active_tier
    temp_dict["exceeded_tier_limit"] = exceeded_tier_limit_string
    temp_dict["number_of_transactions_this_month"] = number_of_transactions_this_month
    temp_dict["dollar_amount_of_transactions_this_month"] = dollar_amount_of_transactions_this_month
    temp_dict["total_number_of_transactions"] = total_number_of_transactions
    temp_dict["total_dollar_amount_of_transactions"] = total_dollar_amount_of_transactions

    subscription_tier_data_list_of_dictionaries.append(temp_dict)
    
    #####
    #build subscription stats/info lists & dicts for the jinja2 table - ends
    #####
    
    #####
    #build payment history lists & dicts for the jinja2 table - begins
    #####
    #payment-time-iso (timezone), order_id, payment_amount_in_usd, number_of_months_paid_for, tier_paid_for, expiration-time-iso (timezone)
    #id	user_id	epoch_of_payment	payment_provider	crypto_or_fiat_gateway	order_id	payment_amount_in_usd	number_of_months_paid_for	tier_paid_for	epoch_expiration	description	referral_code	account_created_epoch	current_us_state
    
    list_of_payment_history_data = []
    payment_history_data_list_of_dictionaries = []
    logging.error("user_payments type:") #debugging
    logging.error(type(user_payments)) #debugging
    logging.error(user_payments) #debugging
    logging.error("pending_payments_many type") #debugging
    logging.error(type(pending_payments_many)) #debugging
    logging.error(pending_payments_many) #debugging
    if len(user_payments) < 1 and len(pending_payments_many) < 1: #if both pending & paid payments are empty then return None, else build the list of dictionaries to be passed to jinja2 template
        payment_history_data_list_of_dictionaries = None
    else:
        #pending
        for pending_payment_row in pending_payments_many: #pending
            temp_dict = {}
            temp_dict["status"] = "Pending"
            temp_dict["datetime_of_payment"] = "--"
            temp_dict["order_id"] = str(pending_payment_row[2])
            temp_dict["payment_amount_in_usd"] = str(pending_payment_row[7])
            temp_dict["number_of_months_paid_for"] = str(pending_payment_row[6])
            temp_dict["tier_paid_for"] = str(pending_payment_row[5])
            temp_dict["datetime_of_expiration"] = "--"
            payment_history_data_list_of_dictionaries.append(temp_dict)
        #pending_payments_many = response_tuple[8] #[[265, 1, '2d42a0dc-235e-4405-8e22-eaca8aa7072f', 'WV', 1640716663]]

        #paid
        for payment_row_list in user_payments: #paid
            logging.error(payment_row_list) #debugging
            temp_list = []
            temp_list.append(payment_row_list[2]) #epoch_of_payment 0
            temp_list.append(payment_row_list[5]) #order_id 1
            temp_list.append(payment_row_list[6]) #payment_amount_in_usd 2
            temp_list.append(payment_row_list[7]) #number_of_months_paid_for 3
            temp_list.append(payment_row_list[8]) #tier_paid_for 4
            temp_list.append(payment_row_list[9]) #epoch_expiration 5
            list_of_payment_history_data.append(temp_list)
    
        for list_item in list_of_payment_history_data:
            temp_dict = {}
            #list_item[0] #epoch_of_payment 0
            utc_datetime_from_epoch = pytz.utc.localize(datetime.datetime.fromtimestamp(int(list_item[0])))
            timezone_adjusted_now = utc_datetime_from_epoch.astimezone(pytz.timezone(current_user.timezone))
            temp_dict["status"] = "Paid"
            temp_dict["datetime_of_payment"] = timezone_adjusted_now.strftime('%Y-%m-%d %H:%M:%S')

            temp_dict["order_id"] = list_item[1] #order_id 1
            temp_dict["payment_amount_in_usd"] = list_item[2] #payment_amount_in_usd 2
            temp_dict["number_of_months_paid_for"] = list_item[3] #number_of_months_paid_for 3
            temp_dict["tier_paid_for"] = list_item[4] #tier_paid_for 4
            
            #list_item[5] #epoch_expiration 5
            utc_datetime_from_epoch = pytz.utc.localize(datetime.datetime.fromtimestamp(int(list_item[5])))
            timezone_adjusted_now = utc_datetime_from_epoch.astimezone(pytz.timezone(current_user.timezone))
            temp_dict["datetime_of_expiration"] = timezone_adjusted_now.strftime('%Y-%m-%d %H:%M:%S')
            payment_history_data_list_of_dictionaries.append(temp_dict)
    #####
    #build payment history lists & dicts for the jinja2 table - ends
    #####
    
    return render_template("subscribe/manage_subscription.html", payment_history_data_list_of_dictionaries=payment_history_data_list_of_dictionaries, subscription_tier_data_list_of_dictionaries=subscription_tier_data_list_of_dictionaries)

@app.route("/subscribe/<user_determined_tier>/<user_determinted_months>", methods=['GET', 'POST'])
@login_required
def subscribe_user_determined_tier_user_determinted_months_state(user_determined_tier, user_determinted_months):
    logging.critical("/subscribe/<user_determined_tier>/<user_determinted_months> called")

    if user_determined_tier not in ["2", "3"]:
        logging.error("/subscribe/<user_determined_tier>/<user_determinted_months> route called and not found, returning 404")
        abort(404)
    if user_determinted_months not in ["1", "3", "6", "12", "1200"]: #lifetime could be zero 0 instead?
        logging.error("/subscribe/<user_determined_tier>/<user_determinted_months> route called and not found, returning 404")
        abort(404)
    
    #Development - https://dev-checkout.opennode.com/ {id}
    #Production - https://checkout.opennode.com/ {id}
    opennode_hosted_checkout_base_url = CSR_service_mesh_map.opennode_hosted_checkout_base_url
    
    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    if current_user.email_verified != "True":
        logging.error("email_verified is not True - redirecting to utilities_verify_email")
        return redirect(url_for('utilities_verify_email'))

    ###############################################################
    ### persona verification enforcement - begins ####
    if not hasattr(current_user, 'persona_verification_status'):
        logging.error("persona_verification_status not found returning 404")
        abort(404)
    
    if int(current_user.persona_verification_status) < 2:
        logging.error("current_user.persona_verification_status is less than 2")
        return redirect(url_for('persona_verification'))
    
    if int(current_user.persona_verification_status) == 2:
        logging.error("current_user.persona_verification_status is 2")
        return redirect(url_for('persona_verification_status'))

    if int(current_user.persona_verification_status) == 9:
        logging.error("current_user.persona_verification_status is 9")
        return redirect(url_for('persona_verification_status'))
    
    if int(current_user.persona_verification_status) == 3: #no action required because the user is validated
        logging.error("current_user.persona_verification_status is 3")
    ### persona verification enforcement - ends ####
    ###############################################################

    form = SelectUsState()
    if form.validate_on_submit():

        form_entered_us_state_sanitized = trim_sanitize_strip(5, form.form_entered_us_state.data)

        if form_entered_us_state_sanitized not in ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC', 'AS', 'GU', 'MP', 'PR', 'VI']:
            logging.error("incorrect state abbreviation posted")
            abort(404)
        us_state = form_entered_us_state_sanitized
        
        if user_determinted_months == "1":
            description = us_state + ":" + "T" + user_determined_tier + ":" + user_determinted_months + "M: " + "Tier " + user_determined_tier + " for " + user_determinted_months + " month"
        elif user_determinted_months == "lifetime":
            description = us_state + ":" + "T" + user_determined_tier + ":" + user_determinted_months + "M: " + "Tier " + user_determined_tier + " for " + user_determinted_months
        else:
            description = us_state + ":" + "T" + user_determined_tier + ":" + user_determinted_months + "M: " + "Tier " + user_determined_tier + " for " + user_determinted_months + " months"

        dollar_amount = csr_price_map[user_determined_tier][user_determinted_months]
        fiat_denomination = "USD"
        
        if int(current_user.time_created_epoch) > int(CSR_toolkit.epoch_plus_months_epoch(CSR_toolkit.current_time_epoch(), -12)):
            logging.error("user's account was created less than 12 months ago, referral code discount is available if user signed up with referral code")
            logging.error("checking for valid referral code")
            users_referral_code = CSR_toolkit.get_referral_code_from_user_subscription_status(current_user.user_id, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
            referral_code_row = CSR_toolkit.get_brand_ambassador_referral_code_row_from_referral_code_subscribe(users_referral_code, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
            if referral_code_row: #if the brand ambassador referral code exists apply a 10% discount
                dollar_amount = int(float(dollar_amount) * float(0.9)) #apply 10% discount

        headers = {}
        headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
        logging.error("NEW OPENNODE INTERNAL CALL") #debugging remove later
        query_url = CSR_service_mesh_map.api_opennode + "?scope=create_charge" + "&dollar_amount=" + str(dollar_amount) + "&fiat_denomination=" + str(fiat_denomination) + "&email_address=" + str(current_user.email) + "&description=" + urllib.parse.quote(description)
        charge_response = requests.post(query_url, headers=headers)
        if charge_response.status_code == 429:
            abort(429)
        charge_response_json = charge_response.json()
        logging.error(charge_response_json) #debugging remove later
        if "failed" not in charge_response_json:
            order_id = charge_response_json["data"]["id"]
            query_url = CSR_service_mesh_map.api_pending_payments + "?user_id=" + str(current_user.user_id) + "&current_us_state=" + str(us_state) + "&order_id=" + str(order_id) + "&purchased_tier=" + str(user_determined_tier) + "&purchased_months=" + str(user_determinted_months) + "&payment_amount_in_usd=" + str(dollar_amount)
            pending_payments_response = requests.post(query_url, headers=headers)
            if pending_payments_response.status_code == 429:
                abort(429)
            redirect_url = opennode_hosted_checkout_base_url + str(order_id)
            return redirect(redirect_url)
        else:
            return redirect("/")

    return render_template("subscribe/subscribe_select_state.html", form=form)


######################################################################################################
########### ADMIN SECTION ############################################################################
######################################################################################################

@app.route("/admin")
@login_required
def admin_portal():
    logging.critical("/admin called")
    
    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        return render_template("admin/main.html", email=current_user.email)

    else:
        abort(404)


@app.route("/admin/check_ba_referral_code_exists", methods=['GET', 'POST'])
@login_required
def admin_portal_check_ba_referral_code_exists():
    logging.critical("/admin/check_ba_referral_code_exists called")
    
    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        message_to_user = None
        form = AdminCheck_ba_ReferralCodeExists()
        if form.validate_on_submit():
            form_entered_referral_code_sanitized = bleach.clean(str(form.form_entered_referral_code.data), strip=True)
            form_entered_referral_code_sanitized = form_entered_referral_code_sanitized[:201]
            referral_code_row = CSR_toolkit.get_brand_ambassador_referral_code_row_from_referral_code(form_entered_referral_code_sanitized, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
            if referral_code_row:
                message_to_user = "User ID: %s - Referral Code: %s - Revenue Share: %s" % (str(referral_code_row[0]), str(referral_code_row[1]), str(referral_code_row[2]))
            if not referral_code_row:
                message_to_user = "Referral Code: %s doesn't exist" % form_entered_referral_code_sanitized
            return render_template("admin/check_ba_referral_code_exists.html", form=form, message_to_user=message_to_user)
        return render_template("admin/check_ba_referral_code_exists.html", form=form, message_to_user=message_to_user)

    else:
        abort(404)


@app.route("/admin/set_ba_referral_code", methods=['GET', 'POST'])
@login_required
def admin_portal_set_ba_referral_code():
    logging.critical("/admin/set_ba_referral_code")
    
    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        message_to_user = None
        form = AdminSet_ba_ReferralCode()
        if form.validate_on_submit():
            form_entered_referral_code_sanitized = bleach.clean(str(form.form_entered_referral_code.data), strip=True)
            form_entered_referral_code_sanitized = form_entered_referral_code_sanitized[:201]
            form_entered_user_id_sanitized = bleach.clean(str(form.form_entered_user_id.data), strip=True)
            form_entered_revenue_share_percentage_sanitized = bleach.clean(str(form.form_entered_revenue_share_percentage.data), strip=True)
            form_entered_revenue_share_percentage_sanitized = int(form_entered_revenue_share_percentage_sanitized)
            try:
                int(form_entered_user_id_sanitized)
            except:
                message_to_user = "didn't enter an int, try again"
                return render_template("admin/set_ba_referral_code.html", form=form, message_to_user=message_to_user)
            api_call_response = CSR_toolkit.set_brand_ambassador_referral_code(form_entered_user_id_sanitized, form_entered_referral_code_sanitized, form_entered_revenue_share_percentage_sanitized, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
            message_to_user = str(api_call_response)

            return render_template("admin/set_ba_referral_code.html", form=form, message_to_user=message_to_user)
        return render_template("admin/set_ba_referral_code.html", form=form, message_to_user=message_to_user)
    else:
        abort(404)


@app.route("/admin/delete_ba_referral_code", methods=['GET', 'POST'])
@login_required
def admin_portal_delete_ba_referral_code():
    logging.critical("/admin/delete_ba_referral_code")
    
    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        message_to_user = None
        form = AdminDelete_ba_ReferralCode()
        if form.validate_on_submit():
            form_entered_user_id_sanitized = bleach.clean(str(form.form_entered_user_id.data), strip=True)
            try:
                int(form_entered_user_id_sanitized)
            except:
                message_to_user = "didn't enter an int, try again"
                return render_template("admin/delete_ba_referral_code.html", form=form, message_to_user=message_to_user)
            api_call_response = CSR_toolkit.delete_brand_ambassador_referral_code_by_user_id(form_entered_user_id_sanitized, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
            message_to_user = str(api_call_response)

            return render_template("admin/delete_ba_referral_code.html", form=form, message_to_user=message_to_user)
        return render_template("admin/delete_ba_referral_code.html", form=form, message_to_user=message_to_user)

    else:
        abort(404)


@app.route("/admin/set_ba_smv_ev", methods=['GET', 'POST'])
@login_required
def admin_portal_set_ba_smv_ev():
    logging.critical("/admin/set_ba_smv_ev")
    #set brand_ambassador & site_metrics_viewer & email_verified

    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        message_to_user = None
        form = Admin_set_ba_smv_ev()
        if form.validate_on_submit():
            form_entered_user_id_sanitized = bleach.clean(str(form.form_entered_user_id.data), strip=True)
            form_entered_brand_ambassador_bool_sanitized = bleach.clean(str(form.form_entered_brand_ambassador_bool.data), strip=True)
            form_entered_site_metrics_viewer_bool_sanitized = bleach.clean(str(form.form_entered_site_metrics_viewer_bool.data), strip=True)
            form_entered_email_verified_bool_sanitized = bleach.clean(str(form.form_entered_email_verified_bool.data), strip=True)
            if form_entered_brand_ambassador_bool_sanitized not in ["True", "False"]:
                abort(404)
            if form_entered_site_metrics_viewer_bool_sanitized not in ["True", "False"]:
                abort(404)
            if form_entered_email_verified_bool_sanitized not in ["True", "False"]:
                abort(404)
            
            try:
                int(form_entered_user_id_sanitized)
            except:
                message_to_user = "didn't enter an int, try again"
                return render_template("admin/set_ba_smv_ev.html", form=form, message_to_user=message_to_user)
            api_call_response = CSR_toolkit.set_brand_ambassador_site_metrics_viewer_email_verified(form_entered_user_id_sanitized, form_entered_brand_ambassador_bool_sanitized, form_entered_site_metrics_viewer_bool_sanitized, form_entered_email_verified_bool_sanitized, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
            message_to_user = str(api_call_response)

            return render_template("admin/set_ba_smv_ev.html", form=form, message_to_user=message_to_user)
        return render_template("admin/set_ba_smv_ev.html", form=form, message_to_user=message_to_user)

    else:
        abort(404)
        

@app.route("/admin/set_sub_tier_and_lock", methods=['GET', 'POST'])
@login_required
def admin_portal_set_sub_tier_and_lock():
    logging.critical("/admin/set_sub_tier_and_lock")

    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        message_to_user = None
        form = AdminSetSubTierAndLock()
        if form.validate_on_submit():
            form_entered_user_id_sanitized = bleach.clean(str(form.form_entered_user_id.data), strip=True)
            form_entered_tier_sanitized = bleach.clean(str(form.form_entered_tier.data), strip=True)
            form_entered_admin_tier_lock_bool_sanitized = bleach.clean(str(form.form_entered_admin_tier_lock_bool.data), strip=True)
            if form_entered_tier_sanitized not in ["1", "2", "3"]:
                abort(404)
            if form_entered_admin_tier_lock_bool_sanitized not in ["True", "False"]:
                abort(404)

            try:
                int(form_entered_user_id_sanitized)
            except:
                message_to_user = "didn't enter an int, try again"
                return render_template("admin/set_sub_tier_and_lock.html", form=form, message_to_user=message_to_user)
            api_call_response = CSR_toolkit.set_tier_and_admin_lock_user_subscription_status(form_entered_user_id_sanitized, form_entered_tier_sanitized, form_entered_admin_tier_lock_bool_sanitized, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
            message_to_user = str(api_call_response[0]) + " & " + str(api_call_response[1])

            return render_template("admin/set_sub_tier_and_lock.html", form=form, message_to_user=message_to_user)
        return render_template("admin/set_sub_tier_and_lock.html", form=form, message_to_user=message_to_user)

    else:
        abort(404)
        


@app.route("/admin/set_verification_status", methods=['GET', 'POST'])
@login_required
def admin_portal_set_verification_status():
    logging.critical("/admin/set_verification_status")

    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        message_to_user = None
        form = AdminUserCognitoVerificationStatus()
        if form.validate_on_submit():
            form_entered_user_id_sanitized = bleach.clean(str(form.form_entered_user_id.data), strip=True)
            form_entered_verification_status_sanitized = bleach.clean(str(form.form_entered_verification_status.data), strip=True)
            if form_entered_verification_status_sanitized not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
                abort(404)

            try:
                int(form_entered_user_id_sanitized)
            except:
                message_to_user = "didn't enter an int, try again"
                return render_template("admin/set_verification_status.html", form=form, message_to_user=message_to_user)
            
            try:
                int(form_entered_verification_status_sanitized)
            except:
                message_to_user = "didn't enter an int, try again"
                return render_template("admin/set_verification_status.html", form=form, message_to_user=message_to_user)
            
            headers = {}
            headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
            query_string = CSR_service_mesh_map.users_api + "?update=persona_verification_status&user_id=" + str(form_entered_user_id_sanitized) + "&persona_verification_status=" + str(form_entered_verification_status_sanitized)
            logging.error(query_string)
            query_response = requests.post(query_string, headers=headers)
            message_to_user = "updated verification status"

            return render_template("admin/set_verification_status.html", form=form, message_to_user=message_to_user)
        return render_template("admin/set_verification_status.html", form=form, message_to_user=message_to_user)

    else:
        abort(404)
        

@app.route("/admin/delete_user_by_email", methods=['GET', 'POST'])
@login_required
def admin_portal_delete_user_by_email():
    logging.critical("/admin/delete_user_by_email")

    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        message_to_user = None
        form = AdminEnterEmailAddress()
        if form.validate_on_submit():
            form_entered_email_address_sanitized = bleach.clean(str(form.form_entered_email_address.data), strip=True)
            CSR_toolkit.delete_user_by_email(form_entered_email_address_sanitized, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
            message_to_user = "user(s) with %s email address deleted" % str(form_entered_email_address_sanitized)
            return render_template("admin/delete_user_by_email.html", form=form, message_to_user=message_to_user)
        return render_template("admin/delete_user_by_email.html", form=form, message_to_user=message_to_user)
    else:
        abort(404)

@app.route("/admin/delete_user_by_user_id", methods=['GET', 'POST'])
@login_required
def admin_portal_delete_user_by_user_id():
    logging.critical("/admin/delete_user_by_user_id")

    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        message_to_user = None
        form = AdminEnterUserID()
        if form.validate_on_submit():
            form_entered_user_id_sanitized = bleach.clean(str(form.form_entered_user_id.data), strip=True)
            try:
                int(form_entered_user_id_sanitized)
            except:
                message_to_user = "didn't enter an int, try again"
                return render_template("admin/delete_user_by_user_id.html", form=form, message_to_user=message_to_user)
            CSR_toolkit.delete_user_by_user_id(form_entered_user_id_sanitized, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
            message_to_user = "user(s) with %s user id deleted" % str(form_entered_user_id_sanitized)
            return render_template("admin/delete_user_by_user_id.html", form=form, message_to_user=message_to_user)
        return render_template("admin/delete_user_by_user_id.html", form=form, message_to_user=message_to_user)
    else:
        abort(404)

@app.route("/admin/delete_and_block_user_by_email", methods=['GET', 'POST'])
@login_required
def admin_portal_delete_and_block_user_by_email():
    logging.critical("/admin/delete_and_block_user_by_email")

    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        message_to_user = None
        form = AdminEnterEmailAddress()
        if form.validate_on_submit():
            form_entered_email_address_sanitized = bleach.clean(str(form.form_entered_email_address.data), strip=True)
            CSR_toolkit.delete_and_block_user_by_email(form_entered_email_address_sanitized, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
            message_to_user = "user(s) with %s email address deleted" % str(form_entered_email_address_sanitized)
            return render_template("admin/delete_user_by_email.html", form=form, message_to_user=message_to_user)
        return render_template("admin/delete_user_by_email.html", form=form, message_to_user=message_to_user)
    else:
        abort(404)

@app.route("/admin/delete_and_block_user_by_user_id", methods=['GET', 'POST'])
@login_required
def admin_portal_delete_and_block_user_by_user_id():
    logging.critical("/admin/delete_and_block_user_by_user_id")

    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        message_to_user = None
        form = AdminEnterUserID()
        if form.validate_on_submit():
            form_entered_user_id_sanitized = bleach.clean(str(form.form_entered_user_id.data), strip=True)
            try:
                int(form_entered_user_id_sanitized)
            except:
                message_to_user = "didn't enter an int, try again"
                return render_template("admin/delete_user_by_user_id.html", form=form, message_to_user=message_to_user)
            CSR_toolkit.delete_and_block_user_by_user_id(form_entered_user_id_sanitized, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
            message_to_user = "user(s) with %s user id deleted" % str(form_entered_user_id_sanitized)
            return render_template("admin/delete_user_by_user_id.html", form=form, message_to_user=message_to_user)
        return render_template("admin/delete_user_by_user_id.html", form=form, message_to_user=message_to_user)
    else:
        abort(404)

@app.route("/admin/delete_dca_schedule", methods=['GET', 'POST'])
@login_required
def admin_portal_delete_dca_schedule():
    logging.critical("/admin/delete_dca_schedule")

    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        message_to_user = None
        form = AdminDeleteDcaSchedule()
        if form.validate_on_submit():
            form_entered_user_id_sanitized = bleach.clean(str(form.form_entered_user_id.data), strip=True)
            form_entered_coin_schedule_sanitized = bleach.clean(str(form.form_entered_coin_schedule.data), strip=True)
            if form_entered_coin_schedule_sanitized not in CSR_toolkit.supported_coins_list:
                abort(404)
            try:
                int(form_entered_user_id_sanitized)
            except:
                message_to_user = "didn't enter an int, try again"
                return render_template("admin/delete_dca_schedule.html", form=form, message_to_user=message_to_user)
            
            CSR_toolkit.delete_dca_schedule(str(form_entered_user_id_sanitized), form_entered_coin_schedule_sanitized.lower(), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
            message_to_user = "Deleted DCA schedule successfully for user ID: %s" % str(form_entered_user_id_sanitized)
            return render_template("admin/delete_dca_schedule.html", form=form, message_to_user=message_to_user)
        return render_template("admin/delete_dca_schedule.html", form=form, message_to_user=message_to_user)
    else:
        abort(404)

@app.route("/admin/delete_api_keys", methods=['GET', 'POST'])
@login_required
def admin_portal_delete_api_keys():
    logging.critical("/admin/delete_api_keys")

    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        message_to_user = None
        form = AdminDeleteApiKeys()
        if form.validate_on_submit():
            form_entered_user_id_sanitized = bleach.clean(str(form.form_entered_user_id.data), strip=True)
            form_entered_exchange_sanitized = bleach.clean(str(form.form_entered_exchange.data), strip=True)
            if form_entered_exchange_sanitized not in CSR_toolkit.supported_exchanges_list_without_notset:
                abort(404)
            try:
                int(form_entered_user_id_sanitized)
            except:
                message_to_user = "didn't enter an int, try again"
                return render_template("admin/delete_api_keys.html", form=form, message_to_user=message_to_user)
            
            CSR_toolkit.delete_users_exchange_api_key_write_only(str(form_entered_user_id_sanitized), form_entered_exchange_sanitized.lower(), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
            message_to_user = "Deleted API key successfully for user ID: %s" % str(form_entered_user_id_sanitized)
            return render_template("admin/delete_api_keys.html", form=form, message_to_user=message_to_user)
        return render_template("admin/delete_api_keys.html", form=form, message_to_user=message_to_user)
    else:
        abort(404)

@app.route("/admin/delete_dca_logs", methods=['GET', 'POST'])
@login_required
def admin_portal_delete_dca_logs():
    logging.critical("/admin/delete_dca_logs")

    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        message_to_user = None
        form = AdminEnterUserID()
        if form.validate_on_submit():
            form_entered_user_id_sanitized = bleach.clean(str(form.form_entered_user_id.data), strip=True)
            try:
                int(form_entered_user_id_sanitized)
            except:
                message_to_user = "didn't enter an int, try again"
                return render_template("admin/delete_dca_logs.html", form=form, message_to_user=message_to_user)
            delete_response = CSR_toolkit.delete_all_dca_logs_for_user_id(form_entered_user_id_sanitized, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
            return render_template("admin/delete_dca_logs.html", form=form, message_to_user=delete_response)
        return render_template("admin/delete_dca_logs.html", form=form, message_to_user=message_to_user)
    else:
        abort(404)

@app.route("/admin/brand_ambassador_metrics", methods=['GET', 'POST'])
@login_required
def admin_portal_brand_ambassador_metrics():
    logging.critical("/admin/brand_ambassador_metrics")

    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        message_to_user = None
        form = AdminEnterUserID()
        if form.validate_on_submit():
            form_entered_user_id_sanitized = bleach.clean(str(form.form_entered_user_id.data), strip=True)
            try:
                int(form_entered_user_id_sanitized)
            except:
                message_to_user = "didn't enter an int, try again"
                return render_template("admin/brand_ambassador_metrics.html", form=form, message_to_user=message_to_user)
            
            brand_ambassador_metrics_tuple = CSR_toolkit.get_brand_ambassador_metrics(form_entered_user_id_sanitized, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
            
            return render_template("admin/brand_ambassador_metrics.html", form=form, email_address=form_entered_user_id_sanitized, referral_code=brand_ambassador_metrics_tuple[0], 
            revenue_share_percentage=brand_ambassador_metrics_tuple[1], total_users_with_referral_code=brand_ambassador_metrics_tuple[2], 
            unique_paying_users=brand_ambassador_metrics_tuple[6], gross_revenue_generated=brand_ambassador_metrics_tuple[3],
            gross_revenue_previous_quarter=brand_ambassador_metrics_tuple[4], gross_revenue_current_quarter=brand_ambassador_metrics_tuple[5],
            gross_revenue_brand_ambassador_share=brand_ambassador_metrics_tuple[7], gross_revenue_previous_quarter_ambassador_share=brand_ambassador_metrics_tuple[8],
            gross_revenue_quarter_to_date_ambassador_share=brand_ambassador_metrics_tuple[9]
            )

        return render_template("admin/brand_ambassador_metrics.html", form=form, message_to_user=message_to_user)
    else:
        abort(404)


@app.route("/admin/view_manage_subscription", methods=['GET', 'POST'])
@login_required
def admin_portal_view_manage_subscription():
    logging.critical("/admin/view_manage_subscription")

    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        message_to_user = None
        form = AdminEnterUserID()
        if form.validate_on_submit():
            form_entered_user_id_sanitized = bleach.clean(str(form.form_entered_user_id.data), strip=True)
            try:
                int(form_entered_user_id_sanitized)
            except:
                message_to_user = "didn't enter an int, try again"
                return render_template("admin/manage_subscription.html", form=form, message_to_user=message_to_user)
            
            response_tuple = CSR_toolkit.get_active_subscription_tier_transaction_stats_exceeded_bool(form_entered_user_id_sanitized, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
            exceeded_tier_limit = response_tuple[0]
            active_tier = response_tuple[1]
            number_of_transactions_this_month = response_tuple[2]
            dollar_amount_of_transactions_this_month = response_tuple[3]
            total_number_of_transactions = response_tuple[4]
            total_dollar_amount_of_transactions = response_tuple[5]
            user_payments = response_tuple[6]
            user_subscription_status = response_tuple[7]
            pending_payments_many = response_tuple[8] #[[1, 26, '6685893e-c0be-4a89-b02e-aa8e05e4cf2d', 'AL', 1641515447, 3, 1200, 585]]
            logging.error(pending_payments_many) #debugging

            #####
            #build subscription stats/info lists & dicts for the jinja2 table - begins
            #####
            list_of_subscription_tier_data = []
            subscription_tier_data_list_of_dictionaries = []
            exceeded_tier_limit_string = "No"
            if exceeded_tier_limit:
                exceeded_tier_limit_string = "Yes"

            temp_dict = {}
            temp_dict["active_tier"] = active_tier
            temp_dict["exceeded_tier_limit"] = exceeded_tier_limit_string
            temp_dict["number_of_transactions_this_month"] = number_of_transactions_this_month
            temp_dict["dollar_amount_of_transactions_this_month"] = dollar_amount_of_transactions_this_month
            temp_dict["total_number_of_transactions"] = total_number_of_transactions
            temp_dict["total_dollar_amount_of_transactions"] = total_dollar_amount_of_transactions

            subscription_tier_data_list_of_dictionaries.append(temp_dict)

            #####
            #build subscription stats/info lists & dicts for the jinja2 table - ends
            #####


            #####
            #build payment history lists & dicts for the jinja2 table - begins
            #####
            #payment-time-iso (timezone), order_id, payment_amount_in_usd, number_of_months_paid_for, tier_paid_for, expiration-time-iso (timezone)
            #id	user_id	epoch_of_payment	payment_provider	crypto_or_fiat_gateway	order_id	payment_amount_in_usd	number_of_months_paid_for	tier_paid_for	epoch_expiration	description	referral_code	account_created_epoch	current_us_state

            list_of_payment_history_data = []
            payment_history_data_list_of_dictionaries = []
            logging.error("user_payments type:") #debugging
            logging.error(type(user_payments)) #debugging
            logging.error(user_payments) #debugging
            logging.error("pending_payments_many type") #debugging
            logging.error(type(pending_payments_many)) #debugging
            logging.error(pending_payments_many) #debugging
            if len(user_payments) < 1 and len(pending_payments_many) < 1: #if both pending & paid payments are empty then return None, else build the list of dictionaries to be passed to jinja2 template
                payment_history_data_list_of_dictionaries = None
            else:
                #pending
                for pending_payment_row in pending_payments_many: #pending
                    temp_dict = {}
                    temp_dict["status"] = "Pending"
                    temp_dict["datetime_of_payment"] = "--"
                    temp_dict["order_id"] = str(pending_payment_row[2])
                    temp_dict["payment_amount_in_usd"] = str(pending_payment_row[7])
                    temp_dict["number_of_months_paid_for"] = str(pending_payment_row[6])
                    temp_dict["tier_paid_for"] = str(pending_payment_row[5])
                    temp_dict["datetime_of_expiration"] = "--"
                    payment_history_data_list_of_dictionaries.append(temp_dict)
                #pending_payments_many = response_tuple[8] #[[1, 26, '6685893e-c0be-4a89-b02e-aa8e05e4cf2d', 'AL', 1641515447, 3, 1200, 585]]
                logging.error(payment_history_data_list_of_dictionaries) #debugging

                #paid
                for payment_row_list in user_payments: #paid
                    logging.error(payment_row_list) #debugging
                    temp_list = []
                    temp_list.append(payment_row_list[2]) #epoch_of_payment 0
                    temp_list.append(payment_row_list[5]) #order_id 1
                    temp_list.append(payment_row_list[6]) #payment_amount_in_usd 2
                    temp_list.append(payment_row_list[7]) #number_of_months_paid_for 3
                    temp_list.append(payment_row_list[8]) #tier_paid_for 4
                    temp_list.append(payment_row_list[9]) #epoch_expiration 5
                    list_of_payment_history_data.append(temp_list)

                for list_item in list_of_payment_history_data:
                    temp_dict = {}
                    #list_item[0] #epoch_of_payment 0
                    utc_datetime_from_epoch = pytz.utc.localize(datetime.datetime.fromtimestamp(int(list_item[0])))
                    timezone_adjusted_now = utc_datetime_from_epoch.astimezone(pytz.timezone(current_user.timezone))
                    temp_dict["status"] = "Paid"
                    temp_dict["datetime_of_payment"] = timezone_adjusted_now.strftime('%Y-%m-%d %H:%M:%S')

                    temp_dict["order_id"] = list_item[1] #order_id 1
                    temp_dict["payment_amount_in_usd"] = list_item[2] #payment_amount_in_usd 2
                    temp_dict["number_of_months_paid_for"] = list_item[3] #number_of_months_paid_for 3
                    temp_dict["tier_paid_for"] = list_item[4] #tier_paid_for 4

                    #list_item[5] #epoch_expiration 5
                    utc_datetime_from_epoch = pytz.utc.localize(datetime.datetime.fromtimestamp(int(list_item[5])))
                    timezone_adjusted_now = utc_datetime_from_epoch.astimezone(pytz.timezone(current_user.timezone))
                    temp_dict["datetime_of_expiration"] = timezone_adjusted_now.strftime('%Y-%m-%d %H:%M:%S')
                    payment_history_data_list_of_dictionaries.append(temp_dict)
                    #####
                    #build payment history lists & dicts for the jinja2 table - ends
                    #####
            return render_template("admin/view_manage_subscription.html", form=form, message_to_user=message_to_user, payment_history_data_list_of_dictionaries=payment_history_data_list_of_dictionaries, subscription_tier_data_list_of_dictionaries=subscription_tier_data_list_of_dictionaries)
        return render_template("admin/view_manage_subscription.html", form=form, message_to_user=message_to_user)
    else:
        abort(404)


@app.route("/admin/view_dca_logs", methods=['GET', 'POST'])
@login_required
def admin_portal_view_dca_logs():
    logging.critical("/admin/view_dca_logs")

    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        
        message_to_user = None
        form = AdminLogViewUserIdForm()
        if form.validate_on_submit():
            form_entered_user_id_sanitized = bleach.clean(str(form.form_entered_user_id.data), strip=True)
            try:
                int(form_entered_user_id_sanitized)
            except:
                message_to_user = "didn't enter an int, try again"
                return render_template("admin/manage_subscription.html", form=form, message_to_user=message_to_user)
                
            if form.form_entered_number_of_log_events.data not in ["1", "5", "10", "50", "100"]:
                return render_template("utilities/dca_logs.html")
            if form.form_entered_log_status_events.data not in ["all", "success", "failed"]:
                return render_template("utilities/dca_logs.html")
            if form.form_entered_coin_type_events.data not in ["all", "btc", "eth", "ltc"]:
                return render_template("utilities/dca_logs.html")
            if form.form_entered_exchange_events.data not in CSR_toolkit.supported_exchanges_list_without_notset_with_all:
                return render_template("utilities/dca_logs.html")
            
            headers = {}
            headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
            query_string = CSR_service_mesh_map.api_dca_purchase_logs + "?" + "user_id=" + str(form_entered_user_id_sanitized) + "&limit=" + str(form.form_entered_number_of_log_events.data) + "&was_successful=" + str(form.form_entered_log_status_events.data) + "&coin_purchased=" + str(form.form_entered_coin_type_events.data) + "&exchange_used=" + str(form.form_entered_exchange_events.data)
            logging.error(query_string)
            query_response = requests.get(query_string, headers=headers)
            query_response_json = query_response.json()
            
            if isinstance(query_response_json, str):
                query_response_json = eval(query_response_json)
            if not isinstance(query_response_json, type([])):
                logging.error("error: response from api is not a list")
                return render_template("utilities/dca_logs.html", form=form)    

            if len(query_response_json) < 1:
                logging.error("no DCA events, empty list")
                return render_template("utilities/dca_logs.html", form=form, list_of_log_events=None)    
            
            logging.error(query_response.json())
            query_response_json_removed_primary_key = []
            query_response_json_list_of_dictionaries = []
            for list in query_response_json:
                del list[0]
                del list[0]
                query_response_json_removed_primary_key.append(list)
            for list in query_response_json_removed_primary_key:
                temp_dict = {}

                utc_datetime_from_epoch = pytz.utc.localize(datetime.datetime.fromtimestamp(int(list[0])))
                timezone_adjusted_now = utc_datetime_from_epoch.astimezone(pytz.timezone(current_user.timezone))
                temp_dict["datetime"] = timezone_adjusted_now.strftime('%Y-%m-%d %H:%M:%S')

                if list[1] == "True":
                    temp_status = "Success"
                elif list[1] == "False":
                    temp_status = "Failed"
                else:
                    temp_status = list[1]
                temp_dict["status"] = temp_status
                temp_dict["coin"] = list[2].upper()
                temp_dict["fiatamount"] = list[3]
                temp_dict["fiatdenomination"] = list[4]
                temp_dict["exchange"] = CSR_toolkit.map_of_exchange_names_computer_to_human[list[5]]
                human_readable_time = seconds_to_human_readable(int(list[6]), granularity=4)
                temp_dict["timeinterval"] = human_readable_time
                temp_dict["highavailabilitytype"] = list[7]
                temp_dict["exchangeorderid"] = bleach.clean(str(list[8]), strip=True)
                temp_dict["additionalinfo"] = list[9]
                query_response_json_list_of_dictionaries.append(temp_dict)
            return render_template("admin/dca_logs.html", form=form, list_of_log_events=query_response_json_list_of_dictionaries)
        return render_template("admin/dca_logs.html", form=form)


@app.route("/admin/view_dca_schedule_by_user_id/<digital_asset_endpoint>/<user_id_input>", methods=['GET', 'POST'])
@login_required
def view_dca_schedule_by_user_id(digital_asset_endpoint, user_id_input):
    logging.critical("/admin/view_dca_schedule_by_user_id/<digital_asset_endpoint>/<user_id_input> route called")
    
    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        
    if digital_asset_endpoint[:10] not in CSR_toolkit.supported_coins_list:
        logging.error("/admin/view_dca_schedule_by_user_id/<digital_asset_endpoint>/<user_id_input> called and not found, returning 404")
        abort(404)
    
    try:
        int(user_id_input)
    except:
        message_to_user = "didn't enter an int, try again"
        return render_template("admin/view_dca_schedule_by_user_id.html", message_to_user=message_to_user)
    
    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    if current_user.email_verified != "True":
        logging.error("email_verified is not True - redirecting to utilities_verify_email")
        return redirect(url_for('utilities_verify_email'))

    message_to_user = None
    query_to_send = CSR_service_mesh_map.api_dca_schedule + "?user_id=" + str(user_id_input) + "&digital_asset=" + str(digital_asset_endpoint)
    logging.error("query to send: %s" % query_to_send) #debugging
    headers = {}
    headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
    query_response = requests.get(query_to_send, headers=headers)
    logging.error(query_response.status_code) #debugging
    logging.error(query_response.json()) #debugging
    logging.error(len(query_response.json())) #debugging

    query_response_object = query_response.json()
    logging.error(query_response_object) #debugging
    if isinstance(query_response_object, str):
        logging.error("is string") #debugging
        query_response_object = eval(query_response.json())
        logging.error(query_response_object) #debugging
        logging.error(type(query_response_object)) #debugging
        logging.error(len(query_response_object)) #debugging

    if query_response_object:
        logging.error("list not empty") #debugging
        list_of_schedule_info_to_display_to_user = []
        list_of_schedule_info_to_display_to_user.append(f"Schedule purchases {query_response.json()[4]} {query_response.json()[5]}")
        human_readable_time = seconds_to_human_readable(int(query_response.json()[3]), granularity=4)
        list_of_schedule_info_to_display_to_user.append("Schedule runs every: %s (%s minutes)" % (str(human_readable_time), str(int(query_response.json()[3]) / 60)))
        
        utc_datetime_from_epoch = pytz.utc.localize(datetime.datetime.fromtimestamp(int(query_response.json()[6])))
        timezone_adjusted_now = utc_datetime_from_epoch.astimezone(pytz.timezone(current_user.timezone))
        temp_time_stamp = timezone_adjusted_now.strftime('%Y-%m-%d %H:%M:%S')
        list_of_schedule_info_to_display_to_user.append("Schedule created at: %s" % (str(temp_time_stamp)))
        
        if int(query_response.json()[7]) == 0:
            temp_time_stamp = "n/a"
        else:
            utc_datetime_from_epoch = pytz.utc.localize(datetime.datetime.fromtimestamp(int(query_response.json()[7])))
            timezone_adjusted_now = utc_datetime_from_epoch.astimezone(pytz.timezone(current_user.timezone))
            temp_time_stamp = timezone_adjusted_now.strftime('%Y-%m-%d %H:%M:%S')
        list_of_schedule_info_to_display_to_user.append("Schedule first ran: %s" % (str(temp_time_stamp)))
        
        if int(query_response.json()[8]) == 0:
            temp_time_stamp = "n/a"
        else:
            utc_datetime_from_epoch = pytz.utc.localize(datetime.datetime.fromtimestamp(int(query_response.json()[8])))
            timezone_adjusted_now = utc_datetime_from_epoch.astimezone(pytz.timezone(current_user.timezone))
            temp_time_stamp = timezone_adjusted_now.strftime('%Y-%m-%d %H:%M:%S')
        list_of_schedule_info_to_display_to_user.append("Schedule last ran: %s" % (str(temp_time_stamp)))
        
        utc_datetime_from_epoch = pytz.utc.localize(datetime.datetime.fromtimestamp(int(query_response.json()[9])))
        timezone_adjusted_now = utc_datetime_from_epoch.astimezone(pytz.timezone(current_user.timezone))
        temp_time_stamp = timezone_adjusted_now.strftime('%Y-%m-%d %H:%M:%S')
        list_of_schedule_info_to_display_to_user.append("Schedule next run: %s" % (str(temp_time_stamp)))
        list_of_schedule_info_to_display_to_user.append("High Availability Type: %s" % (str(query_response.json()[10])))
        list_of_schedule_info_to_display_to_user.append("Exchange priority #1: %s" % (CSR_toolkit.map_of_exchange_names_computer_to_human[str(query_response.json()[11])]))
        list_of_schedule_info_to_display_to_user.append("Exchange priority #2: %s" % (CSR_toolkit.map_of_exchange_names_computer_to_human[str(query_response.json()[12])]))
        list_of_schedule_info_to_display_to_user.append("Exchange priority #3: %s" % (CSR_toolkit.map_of_exchange_names_computer_to_human[str(query_response.json()[13])]))
        list_of_schedule_info_to_display_to_user.append("Exchange priority #4: %s" % (CSR_toolkit.map_of_exchange_names_computer_to_human[str(query_response.json()[14])]))
        list_of_schedule_info_to_display_to_user.append("Exchange priority #5: %s" % (CSR_toolkit.map_of_exchange_names_computer_to_human[str(query_response.json()[15])]))
        list_of_schedule_info_to_display_to_user.append("Exchange priority #6: %s" % (CSR_toolkit.map_of_exchange_names_computer_to_human[str(query_response.json()[16])]))
        
    elif not query_response_object:
        logging.error("list empty - elif") #debugging
        list_of_schedule_info_to_display_to_user = None

    else:
        logging.error("list empty - else") #debugging
        list_of_schedule_info_to_display_to_user = None

    logging.error(list_of_schedule_info_to_display_to_user) #debugging

    return render_template("admin/view_dca_schedule_by_user_id.html", digital_asset=digital_asset_endpoint, list_of_schedule_info_to_display_to_user=list_of_schedule_info_to_display_to_user, message_to_user=message_to_user, user_id_input=user_id_input)


@app.route("/admin/view_sub_status_row_by_user_id/<user_id_input>")
@login_required
def admin_portal_view_sub_status_row_by_user_id(user_id_input):
    logging.critical("/admin/view_sub_status_row_by_user_id/<user_id_input> called")
    
    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        message_to_user = None
        list_of_rows = []
        row = {}
        try:
            int(user_id_input)
        except:
            message_to_user = "didn't enter an int, try again"
        
        user_subscription_status_row = CSR_toolkit.get_user_subscription_status_row_by_user_id(user_id_input, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
        if user_subscription_status_row:
            row["user_id"] = user_subscription_status_row[0]
            row["referral_code"] = user_subscription_status_row[1]
            row["subscription_tier"] = user_subscription_status_row[2]
            row["tier_locked_by_admin"] = user_subscription_status_row[3]
            row["number_of_transactions_this_month"] = user_subscription_status_row[4]
            row["dollar_amount_of_transactions_this_month"] = user_subscription_status_row[5]
            row["total_number_of_transactions"] = user_subscription_status_row[6]
            row["total_dollar_amount_of_transactions"] = user_subscription_status_row[7]
            row["fiat_payment_gateway_customer_id"] = user_subscription_status_row[8]
            row["fiat_payment_provider"] = user_subscription_status_row[9]
        else:
            row["user_id"] = "row not found for user id"
            row["referral_code"] = "row not found for user id"
            row["subscription_tier"] = "row not found for user id"
            row["tier_locked_by_admin"] = "row not found for user id"
            row["number_of_transactions_this_month"] = "row not found for user id"
            row["dollar_amount_of_transactions_this_month"] = "row not found for user id"
            row["total_number_of_transactions"] = "row not found for user id"
            row["total_dollar_amount_of_transactions"] = "row not found for user id"
            row["fiat_payment_gateway_customer_id"] = "row not found for user id"
            row["fiat_payment_provider"] = "row not found for user id"
        list_of_rows.append(row)

        return render_template("admin/view_sub_status_row_by_user_id.html", list_of_rows=list_of_rows, message_to_user=message_to_user)
    
    else:
        abort(404)


@app.route("/admin/view_all_users_by_email_address", methods=['GET', 'POST'])
@login_required
def admin_portal_view_all_users_by_email_address():
    logging.critical("/admin/view_all_users_by_email_address called")
    
    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        list_of_rows = []
        row = {}
        
        form = AdminEnterEmailAddress()
        if form.validate_on_submit():
            email_address = bleach.clean(str(form.form_entered_email_address.data), strip=True) #strip XSS
            user_rows_response = CSR_toolkit.get_list_of_users_from_email_address(email_address, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
            logging.error(user_rows_response) #debugging
            if user_rows_response:
                for user in user_rows_response:
                    logging.error(user) #debugging
                    logging.error(user[0]) #debugging
                    row["user_id"] = user[0]
                    row["identity_provider_sub_id"] = user[1]
                    row["identity_provider"] = user[2]
                    row["first_name"] = user[3]
                    row["last_name"] = user[4]
                    row["email_address"] = user[5]
                    row["email_verified"] = user[6]
                    row["timezone"] = user[7]
                    row["geo_location"] = user[8]
                    row["last_login_epoch"] = user[9]
                    row["time_created_epoch"] = user[10]
                    row["brand_ambassador"] = user[11]
                    row["site_metrics_viewer"] = user[12]
                    row["site_admin_full"] = user[13]
                    list_of_rows.append(row)
                    row = {}
            else:
                row["user_id"] = "no users found"
                row["identity_provider_sub_id"] = "no users found"
                row["identity_provider"] = "no users found"
                row["first_name"] = "no users found"
                row["last_name"] = "no users found"
                row["email_address"] = "no users found"
                row["email_verified"] = "no users found"
                row["timezone"] = "no users found"
                row["geo_location"] = "no users found"
                row["last_login_epoch"] = "no users found"
                row["time_created_epoch"] = "no users found"
                row["brand_ambassador"] = "no users found"
                row["site_metrics_viewer"] = "no users found"
                row["site_admin_full"] = "no users found"
                list_of_rows.append(row)
                #list_of_rows = None
            return render_template("admin/view_all_users_by_email_address.html", form=form, list_of_rows=list_of_rows)
        return render_template("admin/view_all_users_by_email_address.html", form=form, list_of_rows=None)
    else:
        abort(404)


@app.route("/admin/debug_api_keys_by_user_id", methods=['GET', 'POST'])
@login_required
def admin_portal_debug_api_keys_by_user_id():
    logging.critical("/admin/debug_api_keys_by_user_id called")
    
    if not hasattr(current_user, 'site_admin_full'):
        logging.error("site_admin_full not found")
        abort(404)
    
    if current_user.site_admin_full != "True":
        logging.error("not site_admin_full")
        abort(404)
    
    elif current_user.site_admin_full == "True":
        logging.error("site_admin_full true")
        list_of_rows = []
        row = {}
        
        form = AdminEnterUserID()
        if form.validate_on_submit():
            form_entered_user_id_sanitized = bleach.clean(str(form.form_entered_user_id.data), strip=True)
            
            try:
                int(form_entered_user_id_sanitized)
            except:
                message_to_user = "didn't enter an int, try again"
            
            metadata_results_per_exchange = {}
            #retrieve api key metadata
            for exchange in CSR_toolkit.supported_exchanges_list_without_notset:
                meta_data_to_return_to_user = CSR_toolkit.build_api_key_metadata_list(form_entered_user_id_sanitized, exchange, current_user.timezone, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                if meta_data_to_return_to_user:
                    metadata_results_per_exchange[exchange] = "Set"
                else:
                    metadata_results_per_exchange[exchange] = "Not set"

            logging.error(metadata_results_per_exchange) #debugging

            return render_template("admin/debug_api_keys_by_user_id.html", form=form, metadata_results_per_exchange=metadata_results_per_exchange)
        return render_template("admin/debug_api_keys_by_user_id.html", form=form, metadata_results_per_exchange=None)
    else:
        abort(404)


######################################################################################################
########### ADMIN SECTION ############################################################################
######################################################################################################


@app.route("/brand_ambassador")
@login_required
def brand_ambassador_portal_root():
    logging.critical("/brand_ambassador called")

    if current_user.timezone == "None" or current_user.geo_location == "None":
        logging.error("missing timezone or geo_location - redirecting to utilities_firsttimeloginlandingpage")
        return redirect(url_for('utilities_firsttimeloginlandingpage'))

    if current_user.email_verified != "True":
        logging.error("email_verified is not True - redirecting to utilities_verify_email")
        return redirect(url_for('utilities_verify_email'))

    ###############################################################
    ### persona verification enforcement - begins ####
    if not hasattr(current_user, 'persona_verification_status'):
        logging.error("persona_verification_status not found returning 404")
        abort(404)
    
    if int(current_user.persona_verification_status) < 2:
        logging.error("current_user.persona_verification_status is less than 2")
        return redirect(url_for('persona_verification'))
    
    if int(current_user.persona_verification_status) == 2:
        logging.error("current_user.persona_verification_status is 2")
        return redirect(url_for('persona_verification_status'))

    if int(current_user.persona_verification_status) == 9:
        logging.error("current_user.persona_verification_status is 9")
        return redirect(url_for('persona_verification_status'))
    
    if int(current_user.persona_verification_status) == 3: #no action required because the user is validated
        logging.error("current_user.persona_verification_status is 3")
    ### persona verification enforcement - ends ####
    ###############################################################
    
    if not hasattr(current_user, 'brand_ambassador'):
        logging.error("brand_ambassador not found")
        abort(404)
    
    if current_user.brand_ambassador == "True":
        logging.error("brand_ambassador == True")
        
        brand_ambassador_metrics_tuple = CSR_toolkit.get_brand_ambassador_metrics(current_user.user_id, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
        
        #brand_ambassador_metrics_tuple[]
        #brand_ambassador_referral_code 0
        #brand_ambassador_percentage 1
        #total_users_with_referral_code 2
        #gross_revenue_from_referral_code 3
        #gross_revenue_from_referral_code_previous_quarter 4
        #gross_revenue_from_referral_code_quarter_to_date 5
        #count_of_unique_paying_users_with_specific_referral_code 6
        #gross_revenue_from_referral_code_brand_ambassador_share 7
        #gross_revenue_from_referral_code_previous_quarter_ambassador_share 8
        #gross_revenue_from_referral_code_quarter_to_date_ambassador_share 9

        return render_template("brand_ambassador/ambassador.html", email_address=current_user.email, referral_code=brand_ambassador_metrics_tuple[0], 
        revenue_share_percentage=brand_ambassador_metrics_tuple[1], total_users_with_referral_code=brand_ambassador_metrics_tuple[2], 
        unique_paying_users=brand_ambassador_metrics_tuple[6], gross_revenue_generated=brand_ambassador_metrics_tuple[3],
        gross_revenue_previous_quarter=brand_ambassador_metrics_tuple[4], gross_revenue_current_quarter=brand_ambassador_metrics_tuple[5],
        gross_revenue_brand_ambassador_share=brand_ambassador_metrics_tuple[7], gross_revenue_previous_quarter_ambassador_share=brand_ambassador_metrics_tuple[8],
        gross_revenue_quarter_to_date_ambassador_share=brand_ambassador_metrics_tuple[9]
        )
    
    
    elif current_user.brand_ambassador != "True":
        logging.error("brand_ambassador returning redirect(https://blog.cryptostacker.io/contact)")
        return redirect("https://blog.cryptostacker.io/contact")
    else:
        logging.error("brand_ambassador returning 404")
        abort(404)



####################################################################
####################### METRICS - BEGINS ###########################
####################################################################



@app.route("/metrics")
@login_required
def metrics_portal_root():
    logging.critical("/metrics called")

    if not hasattr(current_user, 'site_metrics_viewer'):
        logging.error("site_metrics_viewer not found")
        abort(404)
    
    if current_user.site_metrics_viewer == "True":
        return render_template("metrics/main.html")

    elif current_user.site_metrics_viewer != "True":
        abort(404) 
    else:
        abort(404)


@app.route("/metrics/user_metrics_table", methods=['GET', 'POST'])
@login_required
def metrics_user_metrics_table():
    logging.critical("/metrics/user_metrics_table called")

    if not hasattr(current_user, 'site_metrics_viewer'):
        logging.error("site_metrics_viewer not found")
        abort(404)
    
    if current_user.site_metrics_viewer == "True":
        logging.critical("site_metrics_viewer is True")
        message_to_user = None
        form = MetricsUserMetricsTable()
        if form.validate_on_submit:
            form_entered_number_of_rows_sanitized = bleach.clean(str(form.form_entered_number_of_rows.data), strip=True)
            try:
                int(form_entered_number_of_rows_sanitized)
            except:
                message_to_user = "Must enter an INT between 1-200"
                return render_template("metrics/user_metrics_table.html", form=form, message_to_user=message_to_user)

            if form_entered_number_of_rows_sanitized not in [str(x) for x in range(1,201)]:
                message_to_user = "Must enter an INT between 1-200"
                return render_template("metrics/user_metrics_table.html", form=form, message_to_user=message_to_user)
            
            #query API daily-metrics-API for rows
            headers = {}
            headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
            query_string = CSR_service_mesh_map.api_daily_user_metrics + "?scope=get_multiple_metrics&limit=" + str(form_entered_number_of_rows_sanitized)
            logging.error(query_string) #debugging
            query_response = requests.get(query_string, headers=headers)
            if query_response.status_code == 429:
                abort(429)
            query_response_json = query_response.json()
            logging.error(query_response_json) #debugging
            query_response_json_list_of_dictionaries = []
            #build a dictionary which can be used for both html table & download CSV
            for row_list in query_response_json:
                temp_dict = {}
                temp_dict["row_id"] = row_list[0]
                temp_dict["epoch_time"] = row_list[1]
                temp_dict["iso_date"] = row_list[2]
                temp_dict["total_users"] = row_list[3]
                temp_dict["user_subscription_status_users"] = row_list[4]
                temp_dict["verified_users"] = row_list[5]
                temp_dict["paying_users"] = row_list[6]
                temp_dict["payments_1_month"] = row_list[7]
                temp_dict["payments_3_month"] = row_list[8]
                temp_dict["payments_6_month"] = row_list[9]
                temp_dict["payments_12_month"] = row_list[10]
                temp_dict["payments_1200_month"] = row_list[11]
                temp_dict["payments_tier_2"] = row_list[12]
                temp_dict["payments_tier_3"] = row_list[13]
                temp_dict["users_logged_in_past_24_hours"] = row_list[14]
                temp_dict["users_logged_in_past_48_hours"] = row_list[15]
                temp_dict["users_logged_in_past_168_hours"] = row_list[16]
                temp_dict["users_logged_in_past_336_hours"] = row_list[17]
                temp_dict["users_logged_in_past_720_hours"] = row_list[18]
                temp_dict["active_schedules_btc"] = row_list[19]
                temp_dict["active_schedules_eth"] = row_list[20]
                temp_dict["active_schedules_ltc"] = row_list[21]
                temp_dict["active_schedules_ha_type_failover"] = row_list[22]
                temp_dict["active_schedules_ha_type_round_robin"] = row_list[23]
                temp_dict["active_schedules_ha_type_simultaneous"] = row_list[24]
                temp_dict["active_schedules_ha_type_single_exchange"] = row_list[25]
                temp_dict["active_schedules_dca_logs_past_30_days"] = row_list[26]
                query_response_json_list_of_dictionaries.append(temp_dict)
            return render_template("metrics/user_metrics_table.html", form=form, message_to_user=message_to_user, list_of_metrics=query_response_json_list_of_dictionaries)
        return render_template("metrics/user_metrics_table.html", form=form, message_to_user=message_to_user, list_of_metrics=None)


    elif current_user.site_metrics_viewer != "True":
        abort(404) 
    else:
        abort(404)


@app.route("/metrics/user_metrics_csv", methods=['GET', 'POST'])
@login_required
def metrics_user_metrics_csv():
    logging.critical("/metrics/user_metrics_csv called")

    if not hasattr(current_user, 'site_metrics_viewer'):
        logging.error("site_metrics_viewer not found")
        abort(404)
    
    if current_user.site_metrics_viewer == "True":
        logging.critical("site_metrics_viewer is True")
        message_to_user = None
        form = MetricsUserMetricsTable()
        if form.validate_on_submit:
            form_entered_number_of_rows_sanitized = bleach.clean(str(form.form_entered_number_of_rows.data), strip=True)
            try:
                int(form_entered_number_of_rows_sanitized)
            except:
                message_to_user = "Must enter an INT between 1-200"
                return render_template("metrics/user_metrics_csv.html", form=form, message_to_user=message_to_user)

            if form_entered_number_of_rows_sanitized not in [str(x) for x in range(1,201)]:
                message_to_user = "Must enter an INT between 1-200"
                return render_template("metrics/user_metrics_csv.html", form=form, message_to_user=message_to_user)
            
            #query API daily-metrics-API for rows
            headers = {}
            headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
            query_string = CSR_service_mesh_map.api_daily_user_metrics + "?scope=get_multiple_metrics&limit=" + str(form_entered_number_of_rows_sanitized)
            logging.error(query_string) #debugging
            query_response = requests.get(query_string, headers=headers)
            if query_response.status_code == 429:
                abort(429)
            query_response_json = query_response.json()
            logging.error(query_response_json) #debugging
            query_response_json_list_of_dictionaries = []
            #build a dictionary which can be used for both html table & download CSV
            for row_list in query_response_json:
                temp_dict = {}
                temp_dict["row_id"] = row_list[0]
                temp_dict["epoch_time"] = row_list[1]
                temp_dict["iso_date"] = row_list[2]
                temp_dict["total_users"] = row_list[3]
                temp_dict["user_subscription_status_users"] = row_list[4]
                temp_dict["verified_users"] = row_list[5]
                temp_dict["paying_users"] = row_list[6]
                temp_dict["payments_1_month"] = row_list[7]
                temp_dict["payments_3_month"] = row_list[8]
                temp_dict["payments_6_month"] = row_list[9]
                temp_dict["payments_12_month"] = row_list[10]
                temp_dict["payments_1200_month"] = row_list[11]
                temp_dict["payments_tier_2"] = row_list[12]
                temp_dict["payments_tier_3"] = row_list[13]
                temp_dict["users_logged_in_past_24_hours"] = row_list[14]
                temp_dict["users_logged_in_past_48_hours"] = row_list[15]
                temp_dict["users_logged_in_past_168_hours"] = row_list[16]
                temp_dict["users_logged_in_past_336_hours"] = row_list[17]
                temp_dict["users_logged_in_past_720_hours"] = row_list[18]
                temp_dict["active_schedules_btc"] = row_list[19]
                temp_dict["active_schedules_eth"] = row_list[20]
                temp_dict["active_schedules_ltc"] = row_list[21]
                temp_dict["active_schedules_ha_type_failover"] = row_list[22]
                temp_dict["active_schedules_ha_type_round_robin"] = row_list[23]
                temp_dict["active_schedules_ha_type_simultaneous"] = row_list[24]
                temp_dict["active_schedules_ha_type_single_exchange"] = row_list[25]
                temp_dict["active_schedules_dca_logs_past_30_days"] = row_list[26]
                query_response_json_list_of_dictionaries.append(temp_dict)
            
            with open('/tmp/user_metrics.csv', mode='w') as csv_file:
                fieldnames = ['row_id', 'epoch_time', 'iso_date', 'total_users', 'user_subscription_status_users', 'verified_users',
                'paying_users', 'payments_1_month', 'payments_3_month', 'payments_6_month', 'payments_12_month', 'payments_1200_month', 
                'payments_tier_2', 'payments_tier_3', 'users_logged_in_past_24_hours', 'users_logged_in_past_48_hours', 
                'users_logged_in_past_168_hours', 'users_logged_in_past_336_hours', 'users_logged_in_past_720_hours',
                'active_schedules_btc', 'active_schedules_eth', 'active_schedules_ltc', 'active_schedules_ha_type_failover', 
                'active_schedules_ha_type_round_robin', 'active_schedules_ha_type_simultaneous', 'active_schedules_ha_type_single_exchange', 
                'active_schedules_dca_logs_past_30_days']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for dict_item in query_response_json_list_of_dictionaries:
                    writer.writerow(dict_item)
            
            return send_file('/tmp/user_metrics.csv',
                     mimetype='text/csv',
                     attachment_filename='user_metrics.csv',
                     as_attachment=True)
        return render_template("metrics/user_metrics_csv.html", form=form, message_to_user=message_to_user)

    elif current_user.site_metrics_viewer != "True":
        abort(404) 
    else:
        abort(404)

@app.route("/metrics/user_payments_csv/<user_payments_csv_scope>", methods=['GET', 'POST'])
@login_required
def metrics_user_payments_csv(user_payments_csv_scope):
    logging.critical("/metrics/user_payments_csv called")
    
    allow_scopes = ["previous_month_payments", "month_to_date_payments", "previous_quarter_payments", 
                    "quarter_to_date_payments", "previous_year_payments", "year_to_date_payments"]
    
    user_payments_csv_scope_sanitized = trim_sanitize_strip(50, user_payments_csv_scope)

    if user_payments_csv_scope_sanitized not in allow_scopes:
        abort(404)
    
    if not hasattr(current_user, 'site_metrics_viewer'):
        logging.error("site_metrics_viewer not found")
        abort(404)
    
    if current_user.site_metrics_viewer == "True":
        logging.critical("site_metrics_viewer is True")
        
        headers = {}
        headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
        query_url = CSR_service_mesh_map.api_user_payments + "?scope=" + str(user_payments_csv_scope_sanitized)
        user_payments_response = requests.get(query_url, headers=headers)
        if user_payments_response.status_code == 429:
            abort(429)
        
        #user_payments_response_json = user_payments_response.json()
        #logging.error(user_payments_response.json()) #debugging
        query_response_json_list_of_dictionaries = []
        if user_payments_response.json(): #if response not empty
            #build a dictionary which can be used for both html table & download CSV
            for row_list in user_payments_response.json():
                temp_dict = {}
                temp_dict["id"] = row_list[0]
                temp_dict["user_id"] = row_list[1]
                temp_dict["epoch_of_payment"] = row_list[2]
                temp_dict["payment_provider"] = row_list[3]
                temp_dict["crypto_or_fiat_gateway"] = row_list[4]
                temp_dict["order_id"] = row_list[5]
                temp_dict["payment_amount_in_usd"] = row_list[6]
                temp_dict["number_of_months_paid_for"] = row_list[7]
                temp_dict["tier_paid_for"] = row_list[8]
                temp_dict["epoch_expiration"] = row_list[9]
                temp_dict["description"] = row_list[10]
                temp_dict["referral_code"] = row_list[11]
                temp_dict["account_created_epoch"] = row_list[12]
                temp_dict["current_us_state"] = row_list[13]
                query_response_json_list_of_dictionaries.append(temp_dict)
        
        elif not user_payments_response.json(): #if response is empty
                temp_dict = {}
                temp_dict["id"] = 0
                temp_dict["user_id"] = 0
                temp_dict["epoch_of_payment"] = 0
                temp_dict["payment_provider"] = 0
                temp_dict["crypto_or_fiat_gateway"] = 0
                temp_dict["order_id"] = 0
                temp_dict["payment_amount_in_usd"] = 0
                temp_dict["number_of_months_paid_for"] = 0
                temp_dict["tier_paid_for"] = 0
                temp_dict["epoch_expiration"] = 0
                temp_dict["description"] = 0
                temp_dict["referral_code"] = 0
                temp_dict["account_created_epoch"] = 0
                temp_dict["current_us_state"] = 0
                query_response_json_list_of_dictionaries.append(temp_dict)
        
        with open('/tmp/user_payments.csv', mode='w') as csv_file:
            fieldnames = ['id', 'user_id', 'epoch_of_payment', 'payment_provider', 'crypto_or_fiat_gateway', 'order_id',
            'payment_amount_in_usd', 'number_of_months_paid_for', 'tier_paid_for', 'epoch_expiration', 'description', 'referral_code', 
            'account_created_epoch', 'current_us_state']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for dict_item in query_response_json_list_of_dictionaries:
                writer.writerow(dict_item)
        
        return send_file('/tmp/user_payments.csv',
                    mimetype='text/csv',
                    attachment_filename='user_payments.csv',
                    as_attachment=True)

    elif current_user.site_metrics_viewer != "True":
        abort(404) 
    else:
        abort(404)



@app.route("/metrics/revenue_metrics_table", methods=['GET', 'POST'])
@login_required
def metrics_revenue_metrics_table():
    logging.critical("/metrics/revenue_metrics_table called")

    if not hasattr(current_user, 'site_metrics_viewer'):
        logging.error("site_metrics_viewer not found")
        abort(404)
    
    if current_user.site_metrics_viewer == "True":
        logging.critical("site_metrics_viewer is True")
        message_to_user = None
        form = MetricsUserMetricsTable()
        if form.validate_on_submit:
            form_entered_number_of_rows_sanitized = bleach.clean(str(form.form_entered_number_of_rows.data), strip=True)
            try:
                int(form_entered_number_of_rows_sanitized)
            except:
                message_to_user = "Must enter an INT between 1-200"
                return render_template("metrics/revenue_metrics_table.html", form=form, message_to_user=message_to_user)

            if form_entered_number_of_rows_sanitized not in [str(x) for x in range(1,201)]:
                message_to_user = "Must enter an INT between 1-200"
                return render_template("metrics/revenue_metrics_table.html", form=form, message_to_user=message_to_user)
            
            #query API daily-metrics-API for rows
            headers = {}
            headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
            query_string = CSR_service_mesh_map.api_daily_revenue_metrics + "?scope=get_multiple_metrics&limit=" + str(form_entered_number_of_rows_sanitized)
            logging.error(query_string) #debugging
            query_response = requests.get(query_string, headers=headers)
            if query_response.status_code == 429:
                abort(429)
            query_response_json = query_response.json()
            logging.error(query_response_json) #debugging
            query_response_json_list_of_dictionaries = []
            #build a dictionary which can be used for both html table & download CSV
            for row_list in query_response_json:
                temp_dict = {}
                temp_dict["row_id"] = row_list[0]
                temp_dict["epoch_time"] = row_list[1]
                temp_dict["iso_date"] = row_list[2]
                temp_dict["gross_revenue_past_24_hours"] = row_list[3]
                temp_dict["gross_revenue_past_7_days"] = row_list[4]
                temp_dict["gross_revenue_past_rolling_30_days"] = row_list[5]
                temp_dict["gross_revenue_past_previous_month"] = row_list[6]
                temp_dict["gross_revenue_past_month_to_date"] = row_list[7]
                temp_dict["gross_revenue_past_previous_quarter"] = row_list[8]
                temp_dict["gross_revenue_past_quarter_to_date"] = row_list[9]
                temp_dict["gross_revenue_past_previous_year"] = row_list[10]
                temp_dict["gross_revenue_past_year_to_date"] = row_list[11]
                temp_dict["gross_revenue_past_rolling_1_year"] = row_list[12]
                temp_dict["gross_revenue_past_all_time"] = row_list[13]
                query_response_json_list_of_dictionaries.append(temp_dict)
            return render_template("metrics/revenue_metrics_table.html", form=form, message_to_user=message_to_user, list_of_metrics=query_response_json_list_of_dictionaries)
        return render_template("metrics/revenue_metrics_table.html", form=form, message_to_user=message_to_user, list_of_metrics=None)


    elif current_user.site_metrics_viewer != "True":
        abort(404) 
    else:
        abort(404)


@app.route("/metrics/revenue_metrics_csv", methods=['GET', 'POST'])
@login_required
def metrics_revenue_metrics_csv():
    logging.critical("/metrics/revenue_metrics_csv called")

    if not hasattr(current_user, 'site_metrics_viewer'):
        logging.error("site_metrics_viewer not found")
        abort(404)
    
    if current_user.site_metrics_viewer == "True":
        logging.critical("site_metrics_viewer is True")
        message_to_user = None
        form = MetricsUserMetricsTable()
        if form.validate_on_submit:
            form_entered_number_of_rows_sanitized = bleach.clean(str(form.form_entered_number_of_rows.data), strip=True)
            try:
                int(form_entered_number_of_rows_sanitized)
            except:
                message_to_user = "Must enter an INT between 1-200"
                return render_template("metrics/revenue_metrics_csv.html", form=form, message_to_user=message_to_user)

            if form_entered_number_of_rows_sanitized not in [str(x) for x in range(1,201)]:
                message_to_user = "Must enter an INT between 1-200"
                return render_template("metrics/revenue_metrics_csv.html", form=form, message_to_user=message_to_user)
            
            #query API daily-metrics-API for rows
            headers = {}
            headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
            query_string = CSR_service_mesh_map.api_daily_revenue_metrics + "?scope=get_multiple_metrics&limit=" + str(form_entered_number_of_rows_sanitized)
            logging.error(query_string) #debugging
            query_response = requests.get(query_string, headers=headers)
            query_response_json = query_response.json()
            logging.error(query_response_json) #debugging
            query_response_json_list_of_dictionaries = []
            #build a dictionary which can be used for both html table & download CSV
            for row_list in query_response_json:
                temp_dict = {}
                temp_dict["row_id"] = row_list[0]
                temp_dict["epoch_time"] = row_list[1]
                temp_dict["iso_date"] = row_list[2]
                temp_dict["gross_revenue_past_24_hours"] = row_list[3]
                temp_dict["gross_revenue_past_7_days"] = row_list[4]
                temp_dict["gross_revenue_past_rolling_30_days"] = row_list[5]
                temp_dict["gross_revenue_past_previous_month"] = row_list[6]
                temp_dict["gross_revenue_past_month_to_date"] = row_list[7]
                temp_dict["gross_revenue_past_previous_quarter"] = row_list[8]
                temp_dict["gross_revenue_past_quarter_to_date"] = row_list[9]
                temp_dict["gross_revenue_past_previous_year"] = row_list[10]
                temp_dict["gross_revenue_past_year_to_date"] = row_list[11]
                temp_dict["gross_revenue_past_rolling_1_year"] = row_list[12]
                temp_dict["gross_revenue_past_all_time"] = row_list[13]
                query_response_json_list_of_dictionaries.append(temp_dict)
            
            with open('/tmp/revenue_metrics.csv', mode='w') as csv_file:
                fieldnames = ['row_id', 'epoch_time', 'iso_date', 'gross_revenue_past_24_hours', 'gross_revenue_past_7_days', 'gross_revenue_past_rolling_30_days',
                'gross_revenue_past_previous_month', 'gross_revenue_past_month_to_date', 'gross_revenue_past_previous_quarter', 'gross_revenue_past_quarter_to_date',
                'gross_revenue_past_previous_year', 'gross_revenue_past_year_to_date', 'gross_revenue_past_rolling_1_year', 'gross_revenue_past_all_time'
                ]
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for dict_item in query_response_json_list_of_dictionaries:
                    writer.writerow(dict_item)
            
            return send_file('/tmp/revenue_metrics.csv',
                     mimetype='text/csv',
                     attachment_filename='revenue_metrics.csv',
                     as_attachment=True)
        return render_template("metrics/revenue_metrics_csv.html", form=form, message_to_user=message_to_user)

    elif current_user.site_metrics_viewer != "True":
        abort(404) 
    else:
        abort(404)


####################################################################
######################### METRICS - ENDS ###########################
####################################################################


####################################################################
################## LOAD TESTING & MONITORING #######################
####################################################################

#/dca_scheduler/view_delete/btc
#/9e9c55bb-5455-44f0-ba51-523215638830/462a28d8-65b0-4612-a315-a41568c701f6/btc
@app.route("/9e9c55bb-5455-44f0-ba51-523215638830/462a28d8-65b0-4612-a315-a41568c701f6/<digital_asset_endpoint>", methods=['GET', 'POST'])
def dca_scheduler_view_delete2(digital_asset_endpoint):
    logging.critical("/dca_scheduler/view_delete/<digital_asset_endpoint> route called")
    if digital_asset_endpoint[:10] not in CSR_toolkit.supported_coins_list:
        logging.error("/dca_scheduler/view_delete/<digital_asset_endpoint> called and not found, returning 404")
        abort(404)
    
    query_to_send = CSR_service_mesh_map.api_dca_schedule + "?user_id=" + str(6) + "&digital_asset=" + str(digital_asset_endpoint)
    logging.error("query to send: %s" % query_to_send) #debugging
    headers = {}
    headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
    query_response = requests.get(query_to_send, headers=headers)
    if query_response.status_code == 429:
        abort(429)
    logging.error(query_response.status_code) #debugging
    logging.error(query_response.json()) #debugging
    logging.error(len(query_response.json())) #debugging

    query_response_object = query_response.json()
    logging.error(query_response_object) #debugging
    if isinstance(query_response_object, str):
        logging.error("is string") #debugging
        query_response_object = eval(query_response.json())
        logging.error(query_response_object) #debugging
        logging.error(type(query_response_object)) #debugging
        logging.error(len(query_response_object)) #debugging

    if query_response_object:
        logging.error("list not empty") #debugging
        list_of_schedule_info_to_display_to_user = []
        list_of_schedule_info_to_display_to_user.append(f"Schedule purchases {query_response.json()[4]} {query_response.json()[5]}")
        human_readable_time = seconds_to_human_readable(int(query_response.json()[3]), granularity=4)
        list_of_schedule_info_to_display_to_user.append("Schedule runs every: %s (%s minutes)" % (str(human_readable_time), str(int(query_response.json()[3]) / 60)))
        temp_time_stamp = datetime.datetime.fromtimestamp(int(query_response.json()[6])).strftime('%Y-%m-%d %H:%M:%S')
        list_of_schedule_info_to_display_to_user.append("Schedule created at: %s" % (str(temp_time_stamp)))
        temp_time_stamp = datetime.datetime.fromtimestamp(int(query_response.json()[7])).strftime('%Y-%m-%d %H:%M:%S')
        list_of_schedule_info_to_display_to_user.append("Schedule first ran: %s" % (str(temp_time_stamp)))
        temp_time_stamp = datetime.datetime.fromtimestamp(int(query_response.json()[8])).strftime('%Y-%m-%d %H:%M:%S')
        list_of_schedule_info_to_display_to_user.append("Schedule last ran: %s" % (str(temp_time_stamp)))
        temp_time_stamp = datetime.datetime.fromtimestamp(int(query_response.json()[9])).strftime('%Y-%m-%d %H:%M:%S')
        list_of_schedule_info_to_display_to_user.append("Schedule next run: %s" % (str(temp_time_stamp)))
        
        list_of_schedule_info_to_display_to_user.append("High Availability Type: %s" % (str(query_response.json()[10])))
        list_of_schedule_info_to_display_to_user.append("Exchange priority #1: %s" % (CSR_toolkit.map_of_exchange_names_computer_to_human[str(query_response.json()[11])]))
        list_of_schedule_info_to_display_to_user.append("Exchange priority #2: %s" % (CSR_toolkit.map_of_exchange_names_computer_to_human[str(query_response.json()[12])]))
        list_of_schedule_info_to_display_to_user.append("Exchange priority #3: %s" % (CSR_toolkit.map_of_exchange_names_computer_to_human[str(query_response.json()[13])]))
        list_of_schedule_info_to_display_to_user.append("Exchange priority #4: %s" % (CSR_toolkit.map_of_exchange_names_computer_to_human[str(query_response.json()[14])]))
        list_of_schedule_info_to_display_to_user.append("Exchange priority #5: %s" % (CSR_toolkit.map_of_exchange_names_computer_to_human[str(query_response.json()[15])]))
        list_of_schedule_info_to_display_to_user.append("Exchange priority #6: %s" % (CSR_toolkit.map_of_exchange_names_computer_to_human[str(query_response.json()[16])]))
        
    elif not query_response_object:
        logging.error("list empty - elif") #debugging
        list_of_schedule_info_to_display_to_user = None

    else:
        logging.error("list empty - else") #debugging
        list_of_schedule_info_to_display_to_user = None

    logging.error(list_of_schedule_info_to_display_to_user) #debugging

    return render_template("error_handlers/404.html"), 200


#/subscribe/manage_subscription
#/manage_subscription/beb90300-84db-432e-ba6c-a077de778325/af1d6eae-d785-4d96-b74a-f8cce6d63b0d
@app.route("/manage_subscription/beb90300-84db-432e-ba6c-a077de778325/af1d6eae-d785-4d96-b74a-f8cce6d63b0d")
def manage_subscription_test12345():
    logging.critical("/subscribe/manage_subscription called")

    #threading will make this fucntion faster
    response_tuple = CSR_toolkit.get_active_subscription_tier_transaction_stats_exceeded_bool("6", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
    logging.error(response_tuple) #debugging
    exceeded_tier_limit = response_tuple[0]
    active_tier = response_tuple[1]
    number_of_transactions_this_month = response_tuple[2]
    dollar_amount_of_transactions_this_month = response_tuple[3]
    total_number_of_transactions = response_tuple[4]
    total_dollar_amount_of_transactions = response_tuple[5]
    user_payments = response_tuple[6]
    user_subscription_status = response_tuple[7]
    pending_payments_many = response_tuple[8] #[[265, 1, '2d42a0dc-235e-4405-8e22-eaca8aa7072f', 'WV', 1640716663]]
    logging.error(pending_payments_many) #debugging
    
    #####
    #build subscription stats/info lists & dicts for the jinja2 table - begins
    #####
    list_of_subscription_tier_data = []
    subscription_tier_data_list_of_dictionaries = []
    exceeded_tier_limit_string = "No"
    if exceeded_tier_limit:
        exceeded_tier_limit_string = "Yes"
    
    temp_dict = {}
    temp_dict["active_tier"] = active_tier
    temp_dict["exceeded_tier_limit"] = exceeded_tier_limit_string
    temp_dict["number_of_transactions_this_month"] = number_of_transactions_this_month
    temp_dict["dollar_amount_of_transactions_this_month"] = dollar_amount_of_transactions_this_month
    temp_dict["total_number_of_transactions"] = total_number_of_transactions
    temp_dict["total_dollar_amount_of_transactions"] = total_dollar_amount_of_transactions

    subscription_tier_data_list_of_dictionaries.append(temp_dict)
    
    #####
    #build subscription stats/info lists & dicts for the jinja2 table - ends
    #####
    
    #####
    #build payment history lists & dicts for the jinja2 table - begins
    #####
    #payment-time-iso (timezone), order_id, payment_amount_in_usd, number_of_months_paid_for, tier_paid_for, expiration-time-iso (timezone)
    #id	user_id	epoch_of_payment	payment_provider	crypto_or_fiat_gateway	order_id	payment_amount_in_usd	number_of_months_paid_for	tier_paid_for	epoch_expiration	description	referral_code	account_created_epoch	current_us_state
    
    list_of_payment_history_data = []
    payment_history_data_list_of_dictionaries = []
    logging.error("user_payments type:") #debugging
    logging.error(type(user_payments)) #debugging
    logging.error(user_payments) #debugging
    logging.error("pending_payments_many type") #debugging
    logging.error(type(pending_payments_many)) #debugging
    logging.error(pending_payments_many) #debugging
    if len(user_payments) < 1 and len(pending_payments_many) < 1: #if both pending & paid payments are empty then return None, else build the list of dictionaries to be passed to jinja2 template
        payment_history_data_list_of_dictionaries = None
    else:
        #pending
        for pending_payment_row in pending_payments_many: #pending
            temp_dict = {}
            temp_dict["status"] = "Pending"
            temp_dict["datetime_of_payment"] = "--" 
            temp_dict["order_id"] = str(pending_payment_row[2])
            temp_dict["payment_amount_in_usd"] = str(pending_payment_row[7])
            temp_dict["number_of_months_paid_for"] = str(pending_payment_row[6])
            temp_dict["tier_paid_for"] = str(pending_payment_row[5])
            temp_dict["datetime_of_expiration"] = "--"
            payment_history_data_list_of_dictionaries.append(temp_dict)

        #paid
        for payment_row_list in user_payments: #paid
            logging.error(payment_row_list) #debugging
            temp_list = []
            temp_list.append(payment_row_list[2]) #epoch_of_payment 0
            temp_list.append(payment_row_list[5]) #order_id 1
            temp_list.append(payment_row_list[6]) #payment_amount_in_usd 2
            temp_list.append(payment_row_list[7]) #number_of_months_paid_for 3
            temp_list.append(payment_row_list[8]) #tier_paid_for 4
            temp_list.append(payment_row_list[9]) #epoch_expiration 5
            list_of_payment_history_data.append(temp_list)
    
        for list_item in list_of_payment_history_data:
            temp_dict = {}
            #list_item[0] #epoch_of_payment 0
            utc_datetime_from_epoch = pytz.utc.localize(datetime.datetime.fromtimestamp(int(list_item[0])))
            timezone_adjusted_now = utc_datetime_from_epoch.astimezone(pytz.timezone("America/Los_Angeles"))
            temp_dict["status"] = "Paid"
            temp_dict["datetime_of_payment"] = timezone_adjusted_now.strftime('%Y-%m-%d %H:%M:%S')

            temp_dict["order_id"] = list_item[1] #order_id 1
            temp_dict["payment_amount_in_usd"] = list_item[2] #payment_amount_in_usd 2
            temp_dict["number_of_months_paid_for"] = list_item[3] #number_of_months_paid_for 3
            temp_dict["tier_paid_for"] = list_item[4] #tier_paid_for 4
            
            #list_item[5] #epoch_expiration 5
            utc_datetime_from_epoch = pytz.utc.localize(datetime.datetime.fromtimestamp(int(list_item[5])))
            timezone_adjusted_now = utc_datetime_from_epoch.astimezone(pytz.timezone("America/Los_Angeles"))
            temp_dict["datetime_of_expiration"] = timezone_adjusted_now.strftime('%Y-%m-%d %H:%M:%S')
            payment_history_data_list_of_dictionaries.append(temp_dict)
    #####
    #build payment history lists & dicts for the jinja2 table - ends
    #####

    return render_template("error_handlers/404.html"), 200


#/set_api_keys/coinbase/<coinbase_exchange_endpoint>
#/set_api_keys_coinbase/ada77c58-1df4-40b9-be59-bc157703f130/3cc06736-671e-4936-9e11-fe134516769b/coinbase_pro
@app.route("/set_api_keys_coinbase/ada77c58-1df4-40b9-be59-bc157703f130/3cc06736-671e-4936-9e11-fe134516769b/<coinbase_exchange_endpoint>", methods=['GET'])
def set_api_keys_coinbase_testing1234(coinbase_exchange_endpoint):
    logging.critical("/set_api_keys/coinbase/<coinbase_exchange_endpoint> route called")
    
    coinbase_exchange_endpoint_sanitized = trim_sanitize_strip(20, coinbase_exchange_endpoint)

    if coinbase_exchange_endpoint_sanitized not in ["coinbase_pro"]:
        logging.error("/set_api_keys/coinbase/<coinbase_exchange_endpoint> route called and not found, returning 404")
        abort(404)
    
    if coinbase_exchange_endpoint_sanitized == "coinbase":
        coinbase_exchange_endpoint_jinja_template = "Coinbase"
    if coinbase_exchange_endpoint_sanitized == "coinbase_pro":
        coinbase_exchange_endpoint_jinja_template = "Coinbase Pro"
    
    #retrieve api key metadata
    meta_data_to_return_to_user = CSR_toolkit.build_api_key_metadata_list(str(6), coinbase_exchange_endpoint_sanitized, "America/Los_Angeles", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
    
    # Create instance of the form.
    form = ApiKeyFormCoinbase()

    return render_template("error_handlers/404.html"), 200


#/set_api_keys/standard/<crypto_exchange_endpoint>
#/set_api_keys_standard/5720f640-3ac5-4cbc-81cf-d6957d6d146b/2b0104a8-1869-4b37-a4b3-3aef7f6386f5/bittrex
@app.route("/set_api_keys_standard/5720f640-3ac5-4cbc-81cf-d6957d6d146b/2b0104a8-1869-4b37-a4b3-3aef7f6386f5/<crypto_exchange_endpoint>", methods=['GET'])
def set_api_keys_standard_testing1234(crypto_exchange_endpoint):
    logging.critical("/set_api_keys/standard/<crypto_exchange_endpoint> route called")
    
    crypto_exchange_endpoint_sanitized = trim_sanitize_strip(20, crypto_exchange_endpoint)

    if crypto_exchange_endpoint_sanitized not in ['bittrex', 'kraken', 'binance_us', 'gemini', 'ftx_us']:
            logging.error("/set_api_keys/standard/<crypto_exchange_endpoint> route called and not found, returning 404")
            abort(404)

    if crypto_exchange_endpoint_sanitized == "binance_us":
        crypto_exchange_endpoint_jinja_template = "Binance US"
    if crypto_exchange_endpoint_sanitized == "bittrex":
        crypto_exchange_endpoint_jinja_template = "Bittrex"
    if crypto_exchange_endpoint_sanitized == "kraken":
        crypto_exchange_endpoint_jinja_template = "Kraken"
    if crypto_exchange_endpoint_sanitized == "gemini":
        crypto_exchange_endpoint_jinja_template = "Gemini"
    if crypto_exchange_endpoint_sanitized == "ftx_us":
        crypto_exchange_endpoint_jinja_template = "FTX US"

    meta_data_to_return_to_user = CSR_toolkit.build_api_key_metadata_list(str(6), crypto_exchange_endpoint_sanitized, "America/Los_Angeles", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])

    # Create instance of the form.
    form = ApiKeyFormStandard()

    return render_template("error_handlers/404.html"), 200


#/utilities/dca_logs
#/utilities/dca_logs/695b64c5-4b6c-4675-9b19-2842d8d5b416/2722cca8-5795-4eaa-a8bb-a688b6b155bc
@app.route("/utilities/dca_logs/695b64c5-4b6c-4675-9b19-2842d8d5b416/2722cca8-5795-4eaa-a8bb-a688b6b155bc", methods=['GET'])
def utilities_dca_logs_testing1234():
    logging.critical("/utilities/dca_logs route called")
    
    form = LogViewForm()

    headers = {}
    headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
    query_string = CSR_service_mesh_map.api_dca_purchase_logs + "?" + "user_id=" + str(6) + "&limit=" + str(100) + "&was_successful=" + str("all") + "&coin_purchased=" + str("all") + "&exchange_used=" + str("all")
    logging.error(query_string)
    query_response = requests.get(query_string, headers=headers)
    if query_response.status_code == 429:
        abort(429)
    query_response_json = query_response.json()
    logging.error(query_response_json) #debugging

    if isinstance(query_response_json, str):
        query_response_json = eval(query_response_json)
    if not isinstance(query_response_json, type([])):
        logging.error("error: response from api is not a list")
        return render_template("utilities/dca_logs.html", form=form, list_of_log_events=None, stage_indicator="blank")

    if len(query_response_json) < 1:
        logging.error("no DCA events, empty list")
        return render_template("utilities/dca_logs.html", form=form, list_of_log_events=None, stage_indicator="response")
    
    logging.error(query_response_json) #debugging
    query_response_json_removed_primary_key = []
    query_response_json_list_of_dictionaries = []
    for list in query_response_json:
        del list[0]
        del list[0]
        query_response_json_removed_primary_key.append(list)
    for list in query_response_json_removed_primary_key:
        temp_dict = {}
        
        utc_datetime_from_epoch = pytz.utc.localize(datetime.datetime.fromtimestamp(int(list[0])))
        timezone_adjusted_now = utc_datetime_from_epoch.astimezone(pytz.timezone("America/Los_Angeles"))
        temp_dict["datetime"] = timezone_adjusted_now.strftime('%Y-%m-%d %H:%M:%S')

        if list[1] == "True":
            temp_status = "Success"
        elif list[1] == "False":
            temp_status = "Failed"
        else:
            temp_status = list[1]
        temp_dict["status"] = temp_status
        temp_dict["coin"] = list[2].upper()
        temp_dict["fiatamount"] = list[3]
        temp_dict["fiatdenomination"] = list[4]
        temp_dict["exchange"] = CSR_toolkit.map_of_exchange_names_computer_to_human[list[5]]
        human_readable_time = seconds_to_human_readable(int(list[6]), granularity=4)
        temp_dict["timeinterval"] = human_readable_time
        temp_dict["highavailabilitytype"] = CSR_toolkit.supported_high_availability_type_human_friendly_map[str(list[7])]
        temp_dict["exchangeorderid"] = bleach.clean(str(list[8]), strip=True)
        temp_dict["additionalinfo"] = list[9]
        query_response_json_list_of_dictionaries.append(temp_dict)

    return render_template("error_handlers/404.html"), 200



#########################################################################
################## LOAD TESTING & MONITORING ENDS #######################
#########################################################################


if __name__ == "__main__":
    app.run(threaded=True,ssl_context="adhoc",host='0.0.0.0',port=8000)
