
const fs = require('fs');
const path = require('path');
// read names of all directories in the current directory
const dirs = fs.readdirSync('.', { withFileTypes: true }).filter(dirent => dirent.isDirectory()).map(dirent => dirent.name)
  // strip all but the directory name
  .map(name => name.split('/').pop())
  // filter out node_modules
  .filter(name => name !== 'node_modules')

const results = {}


dirs.slice(0).forEach(dir => {
  getMostRecentCommitDate(path.join(__dirname, dir))
})

// function that takes a path, exec git log command for that path and grab the date of the most recent comment output
function getMostRecentCommitDate(name) {
  const { exec } = require('child_process');
  let str = `
  git log --reverse -- ${name} | awk 'NR>1 {print last} {last=$0}; /^commit/ && ++c==2{exit}'
  `
  console.log(str)
  // exec the string but silence stdout and stderr


  exec(str, { stdio: 'ignore' }, (err, stdout, stderr) => {
    if (err) {
      // node couldn't execute the command
      return;
    }
    // extract the date from the git log output
    try {
      const date = stdout.split('Date:')[1].split('+')[0].split('-')[0].trim()
      // convert to javascript date, yyyy-mm-dd
      const jsDate = new Date(date).toISOString().split('T')[0]
      name = name.split('/').pop()


      // parse name to see if source or destination
      const type = name.startsWith('source') ? 'source' : 'destination'

      // open results.json
      const results = JSON.parse(fs.readFileSync('git2json.json', 'utf8'))
      // save name, date and type to results.json
      results[name] = { date: jsDate, type }
      fs.writeFileSync('git2json.json', JSON.stringify(results, null, 2))


    } catch (err) {
      console.log('error parsing name', name)
      console.log('error parsing stdout', stdout)
      console.log(err)
    }

  })
}
