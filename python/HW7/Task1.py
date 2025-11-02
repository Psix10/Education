import requests


n = int(input("Entry number:"))

def view_post(n: int = 6) -> None:
    for i in range(1, n):
        try:
            response = requests.get(f'https://jsonplaceholder.typicode.com/posts/{i}')
            if response.status_code == 200:
                data = response.json()  # Получаем данные в формате JSON
                print(f"ID: {data["id"]}")
                print(f"Заголовок: {data["title"]}")
                print(f"Тело: {data["body"]}")
            else:
                print(f'Ошибка: {response.status_code}')
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


view_post(n)