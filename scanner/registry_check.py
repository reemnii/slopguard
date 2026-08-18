import requests


def check_pypi_exists(package_name: str) -> dict:
    url = f"https://pypi.org/pypi/{package_name}/json"

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()

            return {
                "exists": True,
                "package": package_name,
                "author": data["info"].get("author"),
                "summary": data["info"].get("summary"),
            }

        if response.status_code == 404:
            return {
                "exists": False,
                "package": package_name,
            }

        return {
            "exists": False,
            "package": package_name,
            "error": f"PyPI returned status code {response.status_code}",
        }

    except requests.RequestException as error:
        return {
            "exists": False,
            "package": package_name,
            "error": str(error),
        }


if __name__ == "__main__":
    print(check_pypi_exists("requests"))
    print(check_pypi_exists("this-package-definitely-does-not-exist-12345"))