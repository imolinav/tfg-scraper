import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
import re


class city:
    def __init__(self, name, latitude, longitude, population, altitude, govern_party):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.population = population
        self.altitude = altitude
        self.govern_party = govern_party


db_parameters = {
    "host": "localhost",
    "user": "imolinav",
    "password": "imolinav",
    "dbname": "postgres",
}

spanish_cities = [
    city("Álava", "42º50'N", "2º45'O", 334412, 650, "PNV"),
    city("Albacete", "38º50'N", "2º00'O", 386464, 845, "PSOE"),
    city("Alicante", "38º30'N", "0º30'O", 1901594, 300, "PP"),
    city("Almería", "37º10'N", "2º20'O", 731792, 400, "PP"),
    city("Asturias", "43º20'N", "6º00'O", 1004499, 700, "PSOE"),
    city("Ávila", "40º36'N", "4º55'O", 158421, 1132, "XAV"),
    city("Badajoz", "38º40'N", "6º10'O", 666971, 185, "PP"),
    city("Barcelona", "41º27'N", "2º05'E", 5714730, 12, "En Comú"),
    city("Burgos", "42º23'N", "3º40'O", 358171, 800, "PSOE"),
    city("Cáceres", "39º40'N", "6º00'O", 389558, 430, "PSOE"),
    city("Cádiz", "36º30'N", "5º45'O", 1260204, 11, "Adelante Andalucía"),
    city("Cantabria", "43º20'N", "4º00'O", 585222, 600, "PRC"),
    city("Provincia de Castellón", "40º10'N", "0º10'O", 587064, 30, "PSOE"),
    city("Ciudad Real", "39º00'N", "4º00'O", 492591, 628, "Ciudadanos"),
    city("Córdoba", "38º00'N", "4º50'O", 781451, 106, "PP"),
    city("A Coruña", "43º22'N", "8º24'O", 1120134, 0, "PSOE"),
    city("Cuenca", "42º00'N", "2º00'O", 195516, 946, "PSOE"),
    city("Girona", "42º10'N", "2º40'E", 786596, 76, "Junts per Catalunya"),
    city("Granada", "37º15'N", "3º15'O", 921987, 1070, "PSOE"),
    city("Guadalajara", "40º50'N", "2º30'O", 265588, 854, "PSOE"),
    city("Huelva", "37º40'N", "7º00'O", 528763, 54, "PSOE"),
    city("Huesca", "42º10'N", "0º10'O", 225456, 488, "PSOE"),
    city("Islas Baleares", "39º30'N", "3º00'E", 1176254, 140, "PSOE"),
    city("Jaén", "38º00'N", "3º30'O", 627190, 733, "PSOE"),
    city("León", "42º37'N", "5º50'O", 448179, 837, "PSOE"),
    city("Lleida", "42º00'N", "1º10'E", 439727, 155, "ERC"),
    city("Lugo", "43º00'N", "7º30'O", 326013, 465, "PSOE"),
    city("Madrid", "40º25'N", "3º41'O", 6744456, 678, "PP"),
    city("Málaga", "36º43'N", "4º25'O", 1717504, 500, "PP"),
    city("Murcia", "38º00'N", "1º50'O", 1531439, 348, "PP"),
    city("Navarra", "42º49'N", "1º39'O", 664117, 400, "PSOE"),
    city("Ourense", "42º10'N", "7º30'O", 304280, 132, "Democracia Ourensana"),
    city("Palencia", "42º25'N", "4º31'O", 158008, 940, "PP"),
    city("Las Palmas de Gran Canaria", "28º20'N", "14º20'O", 1128395, 8, "PSOE"),
    city("Pontevedra", "42º26'N", "8º38'O", 944275, 20, "BNG"),
    city("La Rioja", "42º15'N", "2º30'O", 319485, 850, "PSOE"),
    city("Salamanca", "40º50'N", "6º00'O", 327338, 823, "PP"),
    city("Segovia", "41º10'N", "4º00'O", 153803, 1005, "PSOE"),
    city("Sevilla", "37º30'N", "5º30'O", 1963000, 200, "PSOE"),
    city("Soria", "41º40'N", "2º40'O", 88747, 1065, "PSOE"),
    city("Tarragona", "41º10'N", "1º00'E", 822309, 68, "ERC"),
    city(
        "Santa Cruz de Tenerife",
        "28º10'N",
        "17º20'O",
        1048306,
        120,
        "Coalición Canaria",
    ),
    city("Teruel", "40º40'N", "0º40'O", 134545, 1050, "PP"),
    city("Toledo", "39º50'N", "4º00'O", 709403, 600, "PSOE"),
    city("Valencia", "39º20'N", "0º50'O", 2589312, 500, "PSOE"),
    city("Valladolid", "41º35'N", "4º40'O", 519361, 700, "PSOE"),
    city("Zamora", "41º45'N", "6º00'O", 167215, 652, "PP"),
    city("Zaragoza", "41º35'N", "1º00'O", 967452, 243, "PP"),
]

