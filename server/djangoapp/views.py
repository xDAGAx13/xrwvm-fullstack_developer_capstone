# Uncomment the required imports before adding the code
from .models import CarMake, CarModel
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
import os, requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:3030")
# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
@csrf_exempt
def logout_request(request):
    """
    GET  /djangoapp/logout            → {"userName":""}
    """
    if request.user.is_authenticated:
        logger.info(f"User {request.user.username} logged out.")
        logout(request)
    return JsonResponse({"userName": ""})

# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    context = {}

    # Load JSON data from the request body
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    email_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,password=password, email=email)
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName":username,"status":"Authenticated"}
        return JsonResponse(data)
    else :
        data = {"userName":username,"error":"Already Registered"}
        return JsonResponse(data)

# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
@csrf_exempt              # the React front-end calls this with fetch()
def get_dealerships(request):
    """
    GET  /djangoapp/get_dealers/           → every dealer
    GET  /djangoapp/get_dealers/?state=TX → dealers in Texas

    JSON response format expected by the React <Dealers/> component:
        {
          "dealerships": [
              {
                 "id": …, "city": …, "state": …, "address": …,
                 "zip": …, "lat": …, "long": …,
                 "short_name": …, "full_name": …
              },
              …
          ]
        }
    """
    state_filter = request.GET.get("state")           # None if absent

    # Build URL for the Node service
    if state_filter:
        url = f"{BACKEND_URL}/fetchDealers/{state_filter}"
    else:
        url = f"{BACKEND_URL}/fetchDealers"

    try:
        logger.debug(f"Calling dealer service: {url}")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        dealers = resp.json()                         # the Express route returns a JSON list
    except requests.RequestException as exc:
        logger.error(f"Dealer service error: {exc}")
        return JsonResponse({"error": "Unable to fetch dealerships"}, status=500)

    # Wrap in an object – React expects the key ‘dealerships’
    return JsonResponse({"dealerships": dealers}, safe=False)

# Create a `get_dealer_reviews` view to render the reviews of a dealer
# def get_dealer_reviews(request,dealer_id):
# ...

# Create a `get_dealer_details` view to render the dealer details
# def get_dealer_details(request, dealer_id):
# ...

# Create a `add_review` view to submit a review
# def add_review(request):
# ...
def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if(count == 0):
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels":cars})