#!/bin/bash
USERNAME="bill@sandiego.edu"
PASSWORD="Password"

SPRINT5 = false
SPRINT6 = false

#Can uncomment these lines if you want to input username/password info, won't be fully automated but may be necessary
#read -p "Enter username: " USERNAME
#read -p "Enter password: " PASSWORD

curl -c cookies.txt -s https://alumni-association.dedyn.io/login -o login_page.html

CSRF_TOKEN=$(grep 'csrfmiddlewaretoken' login_page.html | \
  sed -nE 's/.*name="csrfmiddlewaretoken" value="([^"]+)".*/\1/p')


echo "Got CSRF Token:" $CSRF_TOKEN
curl -b cookies.txt -c cookies.txt -s -X POST https://alumni-association.dedyn.io/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "csrfmiddlewaretoken=$CSRF_TOKEN&email=$USERNAME&password=$PASSWORD" \
  -e http://127.0.0.1:8000/login

echo "\nGot cookies:"
cat cookies.txt

echo "\nAttempting to access /account-info/"
curl -b cookies.txt -s https://alumni-association.dedyn.io/account-info/ > account_page.html

if grep -q "<h1>Account Information</h1>" account_page.html; then
  echo "\nTest passed! Logged in and accessed account-info page"
  SPRINT5=true
else
  echo "\nAccount info test failed"
  SPRINT5=false
fi

rm account_page.html login_page.html 

echo "\nAttempting to access /stories-info/"
curl -b cookies.txt -s https://alumni-association.dedyn.io/stories-info/ > stories_page.html

if grep -q "<title>Stories Info</title>" stories_page.html; then
  echo "\nTest passed! Logged in and accessed stories-info page"
  SPRINT6=true
else
  echo "\nStories info test failed"
  SPRINT6=false
fi

rm stories_page.html

if [ $SPRINT5 && $SPRINT6 ]; then
  echo "\nAll tests passed!"
else
  echo "\nOne or more tests failing"
fi

rm cookies.txt