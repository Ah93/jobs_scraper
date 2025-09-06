import re, unicodedata
import tldextract
from urllib.parse import urlparse


SOCIAL_HOSTS = {"linkedin.com","facebook.com","twitter.com","x.com","instagram.com","youtube.com","tiktok.com","quora.com","wikipedia.org","crunchbase.com"}




def normalize_text(s: str) -> str:
    s = unicodedata.normalize('NFKC', s or '').strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def fingerprint(title: str, company: str, location: str) -> str:
    base = f"{normalize_text(title)}|{normalize_text(company)}|{normalize_text(location)}"
    return re.sub(r"[^a-z0-9|]+", "", base)


def is_social_or_info(url: str) -> bool:
    host = tldextract.extract(url).registered_domain
    return host in SOCIAL_HOSTS