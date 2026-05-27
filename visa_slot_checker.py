import requests

URL = "https://checkvisaslots.com/latest-us-visa-availability/h-1b-regular/"

def check_slot():
    try:
        response = requests.get(
            URL,
            timeout=20,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124 Safari/537.36"
                )
            }
        )

        print("Status code:", response.status_code)
        print(response.text[:3000])

    except Exception as e:
        print("Error:", type(e).name, str(e))


if name == "main":
    check_slot()
