module.exports = function (plop) {
  const javaDestinationInputRoot = '../java-destination'
  const pythonSourceInputRoot = '../source-python'


  const outputDir = '../../connectors';
  const javaDestinationOutputRoot = `${outputDir}/destination-{{dashCase name}}`
  const pythonSourceOutputRoot = `${outputDir}/source-{{dashCase name}}`
  const singerSourceOutputRoot = `${outputDir}/source-{{dashCase name}}-singer`

  plop.setGenerator('Java Destination', {
    description: 'Generate an Airbyte destination written in Java',
    prompts: [
      {
        type: 'input',
        name: 'name',
        message: 'destination name (without the "destination" suffix; e.g. "my sql")'
      }
    ],
    actions: [
      {
        type: 'add',
        path: `${javaDestinationOutputRoot}/build.gradle`,
        templateFile: `${javaDestinationInputRoot}/build.gradle.hbs`,
      },
      {
        type: 'add',
        path: `${javaDestinationOutputRoot}/src/main/java/io/airbyte/integrations/destination/{{snakeCase name}}/{{properCase name}}Destination.java`,
        templateFile: `${javaDestinationInputRoot}/Destination.java.hbs`,
      },
      {
        type: 'add',
        path: `${javaDestinationOutputRoot}/Dockerfile`,
        templateFile: `${javaDestinationInputRoot}/Dockerfile.hbs`,
      },
      {
        type: 'add',
        path: `${javaDestinationOutputRoot}/.dockerignore`,
        templateFile: `${javaDestinationInputRoot}/.dockerignore.hbs`,
      },
      {
        type: 'add',
        path: `${javaDestinationOutputRoot}/spec.json`,
        templateFile: `${javaDestinationInputRoot}/spec.json.hbs`,
      },
      'Your new connector has been created. Happy coding~~',
    ],
  });
  plop.setGenerator('Python Source', {
    description: 'Generate an Airbyte Source written in Python',
    prompts: [{type: 'input', name: 'name', message: 'Source name, without the "source-" prefix e.g: "google-analytics"'}],
    actions: [
      {
        abortOnFail: true,
        type:'addMany',
        destination: pythonSourceOutputRoot,
        base: pythonSourceInputRoot,
        templateFiles: `${pythonSourceInputRoot}/**/**`
      },
      'Your new Python source connector has been created. Follow the instructions and TODOs in the newly created package for next steps. Happy coding! 🐍🐍',
    ]
  });
};
