using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading.Tasks;
using Airbyte.Cdk.Sources.Utils;
using Spectre.Console;
using CliWrap;
using HandlebarsDotNet;

namespace Airbyte.Cdk
{
    public static class InitCli
    {
        private static string Check = "[bold gray]CHECK[/] ";
        private static string Error = "[bold red]ERROR[/] ";
        private static string Progress = "[bold green]PROGRESS[/] ";
        private static string SourceConnectorType = "";

        public static async Task Process()
        {
            try
            {
                Spinner spinner = Spinner.Known.BouncingBar;
                await AnsiConsole.Status()
                    .Spinner(spinner)
                    .StartAsync("Validating prerequisites...", async ctx =>
                    {

                        await CheckDotnet();
                        await CheckDocker();
                    });

                string connectorname = AnsiConsole.Ask<string>("Connector name:");
                connectorname = connectorname.ToSnakeCase().Replace(" ", "-").ToLower();
                var connectortype = AnsiConsole.Prompt(
                    new SelectionPrompt<string>()
                        .Title("What kind of connector are you building")
                        .PageSize(3)
                        .AddChoices("source-dotnet-http-api", "source-dotnet-generic", "destination-dotnet-generic"));

                //TODO: We only support template for source for now
                if (connectortype != "source-dotnet-http-api")
                {
                    ToConsole(Error, $"Only supporting source-http connectors for now. " +
                                     $"Please check the connector source code for implementing a {connectortype} connector.");
                    return;
                }
                SourceConnectorType = connectortype;

                var location = Path.Combine(MoveToUpperPath(Assembly.GetExecutingAssembly().Location, 7, true), "airbyte-integrations", "connectors", $"{connectortype.Split('-')[0]}-{connectorname}");
                if (location.Any(Path.GetInvalidPathChars().Contains))
                    throw new Exception($"Path is invalid: " + location);
                if (!AnsiConsole.Confirm("Is this destination correct? " + location))
                    return;

                var dir = Directory.CreateDirectory(location);

                await AnsiConsole.Status()
                    .Spinner(spinner)
                    .StartAsync("Creating project...", async ctx =>
                    {
                        var proj = await CreateDotnetProject(dir, connectorname);
                        var tst = await CreateDotnetProject(dir, connectorname, true);
                        await AddDepdendency(dir, connectorname, "Flurl");
                        await AddDepdendency(dir, connectorname, "Flurl.Http");
                        await AddDepdendency(dir, connectorname, "Airbyte.Cdk");
                        await CreateSolutionFile(dir, proj, tst);
                        await AddGitIgnore(dir);
                        AddChangelog(dir, connectorname);
                        AddDockerFile(dir, connectorname);
                        AddSchemasFolder(dir);
                        AddAndReplaceDefaultFile(dir, connectorname);
                        await TryAndBuildResult(dir, connectorname);
                    });

                ToConsole("[bold green]DONE[/]", " Happy programming ", Emoji.Known.SmilingFace);

            }
            catch (Exception e)
            {
                e = e.InnerException ?? e;
                ToConsole(Error, e.Message);
            }
        }

        private static string MoveToUpperPath(string path, int level, bool removefilename = false)
        {
            for (int i = 0; i < level; i++)
                path = Path.Combine(Path.GetDirectoryName(path), removefilename ? "" : Path.GetFileName(path));

            return path;
        }

        private static void AddSchemasFolder(DirectoryInfo dir)
        {
            string step = "Adding schema's folder...";
            ToConsole(Progress, step);
            Directory.CreateDirectory(Path.Combine(dir.FullName, "schemas"));
            ToConsole(Progress, step, Emoji.Known.CheckMark);
        }

        private static async Task CreateSolutionFile(DirectoryInfo dir, params string[] proj)
        {
            string step = $"Adding solution file...";
            ToConsole(Progress, step);
            var stdOutBuffer = new StringBuilder();
            var cmd = Cli.Wrap("dotnet")
                .WithWorkingDirectory(dir.FullName)
                .WithArguments(new[] { "new", "sln" }) | stdOutBuffer;
            await cmd.ExecuteAsync();

            foreach (var p in proj)
            {
                cmd = Cli.Wrap("dotnet")
                    .WithWorkingDirectory(dir.FullName)
                    .WithArguments(new[] { "sln", "add", p }) | stdOutBuffer;
                await cmd.ExecuteAsync();
            }

            if (stdOutBuffer.ToString().Contains("added to the solution"))
                ToConsole(Progress, step, Emoji.Known.CheckMark);
            else
                throw new Exception("Could not create dotnet solution due to error: \n" + stdOutBuffer);
        }

