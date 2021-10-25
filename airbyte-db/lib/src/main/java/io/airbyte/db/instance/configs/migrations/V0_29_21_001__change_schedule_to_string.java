/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;

public class V0_29_21_001__change_schedule_to_string extends BaseJavaMigration {

  static String cronFor(String timeUnit, int units) {
    var cron = switch (timeUnit) {
      case "minutes" -> {
        if (units > 59) {
          yield cronFor("hours", (units + 30) / 60);
        }
        yield String.format("*/%d * * * *", units);
      }
      case "hours" -> {
        if (units > 23) {
          yield cronFor("days", (units + 12) / 24);
        }
        yield String.format("0 */%d * * *", units);
      }
      case "days" -> {
        if (units > 30) {
          yield cronFor("months", (units + 15) / 30);
        }
        yield String.format("0 0 */%d * *", units);
      }
      case "weeks" -> {
        if (units > 4) {
          yield cronFor("months", (units + 2) / 4);
        }
        yield String.format("0 0 */%d * *", units * 7);
      }
      case "months" -> String.format("0 0 * */%d *", Math.min(units, 12));

      default -> "0 0 */1 * *";
    };
    return cron;
  }

  static String cronFor(JsonNode oldSchedule) {
    // oldSchedule is timeUnit and units
    // timeUnit can be minutes, hours, days, weeks or months
    // unit is number
    // We should try to find right granularity before converting to cron.
    // for example 4 weeks could be 1 month, 80 days could be every 2 month and 20 days
    // note that due to nature of cron certain time ranges rounds up to the nearest valid
    var timeUnit = oldSchedule.get("timeUnit");
    var units = oldSchedule.get("units");
    return cronFor(timeUnit == null ? "days" : timeUnit.asText("days"),
        units == null ? 1 : units.asInt(1));
  }

  @Override
  public void migrate(Context context) throws Exception {
    // Warning: please do not use any jOOQ generated code to write a migration.
    // As database schema changes, the generated jOOQ code can be deprecated. So
    // old migration may not compile if there is any generated code.
    var ctx = DSL.using(context.getConnection());
    var syncRecords = ctx.selectFrom(DSL.name("airbyte_configs"))
        .where("config_type = 'STANDARD_SYNC'")
        .fetchArray();
    if (syncRecords != null) {
      for (var syncRecord : syncRecords) {
        var id = syncRecord.getValue(DSL.field(DSL.name("id"), Long.class));
        var configBlob = Jsons.deserialize(syncRecord.getValue(DSL.field(DSL.name("config_blob"), SQLDataType.JSONB)).data(), JsonNode.class);
        if (configBlob.hasNonNull("schedule") && !(configBlob.get("manual").asBoolean(false))) {
          var cronSchedule = cronFor(configBlob.get("schedule"));
          var updatedConfigBlob = (ObjectNode) configBlob;
          updatedConfigBlob.remove("schedule");
          updatedConfigBlob.put("schedule", cronSchedule);
          ctx.update(DSL.table(DSL.name("airbyte_configs")))
              .set(DSL.field(DSL.name("config_blob")), SQLDataType.JSONB.convert(Jsons.serialize(updatedConfigBlob)))
              .where(DSL.field(DSL.name("id")).eq(id))
              .execute();
        }
      }
    }
  }

}
