# todo: immediately write status file
# todo: wait for file copies
# todo: trap on any failure and write error file
# todo: report failure and cancel early if anyone else writes error file
# todo: allow injecting a failure in any pod as a testing option?
# todo: after completing update status
# todo: run entrypoints with env variables for log access

bucket=$1
file=$2

host=minio.example.com
s3_key=svc_example_user
s3_secret=svc_example_user_password

resource="/${bucket}/${file}"
content_type="application/octet-stream"
date=`date -R`
_signature="PUT\n\n${content_type}\n${date}\n${resource}"
signature=`echo -en ${_signature} | openssl sha1 -hmac ${s3_secret} -binary | base64`

curl -X PUT -T "${file}" \
          -H "Host: ${host}" \
          -H "Date: ${date}" \
          -H "Content-Type: ${content_type}" \
          -H "Authorization: AWS ${s3_key}:${signature}" \
          https://${host}${resource}

