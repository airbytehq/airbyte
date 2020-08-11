package io.dataline.db;

import java.sql.ResultSet;
import java.sql.SQLException;

@FunctionalInterface
public interface ResultSetTransformer<T>  {
    T apply(ResultSet resultSet) throws SQLException;
}