        private static async Task AddGitIgnore(DirectoryInfo dir)
        {
            string step = $"Adding gitignore...";
            ToConsole(Progress, step);
            var stdOutBuffer = new StringBuilder();
            var cmd = Cli.Wrap("dotnet")
                .WithWorkingDirectory(dir.FullName)
                .WithArguments(new[] { "new", "gitignore" }) | stdOutBuffer;

            await cmd.ExecuteAsync();

            if (stdOutBuffer.ToString().Contains("successfully"))
                ToConsole(Progress, step, Emoji.Known.CheckMark);
            else
                throw new Exception("Could not create dotnet project due to error: \n" + stdOutBuffer);
        }

        private static string ConnectorTemplateFolder(DirectoryInfo dir) => Path.Combine(MoveToUpperPath(dir.FullName, 2, true),
            "connector-templates", SourceConnectorType);

        private static string ToUpperFirstString(string input) =>
            $"{char.ToUpper(input[0])}{input.Substring(1)}";

        private static void AddDockerFile(DirectoryInfo dir, string connectorname)
        {
            var source = Path.Combine(ConnectorTemplateFolder(dir), "Dockerfile.hbs");
            var target = Path.Combine(dir.FullName, "Dockerfile");
            string step = $"Adding dockerfile...";
            ToConsole(Progress, step);
            if (!File.Exists(source))
                throw new Exception("Could not find file" + source);

            var template = Handlebars.Compile(File.ReadAllText(source));
            File.WriteAllText(target, template(new
            {
                dashname = connectorname.Replace(" ", "-").Replace("-", "_"),
                snakename = connectorname.ToSnakeCase().Replace("_", "-")
            }));

            if (File.Exists(target))
                ToConsole(Progress, step, Emoji.Known.CheckMark);
            else
                throw new Exception("Could not create dockerfile");
        }

        private static void AddChangelog(DirectoryInfo dir, string connectorname)
        {
            var source = Path.Combine(ConnectorTemplateFolder(dir), "CHANGELOG.md.hbs");
            var target = Path.Combine(dir.FullName, "CHANGELOG.md");
            string step = $"Adding default CHANGELOG...";
            ToConsole(Progress, step);
            if (!File.Exists(source))
                throw new Exception("Could not find file" + source);

            var template = Handlebars.Compile(File.ReadAllText(source));
            File.WriteAllText(target, template(new
            {
                name = connectorname
            }));

            if (File.Exists(target))
                ToConsole(Progress, step, Emoji.Known.CheckMark);
            else
                throw new Exception("Could not create changelog file");
        }

        private static void AddAndReplaceDefaultFile(DirectoryInfo dir, string connectorname)
        {
            var source = Path.Combine(ConnectorTemplateFolder(dir), "Program.cs.hbs");
            var target = Path.Combine(dir.FullName, ToUpperFirstString(connectorname), "Program.cs");
            string step = $"Adding default Program.cs...";
            ToConsole(Progress, step);
            if (!File.Exists(source))
                throw new Exception("Could not find file" + source);

            File.Delete(target);
            var template = Handlebars.Compile(File.ReadAllText(source));
            File.WriteAllText(target, template(new
            {
                snakename = ToUpperFirstString(connectorname.ToSnakeCase().Replace("-", "_"))
            }));

            if (File.Exists(target))
                ToConsole(Progress, step, Emoji.Known.CheckMark);
            else
                throw new Exception("Could not create main file");
        }

