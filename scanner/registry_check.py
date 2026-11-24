import requests


def check_pypi_exists(package_name: str) -> dict:
    url = f"https://pypi.org/pypi/{package_name}/json"

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            info = data.get("info", {})
            releases = data.get("releases", {})

            repository_url = (
                info.get("project_url")
                or info.get("home_page")
                or (info.get("project_urls") or {}).get("Source")
                or (info.get("project_urls") or {}).get("Repository")
            )

            upload_dates = []

            for files in releases.values():
                for file in files:
                    upload_time = file.get("upload_time_iso_8601")

                    if upload_time:
                        upload_dates.append(upload_time)

            first_upload = min(upload_dates) if upload_dates else None

            return {
                "exists": True,
                "package": package_name,
                "summary": info.get("summary"),
                "author": info.get("author"),
                "repository_url": repository_url,
                "first_upload": first_upload,
            }

        if response.status_code == 404:
            return {
                "exists": False,
                "package": package_name,
            }

        return {
            "exists": None,
            "package": package_name,
            "error": f"PyPI returned status code {response.status_code}",
        }

    except (requests.RequestException, ValueError) as error:
        return {
            "exists": None,
            "package": package_name,
            "error": str(error),
        }


def check_npm_exists(package_name: str) -> dict:
    url = f"https://registry.npmjs.org/{package_name}"

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()

            return {
                "exists": True,
                "package": package_name,
                "description": data.get("description"),
            }

        if response.status_code == 404:
            return {
                "exists": False,
                "package": package_name,
            }

        return {
            "exists": None,
            "package": package_name,
            "error": f"npm returned status code {response.status_code}",
        }

    except (requests.RequestException, ValueError) as error:
        return {
            "exists": None,
            "package": package_name,
            "error": str(error),
        }


if __name__ == "__main__":
    print(check_pypi_exists("requests"))
    print(check_pypi_exists("this-package-definitely-does-not-exist-12345"))

if __name__ == "__main__":
    print(check_npm_exists("react"))
    print(check_npm_exists("definitely-fake-npm-package-xyz123"))
