/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.text.ParseException;
import java.sql.Types;

public class TeradataSqlOperations extends JdbcSqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(TeradataSqlOperations.class);

  @Override
  protected JsonNode formatData(final JsonNode data) {
    LOGGER.info("formatData: {}", data);
    return data;
  }

  @Override
  public void insertRecordsInternal(final JdbcDatabase database,
      final List<AirbyteRecordMessage> records,
      final String schemaName,
      final String tableName)
      throws SQLException {
    LOGGER.info("insertRecordsInternal: {}", tableName);
    if (records.isEmpty()) {
      return;
    }
    // >>>> MAXA
    // This is custom for apple Not to keep this is bad ^^

    if (tableName.equalsIgnoreCase("RPT_SPEED_UPGRADE_OPPORTUNITY") || tableName.equalsIgnoreCase("RPT_SPEED_CUSTOM_OPPORTUNITY")) {
      LOGGER.info("Records for table {}: " + records.size(), tableName);

      final String deleteQueryComponent = String.format(
          "delete from %s.%s where product_id=? and external_id=? and recommendation_month=?",
          schemaName, tableName);

      final String insertQueryComponent = String.format(
          "INSERT INTO %s.%s (product_id, external_id, cpm_key, location_key, geo_location_key, gis_key, product_class, access_type, life_cycle_status, eligible_access_type, direct_fibre_eligible, curr_prod_pkg, svc_option, ckt_monthly_bill_amt, ckt_speed_rounded_mbps, avg_util, avg_util_top45hrs, consec_hrs_above_util_thrshld, num_hrs_above_util_thrshld, max_util_avg_hr, max_util_hr, upgrade_candidate_logic, fibre_eligibility_by_telco, speed_upgrade_suggestion, upgrade_speed_suggestion_mbps, prod_pkg_median_monthly_bill, proj_median_monthly_bill, roi, upgrade_list_speed_suggestion, transform_name, transform_by, transform_dt, recommendation_month, device_name, device_type, upgrade_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
          schemaName, tableName);
      database.execute(con -> {
        final PreparedStatement pstmt = con.prepareStatement(insertQueryComponent);
        try {
          int insert_records = 0;
          for (final AirbyteRecordMessage record : records) {
            Boolean canceldelete = false;
            final JsonNode json = record.getData();
            if (json.size() == 0) { continue; }
            try {
              pstmt.setString(2, json.get("EXTERNAL_ID").asText());
              pstmt.setString(33, json.get("RECOMMENDATION_MONTH").asText());
              
              try {
                pstmt.setString(1, json.get("PRODUCT_ID").asText());
              } catch (Exception e) {
                pstmt.setNull(1, Types.VARCHAR);
              }
              try {
                pstmt.setString(3, json.get("CPM_KEY").asText());
              } catch (Exception e) {
                pstmt.setNull(3, Types.VARCHAR);
              }
              try {
                pstmt.setString(4, json.get("LOCATION_KEY").asText());
              } catch (Exception e) {
                pstmt.setNull(4, Types.VARCHAR);
              }
              try {
                pstmt.setString(5, json.get("GEO_LOCATION_KEY").asText());
              } catch (Exception e) {
                pstmt.setNull(5, Types.VARCHAR);
              }
              try {
                pstmt.setString(6, json.get("GIS_KEY").asText());
              } catch (Exception e) {
                pstmt.setNull(6, Types.VARCHAR);
              }
              try {
                pstmt.setString(7, json.get("PRODUCT_CLASS").asText());
              } catch (Exception e) {
                pstmt.setNull(7, Types.VARCHAR);
              }
              try {
                pstmt.setString(8, json.get("ACCESS_TYPE").asText());
              } catch (Exception e) {
                pstmt.setNull(8, Types.VARCHAR);
              }
              try {
                pstmt.setString(9, json.get("LIFE_CYCLE_STATUS").asText());
              } catch (Exception e) {
                pstmt.setNull(9, Types.VARCHAR);
              }
              try {
                pstmt.setString(10, json.get("ELIGIBLE_ACCESS_TYPE").asText());
              } catch (Exception e) {
                pstmt.setNull(10, Types.VARCHAR);
              }
              try {
                pstmt.setString(11, json.get("DIRECT_FIBRE_ELIGIBLE").asText());
              } catch (Exception e) {
                pstmt.setNull(11, Types.VARCHAR);
              }
              try {
                pstmt.setString(12, json.get("CURR_PROD_PKG").asText());
              } catch (Exception e) {
                pstmt.setNull(12, Types.VARCHAR);
              }
              try {
                pstmt.setString(13, json.get("SVC_OPTION").asText());
              } catch (Exception e) {
                pstmt.setNull(13, Types.VARCHAR);
              }
              try {
                pstmt.setFloat(14, (float) json.get("CKT_MONTHLY_BILL_AMT").asDouble());
              } catch (Exception e) {
                pstmt.setNull(14, Types.FLOAT);
              }
              try {
                pstmt.setFloat(15, (float) json.get("CKT_SPEED_ROUNDED_MBPS").asDouble());
              } catch (Exception e) {
                pstmt.setNull(15, Types.FLOAT);
              }
              try {
                pstmt.setFloat(16, (float) json.get("AVG_UTIL").asDouble());
              } catch (Exception e) {
                pstmt.setNull(16, Types.FLOAT);
              }
              try {
                pstmt.setFloat(17, (float) json.get("AVG_UTIL_TOP45HRS").asDouble());
              } catch (Exception e) {
                pstmt.setNull(17, Types.FLOAT);
              }
              try {
                pstmt.setFloat(18, (float) json.get("CONSEC_HRS_ABOVE_UTIL_THRSHLD").asDouble());
              } catch (Exception e) {
                pstmt.setNull(18, Types.FLOAT);
              }
              try {
                pstmt.setFloat(19, (float) json.get("NUM_HRS_ABOVE_UTIL_THRSHLD").asDouble());
              } catch (Exception e) {
                pstmt.setNull(19, Types.FLOAT);
              }
              try {
                pstmt.setFloat(20, (float) json.get("MAX_UTIL_AVG_HR").asDouble());
              } catch (Exception e) {
                pstmt.setNull(20, Types.FLOAT);
              }
              try {
                pstmt.setFloat(21, (float) json.get("MAX_UTIL_HR").asDouble());
              } catch (Exception e) {
                pstmt.setNull(21, Types.FLOAT);
              }
              try {
                pstmt.setString(22, json.get("UPGRADE_CANDIDATE_LOGIC").asText());
              } catch (Exception e) {
                pstmt.setNull(22, Types.VARCHAR);
              }
              try {
                pstmt.setString(23, json.get("FIBRE_ELIGIBILITY_BY_TELCO").asText());
              } catch (Exception e) {
                pstmt.setNull(23, Types.VARCHAR);
              }
              try {
                pstmt.setString(24, json.get("SPEED_UPGRADE_SUGGESTION").asText());
              } catch (Exception e) {
                pstmt.setNull(24, Types.VARCHAR);
              }
              try {
                pstmt.setFloat(25, (float) json.get("UPGRADE_SPEED_SUGGESTION_MBPS").asDouble());
              } catch (Exception e) {
                pstmt.setNull(25, Types.FLOAT);
              }
              try {
                pstmt.setFloat(26, (float) json.get("PROD_PKG_MEDIAN_MONTHLY_BILL").asDouble());
              } catch (Exception e) {
                pstmt.setNull(26, Types.FLOAT);
              }
              try {
                pstmt.setFloat(27, (float) json.get("PROJ_MEDIAN_MONTHLY_BILL").asDouble());
              } catch (Exception e) {
                pstmt.setNull(27, Types.FLOAT);
              }
              try {
                pstmt.setFloat(28, (float) json.get("ROI").asDouble());
              } catch (Exception e) {
                pstmt.setNull(28, Types.FLOAT);
              }
              try {
                pstmt.setString(29, json.get("UPGRADE_LIST_SPEED_SUGGESTION").asText().replace("\n","").replace(" ",""));
              } catch (Exception e) {
                pstmt.setNull(29, Types.VARCHAR);
              }
              try {
                pstmt.setString(30, json.get("TRANSFORM_NAME").asText());
              } catch (Exception e) {
                pstmt.setNull(30, Types.VARCHAR);
              }
              try {
                pstmt.setString(31, json.get("TRANSFORM_BY").asText());
              } catch (Exception e) {
                pstmt.setNull(31, Types.VARCHAR);
              }
              try {
                pstmt.setTimestamp(32, Timestamp.from(Instant.parse(json.get("TRANSFORM_DT").asText())));
              } catch (Exception e) {
                pstmt.setNull(32, Types.TIMESTAMP);
              }
              // device_name, device_type, upgrade_type
              try {
                pstmt.setString(34, json.get("DEVICE_NAME").asText());
              } catch (Exception e) {
                pstmt.setNull(34, Types.VARCHAR);
              }
              try {
                pstmt.setString(35, json.get("DEVICE_TYPE").asText());
              } catch (Exception e) {
                pstmt.setNull(35, Types.VARCHAR);
              }
              try {
                pstmt.setString(36, json.get("LOGICAL_UPDATE").asText());
              } catch (Exception e) {
                pstmt.setNull(36, Types.VARCHAR);
              }


              pstmt.addBatch();
              insert_records++;
            } catch (Exception se) {
              try {
                LOGGER.info("Error Issue with one insert: PRODUCT_ID='{}', EXTERNAL_ID='{}', RECOMMENDATION_MONTH='{}'",
                json.get("PRODUCT_ID").asText(),
                json.get("EXTERNAL_ID").asText(),
                json.get("RECOMMENDATION_MONTH").asText()
                );
              } catch (Exception e) {
                LOGGER.info("Error Issue with one insert (unable to get PKs) record:{}, size:{}", json.toString(), json.size());
              }
              pstmt.clearParameters();
            }
          }
          if (insert_records > 0) {
            LOGGER.info("executeBatch");
            pstmt.executeBatch();
          }
        } catch (final SQLException se) {
          for (SQLException ex = se; ex != null; ex = ex.getNextException()) {
            LOGGER.info(ex.getMessage());
          }
          AirbyteTraceMessageUtility.emitSystemErrorTrace(se,
              "Connector failed while inserting records to staging table");
          throw new RuntimeException(se);
        } catch (final Exception e) {
          AirbyteTraceMessageUtility.emitSystemErrorTrace(e,
              "Connector failed while inserting records to staging table");
          throw new RuntimeException(e);
        }

      });
    } else if (tableName.equalsIgnoreCase("FACT_BALI_SPEED_UTILIZATION")) {
      LOGGER.info("Records for table fact_bali_speed_utilization: " + records.size());

      final String deleteQueryComponent = String.format(
          "delete from %s.%s where bali_keyname=? and product_id=? and bali_util_event_ts=?",
          schemaName, tableName);

      final String insertQueryComponent = String.format(
          "insert into %s.%s " +
              "(bali_cust_api_key, bali_keyname, external_id, bali_avg_util_perc, bali_max_util_perc, bali_last_observed_spd, bali_util_event_ts, curr_prod_pkg, location_key, geo_location_key, ult_par_gis_key, cpm_key, product_id, maxa_ingestion_timestamp, transform_dt, transform_name, transform_by) "
              +
              "values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?)",
          schemaName, tableName);

      LOGGER.info("Call execute fact_bali_speed_utilization");
      database.execute(con -> {
        try {
          PreparedStatement pstmt = con.prepareStatement(insertQueryComponent);
          // PreparedStatement deletestmt = con.prepareStatement(deleteQueryComponent);
          int insert_records = 0;
          for (final AirbyteRecordMessage record : records) {
            final JsonNode json = record.getData();
            if (json.size() == 0) { continue; }
            try {
            pstmt.setString(2, json.get("BALI_KEYNAME").asText());
            try {
              pstmt.setString(1, json.get("BALI_CUST_API_KEY").asText());
            } catch (Exception e) {
              pstmt.setNull(1, Types.VARCHAR);
            }
            try {
              pstmt.setString(3, json.get("EXTERNAL_ID").asText());
            } catch (Exception e) {
              pstmt.setNull(3, Types.VARCHAR);
            }
            try {
              pstmt.setFloat(4, (float) json.get("BALI_AVG_UTIL_PERC").asDouble());
            } catch (Exception e) {
              pstmt.setNull(4, Types.FLOAT);
            }
            try {
              pstmt.setFloat(5, (float) json.get("BALI_MAX_UTIL_PERC").asDouble());
            } catch (Exception e) {
              pstmt.setNull(5, Types.FLOAT);
            }
            try {
              pstmt.setFloat(6, (float) json.get("BALI_LAST_OBSERVED_SPD").asDouble());
            } catch (Exception e) {
              pstmt.setNull(6, Types.FLOAT);
            }
            try {
              pstmt.setTimestamp(7, Timestamp.from(Instant.parse(json.get("BALI_UTIL_EVENT_TS").asText() + "Z")));
            } catch (Exception e) {
              pstmt.setNull(7, Types.TIMESTAMP);
            }
            try {
              pstmt.setString(8, json.get("CURR_PROD_PKG").asText());
            } catch (Exception e) {
              pstmt.setNull(8, Types.VARCHAR);
            }
            try {
              pstmt.setString(9, json.get("LOCATION_KEY").asText());
            } catch (Exception e) {
              pstmt.setNull(9, Types.VARCHAR);
            }
            try {
              pstmt.setString(10, json.get("GEO_LOCATION_KEY").asText());
            } catch (Exception e) {
              pstmt.setNull(10, Types.VARCHAR);
            }
            try {
              pstmt.setString(11, json.get("ULT_PAR_GIS_KEY").asText());
            } catch (Exception e) {
              pstmt.setNull(11, Types.VARCHAR);
            }
            try {
              pstmt.setString(12, json.get("CPM_KEY").asText());
            } catch (Exception e) {
              pstmt.setNull(12, Types.VARCHAR);
            }
            try {
              pstmt.setString(13, json.get("PRODUCT_ID").asText());
            } catch (Exception e) {
              pstmt.setNull(13, Types.VARCHAR);
            }
            try {
              pstmt.setTimestamp(14,
                  Timestamp.from(Instant.parse(json.get("MAXA_INGESTION_TIMESTAMP").asText() + "Z")));
            } catch (Exception e) {
              pstmt.setNull(14, Types.TIMESTAMP);
            }
            try {
              pstmt.setTimestamp(15,
                  Timestamp.from(Instant.parse(json.get("TRANSFORM_DT").asText())));
            } catch (Exception e) {
              pstmt.setNull(15, Types.TIMESTAMP);
            }
            try {
              pstmt.setString(16, json.get("TRANSFORM_NAME").asText());
            } catch (Exception e) {
              pstmt.setNull(16, Types.VARCHAR);
            }
            try {
              pstmt.setString(17, json.get("TRANSFORM_BY").asText());
            } catch (Exception e) {
              pstmt.setNull(17, Types.VARCHAR);
            }
            pstmt.addBatch();
            insert_records++;
            // pstmt.clearParameters();
          } catch (Exception e) {
            try {
              LOGGER.info("Error Issue with one insert: BALI_KEYNAME='{}'", json.get("BALI_KEYNAME").asText());
            } catch (Exception err) {
              LOGGER.info("Error Issue with one insert (unable to get PKs)");
            }
          }
        }
          if (insert_records > 0) {
            pstmt.executeBatch();
            LOGGER.info("Executed");
          }

        } catch (final SQLException se) {
          for (SQLException ex = se; ex != null; ex = ex.getNextException()) {
            LOGGER.info(ex.getMessage());
          }
          AirbyteTraceMessageUtility.emitSystemErrorTrace(se,
              "Connector failed while inserting records to staging table");
          throw new RuntimeException(se);
        } catch (final Exception e) {
          AirbyteTraceMessageUtility.emitSystemErrorTrace(e,
              "Connector failed while inserting records to staging table");
          throw new RuntimeException(e);
        }

      });
    }
    // <<<< MAXA

    else {

      final String insertQueryComponent = String.format("INSERT INTO %s.%s (%s, %s, %s) VALUES (?, ?, ?)", schemaName,
          tableName,
          JavaBaseConstants.COLUMN_NAME_AB_ID,
          JavaBaseConstants.COLUMN_NAME_DATA,
          JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
      database.execute(con -> {
        try {

          final PreparedStatement pstmt = con.prepareStatement(insertQueryComponent);

          for (final AirbyteRecordMessage record : records) {

            final String uuid = UUID.randomUUID().toString();
            final String jsonData = Jsons.serialize(formatData(record.getData()));
            final Timestamp emittedAt = Timestamp.from(Instant.ofEpochMilli(record.getEmittedAt()));
            LOGGER.info("uuid: " + uuid);
            LOGGER.info("jsonData: " + jsonData);
            LOGGER.info("emittedAt: " + emittedAt);
            pstmt.setString(1, uuid);
            pstmt.setString(2, jsonData);
            pstmt.setTimestamp(3, emittedAt);
            pstmt.addBatch();

          }

          pstmt.executeBatch();

        } catch (final SQLException se) {
          for (SQLException ex = se; ex != null; ex = ex.getNextException()) {
            LOGGER.info(ex.getMessage());
          }
          AirbyteTraceMessageUtility.emitSystemErrorTrace(se,
              "Connector failed while inserting records to staging table");
          throw new RuntimeException(se);
        } catch (final Exception e) {
          AirbyteTraceMessageUtility.emitSystemErrorTrace(e,
              "Connector failed while inserting records to staging table");
          throw new RuntimeException(e);
        }

      });
    }
  }

  // public Timestamp toTimestamp(final String timestamp) throws ParseException {
  // SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd
  // hh:mm:ss.SSS");
  // Date parsedDate = dateFormat.parse(timestamp);
  // return new java.sql.Timestamp(parsedDate.getTime());
  // }

  @Override
  public void createSchemaIfNotExists(final JdbcDatabase database, final String schemaName) throws Exception {
    try {
      database.execute(String.format("CREATE DATABASE \"%s\" AS PERMANENT = 120e6, SPOOL = 120e6;", schemaName));
    } catch (final SQLException e) {
      if (e.getMessage().contains("already exists")) {
        LOGGER.warn("Database " + schemaName + " already exists.");
      } else {
        AirbyteTraceMessageUtility.emitSystemErrorTrace(e, "Connector failed while creating schema ");
        throw new RuntimeException(e);
      }
    }

  }

  @Override
  public void createTableIfNotExists(final JdbcDatabase database, final String schemaName, final String tableName)
      throws SQLException {
    try {
      database.execute(createTableQuery(database, schemaName, tableName));
    } catch (final SQLException e) {
      if (e.getMessage().contains("already exists")) {
        LOGGER.warn("Table " + schemaName + "." + tableName + " already exists.");
      } else {
        AirbyteTraceMessageUtility.emitSystemErrorTrace(e, "Connector failed while creating table ");
        throw new RuntimeException(e);
      }
    }
  }

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    return String.format(
        "CREATE SET TABLE %s.%s, FALLBACK ( \n" + "%s VARCHAR(256), \n" + "%s JSON, \n" + "%s TIMESTAMP(6) \n"
            + ");\n",
        schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
  }

  @Override
  public void dropTableIfExists(final JdbcDatabase database, final String schemaName, final String tableName)
      throws SQLException {
    try {
      database.execute(dropTableIfExistsQueryInternal(schemaName, tableName));
    } catch (final SQLException e) {
      AirbyteTraceMessageUtility.emitSystemErrorTrace(e,
          "Connector failed while dropping table " + schemaName + "." + tableName);
    }
  }

  @Override
  public String truncateTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    try {
      return String.format("DELETE %s.%s ALL;\n", schemaName, tableName);
    } catch (final Exception e) {
      AirbyteTraceMessageUtility.emitSystemErrorTrace(e,
          "Connector failed while truncating table " + schemaName + "." + tableName);
    }
    return "";
  }

  private String dropTableIfExistsQueryInternal(final String schemaName, final String tableName) {
    try {
      return String.format("DROP TABLE  %s.%s;\n", schemaName, tableName);
    } catch (final Exception e) {
      AirbyteTraceMessageUtility.emitSystemErrorTrace(e,
          "Connector failed while dropping table " + schemaName + "." + tableName);
    }
    return "";
  }

  @Override
  public void executeTransaction(final JdbcDatabase database, final List<String> queries) throws Exception {
    final StringBuilder appendedQueries = new StringBuilder();
    try {
      for (final String query : queries) {
        LOGGER.info("query: {}", query.toString());
        appendedQueries.append(query);
      }
      LOGGER.info("Queries: {}", appendedQueries.toString());
      if (!appendedQueries.isEmpty()) {
        database.execute(appendedQueries.toString());
      }
    } catch (final SQLException e) {
      AirbyteTraceMessageUtility.emitSystemErrorTrace(e,
          "Connector failed while executing queries : " + appendedQueries.toString());
    }
  }

}
