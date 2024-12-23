The Alumni Association project is a web-based solution aimed at tracking social media engagement to help the University of San Diego's Alumni Association better connect with alumnis. 

## Installation
Clone Git repository to your local machine.

Run ```python3 -m venv env``` if you do not have a proper Django-equipped virtual environment setup already. This command will create the environment.

If you have the environment already, run ```source env/bin/activate``` on Mac or ```env\\Scripts\\activate``` on Windows.

To install dependencies run ```python -m pip install --upgrade pip``` followed by ```pip install Django``` and ```pip install requests```

From here you can use the command

 ```cd AlumniProject``` 
 
 and then you will need to migrate the database by doing 

```python manage.py makemigrations```

```python manage.py migrate```

You will need to create a user in order to use the website properly. Run ```python manage.py createsuperuser``` in order to create an admin user.

## Usage

```python

#Open terminal and run:

sh run.sh dev

#Navigate to http://127.0.0.1:8000/ in any browser
```
Once we are on the web page, you will be redirected to the login page. Use the credentials created in the last step to login.

After successfully logging in, navigate to the homepage where you can input your Instagram API code and download your data.

To run code tests please use ```python manage.py test``` in order to run tests correctly on a mock database.

## Contributing

This project was created by
Bill Erdene Ochir, Connor Boll, Audrey Naidu, and Eli Zublin

## Contacts

berdeneochir@sandiego.edu

cboll@sandiego.edu

anaidu@sandiego.edu

ezublin@sandiego.edu


## License

[MIT](https://choosealicense.com/licenses/mit/)