# University Research Opportunity Portal

A web app where faculty members can post, view, update, close, and delete research opportunities in one place.

**GitHub Repository:** https://github.com/mubashirtech56/research-opportunity-portal

## How it works

```
Browser (index.html + JavaScript)
        |  fetch() with JSON over HTTP
        v
Flask REST API (app.py)   <- validates input, returns status codes
        |  SQL queries (parameterized)
        v
MariaDB / MySQL database (research_portal)
```

1. The user interacts with the web page (frontend).
2. The page sends HTTP requests (GET, POST, PUT, DELETE) to the API.
3. The API validates the data, runs SQL on the database, and replies with JSON and a status code.
4. The page displays the result or an error message. No data is hard-coded; everything comes from the database.

## Technologies

| Part     | Technology                           | Role                               |
| -------- | ------------------------------------ | ---------------------------------- |
| Backend  | Python 3 + Flask                     | REST API and serves the frontend   |
| Database | MySQL-compatible (MariaDB on Arch)   | Stores all opportunities           |
| Driver   | mysql-connector-python               | Lets Python talk to the database   |
| Frontend | HTML, CSS, JavaScript (no libraries) | User interface, calls the API      |
| Testing  | Postman or Bruno                     | Tests the API without the frontend |

## Project structure

| File / Folder                                            | What it does                                                         |
| -------------------------------------------------------- | -------------------------------------------------------------------- |
| `app.py`                                                 | The backend: all 5 API routes, input validation, error handling      |
| `schema.sql`                                             | Creates the database and the `opportunities` table                   |
| `static/index.html`                                      | The frontend: table, details view, create/edit form, messages        |
| `requirements.txt`                                       | Python packages to install (Flask, mysql-connector-python)           |
| `postman/Research_Portal.postman_collection.json`        | Exported Postman collection with 10 requests and 20 assertions       |
| `postman/collections/Research Opportunity Portal/`       | Same collection in Postman's Git-friendly YAML source format         |
| `testing/newman_report.html`                             | HTML report produced by running the collection with Newman           |
| `testing/run_tests.py`                                   | Starts the server and runs the collection with Newman in one step    |
| `testing/screenshots/`                                   | Postman request/response captures and the API test report            |
| `.gitignore`                                             | Keeps `venv/` and secrets out of GitHub                              |

## Setup (Arch Linux / Omarchy)

**1. Install Python and the database server**

```
sudo pacman -S python mariadb
```

**2. Initialise and start the database (first time only)**

```
sudo mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql
sudo systemctl enable --now mariadb
```

The first command creates the database's system files. The second starts the server now and on every boot.

**3. Create the database and table**

```
sudo mariadb < schema.sql
```

This creates the `research_portal` database and the `opportunities` table.

**4. Create a database user for the app** (choose your own username and password)

```
sudo mariadb -e "CREATE USER 'portal'@'localhost' IDENTIFIED BY 'choose_a_password'; GRANT ALL ON research_portal.* TO 'portal'@'localhost'; FLUSH PRIVILEGES;"
```

This gives the app its own login that can only access `research_portal`.

**5. Create a virtual environment and install packages**

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

The virtual environment keeps this project's packages separate from the rest of the system.

**6. Set credentials and start the server**

```
export DB_USER=portal DB_PASSWORD=choose_a_password
python app.py
```

The app reads the database login from environment variables, so no password is stored in the code or on GitHub.

**7. Open the app** at http://localhost:5000

| Variable      | Default           | Meaning           |
| ------------- | ----------------- | ----------------- |
| `DB_HOST`     | `localhost`       | Database server   |
| `DB_USER`     | `root`            | Database username |
| `DB_PASSWORD` | (empty)           | Database password |
| `DB_NAME`     | `research_portal` | Database name     |

> On Debian/Ubuntu: `sudo apt install python3-venv mariadb-server`, then follow the same steps using `python3`.
> The `export` variables last only for the current terminal. Set them again in each new terminal.

## Using the frontend

- **View all:** the table loads automatically from the database.
- **View details:** click _View_ on a row.
- **Create:** fill in the form and click _Save_. Required fields are checked before sending.
- **Update:** click _Edit_ on a row, change the form, and click _Save_.
- **Close:** click _Close_ to change an opportunity from Open to Closed.
- **Delete:** click _Delete_ and confirm.
- Green messages show success; red messages show errors.

