pre-requisites:- 
* Create a project structure like this :

fixmycity-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── config.py
│   └── requirements.txt
├── frontend/
│   └── app.py
├── data/
│   ├── uploads/
│   └── db/
├── docker-compose.yml
└── README.md

* In backend/requirements.txt , add below
fastapi
uvicorn[standard]
pydantic

1. Setup up a virtual environment
    * python -m venv venv
    * source venv/bin/activate

2. Install dependencies
    * pip install -r backend/requirements.txt ( if this doesn't works install all the tools manually - like pip install [package-name])

3. Create basic test API's in main.py and run it
    * uvicorn backend.app.main:app --reload

4. Create a models.py - for defining enums, request & response types 
    * we also added BaseModel type in request & response : In Pydantic, the BaseModel is the fundamental class used to define data schemas and validation logic. By inheriting from BaseModel, you can create classes that automatically validate, parse, and serialize data based on Python type annotations.

5. Create a database.py to define queries to create table during initialization. Further add onStartup() method in main.py to call it on startup.

6. Create routes.py to add more api's that will help to add, get data from database. Register the router in main.py

7. Add new dependencies - python-multipart, opencv-python-headless
    * python-multipart: Handles incoming file uploads (e.g., images) from HTTP requests.
    * opencv-python-headless: Processes those images without needing a graphical user interface (GUI), saving space and reducing dependencies. 

8. 
