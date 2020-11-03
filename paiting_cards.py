import os

import cv2


class ImageMaker:
    """
    Создает открытку, рисуя на ней фон, иконку и текст прогноза погоды.
    В качестве параметров принимает прогноз погоды (tuple) и название для файла-открытки и путь, куда его сохранить.
    """

    def __init__(self, weather_forecast: tuple, name: str, path=None):
        self.path_to_image = os.path.dirname(__file__) if path is None else os.path.normpath(path)
        self.name = name
        self.full_path = os.path.join(self.path_to_image, self.name)
        self.weather_forecast = weather_forecast
        self.blank = 'background_template.jpg'
        self.font = cv2.FONT_HERSHEY_COMPLEX
        self.colors = {
            'deep_sky_blue': [(255, 191, 0), 'weather_img/snow.jpg'],
            'blue': [(255, 0, 0), 'weather_img/rain.jpg'],
            'yellow': [(0, 255, 255), 'weather_img/sun.jpg'],
            'gray': [(169, 169, 169), 'weather_img/cloud.jpg']
        }

    def write_text(self):
        image_open = cv2.imread(self.full_path)
        text_first_part = f'{self.weather_forecast[0]}'
        text_second_part = f'{self.weather_forecast[1]}'
        text_third_part = f'{self.weather_forecast[2]} {self.weather_forecast[3]}'
        image_open = cv2.putText(
            img=image_open,
            text=text_first_part,
            org=(20, 50),
            fontFace=self.font,
            fontScale=1,
            color=(0, 0, 0)
        )
        image_open = cv2.putText(
            img=image_open,
            text=text_second_part,
            org=(20, 90),
            fontFace=self.font,
            fontScale=1,
            color=(0, 0, 0)
        )
        image_open = cv2.putText(
            img=image_open,
            text=text_third_part,
            org=(20, 130),
            fontFace=self.font,
            fontScale=1,
            color=(0, 0, 0)
        )
        cv2.imwrite(self.full_path, image_open)

    def add_picture(self):
        """
        В зависимости от погоды добавляет в нижний правый угол картинки иконку из папки weather_img
        """
        if 'ясно' in self.weather_forecast[1].lower():
            logo_path = self.colors['yellow'][1]
        elif 'снег' in self.weather_forecast[1].lower():
            logo_path = self.colors['deep_sky_blue'][1]
        elif 'дождь' in self.weather_forecast[1].lower():
            logo_path = self.colors['blue'][1]
        else:
            logo_path = self.colors['gray'][1]

        image_background = cv2.imread(self.full_path)
        image_logo = cv2.imread(logo_path)
        split = image_logo[0:100, 0:100]  # [x0:x1, y0:y1]. Размер исходной картинки 100*100, берем ее полностью.
        image_background[155:255, 410:510] = split  # вставляем в правый нижний угол по координатам [x0:x1, y0:y1].
        cv2.imwrite(self.full_path, image_background)

    def add_background(self):
        """
        В зависимости от погоды создает картинку с нужным фоном.
        Солнечно - yellow
        Дождь - blue
        Снег - deep_sky_blue
        Все остальное (облачно, туманно и пр.) - gray
        """
        if 'ясно' in self.weather_forecast[1].lower():
            _color = self.colors['yellow'][0]
        elif 'снег' in self.weather_forecast[1].lower():
            _color = self.colors['deep_sky_blue'][0]
        elif 'дождь' in self.weather_forecast[1].lower():
            _color = self.colors['blue'][0]
        else:
            _color = self.colors['gray'][0]

        image_open = cv2.imread(self.blank)
        image_copy = image_open.copy()
        final_image = cv2.rectangle(img=image_copy, pt1=(0, 0), pt2=(510, 255), color=_color, thickness=-1)
        cv2.imwrite(self.full_path, final_image)

    def run(self):
        """
        Важно не менять порядок вызова методов!
        Методы self.write_text() и self.add_picture() открывают картинку с нужным фоном,
        которая создана методом self.add_background().
        """
        self.add_background()
        self.add_picture()
        self.write_text()
