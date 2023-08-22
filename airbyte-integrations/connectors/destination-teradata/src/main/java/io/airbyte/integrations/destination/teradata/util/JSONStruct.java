package io.airbyte.integrations.destination.teradata.util;

import java.sql.SQLException;
import java.sql.Struct;

/**
 * Struct type to handle Teradata JSON data type. The JSON data type stores text as a CLOB in either CHARACTER SET LATIN or CHARACTER SET UNICODE.
 * A JSON value sent to the Teradata database using a Struct containing String or a Reader attribute.
 */
public class JSONStruct  implements Struct {
    private Object [] m_attributes ;
    private String m_sqlTypeName ;

    public JSONStruct (String sqlTypeName, Object[] attributes)
    {
        m_sqlTypeName = sqlTypeName ;
        m_attributes = attributes ;
    }

    public Object [] getAttributes () throws SQLException
    {
        return m_attributes ;
    }

    public String getSQLTypeName () throws SQLException
    {
        return m_sqlTypeName ;
    }

    // This method is not supported, but needs to be included
    public Object [] getAttributes (java.util.Map map) throws SQLException
    {
        // Unsupported Exception
        throw new SQLException ("getAttributes (Map) NOT SUPPORTED") ;
    }

}