## API reference

Base URL: `http://localhost:5000`

| Method | Endpoint                 | Description                     | Success | Errors   |
| ------ | ------------------------ | ------------------------------- | ------- | -------- |
| POST   | `/api/opportunities`     | Create an opportunity           | 201     | 400      |
| GET    | `/api/opportunities`     | List all opportunities          | 200     |          |
| GET    | `/api/opportunities/:id` | Get one opportunity             | 200     | 404      |
| PUT    | `/api/opportunities/:id` | Update (also used to close one) | 200     | 400, 404 |
| DELETE | `/api/opportunities/:id` | Delete an opportunity           | 200     | 404      |

**Example request body (POST):**

```json
{
  "title": "Network Intrusion Detection",
  "description": "Detect attacks using machine learning",
  "research_area": "Cyber Security",
  "faculty_name": "Dr. Ahmed Khan",
  "department": "Computer Science",
  "required_skills": "Python, Networking",
  "positions": 2,
  "deadline": "2026-12-31",
  "status": "Open"
}
```

`status` is optional on create and defaults to `Open`. A PUT can send only the fields that change, for example `{"status": "Closed"}`.

**Validation rules:** all fields except `status` are required and cannot be empty; `positions` must be a number of at least 1; `deadline` must be `YYYY-MM-DD`; `status` must be `Open` or `Closed`.

**Status codes:** `200` OK, `201` Created, `400` Bad Request (invalid or missing data), `404` Not Found (ID or route does not exist), `500` Internal Server Error (unexpected or database failure).

## Testing with Postman

The collection lives at `postman/Research_Portal.postman_collection.json`. Import it
into Postman and run the requests in order (each request carries automated
assertions, so Postman shows a green pass for every step):

| #   | Request                          | Expected result            |
| --- | -------------------------------- | -------------------------- |
| 1   | Create opportunity #1            | 201 Created                |
| 2   | Create opportunity #2            | 201 Created                |
| 3   | Create opportunity #3            | 201 Created                |
| 4   | Get all opportunities            | 200 OK (array, 3+ items)   |
| 5   | Get one opportunity (id 1)       | 200 OK                     |
| 6   | Update opportunity (id 1)        | 200 OK (fields changed)    |
| 7   | Close opportunity (id 2)         | 200 OK (Open to Closed)    |
| 8   | Delete opportunity (id 3)        | 200 OK                     |
| 9   | Get deleted opportunity (id 3)   | 404 Not Found              |
| 10  | Invalid create (empty, bad data) | 400 Bad Request            |

The collection uses a `baseUrl` variable set to `http://localhost:5000`.

### Running the tests headlessly (Newman)

With the server running and `newman` + `newman-reporter-html` installed
(`npm install -g newman newman-reporter-html`), run:

```
newman run postman/Research_Portal.postman_collection.json -r cli,html --reporter-html-export testing/newman_report.html
```

Or use the helper script, which starts the server for you and then runs the
collection:

```
python testing/run_tests.py
```

Both produce `testing/newman_report.html` (10 requests, 20 assertions, 0 failures).

## Troubleshooting

| Problem                              | Fix                                                                                                                                                                                                         |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ERROR 1396: CREATE USER failed`     | The user already exists. Reset it instead: `sudo mariadb -e "ALTER USER 'portal'@'localhost' IDENTIFIED BY 'choose_a_password'; GRANT ALL ON research_portal.* TO 'portal'@'localhost'; FLUSH PRIVILEGES;"` |
| `Access denied for user`             | Wrong username or password in `DB_USER` / `DB_PASSWORD`, or the `export` was not run in this terminal.                                                                                                      |
| `Unknown database 'research_portal'` | Run step 3: `sudo mariadb < schema.sql`                                                                                                                                                                     |
| API returns 500                      | Check that MariaDB is running: `systemctl status mariadb`                                                                                                                                                   |
| Page shows no data                   | Make sure `python app.py` is running and open http://localhost:5000                                                                                                                                         |

To see the tables: `mariadb -u portal -p research_portal -e "SHOW TABLES;"`

## Security

Database passwords are never committed to this repository. Credentials are supplied through environment variables, and SQL queries are parameterized to prevent SQL injection.
