export function concatenateRawTableName(namespace, name) {
  let plainConcat = namespace + name;
  // Pretend we always have at least one underscore, so that we never generate `_raw_stream_`
  let longestUnderscoreRun = 1;
  for (let i = 0; i < plainConcat.length; i++) {
    // If we've found an underscore, count the number of consecutive underscores
    let underscoreRun = 0;
    while (i < plainConcat.length && plainConcat.charAt(i) === '_') {
        underscoreRun++;
        i++;
    }
    longestUnderscoreRun = Math.max(longestUnderscoreRun, underscoreRun);
  }
  return namespace + "_raw" + "_".repeat(longestUnderscoreRun + 1) + "stream_" + name;
}

export function setSql(namespace, name, destination, sql) {
  var output;
  if (namespace != "" && name != "") {
    output = sql;
  } else {
    output = defaultMessage;
  }
  document.getElementById("sql_output_block_" + destination).innerHTML = output;
}

export const defaultMessage = "Enter your stream's name and namespace to see the SQL output.\nIf your stream has no namespace, take the default value from the destination connector's settings.";
