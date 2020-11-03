# -*- coding: utf-8 -*-
import argparse
import time

from database_manager import WeatherForecast, DatabaseUpdater, database
from forecast_engine import WeatherMaker
from paiting_cards import ImageMaker


if __name__ == '__main__':
    weather = WeatherMaker()
    weather.get_weather()
    path_to_image_with_forecast = 'python_snippets/external_data'
    name_image_with_forecast = 'forecast.jpg'

    database.create_tables([WeatherForecast])
    db_manager = DatabaseUpdater()

    for day in weather.show_weather(period=0, archive=True):
        db_manager.save_data(data=day)

    seconds_since_the_epoch = time.time()
    # Количество секунд в четырех днях, т.к. Яндекс хранит архив пооды только за четыре дня
    seconds_in_four_days = 345600.0000000
    seconds_in_one_days = 86400.0000000
    # Определяем последний доступный в архиве Яндекса день и переводим его в формат 2020-11-01
    first_day_in_archive = time.gmtime(seconds_since_the_epoch - seconds_in_four_days)
    last_day_in_archive = time.gmtime(seconds_since_the_epoch - seconds_in_one_days)
    first_day_in_archive_formated = time.strftime('%Y-%m-%d', first_day_in_archive)
    last_day_in_archive_formated = time.strftime('%Y-%m-%d', last_day_in_archive)

    try:
        weather_console = argparse.ArgumentParser(description='Позволяет работать с прогнозом погоды')
        weather_console.add_argument(
            '--period', type=int, dest='period', help='Количество дней, за которые нужно сохранить прогноз в БД'
        )
        weather_console.add_argument(
            '--archive', type=bool, dest='archive',
            help='Архив погоды (True или False). Если False, то в БД не будет сохранен архив погоды за предыдущие дни.'
        )
        weather_console.add_argument(
            '--from', type=str, dest='_from', help='Начальная дата, начиная с которой нужно получить прогноз из БД.'
                                                   'Формат 2020-12-31'
        )
        weather_console.add_argument(
            '--to', type=str, default=None, dest='_to',
            help='Дата, до которой нужно получить прогноз из БД. Формат 2020-12-31 (Необязательный параметр)'
        )
        weather_console.add_argument(
            '--from_print', type=str, dest='from_print', help='Дата, начиная с которой нужно вывести на консоль прогноз'
                                                              'Формат 2020-12-31'
        )
        weather_console.add_argument(
            '--to_print', type=str, default=None, dest='to_print',
            help='Дата, до которой нужно вывести на консоль прогноз. Формат 2020-12-31 (Необязательный параметр)'
        )

        result = weather_console.parse_args()
        print('\nПогода в Санкт-Петербурге в последние дни:')
        db_manager.print_data(_from=first_day_in_archive_formated, _to=last_day_in_archive_formated)
        print('*' * 35, '\n')

        archive = weather.show_weather(period=result.period, archive=result.archive)
        if archive:
            for day in archive:
                db_manager.save_data(day)

        forecasts_from_database = db_manager.get_data(_from=result._from, _to=result._to)
        if any(forecasts_from_database):
            for day in forecasts_from_database:
                name_image_with_forecast = f'{day[0]}.jpg'
                ImageMaker(weather_forecast=day, name=name_image_with_forecast).run()

        db_manager.print_data(_from=result.from_print, _to=result.to_print)

    except Exception as exc:
        print(f'Что-то пошло не так: {exc}')
