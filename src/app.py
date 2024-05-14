from flask import Flask
from dotenv import load_dotenv
import aria2p
import os

load_dotenv('.env')

aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret=""
    )
)

def config_app():
    app = Flask(__name__, template_folder="templates")

    return app