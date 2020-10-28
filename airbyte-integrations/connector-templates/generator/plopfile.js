module.exports = function (plop) {
  plop.setGenerator('java-destination', {
    description: 'generate java destination',
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
        path: '../../connectors/destination-{{dashCase name}}/build.gradle',
        templateFile: '../java-destination/build.gradle.hbs',
      },
      {
        type: 'add',
        path: '../../connectors/destination-{{dashCase name}}/src/main/java/io/airbyte/integrations/destination/{{snakeCase name}}/{{properCase name}}Destination.java',
        templateFile: '../java-destination/Destination.java.hbs',
      },
      {
        type: 'add',
        path: '../../connectors/destination-{{dashCase name}}/Dockerfile',
        templateFile: '../java-destination/Dockerfile.hbs',
      },
      {
        type: 'add',
        path: '../../connectors/destination-{{dashCase name}}/.dockerignore',
        templateFile: '../java-destination/.dockerignore.hbs',
      },
      {
        type: 'add',
        path: '../../connectors/destination-{{dashCase name}}/spec.json',
        templateFile: '../java-destination/spec.json.hbs',
      },
      'Your new connector has been created. Happy coding~~',
    ],
  });
};
