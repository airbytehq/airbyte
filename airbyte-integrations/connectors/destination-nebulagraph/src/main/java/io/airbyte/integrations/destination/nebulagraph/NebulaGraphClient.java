/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.nebulagraph;

import com.vesoft.nebula.client.graph.NebulaPoolConfig;
import com.vesoft.nebula.client.graph.data.HostAddress;
import com.vesoft.nebula.client.graph.data.ResultSet;
import com.vesoft.nebula.client.graph.net.NebulaPool;
import com.vesoft.nebula.client.graph.net.Session;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public interface NebulaGraphClient extends AutoCloseable {

  void execute(String nGql) throws Exception;

  /**
   * Execute a read-only nGQL and return the specified column as a list of strings. Intended for
   * test-time retrieval of previously written raw JSON (e.g. alias 'd').
   */
  default List<String> queryJsonColumn(String nGql, String alias) throws Exception {
    throw new UnsupportedOperationException("queryJsonColumn is not implemented");
  }

  @Override
  void close();

  static NebulaGraphClient connect(NebulaGraphConfig config) {
    return new DefaultNebulaGraphClient(config);
  }

  final class DefaultNebulaGraphClient implements NebulaGraphClient {

    private final NebulaPool pool;
    private final Session session;
    private static final Logger LOG = LoggerFactory.getLogger(DefaultNebulaGraphClient.class);

    DefaultNebulaGraphClient(NebulaGraphConfig config) {
      this.pool = new NebulaPool();
      this.session = initSession(config);
    }

    private Session initSession(NebulaGraphConfig config) {
      List<HostAddress> addresses = parseAddresses(config.graphdAddresses);

      NebulaPoolConfig poolConfig = new NebulaPoolConfig();
      poolConfig.setMaxConnSize(1);
      poolConfig.setMinConnSize(1);
      poolConfig.setTimeout(10_000);

      try {
        if (!pool.init(addresses, poolConfig)) {
          throw new IllegalStateException("Failed to initialise NebulaPool with provided addresses.");
        }
        return pool.getSession(config.username, config.password, true);
      } catch (Exception e) {
        closeQuietly(null, pool);
        throw new RuntimeException("Unable to create NebulaGraph session", e);
      }
    }

    private static List<HostAddress> parseAddresses(String rawAddresses) {
      if (rawAddresses == null || rawAddresses.isBlank()) {
        throw new IllegalArgumentException("graphd_addresses must not be empty");
      }
      List<HostAddress> result = new ArrayList<>();
      String[] entries = rawAddresses.split(",");
      for (String entry : entries) {
        String trimmed = entry.trim();
        if (trimmed.isEmpty()) {
          continue;
        }
        int sep = trimmed.lastIndexOf(':');
        if (sep <= 0 || sep == trimmed.length() - 1) {
          throw new IllegalArgumentException("Invalid graphd address: " + trimmed);
        }
        String host = trimmed.substring(0, sep).trim();
        String portRaw = trimmed.substring(sep + 1).trim();
        try {
          int port = Integer.parseInt(portRaw);
          result.add(new HostAddress(host, port));
        } catch (NumberFormatException nfe) {
          throw new IllegalArgumentException("Invalid graphd port in address: " + trimmed, nfe);
        }
      }
      if (result.isEmpty()) {
        throw new IllegalArgumentException("No valid graphd addresses provided");
      }
      return result;
    }

    @Override
    public void execute(String nGql) throws Exception {
      ResultSet result = session.execute(nGql);
      if (!result.isSucceeded()) {
        throw new Exception("NebulaGraph execution failed (code=" + result.getErrorCode() + "): " + result.getErrorMessage());
      }
    }

    @Override
    public List<String> queryJsonColumn(String nGql, String alias) throws Exception {
      ResultSet rs = session.execute(nGql);
      if (!rs.isSucceeded()) {
        throw new Exception("NebulaGraph query failed (code=" + rs.getErrorCode() + "): " + rs.getErrorMessage());
      }
      try {
        List<String> colNames = rs.getColumnNames();
        int idx = 0;
        if (alias != null && !alias.isEmpty() && colNames != null) {
          for (int i = 0; i < colNames.size(); i++) {
            if (alias.equalsIgnoreCase(colNames.get(i))) {
              idx = i;
              break;
            }
          }
        }
        int rowCount = 0;
        try {
          rowCount = rs.rowsSize();
        } catch (Throwable t) {
          try {
            rowCount = (int) rs.getClass().getMethod("rowsSize").invoke(rs);
          } catch (Exception ignore) {}
        }
        LOG.debug("nGQL exec ok. sql='{}' cols={} targetAlias='{}' resolvedIndex={} rows={}", nGql, colNames, alias, idx, rowCount);
        List<String> out = new ArrayList<>(rowCount);
        for (int r = 0; r < rowCount; r++) {
          Object rowObj;
          try {
            rowObj = rs.rowValues(r);
          } catch (Throwable t) {
            try {
              rowObj = rs.getClass().getMethod("getRowValues", int.class).invoke(rs, r);
            } catch (Throwable inner) {
              LOG.debug("row {} fetch failed: {}", r, inner.toString());
              out.add(null);
              continue;
            }
          }
          List<?> cells = null;
          if (rowObj instanceof List) {
            cells = (List<?>) rowObj;
          } else {
            String[] accessors = {"values", "getValues", "columns", "getColumns"};
            for (String m : accessors) {
              try {
                Object v = rowObj.getClass().getMethod(m).invoke(rowObj);
                if (v instanceof List) {
                  cells = (List<?>) v;
                  break;
                }
              } catch (Exception ignore) {}
            }
          }
          if (cells == null) {
            LOG.debug("row {} has no accessible cells: class={} raw={}", r, rowObj == null ? "null" : rowObj.getClass().getName(), rowObj);
            out.add(null);
            continue;
          }
          if (cells.isEmpty()) {
            out.add(null);
            continue;
          }
          if (idx >= cells.size()) {
            LOG.debug("row {} index {} out of bounds (size={}), fallback idx=0", r, idx, cells.size());
            idx = 0;
          }
          Object cell = cells.get(idx);
          String s = null;
          boolean isNull = false;
          try {
            Object nv = cell.getClass().getMethod("isNull").invoke(cell);
            if (nv instanceof Boolean && (Boolean) nv)
              isNull = true;
          } catch (Exception ignore) {}
          if (!isNull) {
            try {
              s = (String) cell.getClass().getMethod("asString").invoke(cell);
            } catch (Exception e1) {
              try {
                s = String.valueOf(cell);
              } catch (Exception ignore) {}
            }
          }
          // Fallback: if s still null but we have a cell, use cell.toString()
          if (s == null && cell != null) {
            try {
              s = cell.toString();
            } catch (Exception ignore) { /* ignore */ }
          }
          // Only treat value as null if explicit null marker
          if (s == null || "null".equalsIgnoreCase(s)) {
            out.add(null);
          } else {
            out.add(s);
          }
          if (r < 3) {
            LOG.info("sample row {} cellClass={} rawCell='{}' parsed='{}' isNullFlag={} index={} cols={}", r,
                cell == null ? "null" : cell.getClass().getName(), cell, s, isNull, idx, colNames);
          }
        }
        return out;
      } catch (Throwable direct) {
        LOG.debug("direct path failed, fallback reflection: {}", direct.toString());
        return reflectiveQueryJsonColumn(rs, alias);
      }
    }

    // Legacy reflective implementation extracted for clarity
    private List<String> reflectiveQueryJsonColumn(ResultSet rs, String alias) throws Exception {
      int columnIndex = 0;
      try {
        List<String> names;
        try {
          names = (List<String>) rs.getClass().getMethod("getColumnNames").invoke(rs);
        } catch (NoSuchMethodException e1) {
          names = (List<String>) rs.getClass().getMethod("getColNames").invoke(rs);
        }
        if (names != null && alias != null && !alias.isEmpty()) {
          for (int i = 0; i < names.size(); i++) {
            String n = names.get(i);
            if (alias.equals(n) || alias.equalsIgnoreCase(n)) {
              columnIndex = i;
              break;
            }
          }
        }
      } catch (ReflectiveOperationException ignore) {}

      int rows;
      try {
        try {
          rows = (int) rs.getClass().getMethod("rowsSize").invoke(rs);
        } catch (NoSuchMethodException e1) {
          rows = (int) rs.getClass().getMethod("getRowsSize").invoke(rs);
        }
      } catch (ReflectiveOperationException e) {
        throw new RuntimeException("Unable to read Nebula ResultSet row count via reflection", e);
      }

      List<String> out = new ArrayList<>(rows);
      for (int i = 0; i < rows; i++) {
        try {
          Object rowObj;
          try {
            rowObj = rs.getClass().getMethod("rowValues", int.class).invoke(rs, i);
          } catch (NoSuchMethodException e1) {
            rowObj = rs.getClass().getMethod("getRowValues", int.class).invoke(rs, i);
          }

          List<?> cells = null;
          if (rowObj instanceof java.util.List) {
            cells = (List<?>) rowObj;
          } else {
            String[] accessors = {"getValues", "values", "getColumns"};
            for (String m : accessors) {
              try {
                Object v = rowObj.getClass().getMethod(m).invoke(rowObj);
                if (v instanceof List) {
                  cells = (List<?>) v;
                  break;
                }
              } catch (Exception ignore) {}
            }
            if (cells == null) {
              try {
                Object single = rowObj.getClass().getMethod("get", int.class).invoke(rowObj, columnIndex);
                java.util.List<Object> tmp = new java.util.ArrayList<>();
                tmp.add(single);
                cells = tmp;
                columnIndex = 0;
              } catch (Exception ex) {
                throw new RuntimeException("Unsupported Nebula ResultSet row representation: " + rowObj.getClass(), ex);
              }
            }
          }

          Object cell = cells.get(columnIndex);
          String s = null;
          boolean isNull = false;
          String[] nullCheckMethods = {"isNull", "isNullValue"};
          for (String m : nullCheckMethods) {
            try {
              Object r = cell.getClass().getMethod(m).invoke(cell);
              if (r instanceof Boolean && (Boolean) r) {
                isNull = true;
                break;
              }
            } catch (Exception ignore) {}
          }
          if (!isNull) {
            try {
              s = (String) cell.getClass().getMethod("asString").invoke(cell);
            } catch (NoSuchMethodException e2) {
              try {
                s = (String) cell.getClass().getMethod("getString").invoke(cell);
              } catch (NoSuchMethodException e3) {
                s = String.valueOf(cell);
              } catch (Exception innerGetString) {
                LOG.debug("Nebula cell getString invocation failed: {}", innerGetString.getMessage());
              }
            } catch (java.lang.reflect.InvocationTargetException ite) {
              Throwable cause = ite.getCause();
              if (cause != null && cause.getMessage() != null && cause.getMessage().toLowerCase().contains("type is null")) {
                isNull = true;
              } else {
                LOG.debug("Nebula cell asString invocation error (will fallback): {}", cause == null ? ite.getMessage() : cause.getMessage());
              }
            } catch (Exception generic) {
              LOG.debug("Nebula cell asString unexpected error: {}", generic.getMessage());
            }
          }
          if (isNull || s == null || s.equalsIgnoreCase("null")) {
            out.add(null);
          } else {
            out.add(s);
          }
        } catch (ReflectiveOperationException re) {
          throw new RuntimeException("Unable to read Nebula ResultSet row/column via reflection", re);
        }
      }
      return out;
    }

    @Override
    public void close() {
      closeQuietly(session, pool);
    }

    private static void closeQuietly(Session session, NebulaPool pool) {
      try {
        if (session != null) {
          session.release();
        }
      } catch (Exception ignored) {
        // ignore close exceptions
      } finally {
        try {
          if (pool != null) {
            pool.close();
          }
        } catch (Exception ignored) {
          // ignore close exceptions
        }
      }
    }

  }

}
