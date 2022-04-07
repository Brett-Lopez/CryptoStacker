#delete all session keys in redis
#runs daily 1am pacific
#cron syntax:
# 0 9 * * ? *

import logging
import redis
import CSR_toolkit

redis_client = redis.StrictRedis(host='csr-redis-flask-session-tf.bwd3wc.ng.0001.use2.cache.amazonaws.com', port=6379, db=0)

#configure logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

def lambda_handler(event, context):
    logging.error("lambda begins") #debugging
    logging.error("for loop begins") #debugging
    loop_counter = 0
    for key in redis_client.scan_iter("*"):
        #logging.error(key) #debugging
        loop_counter += 1
        redis_client.delete(key)
    logging.error("for loop ends") #debugging
    logging.error("deleted %s redis session keys" % str(loop_counter)) #debugging
