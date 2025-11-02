import requests


url = "https://jsonplaceholder.typicode.com/posts"

payload = {
    "title" : "Task 1",
    "body" : "Body task 1",
    "userId" : 1
}

headers = {
    "Content-type" : "application/json; charset=UTF-8"
}

def post_send(url: str, payload: dict, headers: dict) -> None:
    try:
        response = requests.post(url, json=payload, headers=headers)
        print("Status code:", response.status_code)
        print("Response JSON")
        print(response.json())
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


post_send(url, payload, headers) 