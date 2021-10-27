# Amazon SQS Source

## What
This is a connector for consuming messages from an [Amazon SQS Queue](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)

## How
### Polling
It uses [long polling](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-short-and-long-polling.html) to consume in batches 
of up to 10 at a time (10 is the maximum defined by the AWS API).

The batch size is configurable between 1 and 10 (a size of 0 would use short-polling, this is not allowed).

Using larger batches reduces the amount of connections thus increasing performance.

### Deletes
Optionally, it can delete messages after reading - the delete_message() call is made __after__ yielding the message to the generator.
This means that messages aren't deleted unless read by a Destination - however, there is still potential that this could result in 
missed messages if the Destination fails __after__ taking the message, but before commiting to to its own downstream.

### Credentials
Requires an AWS IAM Access Key ID and Secret Key.

This could be improved to add support for configured AWS profiles, env vars etc.

### Output
Although messages are consumed in batches, they are output from the Source as individual messages.