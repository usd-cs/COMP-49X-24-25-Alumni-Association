# Alumni Association Project

The Alumni Association project is a web-based solution aimed at tracking social media engagement to help the University of San Diego's Alumni Association better connect with alumni.

---

## Installation & Setup

### 1. Clone the Repository Inside your Docker

```bash
git clone https://github.com/usd-cs/COMP-49X-24-25-Alumni-Association.git
cd COMP-49X-24-25-Alumni-Association
````

### 2. Start the Project with Docker

Ensure Docker and Docker Compose are installed. Then, run the following command to build and start the application:

```bash
docker compose up --build
```

This will launch the web server and other required services.

### 3. Set Up Google OAuth

Create a `.env` file inside the `Alumni/Alumni/` directory with your Google OAuth client ID:

```env
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
```

> Make sure your Google API credentials are configured for web application use.

### 4. Create a Superuser

In a separate terminal window, run the following command to create a Django admin user:

```bash
docker compose exec web python manage.py createsuperuser
```

Follow the prompts to complete user setup.

---

## Logging In

You can access the project locally or via the live deployment:

* **Local**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **Live**: [https://alumni-association.dedyn.io/](https://alumni-association.dedyn.io/)

Log in using the admin credentials created in the setup step.
After logging in, you will be prompted to enter your **Instagram API Key**.

> Required scopes for the Instagram API:
>
> * `instagram_basic`
> * `instagram_business_basic`
> * `instagram_manage_comments`

---

## Running Tests

To run tests on the mock database:

```bash
docker compose exec web python manage.py test
```

---

## Contributing

This project was created by:

* Bill Erdene Ochir
* Connor Boll
* Audrey Naidu
* Eli Zublin

---

## Contact

* [berdeneochir@sandiego.edu](mailto:berdeneochir@sandiego.edu)
* [cboll@sandiego.edu](mailto:cboll@sandiego.edu)
* [anaidu@sandiego.edu](mailto:anaidu@sandiego.edu)
* [ezublin@sandiego.edu](mailto:ezublin@sandiego.edu)

---

## License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).
