def get_url_list() -> list[str]:
    prefix = "http://127.0.0.1:8080/hello"
    url_list: list[str] = []
    for i in range(100):
        url_list.append(f"{prefix}/{i}")
    return url_list
