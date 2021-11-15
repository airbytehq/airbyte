using System.Collections.Generic;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Airbyte.Cdk.Models
{
    public class AirbyteStream
    {
        /// <summary>
        /// Stream's name.
        /// </summary>
        [JsonPropertyName("name")]
        public string Name { get; set; }

        /// <summary>
        /// Stream schema using Json Schema specs.
        /// </summary>
        [JsonPropertyName("json_schema")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingDefault)]
        public JsonElement JsonSchema { get; set; }

        [JsonPropertyName("supported_sync_modes")]
        public SyncMode[]? SupportedSyncModes { get; set; }

        /// <summary>
        /// If the source defines the cursor field, then any other cursor field inputs will be ignored. If it does not, either the user_provided one is used, or the default one is used as a backup.
        /// </summary>
        [JsonPropertyName("source_defined_cursor")]
        public bool? SourceDefinedCursor { get; set; }

        /// <summary>
        /// Path to the field that will be used to determine if a record is new or modified since the last sync. If not provided by the source, the end user will have to specify the comparable themselves.
        /// </summary>
        [JsonPropertyName("default_cursor_field")]
        public string[]? DefaultCursorField { get; set; }

        /// <summary>
        /// If the source defines the primary key, paths to the fields that will be used as a primary key. If not provided by the source, the end user will have to specify the primary key themselves.
        /// </summary>
        [JsonPropertyName("source_defined_primary_key")]
        public List<List<string>>? SourceDefinedPrimaryKey { get; set; }

        /// <summary>
        /// Optional Source-defined namespace. Currently only used by JDBC destinations to determine what schema to write to. Airbyte streams from the same sources should have the same namespace.
        /// </summary>
        [JsonPropertyName("namespace")]
        public string? Namespace { get; set; }
    }
}