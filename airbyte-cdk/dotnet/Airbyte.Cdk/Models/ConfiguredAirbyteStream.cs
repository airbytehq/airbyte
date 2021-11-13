using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace Airbyte.Cdk.Models
{
    public class ConfiguredAirbyteStream
    {
        [JsonPropertyName("stream")]
        public AirbyteStream Stream { get; set; }

        [JsonPropertyName("sync_mode")]
        public SyncMode SyncMode { get; set; }

        /// <summary>
        /// Path to the field that will be used to determine if a record is new or modified since the last sync. This field is REQUIRED if `sync_mode` is `incremental`. Otherwise it is ignored.
        /// </summary>
        [JsonPropertyName("cursor_field")]
        public string[] CursorField { get; set; }

        [JsonPropertyName("destination_sync_mode")]
        public DestinationSyncMode DestinationSyncMode { get; set; }

        /// <summary>
        /// Paths to the fields that will be used as primary key. This field is REQUIRED if `destination_sync_mode` is `*_dedup`. Otherwise it is ignored.
        /// </summary>
        [JsonPropertyName("primary_key")]
        public List<List<string>>? PrimaryKey { get; set; }
    }
}