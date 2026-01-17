import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


class DB_Map():
    def __init__(self, database):
        self.database = database
    
    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                conn.execute(
                    'INSERT INTO users_cities VALUES (?, ?)',
                    (user_id, city_id)
                )
                conn.commit()
                return True
            return False

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT cities.city 
                FROM users_cities  
                JOIN cities ON users_cities.city_id = cities.id
                WHERE users_cities.user_id = ?
            ''', (user_id,))
            return [row[0] for row in cursor.fetchall()]

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT lat, lng
                FROM cities  
                WHERE city = ?
            ''', (city_name,))
            return cursor.fetchone()

    def create_graph(self, path, cities):
        """
        cities: list[str] — список городов
        path: str — путь сохранения картинки
        """
        fig = plt.figure(figsize=(10, 6))
        ax = plt.axes(projection=ccrs.PlateCarree())

        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.LAKES, alpha=0.5)
        ax.add_feature(cfeature.RIVERS)

        for city in cities:
            coords = self.get_coordinates(city)
            if coords:
                lat, lng = coords
                ax.plot(lng, lat, 'ro', markersize=6, transform=ccrs.PlateCarree())
                ax.text(
                    lng + 0.5,
                    lat + 0.5,
                    city,
                    transform=ccrs.PlateCarree(),
                    fontsize=9
                )

        ax.set_global()
        ax.set_title("Cities on map")

        plt.savefig(path, bbox_inches='tight')
        plt.close()
