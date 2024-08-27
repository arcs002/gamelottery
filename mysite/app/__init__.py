from flask import Flask

app = Flask(__name__)

# Import the routes after the app object is created
from app import routes