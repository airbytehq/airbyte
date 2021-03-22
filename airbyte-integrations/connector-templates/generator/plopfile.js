'use strict';
const path = require('path');

const getSuccessMessage = function(connectorName, outputPath, additionalMessage){
    return `
🚀 🚀 🚀 🚀 🚀 🚀

Success! 

Your ${connectorName} connector has been created at ${path.resolve(outputPath)}.

Follow instructions in NEW_SOURCE_CHECKLIST.md to finish your connector.

Questions, comments, or concerns? Let us know at:
Slack: https://slack.airbyte.io
Github: https://github.com/airbytehq/airbyte

We're always happy to provide you with any support :)

${additionalMessage || ""}
`
}

module.exports = function (plop) {
  const pythonSourceInputRoot = '../source-python';
  const singerSourceInputRoot = '../source-singer';
  const genericSourceInputRoot = '../source-generic';

  const outputDir = '../../connectors';
  const pythonSourceOutputRoot = `${outputDir}/source-{{dashCase name}}`;
  const singerSourceOutputRoot = `${outputDir}/source-{{dashCase name}}-singer`;
  const genericSourceOutputRoot = `${outputDir}/source-{{dashCase name}}`;

  plop.setActionType('emitSuccess', function(answers, config, plopApi){
      console.log(getSuccessMessage(answers.name, plopApi.renderString(config.outputPath, answers), config.message));
  });

  plop.setGenerator('source-python', {
    description: 'Generate an Airbyte Source written in Python',
    prompts: [{type: 'input', name: 'name', message: 'Source name, without the "source-" prefix e.g: "google-analytics"'}],
    actions: [
         {
         abortOnFail: true,
         type:'addMany',
         destination: pythonSourceOutputRoot,
         base: pythonSourceInputRoot,
         templateFiles: `${pythonSourceInputRoot}/**/**`,
       },
         // plop doesn't add dotfiles by default so we manually add them
       {
         type:'add',
         abortOnFail: true,
         templateFile: `${pythonSourceInputRoot}/.gitignore.hbs`,
         path: `${pythonSourceOutputRoot}/.gitignore`
       },
       {
         type:'add',
         abortOnFail: true,
         templateFile: `${pythonSourceInputRoot}/.dockerignore.hbs`,
         path: `${pythonSourceOutputRoot}/.dockerignore`
       },
      {type: 'emitSuccess', outputPath: pythonSourceOutputRoot, message: "For a checklist of what to do next go to https://docs.airbyte.io/tutorials/building-a-python-source"}]
  });

  plop.setGenerator('source-python-singer', {
    description: 'Generate an Airbyte Source written on top of a Singer Tap.',
    prompts: [
      {type: 'input', name: 'name', message: 'Source name, without the "source-" prefix e.g: "google-analytics"', filter: function (name) {
        return name.endsWith('-singer') ? name.replace(/-singer$/, '') : name;
      }},
       {type: 'input', name: 'tap_name', message: 'Singer tap package'},
    ],
    actions: [
       {
         abortOnFail: true,
         type:'addMany',
         destination: singerSourceOutputRoot,
         base: singerSourceInputRoot,
         templateFiles: `${singerSourceInputRoot}/**/**`,
       },
       {
         type:'add',
         abortOnFail: true,
         templateFile: `${singerSourceInputRoot}/.gitignore.hbs`,
         path: `${singerSourceOutputRoot}/.gitignore`
       },
       {
         type:'add',
         abortOnFail: true,
         templateFile: `${singerSourceInputRoot}/.dockerignore.hbs`,
         path: `${singerSourceOutputRoot}/.dockerignore`
       },
        {type: 'emitSuccess', outputPath: singerSourceOutputRoot},
    ]
  });

  plop.setGenerator('source-generic', {
      description: 'Use if none of the other templates apply to your use case.',
      prompts: [{type: 'input', name: 'name', message: 'Source name, without the "source-" prefix e.g: "google-analytics"'}],
      actions: [
        {
          abortOnFail: true,
          type:'addMany',
          destination: genericSourceOutputRoot,
          base: genericSourceInputRoot,
          templateFiles: `${genericSourceInputRoot}/**/**`,
        },
        {
          type:'add',
          abortOnFail: true,
          templateFile: `${genericSourceInputRoot}/.gitignore.hbs`,
          path: `${genericSourceOutputRoot}/.gitignore`
        },
          {type: 'emitSuccess', outputPath: genericSourceOutputRoot}
      ]
    });
};
