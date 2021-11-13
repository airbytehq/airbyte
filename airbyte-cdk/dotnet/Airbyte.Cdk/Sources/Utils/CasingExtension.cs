using System.Linq;

namespace Airbyte.Cdk.Sources.Utils
{
    public static class CasingExtension
    {
        public static string ToSnakeCase(this string str) => 
            string.Concat((str ?? string.Empty).Select((x, i) => i > 0 && char.IsUpper(x) && !char.IsUpper(str[i - 1]) ? $"_{x}" : x.ToString())).ToLower();
    }
}