cities_url_regex = r"/.*.html"

base_tripadvisor_url = "https://www.tripadvisor.es"


def initializeWebdriver():
    options = Options()
    options.add_argument("--headless=true")
    options.add_argument("start-maximized")
    options.add_argument("--log-level=2")
    return webdriver.Chrome(options=options)


browser = initializeWebdriver()

connection = psycopg2.connect(**db_parameters)
cur = connection.cursor()

# retrieving cities
for city in spanish_cities:
    city_id = 0
    cur.execute("SELECT id FROM cities WHERE name = %s", (city.name,))
    found = cur.fetchone()
    if found is None:
        cur.execute(
            "INSERT INTO cities (name, latitude, longitude, population, altitude, govern_party) values (%s, %s, %s, %s, %s, %s) RETURNING id",
            (
                city.name,
                city.latitude,
                city.longitude,
                city.population,
                city.altitude,
                city.govern_party,
            ),
        )
        city_id = int(cur.fetchone()[0])
        connection.commit()
    else:
        city_id = int(found[0])

    print(f"Retrieving data from {city.name}")
    search_url = f"{base_tripadvisor_url}/Search?q={city.name}"
    city_url = ""

    browser.get(search_url)
    try:
        WebDriverWait(browser, 100).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "search-results-list"))
        )
    except TimeoutException:
        continue

    try:
        accept_button = browser.find_element(By.ID, "onetrust-accept-btn-handler")
        accept_button.click()
    except NoSuchElementException:
        pass

    cities_list = BeautifulSoup(browser.page_source, "html.parser")

    for result in cities_list.find("div", {"class": "search-results-list"}).find_all(
        "div", {"class": "result-card"}
    ):
        if (
            result.find("div", {"class": "result-title"}).find("span").text == city.name
            and result.find("div", {"class": "location-string"}) != None
            and result.find("div", {"class": "location-string"}).text.find("España")
            != -1
        ):
            match = re.search(
                cities_url_regex,
                result.find("div", {"class": "result-content-columns"})["onclick"],
            )
            if match:
                city_url = match.group()

            id = city_url.split("-")[1]
            attractions_url = city_url.replace(
                f"Tourism-{id}", f"Attractions-{id}-Activities-oa0"
            )
            restaurants_url = city_url.replace("Tourism", "Restaurants")

            # retrieving attractions
            browser.get(base_tripadvisor_url + attractions_url)

            try:
                WebDriverWait(browser, 100).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "DDJze"))
                )
            except TimeoutException:
                continue
        
            attractions_list = BeautifulSoup(browser.page_source, "html.parser")

            print(f"Saving attractions")

            for attraction in attractions_list.find("div", {"class": "DDJze"}).find_all(
                "section", {"data-automation": "WebPresentation_SingleFlexCardSection"}
            ):
                attraction_url = attraction.find(
                    "div", {"class": "alPVI eNNhq PgLKC tnGGX"}
                ).find("a")["href"]

                # single attraction
                browser.get(base_tripadvisor_url + attraction_url)

                try:
                    WebDriverWait(browser, 100).until(
                        EC.visibility_of_element_located((By.CLASS_NAME, "ycuCc"))
                    )
                except TimeoutException:
                    continue

                attraction_page = BeautifulSoup(browser.page_source, "html.parser")

                try:
                    attraction_name = attraction_page.find(
                        "h1", {"data-automation": "mainH1"}
                    ).text
                except:
                    attraction_name = ""

                try:
                    attraction_score = (
                        attraction_page.find(
                            "div", {"data-automation": "WebPresentation_PoiOverviewWeb"}
                        )
                        .find("div", {"class": "jVDab o W f u w GOdjs"})["aria-label"]
                        .split(" ")[0]
                    )
                except:
                    attraction_score = "-1"

                attraction_types = (
                    attraction_page.find(
                        "div", {"data-automation": "WebPresentation_PoiOverviewWeb"}
                    )
                    .find("div", {"class": "fIrGe _T bgMZj"})
                    .text.split(" • ")
                )

                try:
                    attraction_direction = attraction_page.find("div", {"data-automation": "WebPresentation_PoiLocationSectionGroup"}).find("button", {"class": "UikNM _G B- _S _T c G_ P0 wSSLS wnNQG raEKE"}).find("span", {"class": "biGQs _P XWJSj Wb"})
                except:
                    attraction_direction = ""
                attraction_description = ""

                cur.execute(
                    "SELECT * FROM entities WHERE name = %s AND city_id = %s",
                    (
                        attraction_name,
                        city_id,
                    ),
                )
                found = cur.fetchone()
                if found is None:
                    cur.execute(
                        "INSERT INTO entities (name, score, address, city_id) values (%s, %s, %s, %s) RETURNING id",
                        (
                            attraction_name,
                            attraction_score,
                            attraction_direction,
                            city_id,
                        ),
                    )
                    entity_id = int(cur.fetchone()[0])
                    connection.commit()
                    for entity_type in attraction_types:
                        cur.execute(
                            "INSERT INTO entity_types (entity_id, type) values (%s, %s)",
                            (
                                entity_id,
                                entity_type,
                            ),
                        )
                        connection.commit()

                print(attraction_name + " - " + attraction_score + " ⭐ - " + " 🗺️")

            # retrieving restaurants
            browser.get(base_tripadvisor_url + restaurants_url)

            try:
                WebDriverWait(browser, 100).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "coverpage-list-container"))
                )
            except TimeoutException:
                continue

            restaurants_list = BeautifulSoup(browser.page_source, "html.parser")

            print(f"Saving restaurants")

            for restaurant in restaurants_list.find(
                "div", {"data-test-target": "restaurants-list"}
            ).find_all("div", {"class": "ygtQB Gi o"}):
                if restaurant["data-test"] == "SL_list_item":
                    continue
                restaurant_url = restaurant.find("a", {"class": "Lwqic Cj b"})["href"]

                # single restaurant
                browser.get(base_tripadvisor_url + restaurant_url)

                try:
                    WebDriverWait(browser, 100).until(
                        EC.visibility_of_element_located((By.CLASS_NAME, "HjBfq"))
                    )
                except TimeoutException:
                    continue
                
                restaurant_page = BeautifulSoup(browser.page_source, "html.parser")

                restaurant_name = restaurant_page.find(
                    "h1", {"data-test-target": "top-info-header"}
                ).text
                restaurant_score = (
                    restaurant_page.find(
                        "div", {"data-test-target": "restaurant-detail-info"}
                    )
                    .find("svg", {"class": "UctUV d H0"})["aria-label"]
                    .split(" ")[0]
                )
                restaurant_direction = (
                    restaurant_page.find(
                        "div", {"data-test-target": "restaurant-detail-info"}
                    )
                    .find("a", {"href": "#MAPVIEW"})
                    .text
                )

                cur.execute(
                    "SELECT * FROM entities WHERE name = %s AND city_id = %s",
                    (
                        restaurant_name,
                        city_id,
                    ),
                )
                found = cur.fetchone()
                if found is None:
                    cur.execute(
                        "INSERT INTO entities (name, score, address, city_id) values (%s, %s, %s, %s) RETURNING id",
                        (
                            restaurant_name,
                            restaurant_score,
                            restaurant_direction,
                            city_id,
                        ),
                    )
                    entity_id = int(cur.fetchone()[0])
                    connection.commit()
                    cur.execute(
                        "INSERT INTO entity_types (entity_id, type) values (%s, %s)",
                        (
                            entity_id,
                            "Restaurant",
                        ),
                    )
                    connection.commit()

                print(
                    restaurant_name
                    + " - "
                    + restaurant_score
                    + " ⭐ - "
                    + restaurant_direction
                    + " 🗺️\r"
                )

        continue
