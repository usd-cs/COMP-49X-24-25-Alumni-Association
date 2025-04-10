#!/bin/bash
USERNAME="bill@sandiego.edu"
PASSWORD="Password"

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
curl -b cookies.txt -s https://alumni-association.dedyn.io/account-info/ > final_page.html

if grep -q "<h1>Account Information</h1>" final_page.html; then
  echo "\nTest passed! Logged in and accessed account-info page"
else
  echo "\nTest failed"
fi

rm final_page.html login_page.html cookies.txt