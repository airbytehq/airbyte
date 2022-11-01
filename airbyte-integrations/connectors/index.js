
const { exec } = require('child_process');


// exec(`
// git log --reverse -- /Users/swyx/Desktop/Work/airbyte/airbyte-integrations/connectors/destination-amazon-sqs | awk 'NR>1 {print last} {last=$0}; /^commit/ && ++c==2{exit}'
// `, (err, stdout, stderr) => {
//   if (err) {
//     // node couldn't execute the command
//     return;
//   }
//   // the *entire* stdout and stderr (buffered)
//   console.log(`stdout: ${stdout}`);
//   console.log(`stderr: ${stderr}`);
// })
// stdout: commit 84b3bf55acff30ee0f571e4b1709b90f0278fdc5
// Author: Alasdair Brown <sdairs@users.noreply.github.com>
// Date:   Thu Dec 9 22:21:51 2021 +0000

//     :tada: Destination Amazon SQS: New connector (#7503)

//     * initial commit, working sending single messages

const fs = require('fs');
const path = require('path');
// read names of all directories in the current directory
const dirs = fs.readdirSync('.', { withFileTypes: true }).filter(dirent => dirent.isDirectory()).map(dirent => dirent.name)
  // strip all but the directory name
  .map(name => name.split('/').pop())
  // filter out node_modules
  .filter(name => name !== 'node_modules')

const results = {}


const yaml = require('js-yaml');
// read from airbyte-config/init/src/main/resources/seed/source_definitions.yaml
const sourceDefinitions = yaml.load(fs.readFileSync(path.join(__dirname, '../../airbyte-config/init/src/main/resources/seed/source_definitions.yaml'), 'utf8'));
const destDefinitions = yaml.load(fs.readFileSync(path.join(__dirname, '../../airbyte-config/init/src/main/resources/seed/destination_definitions.yaml'), 'utf8'));
const definitions = [...sourceDefinitions, ...destDefinitions]
// console.log(sourceDefinitions)
// [
//   {
//     name: 'Monday',
//     sourceDefinitionId: '80a54ea2-9959-4040-aac1-eee42423ec9b',
//     dockerRepository: 'airbyte/source-monday',
//     dockerImageTag: '0.1.4',
//     documentationUrl: 'https://docs.airbyte.com/integrations/sources/monday',
//     icon: 'monday.svg',
//     sourceType: 'api',
//     releaseStage: 'alpha'
//   },
//   {
//     name: 'MongoDb',
//     sourceDefinitionId: 'b2e713cd-cc36-4c0a-b5bd-b47cb8a0561e',
//     dockerRepository: 'airbyte/source-mongodb-v2',
//     dockerImageTag: '0.1.19',
//     documentationUrl: 'https://docs.airbyte.com/integrations/sources/mongodb-v2',
//     icon: 'mongodb.svg',
//     sourceType: 'database',
//     releaseStage: 'alpha'
//   },
//   // ...
// ]


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

      // optional: skip if already have result
      const resultsJson = JSON.parse(fs.readFileSync(path.join(__dirname, 'results.json'), 'utf8'))
      if (resultsJson[name]?.url) return // break out


      // parse name to see if source or destination
      const type = name.startsWith('source') ? 'source' : 'destination'
      // match name with sourceDefinitions by dockerRepository
      const definition = definitions.find(s => s.dockerRepository === `airbyte/${name}`)
      if (!definition) {
        // open errors.json
        const errors = JSON.parse(fs.readFileSync(path.join(__dirname, 'errors.json'), 'utf8'))
        // add the name key under to errors.json
        const myerr = errors[name] || {}
        myerr[1] = 'Error 1: no definition found in definitions.yaml'
        errors[name] = myerr
        console.log(`Error 1: there is a ${name} connector, but no definition found for ${name} in ${type}_definitions.yaml`)
        // write errors.json
        fs.writeFileSync(path.join(__dirname, 'errors.json'), JSON.stringify(errors, null, 2))
      } else {
        if (!definition.icon) {
          // report no icon defined
          console.log(`Error 2: no icon defined for ${name} in ${type}_definitions.yaml`)
          // open errors.json
          const errors = JSON.parse(fs.readFileSync(path.join(__dirname, 'errors.json'), 'utf8'))
          // add the name key under to errors.json
          const myerr = errors[name] || {}
          myerr[2] = 'Error 2: no icon defined in definitions.yaml'
          errors[name] = myerr
          // write errors.json
          fs.writeFileSync(path.join(__dirname, 'errors.json'), JSON.stringify(errors, null, 2))
        } else {
          const iconExists = fs.existsSync(path.join(__dirname, `../../airbyte-config/init/src/main/resources/icons/${definition.icon}`))
          // if icon doesnt exist, delete key and report
          if (!iconExists) {
            console.log(`Error 3: icon defined but NOT FOUND for ${name}!!! bad data!`)
            delete definition.icon
            // open errors.json
            const errors = JSON.parse(fs.readFileSync(path.join(__dirname, 'errors.json'), 'utf8'))
            // add the name key under to errors.json
            const myerr = errors[name] || {}
            myerr[3] = `Error 3: icon defined but NOT FOUND for ${name}!!! bad data!`
            errors[name] = myerr
            // write errors.json
            fs.writeFileSync(path.join(__dirname, 'errors.json'), JSON.stringify(errors, null, 2))
          }
        }
      }

      // web scraping section
      // take name from definitionNname or name variable
      const definitionName = definition?.name || name.split('strict')[0]
        .split('denormalized')[0]
        .split('-').slice(1).join(' ')
      // drop anything after "strict" in the name
      // log name
      // put name into google and get first url result
      const googleUrl = `https://www.google.com/search?q=${definitionName}+data+website`
      // synchronously fetch this url from the google url
      const fetch = require('node-fetch');
      const cheerio = require('cheerio');
      // sleep for random amount of time to avoid google blocking us
      const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
      const randomSleep = Math.floor(Math.random() * 10000) + 500
      sleep(randomSleep).then(() => {
        // fetch the url with chrome user agent
        fetch(googleUrl, {
          headers: {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
          }
        })
          .then(res => res.text())
          .then(body => {
            // scrape the first page of google results for the first search result with the class yuRUbf
            const $ = cheerio.load(body);
            // find the first div with the class yuRUbf
            const firstResult = $('.yuRUbf').first()
            // get the text and href attribute of the first result for url and description
            const url = firstResult.find('a').attr('href')
            // get the full html of the parent of the first result
            const a = $('.IsZvec').first().text()
            const b = $('.Z26q7c').first().text()
            console.log({ a, b })
            // get the description fro the parent of the first result 
            // let description = a.length < b.length ? a : b
            let description = a || b
            // remove url from description
            try {
              description = description.split('https://')[0]
            } catch (e) {
              console.log(e)
            }


            // log 
            console.log(`${definitionName}: ${description} ${url}`)
            // add to results object as scrape key
            const scrape = {
              description,
              url
            }

            // if url is undefined, report error
            if (!url) {
              console.log(`Error 4: no url found for ${definitionName} in google search`)// if url is defined, add it to the results


              // open errors.json
              const errors = JSON.parse(fs.readFileSync(path.join(__dirname, 'errors.json'), 'utf8'))
              // add the name key under to errors.json
              const myerr = errors[name] || {}
              myerr[4] = `Error 4: no url found for ${definitionName} in google search`// if url is defined, add it to the results
              errors[name] = myerr
              // write errors.json
              fs.writeFileSync(path.join(__dirname, 'errors.json'), JSON.stringify(errors, null, 2))


              // read results json
              const resultsJson = fs.readFileSync(path.join(__dirname, 'results.json'), 'utf8')
              // add new results to results json
              const newResults = JSON.parse(resultsJson)
              newResults[name] = {
                date: jsDate,
                definition,
                scrape
              }
              // write results json
              const ordered = Object.keys(newResults).sort().reduce(
                (obj, key) => {
                  obj[key] = newResults[key];
                  return obj;
                },
                {}
              );
              fs.writeFileSync(path.join(__dirname, 'results.json'), JSON.stringify(ordered, null, 2))
            } else {
              // read results json
              const resultsJson = fs.readFileSync(path.join(__dirname, 'results.json'), 'utf8')
              // add new results to results json
              const newResults = JSON.parse(resultsJson)
              newResults[name] = {
                date: jsDate,
                url,
                definition,
                scrape
              }
              // write results json
              const ordered = Object.keys(newResults).sort().reduce(
                (obj, key) => {
                  obj[key] = newResults[key];
                  return obj;
                },
                {}
              );
              fs.writeFileSync(path.join(__dirname, 'results.json'), JSON.stringify(ordered, null, 2))
            }
          })
          .catch(err => {
            console.log(err)
          })

      })
      // end web scraping section
    } catch (err) {
      console.log('error parsing name', name)
      console.log('error parsing stdout', stdout)
      console.log(err)
    }

  })
}

