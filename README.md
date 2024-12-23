# COMP-49X-24-25-Alumni-Association

The Alumni Association project is a web-based solution aimed at tracking social media engagement to help the University of San Diego's Alumni Association better connect with alumnis. 

## Installation
Clone Git repository to your local machine.

Run ```sh envsetup.sh``` if you do not have a proper Django-equipped virtual environment setup already. This command will create the environment, install Django on the environment, and start the environment.

If you have the environment already, run ```source env/bin/activate``` on Mac or ```env\\Scripts\\activate``` on Windows.

From here you can use the command

 ```cd AlumniProject``` 
 
 and then you will need to migrate the database by doing 

```python manage.py makemigrations```

```python manage.py migrate```

## Usage

```python
#Open terminal and run:

python manage.py runserver

#Navigate to http://127.0.0.1:8000/ in any browser
```
Once we are on the web page, use the credentials to login.

After successfully logging in, we can download the Alumni Instagram data by pressing the download button.

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