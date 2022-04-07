resource "aws_sqs_queue" "CRS-cron-events-dca-tf" {
  name                      = "CRS-cron-events-dca-tf"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 3960
  receive_wait_time_seconds = 0
  visibility_timeout_seconds = 1200 
  kms_master_key_id = aws_kms_key.CRS-cron-events-dca-tf.key_id 
  
  tags = {
  }
}

resource "aws_sqs_queue_policy" "CRS-cron-events-dca-tf" {
  queue_url = aws_sqs_queue.CRS-cron-events-dca-tf.id

  policy = <<POLICY
{
   "Version": "2012-10-17",
   "Id": "CRS-cron-events-dca-tf",
   "Statement": [{
      "Sid":"First",
      "Effect": "Allow",
      "Principal": {
         "AWS": [ 
            "${aws_iam_role.CSR-cron-events-lambda-tf.arn}",
            "${aws_iam_role.CSR-dca-purchaser-lambda-tf.arn}"
         ]
      },
      "Action": [
         "sqs:SendMessage",
         "sqs:ReceiveMessage",
         "sqs:DeleteMessage",
         "sqs:GetQueueAttributes"
      ],
      "Resource": "${aws_sqs_queue.CRS-cron-events-dca-tf.arn}"
   }]
}
POLICY
}

