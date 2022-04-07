import boto3
import base64
import logging
import CSR_service_mesh_map


def encrypt_string_with_kms(plaintext_string, Key_Id):
    '''
    input: plaintext string
    output: encrypted binary encoded with base64
    '''
    #ENCRYPT PLAINTEXT STRING
    logging.critical("encrypt_string_with_kms() called")
    kms_client = boto3.client('kms')
    kms_response_object_encrypted = kms_client.encrypt(KeyId=Key_Id, Plaintext=plaintext_string)
    kms_binary_encrypted_object = kms_response_object_encrypted[u'CiphertextBlob']
    kms_base64_binary_encrypted_password = base64.b64encode(kms_binary_encrypted_object)
    kms_base64_decoded_encrypted_password = kms_base64_binary_encrypted_password.decode()
    return kms_base64_decoded_encrypted_password

def decrypt_string_with_kms(encrypted_base64_string):
    '''
    input: encrypted binary encoded with base64
    output: plaintext string
    '''
    #DECRYPT PLAINTEXT STRING
    logging.critical("decrypt_string_with_kms() called")
    kms_client = boto3.client('kms')
    kms_encrypted_binary_object = base64.b64decode(encrypted_base64_string)
    kms_response_object_decrypted = kms_client.decrypt(CiphertextBlob=kms_encrypted_binary_object)
    plaintext_object = kms_response_object_decrypted[u'Plaintext']
    return plaintext_object.decode()

def get_aws_secret(secret_name_input):
    """
    Retrieve a plaintext secret from AWS secret manager, this code is taken from AWS documentation.
    Input: AWS secrets manager secret name
    Output: plaintext secret - string
    """
    logging.critical("get_aws_secret() called")
    logging.error("requested secret: %s" % secret_name_input)
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')

    get_secret_value_response = client.get_secret_value(SecretId=secret_name_input)

    # Decrypts secret using the associated KMS CMK.
    # Depending on whether the secret is a string or binary, one of these fields will be populated.
    if 'SecretString' in get_secret_value_response:
        secret = get_secret_value_response['SecretString']
    else:
        decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
        return decoded_binary_secret
    
    return secret

