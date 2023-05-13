import random
from couchdb import Server
from django.conf import settings


def get_random_database():
    databases = list(settings.COUCHDB_DATABASES.keys())
    return random.choice(databases)


def check_couchdb_status():
    server_url = "http://172.26.132.68:5984/"
    try:
        server = Server(server_url)
        server.version()  # Perform a simple operation to check the server's availability
        print(f"CouchDB server is running: False")
    except Exception:
        print(f"CouchDB server is running: True")

check_couchdb_status()