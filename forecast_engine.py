import re

import requests
from bs4 import BeautifulSoup


class WeatherMaker:
    """
    Use Python3.8
    Сообщает прогноз погоды.
    Обращается к разделу "Погода" на yandex.ru.
    """

    def __init__(self):
        self.url = 'https://yandex.ru/pogoda/saint-petersburg?utm_campaign=informer&utm_content=' \
                   'main_informer&utm_medium=web&utm_source=home&utm_term=title'
        self.weather_forecast = {'погода': [], 'температура': [], 'дата': []}

    def get_weather(self):
        """
        Записывает в словарь полученные данные {погода: [Облачная, ...] температура: [10, ...] дата: [datetime, ...]}
        """

        # регулярное выражение будет проверять и искать дату. формат даты '2020-11-01'
        template_for_date = r'\d{4}[-]([0][0-9]{1,2}|[1][0-2]{1,2})[-]([0-2][0-9]{1,2}|[3][0-1]{1,2})'
        check_date = re.compile(template_for_date)

        web_response = requests.get(self.url)
        if web_response.status_code == 200:
            weather_parser = BeautifulSoup(web_response.text, features='html.parser')
            list_of_days = weather_parser.find_all('time', {'class': 'time forecast-briefly__date'})
            day_temperature = weather_parser.find_all(
                'div',
                {'class': ['temp forecast-briefly__temp forecast-briefly__temp_day', 'temp__value']})
            night_temperature = weather_parser.find_all(
                'div',
                {'class': ['temp forecast-briefly__temp forecast-briefly__temp_night', 'temp__value']})
            atmospheric_precipitation = weather_parser.find_all('div', {'class': 'forecast-briefly__condition'})

        for atmospheric, day_temperature, night_temperature, day in zip \
                    (atmospheric_precipitation, day_temperature, night_temperature, list_of_days):
            self.weather_forecast['погода'].append(atmospheric.text)
            # Меняем букву ё на е и убираем символ градусов, т.к. cv2 не поддерживает эти символы
            temperature = (str(day_temperature.text)[:-1].replace('ё', 'е'), str(night_temperature.text)[:-1])
            # Меняем знак минус (ord 8722) на поддерживаемый cv2 '-'(ord 45)
            temperature = (temperature[0].replace(chr(8722), '-'), temperature[1].replace(chr(8722), '-'))
            self.weather_forecast['температура'].append(temperature)
            date = re.search(check_date, str(day))
            date = date[0]
            self.weather_forecast['дата'].append(date)

    def prepare_data(self, index_number):
        """
        Формирует из словаря кортеж с прогнозом погоды на один день (дата, погода, температура днем, температура ночью).
        """
        day = self.weather_forecast['дата'][index_number]
        _weather = self.weather_forecast['погода'][index_number]
        temperature = self.weather_forecast['температура'][index_number]
        result = (day, _weather, temperature[0], temperature[1])
        return result

    def show_weather(self, period=1, archive=False):
        """
        Возвращает кортеж с прогнозом погоды на нужное количество дней.
        :param period: количество дней, на которое необходимо получить прогноз. Максимально - на 31 день вперед.
        :param archive: архив погоды за предыдущие четыре дня.
        """

        total_quantity_days = len(self.weather_forecast['дата'])  # Общее количество дней, на которые есть прогноз

        if str(period).isdigit() and 0 <= period <= total_quantity_days - 4:
            quantity = period + 4
            if archive:
                for _day in range(quantity):
                    day_forecast = self.prepare_data(index_number=_day)
                    yield day_forecast

            else:
                for _day in range(4, quantity):
                    day_forecast = self.prepare_data(index_number=_day)
                    yield day_forecast

        else:
            print('Введено некорректное значение')
