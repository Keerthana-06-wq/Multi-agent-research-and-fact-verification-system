from urllib.parse import urlparse
from backend.core.models import SourceTier

GOVERNMENT_SUFFIXES = [
    ".gov", ".gov.in", ".nic.in", ".gov.uk", ".gov.au", ".gouv.fr",
    ".fed.us", ".mil", ".gc.ca"
]

ACADEMIC_SUFFIXES = [
    ".edu", ".ac.in", ".ac.uk", ".edu.au", ".edu.cn"
]

ACADEMIC_DOMAINS = {
    "arxiv.org", "jstor.org", "sciencedirect.com", "springer.com",
    "wiley.com", "ieee.org", "ncbi.nlm.nih.gov", "researchgate.net",
    "nature.com", "science.org", "cell.com", "pnas.org"
}

SCIENTIFIC_INSTITUTIONS = {
    "nasa.gov", "who.int", "un.org", "isro.gov.in", "cern.ch",
    "noaa.gov", "usgs.gov", "nih.gov", "cdc.gov", "esa.int",
    "ipcc.ch", "wmo.int", "iaea.org"
}

REFERENCE_DOMAINS = {
    "wikipedia.org", "en.wikipedia.org", "britannica.com",
    "merriam-webster.com", "oxfordreference.com", "plato.stanford.edu",
    "worldcat.org", "loc.gov", "snopes.com", "politifact.com",
    "factcheck.org"
}

REPUTABLE_NEWS = {
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk",
    "theguardian.com", "nytimes.com", "washingtonpost.com",
    "thehindu.com", "economist.com", "wsj.com", "bloomberg.com",
    "aljazeera.com", "npr.org", "time.com", "nature.com"
}

def analyze_source_credibility(url: str, title: str = "") -> tuple[str, int, str]:
    """
    Analyzes a URL and domain to assign SourceTier, credibility score (0-100), and clean domain name.
    """
    if not url:
        return SourceTier.GENERAL_WEB.value, 40, "web"
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
    except Exception:
        return SourceTier.GENERAL_WEB.value, 40, "web"

    # 1. Scientific Institutions
    for sci in SCIENTIFIC_INSTITUTIONS:
        if netloc == sci or netloc.endswith("." + sci):
            return SourceTier.SCIENTIFIC.value, 98, netloc

    # 2. Government domains
    for gov in GOVERNMENT_SUFFIXES:
        if netloc.endswith(gov) or f"{gov}/" in url.lower():
            return SourceTier.GOVERNMENT.value, 96, netloc

    # 3. Academic domains
    for acad in ACADEMIC_DOMAINS:
        if netloc == acad or netloc.endswith("." + acad):
            return SourceTier.ACADEMIC.value, 93, netloc
            
    for suf in ACADEMIC_SUFFIXES:
        if netloc.endswith(suf):
            return SourceTier.ACADEMIC.value, 92, netloc

    # 4. Reference & Encyclopedias
    for ref in REFERENCE_DOMAINS:
        if netloc == ref or netloc.endswith("." + ref):
            return SourceTier.ENCYCLOPEDIC.value, 88, netloc

    # 5. Reputable News
    for news in REPUTABLE_NEWS:
        if netloc == news or netloc.endswith("." + news):
            return SourceTier.REPUTABLE_NEWS.value, 84, netloc

    # Default general web
    return SourceTier.GENERAL_WEB.value, 65, netloc
