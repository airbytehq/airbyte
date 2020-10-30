'use strict';
const fs = require('fs');
const path = require('path');

module.exports = function (plop) {
  const singerSourceInputRoot = '../source-singer';

  const outputDir = '../../connectors';
  const singerSourceOutputRoot = `${outputDir}/source-{{dashCase name}}-singer`;

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
  plop.setGenerator('Singer-based Python Source', {
    description: 'Generate an Airbyte Source written on top of a Singer Tap.',
    prompts: [{type: 'input', name: 'name', message: 'Source name, without the "source-" prefix e.g: "google-analytics"'}],
    actions: [
      {
        abortOnFail: true,
        type:'addMany',
        destination: singerSourceOutputRoot,
        base: singerSourceInputRoot,
        templateFiles: `${singerSourceInputRoot}/**/**`,
        globOptions: {ignore:'.secrets'}
      },
      {
        type:'add',
        abortOnFail: true,
        templateFile: `${singerSourceInputRoot}/.secrets/credentials.json.hbs`,
        path: `${singerSourceOutputRoot}/secrets/credentials.json`
      },
      function(answers, config, plop){
        const renderedOutputDir = plop.renderString(singerSourceOutputRoot, answers);
        const basesDir = path.resolve(__dirname, '../../bases');
        fs.symlinkSync(`${basesDir}/base-python/base_python`, `${renderedOutputDir}/base_python`);
        fs.symlinkSync(`${basesDir}/airbyte-protocol/airbyte_protocol`, `${renderedOutputDir}/airbyte_protocol`);
        fs.symlinkSync(`${basesDir}/base-singer/base_singer`, `${renderedOutputDir}/base_singer`);
      },
      'Your new Singer-based source connector has been created. Follow the instructions and TODOs in the newly created package for next steps. Happy coding! 🐍🐍',
    ]
  });
};
