import re, requests

def match(url: str) -> bool:
    return "ddownload.com" in url or "ddl.to" in url

def resolve(url: str, api_key: str) -> str:
    m = re.search(r"(?:ddownload\.com|ddl\.to)/(?:[^/]+)?([A-Za-z0-9]{10,})", url)
    if not m:
        return url
    code = m.group(1)
    if api_key:
        api = f"https://api-v2.ddownload.com/api/file/direct_link?key={api_key}&file_code={code}"
        r = requests.get(api, timeout=15)
        if r.status_code == 200 and "result" in r.json():
            return r.json()["result"]["direct_link"]
    return url
