import psycopg2

hostname = "localhost"
username = "imolinav"
password = "imolinav"
database = "postgres"

spanish_cities = [
    "A Coruña",
    "Alacant",
    "Albacete",
    "Almería",
    "Araba",
    "Asturias",
    "Badajoz",
    "Barcelona",
    "Bizkaia",
    "Burgos",
    "Cantabria",
    "Castelló",
    "Ceuta",
    "Ciudad Real",
    "Cuenca",
    "Cáceres",
    "Cádiz",
    "Córdoba",
    "Gipuzcoa",
    "Girona",
    "Granada",
    "Guadalajara",
    "Huelva",
    "Huesca",
    "Illes Balears",
    "Jaén",
    "La Rioja",
    "Las Palmas",
    "León",
    "Lleida",
    "Lugo",
    "Madrid",
    "Melilla",
    "Murcia",
    "Málaga",
    "Navarra",
    "Ourense",
    "Palencia",
    "Pontevedra",
    "Salamanca",
    "Santa Cruz de Tenerife",
    "Segovia",
    "Sevilla",
    "Soria",
    "Tarragona",
    "Teruel",
    "Toledo",
    "Valladolid",
    "València",
    "Zamora",
    "Zaragoza",
    "Ávila",
]

for city in spanish_cities:
    print(city)

# connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
# cur = connection.cursor()

# cur.execute("""INSERT INTO cities (name, postal_code) values (%s, %s)""", ('Valencia', str(46016)))
# connection.commit()
