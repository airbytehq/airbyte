using System;
using System.IO;
using System.Text.Json;
using Airbyte.Cdk.Models;
using Json.Schema;

namespace Airbyte.Cdk.Sources.Utils
{
    public class ResourceSchemaLoader
    {
        public static bool TryCheckConfigAgainstSpecOrExit(JsonDocument config, ConnectorSpecification spec,
            out Exception exc)
            => VerifySchema(config, JsonSchema.FromText(spec.ConnectionSpecification.RootElement.GetRawText()), out exc);

        public ResourceSchemaLoader(string filename) => FileName = filename;
        public string FileName { get; }

        public JsonSchema GetSchema()
        {
            string path = Path.Join(Path.GetDirectoryName(AirbyteEntrypoint.AirbyteImplPath), "schemas", FileName + ".json");
            if (!File.Exists(path))
                throw new FileNotFoundException($"Could not find schema file [{FileName}]: {path}");

            return JsonSchema.FromFile(path);
        }

        public static bool VerifySchema(JsonElement jsonElement, JsonSchema schema, out Exception exc)
        {
            var result = schema.Validate(jsonElement, new ValidationOptions { OutputFormat = OutputFormat.Detailed });
            exc = !result.IsValid ? new Exception(result.Message) : null;
            return result.IsValid;
        }

        public static bool VerifySchema(JsonDocument jsonDocument, JsonSchema schema, out Exception exc)
            => VerifySchema(jsonDocument.RootElement, schema, out exc);
    }
}
