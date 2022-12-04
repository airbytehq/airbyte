countAttempt=0
maxAttempt=10
while : ; do
  cockroach sql -e "create user test_user with password 'test_user'" &> user_creation.log && cockroach sql -e "GRANT ALL ON DATABASE defaultdb TO test_user" &>> user_creation.log
  ((countAttempt++))

  if [ "$countAttempt" = "$maxAttempt" ] || [ "$(grep -c 'ERROR' user_creation.log)" = 0 ]; then
    echo "User test_user is created with grants to defaultdb! Login=Pass"
    break
  fi
  sleep 2
  echo "Attempt #$countAttempt to create a user is failed!"
done