/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.util;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import java.util.Iterator;
import java.util.Map.Entry;
import org.apache.spark.sql.types.ArrayType;
import org.apache.spark.sql.types.DataType;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.StructType;

public class AirbyteSchemaConverter {

    public static StructType toStructType(JsonNode airbyteSchema) {
        DataType dataType = toDataType(airbyteSchema);
        if (dataType instanceof StructType) {
            return (StructType) dataType;
        } else {
            // If the root is not an object, wrap it (though Airbyte streams are usually
            // objects)
            return new StructType().add("value", dataType);
        }
    }

    private static DataType toDataType(JsonNode node) {
        if (node == null || !node.has("type")) {
            return DataTypes.StringType;
        }

        JsonNode typeNode = node.get("type");
        String type;
        if (typeNode.isArray()) {
            // Handle ["string", "null"] etc.
            type = getNonNullableType((ArrayNode) typeNode);
        } else {
            type = typeNode.asText();
        }

        switch (type) {
            case "string":
                return DataTypes.StringType;
            case "integer":
                return DataTypes.LongType;
            case "number":
                return DataTypes.DoubleType;
            case "boolean":
                return DataTypes.BooleanType;
            case "object":
                return toStructTypeFromObject(node);
            case "array":
                return toArrayType(node);
            default:
                return DataTypes.StringType;
        }
    }

    private static String getNonNullableType(ArrayNode types) {
        for (JsonNode t : types) {
            String typeName = t.asText();
            if (!"null".equals(typeName)) {
                return typeName;
            }
        }
        return "string";
    }

    private static StructType toStructTypeFromObject(JsonNode node) {
        StructType struct = new StructType();
        if (node.has("properties")) {
            JsonNode properties = node.get("properties");
            Iterator<Entry<String, JsonNode>> fields = properties.fields();
            while (fields.hasNext()) {
                Entry<String, JsonNode> field = fields.next();
                struct = struct.add(field.getKey(), toDataType(field.getValue()));
            }
        }
        return struct;
    }

    private static ArrayType toArrayType(JsonNode node) {
        if (node.has("items")) {
            return DataTypes.createArrayType(toDataType(node.get("items")));
        }
        return DataTypes.createArrayType(DataTypes.StringType);
    }
}
