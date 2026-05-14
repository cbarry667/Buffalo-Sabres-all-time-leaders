from typing import List, Optional
import unicodedata

import requests
from bs4 import BeautifulSoup

from .models import Leader

BASE_URL = "https://www.hockey-reference.com"
SOURCE_URL = "https://www.hockey-reference.com/teams/FLA/leaders_career.html"

REQUESTED_CATEGORIES = {
    "Goals",
    "Assists",
    "Hat Tricks",
    "Games Played",
    "Games Played (Goalie)",
    "Save Percentage",
    "Saves",
    "Shutouts",
    "Goals Against Average",
}


def fetch_leader_html(url: str = SOURCE_URL) -> str:
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.text


def normalize_player_name(name: str) -> str:
    fixed = name
    try:
        fixed = fixed.encode("latin-1").decode("utf-8")
    except UnicodeEncodeError:
        pass
    fixed = unicodedata.normalize("NFKD", fixed)
    fixed = "".join(ch for ch in fixed if not unicodedata.combining(ch))
    return fixed.strip()


def parse_leaders(html: str) -> List[Leader]:
    soup = BeautifulSoup(html, "html.parser")
    leaders: List[Leader] = []

    for div in soup.find_all("div", id=lambda value: value and value.startswith("leaders_")):
        category_tag = div.find("h4")
        category = category_tag.get_text(strip=True) if category_tag else div["id"].replace("leaders_", "").replace("_", " ").title()
        if category not in REQUESTED_CATEGORIES:
            continue

        for rank_span in div.select("span.rank"):
            rank_text = rank_span.get_text(strip=True).rstrip(".")
            try:
                rank = int(rank_text)
            except ValueError:
                continue

            item_div = rank_span.find_parent("div")
            if item_div is None:
                continue

            who_span = item_div.find("span", class_="who")
            value_span = item_div.find("span", class_="value")
            if who_span is None or value_span is None:
                continue

            player_name = who_span.get_text(strip=True)
            player_name = normalize_player_name(player_name)
            player_url = None
            player_link = who_span.find("a")
            if player_link and player_link.get("href"):
                player_url = BASE_URL + player_link["href"]

            leaders.append(
                Leader(
                    category=category,
                    rank=rank,
                    player_name=player_name,
                    value=value_span.get_text(strip=True),
                    player_url=player_url,
                )
            )

    return leaders


def scrape_leaders() -> List[Leader]:
    html = fetch_leader_html()
    return parse_leaders(html)
