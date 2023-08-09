package io.airbyte.integrations.destination.jdbc;

import java.sql.SQLType;
import lombok.Getter;

@Getter
public record CustomSqlType(String name, String vendor, Integer vendorTypeNumber) implements SQLType {

}
