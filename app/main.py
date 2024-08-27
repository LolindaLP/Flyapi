import os
import boto3
from fastapi import FastAPI, HTTPException, Request, Query, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from amadeus import Client, ResponseError
import Levenshtein

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")

amadeus = Client(
    client_id=AMADEUS_API_KEY,
    client_secret=AMADEUS_API_SECRET
)

app = FastAPI()

dynamodb = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)


cities_table = dynamodb.Table('Cities')

templates = Jinja2Templates(directory="E:/Fly_searcher/app/templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# @app.get("/autocomplete", response_class=JSONResponse)
# async def autocomplete(query: str = Query(..., min_length=1)):
#     try:
#         response = cities_table.scan()
#         cities = response.get('Items', [])
        
#         lower_query = query.lower()
#         max_distance = 2

#         scored_cities = []

#         for city in cities:
#             city_name = city['cityName'].lower()
#             distance = Levenshtein.distance(lower_query, city_name)
#             if city_name.startswith(lower_query) or distance <= max_distance:
#                 scored_cities.append({
#                     "cityName": city['cityName'],
#                     "cityCode": city['cityCode'],
#                     "score": distance
#                 })

#         scored_cities.sort(key=lambda x: x['score'])


#         return JSONResponse(content=list(scored_cities))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
@app.get("/autocomplete", response_class=JSONResponse)
async def autocomplete(query: str = Query(..., min_length=1)):
    try:
        response = cities_table.scan()
        cities = response.get('Items', [])
        
        lower_query = query.lower()
        max_distance = 2  # Maximum Levenshtein distance for fuzzy matching

        scored_cities = []

        for city in cities:
            city_name = city['cityName'].lower()
            distance = Levenshtein.distance(lower_query, city_name)

            # Match based on city name
            if city_name.startswith(lower_query) or distance <= max_distance:
                scored_city = {
                    "cityName": city['cityName'],
                    "cityCode": city['cityCode'],
                    "score": distance,
                    "airports": city.get('airports', [])
                }
                scored_cities.append(scored_city)

        # Sort by score (Levenshtein distance)
        scored_cities.sort(key=lambda x: x['score'])

        # Return the list of cities with their associated airports
        return JSONResponse(content=scored_cities)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.post("/search", response_class=JSONResponse)
async def search_flights(
    from_city_code: str = Form(...),
    to_city_code: str = Form(...),
    departure_date: str = Form(...)
):
    try:
        # Запрос к Amadeus API с использованием кодов городов
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=from_city_code,
            destinationLocationCode=to_city_code,
            departureDate=departure_date,
            adults=1
        )
        
        return JSONResponse(content=response.data)
    except ResponseError as error:
        return JSONResponse(status_code=500, content={"error": str(error)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

