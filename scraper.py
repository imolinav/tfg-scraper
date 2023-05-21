import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import pandas as pd

db_parameters = {
    "host": "localhost",
    "user": "imolinav",
    "password": "imolinav",
    "dbname": "postgres"
}

cities_url_regex = r'/.*.html'

base_wiki_url = "https://es.wikipedia.org"
base_tripadvisor_url = "https://www.tripadvisor.es"

spanish_cities = [
    "Valencia",
#    "Barcelona",
#    "Madrid"
]

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
browser.get(f"{base_wiki_url}/wiki/Anexo:Provincias_y_ciudades_autónomas_de_España")
WebDriverWait(browser, 15).until(EC.visibility_of_element_located((By.CLASS_NAME, "mw-parser-output")))
wiki_content = BeautifulSoup(browser.page_source, "html.parser")

for city in wiki_content.find("table").find("tbody").find_all("tr"):
    city_url = city.find_all("td")[2].find("a")["href"]
    city_name = city.find_all("td")[2].find("a").text
    cur.execute("INSERT INTO cities (name) values (%s)", (city_name,))
    connection.commit()
    
    print(f"Retrieving data from {city_name}")
    search_url = f"{base_tripadvisor_url}/Search?q={city_name}"
    city_url = ''
    
    browser.get(search_url)
    WebDriverWait(browser, 15).until(EC.visibility_of_element_located((By.CLASS_NAME, "search-results-list")))
    
    accept_button = browser.find_element(By.ID, "onetrust-accept-btn-handler")
    if (accept_button): 
        accept_button.click()

    cities_list = BeautifulSoup(browser.page_source, "html.parser")

    for result in cities_list.find("div", {"class": "search-results-list"}).find_all("div", {"class": "result-card"}):
        if (result.find("div", {"class": "result-title"}).find("span").text == city_name):
            match = re.search(cities_url_regex, result.find("div", {"class": "result-content-columns"})['onclick'])
            if match:
                city_url = match.group()

            id = city_url.split("-")[1]
            attractions_url = city_url.replace(f"Tourism-{id}", f"Attractions-{id}-Activities-oa0")
            restaurants_url = city_url.replace("Tourism", "Restaurants")

            # retrieving attractions
            browser.get(base_tripadvisor_url + attractions_url)
            WebDriverWait(browser, 15).until(EC.visibility_of_element_located((By.CLASS_NAME, "DDJze")))
            attractions_list = BeautifulSoup(browser.page_source, "html.parser")

            print(f"Saving attractions")

            for attraction in attractions_list.find("div", {"class": "DDJze"}).find_all("section", {"data-automation": "WebPresentation_SingleFlexCardSection"}):
                attraction_url = attraction.find("div", {"class": "alPVI eNNhq PgLKC tnGGX"}).find("a")['href']

                # single attraction
                browser.get(base_tripadvisor_url + attraction_url)
                WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, "ycuCc")))
                attraction_page = BeautifulSoup(browser.page_source, "html.parser")

                attraction_name = attraction_page.find("h1", {"data-automation": "mainH1"}).text
                attraction_score = attraction_page.find("div", {"data-automation": "WebPresentation_PoiOverviewWeb"}).find("div", {"class": "jVDab o W f u w GOdjs"})["aria-label"].split(" ")[0]
                attraction_types = attraction_page.find("div", {"data-automation": "WebPresentation_PoiOverviewWeb"}).find("div", {"class": "fIrGe _T bgMZj"}).text.split(" • ")
                """ if attraction_page.find("div", {"data-automation": "WebPresentation_PoiLocationSectionGroup"}).find("span", {"class": "biGQs _P XWJSj Wb"}) and attraction_page.find("div", {"data-automation": "WebPresentation_PoiLocationSectionGroup"}).find("span", {"class": "biGQs _P XWJSj Wb"}).text != "Leer más":
                    attraction_direction = attraction_page.find("div", {"data-automation": "WebPresentation_PoiLocationSectionGroup"}).find("span", {"class": "biGQs _P XWJSj Wb"}).text
                else:
                    attraction_direction = "" """

                print(attraction_name + " - " + attraction_score + " ⭐ - " + " 🗺️", end='\r')

            # retrieving restaurants
            browser.get(base_tripadvisor_url + restaurants_url)
            WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, "coverpage-list-container")))
            restaurants_list = BeautifulSoup(browser.page_source, "html.parser")
            
            print(f"Saving restaurants")

            for restaurant in restaurants_list.find("div", {"data-test-target": "restaurants-list"}).find_all("div", {"class": "ygtQB Gi o"}):
                if (restaurant['data-test'] == "SL_list_item"):
                    continue
                restaurant_url = restaurant.find("a", {"class": "Lwqic Cj b"})['href']

                # single restaurant
                browser.get(base_tripadvisor_url + restaurant_url)
                WebDriverWait(browser, 15).until(EC.visibility_of_element_located((By.CLASS_NAME, "HjBfq")))
                restaurant_page = BeautifulSoup(browser.page_source, "html.parser")

                restaurant_name = restaurant_page.find("h1", {"data-test-target": "top-info-header"}).text
                restaurant_score = restaurant_page.find("div", {"data-test-target": "restaurant-detail-info"}).find("svg", {"class": "UctUV d H0"})['aria-label'].split(" ")[0]
                restaurant_direction = restaurant_page.find("div", {"data-test-target": "restaurant-detail-info"}).find_all("a", {"class": "AYHFM"})[1].text

                print(restaurant_name + " - " + restaurant_score + " ⭐ - " + restaurant_direction + " 🗺️\r")



# cur.execute("""INSERT INTO cities (name, postal_code) values (%s, %s)""", ('Valencia', str(46016)))
# connection.commit()
