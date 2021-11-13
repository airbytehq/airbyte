using System;

namespace Airbyte.Cdk.Sources.Utils
{
    public class DynamicProperty
    {
        public string Signature { get; set; }
        public Type FType { get; set; }
        public object Value { get; set; }
    }

    public class DynamicMethod
    {
        public string Signature { get; set; }
        public object Body { get; set; }
    }
}
