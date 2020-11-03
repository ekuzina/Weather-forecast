import re

import peewee

database = peewee.SqliteDatabase('weather_forecast.db')


class BaseTable(peewee.Model):
    class Meta:
        database = database


class WeatherForecast(BaseTable):
    date = peewee.CharField()
    weather = peewee.CharField()
    temperature_day = peewee.CharField()
    temperature_night = peewee.CharField()


class DatabaseUpdater(WeatherForecast):
    """
    Сохраняет и выводит на консоль данные из БД.
    Если в БД уже есть прогноз на конкретную дату - не сохраняет его в БД'.
    """

    def save_data(self, data):
        if WeatherForecast.select().where(WeatherForecast.date == data[0]):
            pass
        else:
            WeatherForecast.create(
                date=data[0],
                weather=data[1],
                temperature_day=data[2],
                temperature_night=data[3]
            )

    def get_data(self, _from, _to=None):
        template = r'\d{4}[-]([0][0-9]{1,2}|[1][0-2]{1,2})[-]([0-2][0-9]{1,2}|[3][0-1]{1,2})'
        check_data = re.compile(template)
        result = []
        for data in WeatherForecast.select():
            if _to is None:
                if re.search(check_data, _from):
                    if _from <= data.date:
                        forecast = (data.date, data.weather, data.temperature_day, data.temperature_night)
                        result.append(forecast)
                else:
                    print('Неверный формат даты. Нужно вводить ГГ-ММ-ДД: 2020-12-31')
                    break
            else:
                if re.search(check_data, _from) and re.search(check_data, _to):
                    if _from <= data.date <= _to:
                        forecast = (data.date, data.weather, data.temperature_day, data.temperature_night)
                        result.append(forecast)
                else:
                    print('Неверный формат даты. Нужно вводить ГГ-ММ-ДД: 2020-12-31')
                    break
        return result

    def print_data(self, _from, _to=None):
        template = r'\d{4}[-]([0][0-9]{1,2}|[1][0-2]{1,2})[-]([0-2][0-9]{1,2}|[3][0-1]{1,2})'
        check_data = re.compile(template)
        for data in WeatherForecast.select():
            if _to is None:
                if re.search(check_data, _from):
                    if _from <= data.date:
                        print(data.date, data.weather, data.temperature_day, data.temperature_night)
                else:
                    print('Неверный формат даты. Нужно вводить ГГ-ММ-ДД: 2020-12-31')
                    break
            else:
                if re.search(check_data, _from) and re.search(check_data, _to):
                    if _from <= data.date <= _to:
                        print(data.date, data.weather, data.temperature_day, data.temperature_night)
                else:
                    print('Неверный формат даты. Нужно вводить ГГ-ММ-ДД: 2020-12-31')
                    break
