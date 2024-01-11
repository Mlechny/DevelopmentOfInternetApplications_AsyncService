from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

import time
import random
import requests

from concurrent import futures

CALLBACK_URL = "http://127.0.0.1:8080/api/forms/"

executor = futures.ThreadPoolExecutor(max_workers=1)
TOKEN = 'secret_token'


def get_random_status(form_id):
    time.sleep(5)
    return {
        "form_id": form_id,
        "result":bool(random.randint(0, 3)),
    }


def status_callback(task):
    try:
        result = task.result()
        print(result)
    except futures._base.CancelledError:
        return

    url = str(CALLBACK_URL+str(result["form_id"])+'/testing/')
    requests.put(url, data={"testing_status": result['result'], "token": TOKEN}, timeout=3)


@api_view(['POST'])
def set_status(request):
    if "form_id" in request.data.keys():
        form_id = request.data["form_id"]

        task = executor.submit(get_random_status, form_id)
        task.add_done_callback(status_callback)
        return Response(result=status.HTTP_200_OK)
    return Response(result=status.HTTP_400_BAD_REQUEST)