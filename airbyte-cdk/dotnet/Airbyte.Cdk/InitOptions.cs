using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using CommandLine;

namespace Airbyte.Cdk
{
    [Verb("init", HelpText = "Initialize a dotnet new connector")]
    public class InitOptions : Options
    {

    }
}
