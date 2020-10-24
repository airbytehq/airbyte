module.exports = function (plop) {
	plop.setGenerator('java-destination', {
		description: 'generate java destination',
		prompts: [
		  {
        type: 'input',
			  name: 'name',
			  message: 'name of the destination connector (e.g. "big query")'
		  },
		],
		actions: [
		  'Happy coding!',
		],
	});
};
