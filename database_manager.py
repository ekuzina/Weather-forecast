import re
import peewee


database = peewee.SqliteDatabase('weather_forecast.db')
from datetime import datetime


class BaseTable(peewee.Model):
    class Meta:
        database = database

class Location(BaseTable):
    # автоинкрементный первичный ключи формируется автоматически
    location  = peewee.CharField(unique = True)
    latitude  = peewee.DoubleField()
    longitude = peewee.DoubleField()

    # название таблицы формируется автоматически

class WeatherForecast(BaseTable):
    date = peewee.DateField(unique = True)
    weather = peewee.CharField()
    temperature_day   = peewee.SmallIntegerField()
    temperature_night = peewee.SmallIntegerField()
    
    location = peewee.ForeignKeyField(Location, to_field='id')

class DatabaseManager():
    ''' Выполняет запись и чтение из БД. '''

    def __init__(self):
        self.hardcode_location()

    def hardcode_location(self):
        result = (Location
          .insert(
            location = 'НИЯУ МИФИ (г. Москва)',
            latitude = 55.6501703776999,
            longitude = 37.66533398689662
          )
          .on_conflict_ignore()
          .execute())        
    
    def get_location(self):
    ''' Извлечение местоположения из таблицы Location '''

        query = Location.select().where(Location.id == 1).limit(1)
        for q in query:
            return q.location, q.latitude, q.longitude

    def get_location_fk(self):
    ''' Извлечение местоположения по вторичному ключу (в учебных целях) '''

        query = ( Location
         .select(Location.location.alias('loc'))
         .join(WeatherForecast)
         .where(WeatherForecast.location == 1).limit(1)
        )
        for q in query:
            return q.loc

    def save(self, data):
        result = (WeatherForecast
          .insert(
            date = data[0],
            weather = data[1][0],
            temperature_day = data[1][1],
            temperature_night = data[1][2],
            location = 1
          )
          .on_conflict_replace()
          .execute())

    @staticmethod
    def check_date_str(date):
    ''' Проверка корректности формата даты ''' 

        if date:
            try:
                date = datetime.strptime(date , "%Y-%m-%d").date()
            except ValueError as err:
                date = None
        return date


    def get_last_day(self):
        return WeatherForecast.select(peewee.fn.MAX(WeatherForecast.date)).scalar()

    def prepare_range(self, _from, _to):
    ''' Формирование значений граничных дат по умолчанию ''' 

        _from = DatabaseUpdater.check_date_str(_from)
        if not _from:
            today = datetime.today().date()
            _from = today

        _to = DatabaseUpdater.check_date_str(_to)
        if not _to:
            _to = self.get_last_day()

        if _from > _to:
            _from, _to = _to, _from

        return _from, _to


    def get(self, _from = None, _to = None):
        _from, _to = self.prepare_range(_from, _to)
        res = WeatherForecast.select().where(WeatherForecast.date.between(_from, _to))
        return res 

    def print(self, _from, _to=None):
        res = self.get(_from, _to)
        for data in res:
            print('{0}:\t{1}. Днем {2:+}*C, ночью {3:+}*C.'\
                .format(data.date.strftime('%Y-%m-%d'), data.weather, data.temperature_day, data.temperature_night))
