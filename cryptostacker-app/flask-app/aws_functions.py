import datetime
import time
import boto3
import os
import base64
import CSR_service_mesh_map
import logging
import CSR_toolkit

kms_client = boto3.client('kms',region_name="us-east-2")

#configure logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

def encrypt_string_with_kms(plaintext_string, KMS_KEY_ID):
    logging.critical("encrypt_string_with_kms() called")
    '''
    input: plaintext string
    output: encrypted binary encoded with base64
    '''
    #ENCRYPT PLAINTEXT STRING
    kms_response_object_encrypted = kms_client.encrypt(KeyId=KMS_KEY_ID, Plaintext=plaintext_string)
    kms_binary_encrypted_object = kms_response_object_encrypted[u'CiphertextBlob']
    kms_base64_binary_encrypted_password = base64.b64encode(kms_binary_encrypted_object)
    kms_base64_decoded_encrypted_password = kms_base64_binary_encrypted_password.decode()
    return kms_base64_decoded_encrypted_password

def decrypt_string_with_kms(encrypted_base64_string):
    logging.critical("decrypt_string_with_kms() called")
    '''
    input: encrypted binary encoded with base64
    output: plaintext string
    '''
    #DECRYPT PLAINTEXT STRING
    kms_encrypted_binary_object = base64.b64decode(encrypted_base64_string)
    kms_response_object_decrypted = kms_client.decrypt(CiphertextBlob=kms_encrypted_binary_object)
    plaintext_object = kms_response_object_decrypted[u'Plaintext']
    return plaintext_object.decode()

def get_aws_secret(secret_name_input):
    logging.critical("get_aws_secret() called")
    """
    Retrieve a plaintext secret from AWS secret manager, this code is taken from AWS documentation.
    Input: AWS secrets manager secret name
    Output: plaintext secret - string
    """

    secret_name = secret_name_input
    region_name = "us-east-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except boto3.ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
    return secret
