import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.feature import NaturalEarthFeature

class DB_Map():
    def __init__(self, database):
        self.database = database

    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users_cities (
                    user_id INTEGER,
                    city_id TEXT,
                    FOREIGN KEY(city_id) REFERENCES cities(id)
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users_settings (
                    user_id INTEGER PRIMARY KEY,
                    marker_color TEXT DEFAULT 'red'
                )
            ''')
            conn.commit()

    # ---------- НАСТРОЙКИ ----------

    def set_marker_color(self, user_id, color):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''
                INSERT INTO users_settings (user_id, marker_color)
                VALUES (?, ?)
                ON CONFLICT(user_id)
                DO UPDATE SET marker_color=excluded.marker_color
            ''', (user_id, color))
            conn.commit()

    def get_marker_color(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT marker_color FROM users_settings WHERE user_id=?",
                (user_id,)
            )
            res = cursor.fetchone()
            return res[0] if res else 'red'

    # ---------- ГОРОДА ----------

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT lat, lng FROM cities WHERE city=?",
                (city_name,)
            )
            return cursor.fetchone()

    # ---------- КАРТА ----------

    def create_graph(self, path, cities, marker_color='red'):
        fig = plt.figure(figsize=(12, 7))
        ax = plt.axes(projection=ccrs.PlateCarree())

        # 🌍 Заливка океанов и континентов
        ax.add_feature(cfeature.OCEAN, facecolor='#A6CAE0')
        ax.add_feature(cfeature.LAND, facecolor='#E0E0C8')

        # 🗺 Географические объекты
        ax.add_feature(cfeature.COASTLINE, linewidth=1)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.LAKES, alpha=0.6)
        ax.add_feature(cfeature.RIVERS, linewidth=0.8)

        # 📍 Города
        for city in cities:
            coords = self.get_coordinates(city)
            if coords:
                lat, lng = coords

                ax.scatter(
                    lng, lat,
                    color=marker_color,
                    s=60,
                    edgecolors='black',
                    transform=ccrs.PlateCarree(),
                    zorder=5
                )

                ax.text(
                    lng + 0.3,
                    lat + 0.3,
                    city,
                    fontsize=9,
                    transform=ccrs.PlateCarree()
                )

        ax.set_global()
        ax.set_title("Cities on map 🌍")

        plt.savefig(path, bbox_inches='tight')
        plt.close()
    
    def get_cities_by_country(self, country):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT city FROM cities WHERE country = ?",
                (country,)
            )
            return [row[0] for row in cursor.fetchall()]
        
    def get_cities_by_population(self, min_population, max_population=None):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()

            if max_population:
                cursor.execute(
                    "SELECT city FROM cities WHERE population BETWEEN ? AND ?",
                    (min_population, max_population)
                )
            else:
                cursor.execute(
                    "SELECT city FROM cities WHERE population >= ?",
                    (min_population,)
                )

            return [row[0] for row in cursor.fetchall()]
        
    def get_cities_by_country_and_population(
        self, country, min_population, max_population=None
):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()

            if max_population:
                cursor.execute(
                    '''
                    SELECT city FROM cities
                    WHERE country = ?
                    AND population BETWEEN ? AND ?
                    ''',
                    (country, min_population, max_population)
                )
            else:
                cursor.execute(
                    '''
                    SELECT city FROM cities
                    WHERE country = ?
                    AND population >= ?
                    ''',
                    (country, min_population)
                )

            return [row[0] for row in cursor.fetchall()]


