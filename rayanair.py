from datetime import datetime, timedelta
from ryanair import Ryanair
from ryanair.types import Flight

api = Ryanair(currency="EUR")  # Euro currency, so could also be GBP etc. also
tomorrow = datetime.today().date() + timedelta(days=1)

flights = api.get_cheapest_flights("WMI", tomorrow, tomorrow + timedelta(days=1))

for flight in flights:
    print(flight) 