#!/usr/bin/env bash

cd "$(dirname "$0")"

FILE="/tmp/csv/users.csv"

rm -rf $FILE

echo "id,created_at,updated_at,name,title,age,email,telephone,gender,language,academic_degree,nationality,occupation,height,blood_type,weight" >> $FILE

jq -c 'select((.type | contains("RECORD")) and (.record.stream | contains("users"))) .record.data' \
  | jq -r '[.id, .created_at, .updated_at, .name, .title, .age, .email, .telephone, .gender, .language, .academic_degree, .nationality, .occupation, .height, .blood_type, .weight] | @csv' \
  >> $FILE
