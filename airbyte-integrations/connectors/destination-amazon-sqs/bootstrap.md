# Amazon SQS Destination

## What

This is a connector for producing messages to an [Amazon SQS Queue](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)

## How

### Sending messages

Amazon SQS allows messages to be sent individually or in batches. Currently, this Destination only supports sending messages individually. This can
have performance implications if sending high volumes of messages.

#### Message Body

By default, the SQS Message body is built using the AirbyteMessageRecord's 'data' property.

If the **message_body_key** config item is set, we use the value as a key within the AirbyteMessageRecord's 'data' property. This could be
improved to handle nested keys by using JSONPath syntax to lookup values.

For example, given the input Record:

```
{
    "data":
    {
        "parent_key": {
            "nested_key": "nested_value"
        },
        "top_key": "top_value"
    }
}
```

With no **message_body_key** set, the output SQS Message body will be

```
{
    "parent_key": {
        "nested_key": "nested_value"
    },
    "top_key": "top_value"
}
```

With **message_body_key** set to `parent_key`, the output SQS Message body will be

```
{
    "nested_key": "nested_value"
}
```

#### Message attributes

The airbyte_emmited_at timestamp is added to every message as an Attribute by default. This could be improved to allow the user to set Attributes through the UI, or to take keys from the Record as Attributes.

#### FIFO Queues

A Queue URL that ends with '.fifo' **must** be a valid FIFO Queue. When the queue is FIFO, the _message_group_id_ property is required.

Currently, a unique uuid4 is generated as the dedupe ID for every message. This could be improved to allow the user to specify a path in the Record
to use as a dedupe ID.

### Credentials

Requires an AWS IAM Access Key ID and Secret Key.

This could be improved to add support for configured AWS profiles, env vars etc.
