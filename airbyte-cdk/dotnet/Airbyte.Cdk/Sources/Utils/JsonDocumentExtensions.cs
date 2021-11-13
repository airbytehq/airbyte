using System.Text.Json;

namespace Airbyte.Cdk.Sources.Utils
{
    public static class JsonDocumentExtensions
    {
        public static T ToType<T>(this JsonDocument json)
        {
            try
            {
                return JsonSerializer.Deserialize<T>(json.RootElement.GetRawText());
            }
            catch
            {
                // ignored
            }

            return default;
        }

        public static JsonDocument AsJsonDocument(this object obj) => 
            JsonDocument.Parse(JsonSerializer.Serialize(obj));

        public static JsonDocument AsJsonDocument(this string str) =>
            JsonDocument.Parse(str);
    }
}
