"""Regional Rail station names for the SEPTA Arrivals and NextToArrive APIs.

Official source: https://www3.septa.org/VIRegionalRail.html

The API requires the *parameter* string exactly (spaces and capitalization).
Display names sometimes differ from those parameters.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RailStation:
    display_name: str
    api_name: str


# Official Regional Rail Inputs list, plus Wawa (present in live TrainView /
# Arrivals data but missing from the published input page).
REGIONAL_RAIL_STATIONS: tuple[RailStation, ...] = (
    RailStation("9th Street Station", "9th St"),
    RailStation("30th Street Station", "30th Street Station"),
    RailStation("49th Street", "49th St"),
    RailStation("Airport Terminal A", "Airport Terminal A"),
    RailStation("Airport Terminal B", "Airport Terminal B"),
    RailStation("Airport Terminals C & D", "Airport Terminal C-D"),
    RailStation("Airport Terminals E & F", "Airport Terminal E-F"),
    RailStation("Allegheny", "Allegheny"),
    RailStation("Allen Lane", "Allen Lane"),
    RailStation("Ambler", "Ambler"),
    RailStation("Angora", "Angora"),
    RailStation("Ardmore", "Ardmore"),
    RailStation("Ardsley", "Ardsley"),
    RailStation("Bala", "Bala"),
    RailStation("Berwyn", "Berwyn"),
    RailStation("Bethayres", "Bethayres"),
    RailStation("Bridesburg", "Bridesburg"),
    RailStation("Bristol", "Bristol"),
    RailStation("Bryn Mawr", "Bryn Mawr"),
    RailStation("Carpenter", "Carpenter"),
    RailStation("Chalfont", "Chalfont"),
    RailStation("Chelten Avenue", "Chelten Avenue"),
    RailStation("Cheltenham", "Cheltenham"),
    RailStation("Chester Transportation Center", "Chester TC"),
    RailStation("Chestnut Hill East", "Chestnut Hill East"),
    RailStation("Chestnut Hill West", "Chestnut Hill West"),
    RailStation("Churchmans Crossing", "Churchmans Crossing"),
    RailStation("Claymont", "Claymont"),
    RailStation("Clifton-Aldan", "Clifton-Aldan"),
    RailStation("Colmar", "Colmar"),
    RailStation("Conshohocken", "Conshohocken"),
    RailStation("Cornwells Heights", "Cornwells Heights"),
    RailStation("Crestmont", "Crestmont"),
    RailStation("Croydon", "Croydon"),
    RailStation("Crum Lynne", "Crum Lynne"),
    RailStation("Curtis Park", "Curtis Park"),
    RailStation("Cynwyd", "Cynwyd"),
    RailStation("Darby", "Darby"),
    RailStation("Daylesford", "Daylesford"),
    RailStation("Delaware Valley College", "Delaware Valley College"),
    RailStation("Devon", "Devon"),
    RailStation("Downingtown", "Downingtown"),
    RailStation("Doylestown", "Doylestown"),
    RailStation("East Falls", "East Falls"),
    RailStation("Eastwick Station", "Eastwick Station"),
    RailStation("Eddington", "Eddington"),
    RailStation("Eddystone", "Eddystone"),
    RailStation("Elkins Park", "Elkins Park"),
    RailStation("Elm Street, Norristown", "Elm St"),
    RailStation("Elwyn", "Elwyn Station"),
    RailStation("Exton", "Exton"),
    RailStation("Fern Rock Transportation Center", "Fern Rock TC"),
    RailStation("Fernwood–Yeadon", "Fernwood"),
    RailStation("Folcroft", "Folcroft"),
    RailStation("Forest Hills", "Forest Hills"),
    RailStation("Fort Washington", "Ft Washington"),
    RailStation("Fortuna", "Fortuna"),
    RailStation("Fox Chase", "Fox Chase"),
    RailStation("Germantown", "Germantown"),
    RailStation("Gladstone", "Gladstone"),
    RailStation("Glenolden", "Glenolden"),
    RailStation("Glenside", "Glenside"),
    RailStation("Gravers", "Gravers"),
    RailStation("Gwynedd Valley", "Gwynedd Valley"),
    RailStation("Hatboro", "Hatboro"),
    RailStation("Haverford", "Haverford"),
    RailStation("Highland", "Highland"),
    RailStation("Highland Avenue", "Highland Ave"),
    RailStation("Holmesburg Junction", "Holmesburg Jct"),
    RailStation("Ivy Ridge", "Ivy Ridge"),
    RailStation("Jefferson Station (Market East)", "Market East"),
    RailStation("Jenkintown-Wyncote", "Jenkintown-Wyncote"),
    RailStation("Langhorne", "Langhorne"),
    RailStation("Lansdale", "Lansdale"),
    RailStation("Lansdowne", "Lansdowne"),
    RailStation("Lawndale", "Lawndale"),
    RailStation("Levittown", "Levittown"),
    RailStation("Link Belt", "Link Belt"),
    RailStation("Main Street, Norristown", "Main St"),
    RailStation("Malvern", "Malvern"),
    RailStation("Manayunk", "Manayunk"),
    RailStation("Marcus Hook", "Marcus Hook"),
    RailStation("Meadowbrook", "Meadowbrook"),
    RailStation("Media", "Media"),
    RailStation("Melrose Park", "Melrose Park"),
    RailStation("Merion", "Merion"),
    RailStation("Miquon", "Miquon"),
    RailStation("Morton", "Morton"),
    RailStation("Mount Airy", "Mt Airy"),
    RailStation("Moylan-Rose Valley", "Moylan-Rose Valley"),
    RailStation("Narberth", "Narberth"),
    RailStation("Neshaminy Falls", "Neshaminy Falls"),
    RailStation("New Britain", "New Britain"),
    RailStation("Newark", "Newark"),
    RailStation("Noble", "Noble"),
    RailStation("Norristown Transportation Center", "Norristown TC"),
    RailStation("North Broad", "North Broad St"),
    RailStation("North Hills", "North Hills"),
    RailStation("North Philadelphia", "North Philadelphia"),
    RailStation("North Wales", "North Wales"),
    RailStation("Norwood", "Norwood"),
    RailStation("Olney", "Olney"),
    RailStation("Oreland", "Oreland"),
    RailStation("Overbrook", "Overbrook"),
    RailStation("Paoli", "Paoli"),
    RailStation("Penllyn", "Penllyn"),
    RailStation("Pennbrook", "Pennbrook"),
    RailStation("Penn Medicine Station (University City)", "Penn Medicine Station"),
    RailStation("Philmont", "Philmont"),
    RailStation("Primos", "Primos"),
    RailStation("Prospect Park", "Prospect Park"),
    RailStation("Queen Lane", "Queen Lane"),
    RailStation("Radnor", "Radnor"),
    RailStation("Ridley Park", "Ridley Park"),
    RailStation("Rosemont", "Rosemont"),
    RailStation("Roslyn", "Roslyn"),
    RailStation("Rydal", "Rydal"),
    RailStation("Ryers", "Ryers"),
    RailStation("Secane", "Secane"),
    RailStation("Sedgwick", "Sedgwick"),
    RailStation("Sharon Hill", "Sharon Hill"),
    RailStation("Somerton", "Somerton"),
    RailStation("Spring Mill", "Spring Mill"),
    RailStation("St. Davids", "St. Davids"),
    RailStation("St. Martins", "St. Martins"),
    RailStation("Stenton", "Stenton"),
    RailStation("Strafford", "Strafford"),
    RailStation("Suburban Station", "Suburban Station"),
    RailStation("Swarthmore", "Swarthmore"),
    RailStation("Tacony", "Tacony"),
    RailStation("Temple University", "Temple U"),
    RailStation("Thorndale", "Thorndale"),
    RailStation("Torresdale", "Torresdale"),
    RailStation("Trenton Transit Center", "Trenton"),
    RailStation("Trevose", "Trevose"),
    RailStation("Tulpehocken", "Tulpehocken"),
    RailStation("Upsal", "Upsal"),
    RailStation("Villanova", "Villanova"),
    RailStation("Wawa", "Wawa"),
    RailStation("Wallingford", "Wallingford"),
    RailStation("Warminster", "Warminster"),
    RailStation("Washington Lane", "Washington Lane"),
    RailStation("Wayne", "Wayne"),
    RailStation("Wayne Junction", "Wayne Jct"),
    RailStation("West Trenton", "West Trenton"),
    RailStation("Whitford", "Whitford"),
    RailStation("Willow Grove", "Willow Grove"),
    RailStation("Wilmington", "Wilmington"),
    RailStation("Wissahickon", "Wissahickon"),
    RailStation("Wister", "Wister"),
    RailStation("Woodbourne", "Woodbourne"),
    RailStation("Wyndmoor", "Wyndmoor"),
    RailStation("Wynnefield Avenue", "Wynnefield Avenue"),
    RailStation("Wynnewood", "Wynnewood"),
    RailStation("Yardley", "Yardley"),
)

# Extra aliases seen in TrainView / Arrivals payloads that are not official
# input names but should still resolve to a valid API parameter.
_ALIASES = {
    "jefferson station": "Market East",
    "jefferson": "Market East",
    "market east": "Market East",
    "30th st": "30th Street Station",
    "30th street": "30th Street Station",
    "gray 30th street": "30th Street Station",
    "university city": "Penn Medicine Station",
    "penn medicine": "Penn Medicine Station",
    "temple": "Temple U",
    "temple university": "Temple U",
    "eastwick": "Eastwick Station",
    "elwyn": "Elwyn Station",
    "wayne junction": "Wayne Jct",
    "norristown": "Norristown TC",
    "fern rock": "Fern Rock TC",
}


def resolve_station(name: str) -> str:
    """Return the official API station parameter for a display name or alias."""
    raw = (name or "").strip()
    if not raw:
        raise ValueError("Station name is required")

    lowered = raw.casefold()
    for station in REGIONAL_RAIL_STATIONS:
        if station.api_name.casefold() == lowered or station.display_name.casefold() == lowered:
            return station.api_name

    alias = _ALIASES.get(lowered)
    if alias:
        return alias

    raise ValueError(
        f"Unknown Regional Rail station {name!r}. "
        "Use an official name from https://www3.septa.org/VIRegionalRail.html"
    )


def station_choices() -> list[str]:
    """Display labels for combo boxes, using the official API parameter in parens when it differs."""
    choices = []
    for station in REGIONAL_RAIL_STATIONS:
        if station.display_name == station.api_name:
            choices.append(station.display_name)
        else:
            choices.append(f"{station.display_name} [{station.api_name}]")
    return choices


def api_name_from_choice(choice: str) -> str:
    """Extract the API parameter from a combo-box label or free-typed station name."""
    text = (choice or "").strip()
    if text.endswith("]") and "[" in text:
        text = text[text.rfind("[") + 1 : -1]
    return resolve_station(text)
