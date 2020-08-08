package io.dataline.conduit.server;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.networknt.schema.*;
import io.dataline.conduit.conduit_config.StandardScheduleConfiguration;

import java.io.File;
import java.io.IOException;
import java.util.Set;

public class ValidateJson {
  public static void main(String[] args) throws IOException {

    //    ObjectMapper objectMapper = new ObjectMapper();
    //    File schemaFile = new File("/Users/charles/code/conduit/sampleSchema.json");
    //    JsonNode jsonNodeSchema = objectMapper.readTree(schemaFile);
    //
    //    File validObjectFile = new File("/Users/charles/code/conduit/validObject.json");
    //    JsonNode jsonNoteValidObject = objectMapper.readTree(validObjectFile);
    //
    //    File invalidObjectFile = new File("/Users/charles/code/conduit/invalidObject.json");
    //    JsonNode jsonNoteInvalidObject = objectMapper.readTree(invalidObjectFile);
    //
    //    SchemaValidatorsConfig config = new SchemaValidatorsConfig();
    //    config.setTypeLoose(false);
    //    JsonSchema jsonSchema =
    //        JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V7).getSchema(jsonNodeSchema,
    // config);
    //
    //    Set<ValidationMessage> validateValid = jsonSchema.validate(jsonNoteValidObject);
    //    System.out.println("validateValid = " + validateValid);
    //
    //    Set<ValidationMessage> validateInvalid = jsonSchema.validate(jsonNoteInvalidObject);
    //    System.out.println("validateInvalid = " + validateInvalid);

    // schema

    ObjectMapper objectMapper2 = new ObjectMapper();
    SchemaValidatorsConfig config2 = new SchemaValidatorsConfig();
    File scheduleSchemaFile =
        new File(
            "/Users/charles/code/conduit/conduit-config/src/main/resources/json/StandardScheduleConfiguration.json");
    JsonNode scheduleSchema = objectMapper2.readTree(scheduleSchemaFile);
    System.out.println("scheduleSchema = " + scheduleSchema);
    System.out.println("config2 = " + config2);
    config2.setTypeLoose(false);
    JsonSchemaFactory instance = JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V7);
    JsonSchema jsonScheduleSchema = instance.getSchema(scheduleSchema, config2);

    File scheduleObjectFile = new File("/Users/charles/code/conduit/scheduleObject.json");

    JsonNode jsonScheduleObject = objectMapper2.readTree(scheduleObjectFile);
    Set<ValidationMessage> validateSchedule = jsonScheduleSchema.validate(jsonScheduleObject);
    System.out.println("validateSchedule = " + validateSchedule);

    StandardScheduleConfiguration scheduleObject =
        objectMapper2.readValue(scheduleObjectFile, StandardScheduleConfiguration.class);
    System.out.println("scheduleObject = " + scheduleObject);
  }
}
