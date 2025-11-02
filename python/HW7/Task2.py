import requests


with open("lock.txt", "r") as f:
    api_key = f.readline()

city = input("Entry name of the city: ")


def weather_info(city: str, api_key: str) -> None:
    try:
        response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}")
        data = response.json()
        temp = float(data["main"]["temp"]) - 273.15
        print(f"City selected: {data["name"]}")
        print(f"Weather: {data["weather"][0]["main"]}")
        print(f"Temperature: {temp:.2f} °C")
    except requests.exceptions.ConnectionError:
        print("The server is not available (wrong address, no network, API unavailable")
    except requests.exceptions.Timeout:
        print("The server is taking too long to respond")
    except requests.exceptions.TooManyRedirects:
        print("Cyclic redirects")
    except requests.exceptions.RequestException:
        print("A common base class for all requests errors")
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        if status == 400:
            print("Invalid request (client error)")
        if status == 401:
            print("Authorization error. Check the API key")
        if status == 403:
            print("Access is denied")
        if status == 404:
            print("The resource was not found")
        if status == 429:
            print("Too many requests (rate limit)")
        if status in [500, 502, 503, 504]:
            print("Errors on the API server")

weather_info(city, api_key)