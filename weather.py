import argparse
import time
from datetime import datetime, timedelta

from database_manager import Location, WeatherForecast, DatabaseUpdater, database
from forecast_engine import WeatherMaker

import atexit

# Закрытие соединения с БД на выходе из приложения
@atexit.register
def goodbye():
    # print('Closing DB...')
    database.close()

if __name__ == '__main__':

    database.connect()
    database.create_tables([WeatherForecast, Location])
    db_manager = DatabaseManager()

    loc, lat, lon = db_manager.get_location()
    weather = WeatherMaker(lat, lon)

    try:
        weather_console = argparse.ArgumentParser(description='Позволяет работать с прогнозом погоды')
        
        # Регистрация консольных аргументов
        weather_console.add_argument(
            '--get-loc', type=bool, dest='_loc', default=False,
            help='Местоположение по внешнему ключу.'
        )

        weather_console.add_argument(
            '--upd-from', type=str, dest='upd_from', default=None,
            help='Дата, с которой надо обновить/дополнить сохраненный в БД прогноз.'
                 'Формат 2020-12-31'
        )
        weather_console.add_argument(
            '--upd-to', type=str, default=None, dest='upd_to',
            help='Дата, до которой надо обновить/дополнить сохраненный в БД прогноз.'
                 'Формат 2020-12-31'
        )
        weather_console.add_argument(
            '--print-from', type=str, dest='print_from', default=None,
            help='Дата, начиная с которой надо вывести на консоль прогноз.'
                 'Формат 2020-12-31'
        )
        weather_console.add_argument(
            '--print-to', type=str, default=None, dest='print_to',
            help='Дата, до которой надо вывести на консоль прогноз.'
                 'Формат 2020-12-31'
        )

        weather_console.add_argument(
            '--show-prev', type=int, default=-1, dest='show_prev',
            help='Количество архивных дней, за которые нужно вывести на консоль прогноз.'
        )

        # Обработка переданных агрументов
        args = weather_console.parse_args()

        # Логика согласно переданным аргументам

        if args._loc:
            print('В БД хранятся прогнозы для', db_manager.get_location_fk())

        if args.show_prev >= 0: 
            today = datetime.today()
            first_archived_day = (today - timedelta(days = args.show_prev)).strftime('%Y-%m-%d')
            today = today.strftime('%Y-%m-%d')

            print(f'\nПогода над {loc} в последние дни:')
            print('*' * 35)        
            db_manager.print(_from=first_archived_day, _to=today)
            print('*' * 35, '\n')        

        if args.upd_from or args.upd_to:
            weather.read()
            for val in weather.get(_from = args.upd_from, _to = args.upd_to):
                db_manager.save(data = val)
                # print(val)

        if args.print_from or args.print_to:
            print(f'\nПрогноз погоды над {loc}:')
            print('*' * 35)        
            db_manager.print(args.print_from, args.print_to)
            print('*' * 35, '\n')        

    except Exception as exc:
        print(f'Что-то пошло не так: {exc}')
