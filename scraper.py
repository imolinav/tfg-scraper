import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import pandas as pd

hostname = "localhost"
username = "imolinav"
password = "imolinav"
database = "postgres"

cities = []
cities_url_regex = r'/.*.html'

#spanish_cities = [
#    "A Coruña",
#    "Alacant",
#    "Albacete",
#    "Almería",
#    "Araba",
#    "Asturias",
#    "Ávila",
#    "Badajoz",
#    "Barcelona",
#    "Bizkaia",
#    "Burgos",
#    "Cantabria",
#    "Castelló",
#    "Ceuta",
#    "Ciudad Real",
#    "Cuenca",
#    "Cáceres",
#    "Cádiz",
#    "Córdoba",
#    "Gipuzcoa",
#    "Girona",
#    "Granada",
#    "Guadalajara",
#    "Huelva",
#    "Huesca",
#    "Illes Balears",
#    "Jaén",
#    "La Rioja",
#    "Las Palmas",
#    "León",
#    "Lleida",
#    "Lugo",
#    "Madrid",
#    "Melilla",
#    "Murcia",
#    "Málaga",
#    "Navarra",
#    "Ourense",
#    "Palencia",
#    "Pontevedra",
#    "Salamanca",
#    "Santa Cruz de Tenerife",
#    "Segovia",
#    "Sevilla",
#    "Soria",
#    "Tarragona",
#    "Teruel",
#    "Toledo",
#    "Valladolid",
#    "València",
#    "Zamora",
#    "Zaragoza",
#]

spanish_cities = [
    "Valencia",
#    "Barcelona",
#    "Madrid"
]

def checkCookies(browser):
    accept_button = browser.find_element(By.ID, "onetrust-accept-btn-handler")
    if (accept_button): 
        accept_button.click()

for city in spanish_cities:
    base_url = 'https://www.tripadvisor.es'
    search_url = base_url + '/Search?q=' + city
    city_url = ''
    
    options = Options()
    options.add_argument("--headless=true")
    options.add_argument("start-maximized")
    options.add_argument("--log-level=2")
    browser = webdriver.Chrome(options=options)
    browser.get(search_url)
    WebDriverWait(browser, 15).until(EC.visibility_of_element_located((By.CLASS_NAME, "search-results-list")))
    
    accept_button = browser.find_element(By.ID, "onetrust-accept-btn-handler")
    if (accept_button): 
        accept_button.click()

    content = browser.page_source
    soup = BeautifulSoup(content, "html.parser")

    for result in soup.find("div", {"class": "search-results-list"}).find_all("div", {"class": "result-card"}):
        if (result.find("div", {"class": "result-title"}).find("span").text == city):
            match = re.search(cities_url_regex, result.find("div", {"class": "result-content-columns"})['onclick'])
            if match:
                city_url = match.group()

            id = city_url.split('-')[1]
            attractions_url = city_url.replace('Tourism-' + id, 'Attractions-' + id + '-Activities-oa0')
            restaurants_url = city_url.replace('Tourism', 'Restaurants')

            # retrieving attractions
            browser.get(base_url + attractions_url)
            WebDriverWait(browser, 15).until(EC.visibility_of_element_located((By.CLASS_NAME, "DDJze")))
            
            attractions_list = browser.page_source
            attractions_list_bs = BeautifulSoup(attractions_list, "html.parser")

            for attraction in attractions_list_bs.find("div", {"class": "DDJze"}).find_all("section", {"data-automation": "WebPresentation_SingleFlexCardSection"}):
                attraction_url = attraction.find("div", {"class": "alPVI eNNhq PgLKC tnGGX"}).find("a")['href']

                # single attraction
                browser.get(base_url + attraction_url)
                WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, "ycuCc")))
                
                attraction_page = browser.page_source
                attraction_page_bs = BeautifulSoup(attraction_page, "html.parser")

                attraction_name = attraction_page_bs.find("h1", {"data-automation": "mainH1"}).text
                attraction_puntuation = attraction_page_bs.find("div", {"data-automation": "WebPresentation_PoiOverviewWeb"}).find("div", {"class": "jVDab o W f u w GOdjs"})["aria-label"].split(" ")[0]
                attraction_types = attraction_page_bs.find("div", {"data-automation": "WebPresentation_PoiOverviewWeb"}).find("div", {"class": "fIrGe _T bgMZj"}).text.split(" • ")
                attraction_direction = attraction_page_bs.find("div", {"data-automation": "WebPresentation_PoiLocationSectionGroup"}).find("span", {"class": "biGQs _P XWJSj Wb"}).text if attraction_page_bs.find("div", {"data-automation": "WebPresentation_PoiLocationSectionGroup"}).find("span", {"class": "biGQs _P XWJSj Wb"}).text != "Leer más" else ""
                attraction_description = attraction_page_bs.find("div", {"data-automation": "WebPresentation_AttractionAboutSectionGroup"}).find("span", {"class": "biGQs _P pZUbB KxBGd"}).text if hasattr(attraction_page_bs.find("div", {"data-automation": "WebPresentation_AttractionAboutSectionGroup"}).find("span", {"class": "biGQs _P pZUbB KxBGd"}), "text") else ""

                print("Found " + attraction_name + " with " + attraction_puntuation + " stars and located in " + attraction_direction)
            

# connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
# cur = connection.cursor()

# cur.execute("""INSERT INTO cities (name, postal_code) values (%s, %s)""", ('Valencia', str(46016)))
# connection.commit()
