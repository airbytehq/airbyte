using System.Text.Json;

namespace Airbyte.Cdk.Sources.Utils
{
    public static class JsonDocumentExtensions
    {
        public static T ToType<T>(this JsonElement json)
        {
            try
            {
                return JsonSerializer.Deserialize<T>(json.GetRawText());
            }
            catch
            {
                // ignored
            }

            return default;
        }

        public static JsonElement AsJsonElement(this object obj) =>
            JsonDocument.Parse(JsonSerializer.Serialize(obj)).RootElement.Clone();

        public static JsonElement AsJsonElement(this string str) =>
            (string.IsNullOrWhiteSpace(str) ? JsonDocument.Parse("{}") : JsonDocument.Parse(str)).RootElement.Clone();
    }
}