/*****
 * 
 * 
 * 
 * DANGER ZONE
 */

// // loop through all directories and run the function
// dirs.slice(150).forEach(dir => {
//   getMostRecentCommitDate(path.join(__dirname, dir))
// })


/*****
 *
 *
 *
 * MISC
 */

// // format and store all results in a csv file
// read results.json
let resultsJson = fs.readFileSync(path.join(__dirname, 'results.json'), 'utf8')
resultsJson = JSON.parse(resultsJson)
// format and store all results in a csv file
const csv = Object.keys(resultsJson).map(x => {
  console.log(x)
  const { date, definition, scrape } = resultsJson[x]
  // return `${x},${date},${definition?.name},${definition?.sourceDefinitionId},${definition?.dockerRepository},${definition?.dockerImageTag},${definition?.documentationUrl},${definition?.icon},${definition?.sourceType},${definition?.releaseStage},${scrape?.description},${scrape?.url}`
  // tab separated strings
  return `${x}\t${date}\t${definition?.name}\t${definition?.sourceDefinitionId}\t${definition?.dockerRepository}\t${definition?.dockerImageTag}\t${definition?.documentationUrl}\t${definition?.icon}\t${definition?.sourceType}\t${definition?.releaseStage}\t${scrape?.description}\t${scrape?.url}`
}
).join('\n')
// add headers
// const headers = 'name,date,definitionName,definitionId,definitionDockerRepository,definitionDockerImageTag,definitionDocumentationUrl,definitionIcon,definitionSourceType,definitionReleaseStage,scrapeDescription,scrapeUrl'
// tab separated headers
const headers = 'name\tdate\tdefinitionName\tdefinitionId\tdefinitionDockerRepository\tdefinitionDockerImageTag\tdefinitionDocumentationUrl\tdefinitionIcon\tdefinitionSourceType\tdefinitionReleaseStage\tscrapeDescription\tscrapeUrl'
fs.writeFileSync(path.join(__dirname, 'results.csv'), `${headers}\n${csv}`)