        private static async Task TryAndBuildResult(DirectoryInfo dir, string name)
        {
            string step = $"Building and testing result...";
            ToConsole(Progress, step);
            var stdOutBuffer = new StringBuilder();
            var cmd = Cli.Wrap("docker")
                .WithWorkingDirectory(dir.FullName)
                .WithValidation(CommandResultValidation.None)
                .WithStandardOutputPipe(PipeTarget.ToStringBuilder(stdOutBuffer))
                .WithStandardErrorPipe(PipeTarget.ToStringBuilder(stdOutBuffer))
                .WithArguments(new[] { "build", ".", "-t", "local" });
            await cmd.ExecuteAsync();

            if (stdOutBuffer.ToString().Contains("exporting to image"))
                ToConsole(Progress, step, Emoji.Known.CheckMark);
            else
                throw new Exception("Could not build resulting docker image due to error");
        }

        private static async Task AddDepdendency(DirectoryInfo dir, string project, string nuget)
        {
            string step = $"Adding dependency {nuget}...";
            string path = Path.Combine(dir.FullName, project);
            ToConsole(Progress, step);
            var stdOutBuffer = new StringBuilder();
            var cmd = Cli.Wrap("dotnet")
                .WithWorkingDirectory(path)
                .WithArguments(new[] { "add", "package", nuget }) | stdOutBuffer;
            await cmd.ExecuteAsync();

            if (stdOutBuffer.ToString().Contains("Restored"))
                ToConsole(Progress, step, Emoji.Known.CheckMark);
            else
                throw new Exception("Could not create dotnet project due to error: \n" + stdOutBuffer);
        }

        private static async Task<string> CreateDotnetProject(DirectoryInfo dir, string name, bool istestproject = false)
        {
            name = istestproject ? name + ".Tests" : name;
            name = ToUpperFirstString(name);
            string step = istestproject ? $"Creating test project ({name})..." : $"Creating project ({name})...";
            var workingdir = Directory.CreateDirectory(Path.Combine(dir.FullName, name));
            string dotnettype = istestproject ? "xunit" : "console";
            ToConsole(Progress, step);
            var stdOutBuffer = new StringBuilder();
            var cmd = Cli.Wrap("dotnet")
                .WithWorkingDirectory(workingdir.FullName)
                .WithArguments(new[] { "new", dotnettype }) | stdOutBuffer;
            await cmd.ExecuteAsync();

            if (stdOutBuffer.ToString().Contains("succeeded"))
                ToConsole(Progress, step, Emoji.Known.CheckMark);
            else
                throw new Exception("Could not create dotnet project due to error: \n" + stdOutBuffer);

            return workingdir.FullName;
        }

        private static async Task CheckDotnet()
        {
            ToConsole(Check, "Validating dotnet...");
            var stdOutBuffer = new StringBuilder();
            var cmd = Cli.Wrap("dotnet").WithArguments("--version") | stdOutBuffer;
            await cmd.ExecuteAsync();
            if (Version.TryParse(stdOutBuffer.ToString(), out var v) && v.Major >= 5)
                ToConsole(Check, "Found dotnet version: ", v.ToString(), " ", Emoji.Known.CheckMark);
            else if (v?.Major < 5)
            {
                ToConsole(Check, "Validating dotnet...", Emoji.Known.CrossMark);
                throw new Exception($"Your dotnet version is out of date, please download the latest version at: https://dotnet.microsoft.com/download");
            }
            else
            {
                ToConsole(Check, "Validating dotnet...", Emoji.Known.CrossMark);
                throw new Exception("Could not find dotnet, please download at: https://dotnet.microsoft.com/download");
            }
        }

        private static async Task CheckDocker()
        {
            ToConsole(Check, "Validating Docker...");
            var stdOutBuffer = new StringBuilder();
            var cmd = Cli.Wrap("docker").WithArguments("--version") | stdOutBuffer;
            await cmd.ExecuteAsync();
            if (Version.TryParse(stdOutBuffer.ToString().Replace("Docker version", "").Split(",")[0], out var v))
                ToConsole(Check, "Found docker version: ", v.ToString(), Emoji.Known.CheckMark);
            else
            {
                ToConsole(Check, "Validating Docker...", Emoji.Known.CrossMark);
                throw new Exception("Could not find docker, please download at: https://docs.docker.com/get-docker/");
            }
        }

        private static void ToConsole(params string[] lines) => AnsiConsole.MarkupLine(string.Concat(lines));
    }
}
