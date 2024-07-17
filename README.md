# Shows Manager
EASS Project by Ronel Yust

Shows Manager is a FastAPI application designed to help users keep track of all their favorite shows.

Whether you're switching between streaming services or sticking with traditional TV, Shows Manager provides a simple and effective solution for organizing your shows.


## Features

- Create a new show list.
- Add shows by title, specify their watch status, and note the current episode.
- Sort shows by watch status.
- Edit show information.
- Remove shows from your list.
- Export and import your show lists.


## Prerequisites

- Docker
- Python (with Pytest)


## Installation

Clone the project repository using:
```
git clone https://github.com/EASS-HIT-PART-A-2024-CLASS-V/ShowsManager.git
```
Go to project directory and build the Docker containers:
```
docker-compose up --build
```
## Usage

Access the frontend at http://localhost:3000/

Start a new list or import your own.

Access the backend documentation at http://localhost:8000/docs


## Project Structure
```
ShowsManager/
├── backend/
│   ├── mongo-init.js/
│   ├── Dockerfile
│   ├── integration_test.py
│   ├── main.py
│   ├── mongo-in.js
│   ├── requirements.txt
│   └── test_unit.py
├── Frontend/
│   ├── public/
│   ├── sec/
│   ├── .gitignore
│   ├── Dockerfile
│   ├── package-lock.json
│   └── package.json
├── .gitignore
├── docker-compose.yml
├── mongod.conf
└── README.md
```


## Running Tests
Assuming you are in the root directory of the project, run the next code on terminal:
```
pytest ./backend/test_unit.py
pytest ./backend/integration_test.py
```


## Video Demo

Watch a demonstration of Shows Manager in action on [YouTube](https://youtu.be/VTdqYYW5VYw).

![Video Thumbnail](https://img.youtube.com/vi/VTdqYYW5VYw/hqdefault.jpg)



## Technologies Used
[![My Skills](https://skillicons.dev/icons?i=py,js,docker,mongodb,react)](https://skillicons.dev)
- Backend: Python, FastAPI
- Frontend: React, JavaScript
- Database: Mongodb
