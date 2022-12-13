import re

import requests
from bs4 import BeautifulSoup
from datetime import datetime

class WeatherMaker:
    """
    Use Python3.8
    Сообщает прогноз погоды.
    Обращается к разделу "Погода" на yandex.ru.
    """

    def __init__(self, lat, lon):
        self.url = f'https://yandex.com.am/weather/?lat={lat}&lon={lon}'
        self.headers = {'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.114 YaBrowser/22.9.1.1110 (beta) Yowser/2.5 Safari/537.36'}
        self.forecast = {}

    @staticmethod
    def forecast_parse(web_response):
        weather_parser = BeautifulSoup(web_response, features='html.parser')

        list_of_days = weather_parser.find_all('time', {'class': 'time forecast-briefly__date'})
        day_temperature = weather_parser.find_all('div',
            {'class': 'temp forecast-briefly__temp forecast-briefly__temp_day'})
        night_temperature = weather_parser.find_all('div',
            {'class': 'temp forecast-briefly__temp forecast-briefly__temp_night'})
        atmospheric_precipitation = weather_parser.find_all('div', {'class': 'forecast-briefly__condition'})
        return list_of_days, atmospheric_precipitation, day_temperature, night_temperature

    @staticmethod
    def forecast_cleanup(day, atmospheric, day_temperature, night_temperature):
        day = WeatherMaker.date_cleanup(day)
        atmospheric = WeatherMaker.atmospheric_cleanup(atmospheric)
        day_temperature = WeatherMaker.temperature_cleanup(day_temperature)
        night_temperature = WeatherMaker.temperature_cleanup(night_temperature)
        return [day, atmospheric, day_temperature, night_temperature]
    
    @staticmethod
    def atmospheric_cleanup(atmospheric):
        return atmospheric.text

    @staticmethod
    def temperature_cleanup(temperature):
        temp = temperature.find('span', {'class': 'temp__value temp__value_with-unit'}).text
        temp = str(temp).replace(chr(8722), '-')
        try:
            temp = int(temp)
        except Exception as e:
            temp = 10000
        return temp

    @staticmethod
    def date_cleanup(day):
        date_ = str(day.get('datetime'))[:10]
        date_ = datetime.strptime(date_, "%Y-%m-%d").date()
        return date_

    def read(self):
        """
        Записывает в словарь полученные данные {погода: [Облачная, ...] температура: [10, ...] дата: [datetime, ...]}
        """
        web_response = requests.get(self.url, headers = self.headers)

        if web_response.status_code == 200:
            list_of_days, atmospheric_precipitation, day_temperature, night_temperature = \
                                                        WeatherMaker.forecast_parse(web_response.text)
        else:
            print('Bad response status code...')
            return
        
        for day, atmospheric, day_temperature, night_temperature in zip \
                    (list_of_days, atmospheric_precipitation, day_temperature, night_temperature):
            forecast_instance = WeatherMaker.forecast_cleanup(day, atmospheric, day_temperature, night_temperature)            
            self.forecast[forecast_instance[0]] = forecast_instance[1:]
        
    def get_last_day(self):
        return list(self.forecast.keys())[-1]       

    def get_first_day(self):
        return list(self.forecast.keys())[0]
    
    def get_location(self):
        return self.location

    @staticmethod
    def check_date_str(date):
        if date:
            try:
                date = datetime.strptime(date, "%Y-%m-%d").date()
                # print(date)
            except ValueError as err:
                date = None
        return date

    def prepare_range(self, _from, _to):
        _from = WeatherMaker.check_date_str(_from)
        if not _from:
            _from = self.get_first_day()
        
        _to = WeatherMaker.check_date_str(_to)
        if not _to:
            _to = self.get_last_day()

        if _from > _to:
            _from, _to = _to, _from
            
        return _from, _to

 
    def get(self, _from = None, _to = None):

        _from, _to = self.prepare_range(_from, _to)            

        for _day in self.forecast.keys():
            if _from <= _day <= _to:
              yield (_day, self.forecast[_day])
