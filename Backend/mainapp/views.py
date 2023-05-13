import json
from random import random

import couchdb
from couchdb import Server
from django.http import HttpResponse, JsonResponse
from Backend.settings import COUCHDB_DATABASES
from mainapp.utils import get_random_database


def get_full_db(request):
    database_settings = COUCHDB_DATABASES[get_random_database()]
    server_url = database_settings['URL']
    database_name = database_settings['NAME']

    server = Server(server_url)
    database = server[database_name]

    # 获取数据库中的所有文档
    documents = []
    for doc_id in database:
        document = database[doc_id]

        # Filter "_rev"
        filtered_document = {key: value for key, value in document.items() if key != "_rev"}

        # Create document with "_id" as key
        document_with_id_as_key = {doc_id: filtered_document}
        documents.append(document_with_id_as_key)

    return JsonResponse(documents, safe=False, json_dumps_params={'indent': 4})



