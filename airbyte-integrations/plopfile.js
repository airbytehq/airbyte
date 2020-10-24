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
        path: 'connectors/destination-test/build.gradle',
        templateFile: 'connector-templates/java-destination/build.gradle.hbs',
      },
		  {
		    type: 'add',
		    path: 'connectors/destination-{{dashCase name}}/src/main/java/io/airbyte/integrations/destination/{{snakeCase name}}/{{properCase name}}Destination.java',
		    templateFile: 'connector-templates/java-destination/Destination.java.hbs',
		  },
		  {
        type: 'add',
        path: 'connectors/destination-{{dashCase name}}/Dockerfile',
        templateFile: 'connector-templates/java-destination/Dockerfile.hbs',
      },
      {
        type: 'add',
        path: 'connectors/destination-{{dashCase name}}/.dockerignore',
        templateFile: 'connector-templates/java-destination/.dockerignore.hbs',
      },
      {
        type: '`add',
        path: 'connectors/destination-{{dashCase name}}/spec.json',
        templateFile: 'connector-templates/java-destination/spec.json.hbs',
      },
		],
	});
};
