const MAX_LOG_LENGTH = 500;

function toSafeLogString(value) {
  let stringValue;
  try {
    stringValue = String(value);
  } catch {
    stringValue = "[unprintable value]";
  }

  return stringValue
    .replace(/\r/g, " ")
    .replace(/\n/g, " ")
    .replace(/[\u0000-\u001F\u007F]/g, "")
    .slice(0, MAX_LOG_LENGTH);
}

module.exports = { toSafeLogString };
