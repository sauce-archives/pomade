from urlparse import urlparse, urljoin

def clean_url(url, base_url, https=False):
    if not urlparse(url).netloc:
        if https:
            base_url = base_url.replace('http://', 'https://')
        url = urljoin(base_url, url)
    return url