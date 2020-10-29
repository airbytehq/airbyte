module.exports = function (plop) {
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
        templateFile: '../java-destination/build.gradle.hbs',
      },
      {
        type: 'add',
        path: `${javaDestinationOutputRoot}/src/main/java/io/airbyte/integrations/destination/{{snakeCase name}}/{{properCase name}}Destination.java`,
        templateFile: '../java-destination/Destination.java.hbs',
      },
      {
        type: 'add',
        path: `${javaDestinationOutputRoot}/Dockerfile`,
        templateFile: '../java-destination/Dockerfile.hbs',
      },
      {
        type: 'add',
        path: `${javaDestinationOutputRoot}/.dockerignore`,
        templateFile: '../java-destination/.dockerignore.hbs',
      },
      {
        type: 'add',
        path: `${javaDestinationOutputRoot}/spec.json`,
        templateFile: '../java-destination/spec.json.hbs',
      },
      'Your new connector has been created. Happy coding~~',
    ],
  });
  plop.setGenerator('Python Source', {
    description: 'Generate an Airbyte Source written in Python',
    prompts: [

    ],
    actions: [
      {type: 'add', 'path'}
      'Your new connector has been created. Happy coding~~',
    ]
  });
};
