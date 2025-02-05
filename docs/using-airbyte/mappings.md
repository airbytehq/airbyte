---
products: cloud-teams
---

# Mapping fields

Use mappings to hash, encrypt, and rename fields, and filter rows. You set up mappings on each stream, ensuring your source data arrives in your destination exactly as you want it.

![Screenshot of mappings feature showing several streams with mappings applied](images/mappings.png)

## More about mapping in Airbyte

It’s often the case that you want to move data from a source to a destination in a non-literal way, obscuring sensitive information and improving the consistency and usability of that data in its final destination. Mapping allows you to match a field from your source to your destination and sync data in a way that is still accurate, but also more meaningful and appropriate for your needs.

Several types of mapping are possible in Airbyte, and you can combine them together in meaningful ways.

### Hash

Hashing is an **irreversible** process that protects sensitive data by obscuring it. Airbyte supports MD5, SHA-256, and SHA-512 hashing methods. Support for MD2, SHA-1, and SHA-384 is only available [through the API](https://reference.airbyte.com).

![](images/mapping-hash.png)

There are many reasons you might want to hash data.

- **Data security**: Source datasets can contain data like passwords or credit card information. It's more secure to store a hashed or encrypted version of this data.
- **Data integrity**: You can compare hashed values to ensure nobody has tampered with the data.
- **Efficient retrieval**: Hashing can enable faster lookups in databases.
- **Anonymity and compliance**: Source datasets can contain personally identifiable information (PII). Anonymizing PII can help you meet data privacy regulations like GDPR and HIPAA.

### Encrypt

Encryption is a **reversible** process that protects sensitive data by obscuring it. Airbyte supports RSA and AES encryption using an encryption key you generate yourself.

![](images/mapping-encrypt.png)

There are many reasons you might want to encrypt data.

- **Data security**: Source datasets can contain data like passwords or credit card information. It's more secure to store a hashed or encrypted version of this data.
- **Data integrity**: You can compare hashed values to ensure nobody has tampered with the data.
- **Efficient retrieval**: Hashing can enable faster lookups in databases.
- **Anonymity and compliance**: Source datasets can contain personally identifiable information (PII). Anonymizing PII can help you meet data privacy regulations like GDPR and HIPAA.

<!-- Probably need some guidance on the use of keys with Airbyte, esp. wrt external secrets managers and AES encryption, and the validation rules -->

### Rename field

Renaming fields helps you ensure clarity, consistency, and compatibility in your destination data. 

![](images/mapping-rename.png)

There are many reasons you might want to rename fields.

- **Schema alignment**: Sources and destinations can use different naming conventions, or your destination can have more stringent naming requirements.
- **Readability and understanding**: Sources won't always have descriptive field names and the purpose of a field can be lost out of context. In an HRIS system, you might guess that `emp_num` is an employee number, but that might be less obvious years later in a data warehouse. Meaningful, descriptive names help teams understand and manage their data more efficiently.
- **Avoid conflicts**: Prevent multiple fields from having unnecessarily similar or identical names, and avoid the use of reserved keywords as field names.

### Filter rows

Filtering rows is how you ensure you only sync relevant, high-quality, and meaningful data to your destination. 

![](images/mapping-filter.png)

There are many reasons you might want to filter rows.

- **Remove irrelevant or corrupted data**: Data sources can contain test data, incomplete transactions, null values, and other things you don't want to preserve.
- **Optimization**: Smaller datasets require less processing and storage, and you can query them faster.
- **Compliance**: You don't want to keep data longer than is needed for a defined business purpose, and you want to ensure you don't accidentally archive data from individuals who opted out of data collection.

:::note
You can only filter fields whose type is string and number.
:::

## Considerations and limitations

Before you begin mapping fields, consider the following.

- If you set up mapping on an existing connection, Airbyte prompts you to clear your stream and the data in your destination. You almost certainly should do this. Not doing this could result in undesirable or unexpected behavior. For example, if you set up hashing on a field that contains personally identifiable information (PII), you want all data in that column to be hashed, not just new data. Clearing your destination accomplishes this. However, if you're dealing with an extremely large database, a complete resync might take a significant amount of time.
- Do not map a cursor or primary key field if the [sync mode](core-concepts/sync-modes) depends on it. Doing this disrupts Airbyte's ability to use them for incremental syncing and deduplication.

## Create a new mapping

Follow these steps to create a new mapping. Once you add a mapping to a stream, you cannot disable that stream until you [delete that stream's mappings](#delete).

1. Click **Connections** in the sidebar.
2. Click the connection on which you want to set up mappings.
3. Click **Mappings**.
4. Click **Select stream** or **Add stream**.
5. Select the stream on which you want to set up mappings.
6. Define your mappings for that stream. 
7. When you're done, click **Submit**. Airbyte may prompt you to clear your stream and destination to avoid unexpected behavior. The mapping is applied next time you sync data.

## Modify a mapping

Follow these steps to change an existing mapping.

1. Click **Connections** in the sidebar.
2. Click the connection on which you want to set up mappings.
3. Click **Mappings**.
4. Find the mappings you want to modify, and adjust them.
5. When you're done, click **Submit**.

## Delete a mapping {#delete}

Follow these steps to create a new mapping.

1. Click **Connections** in the sidebar.
2. Click the connection on which you want to set up mappings.
3. Click **Mappings**.
4. Click the trash can icon next to the mapping you want to remove.
