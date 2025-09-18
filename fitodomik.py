#!/usr/bin/python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
from datetime import datetime, timedelta
import threading
import time as time_module
from datetime import time as datetime_time
import serial
import serial.tools.list_ports
import re
from PIL import Image, ImageTk
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import numpy as np
from collections import deque
import matplotlib
import requests
import cv2
import base64
import sys
import urllib3
urllib3.disable_warnings()
matplotlib.use("TkAgg")  
DISEASES_DB = {
    "yellow_leaves": {
        "name": "Хлороз",
        "description": "Пожелтение листьев",
        "causes": ["Недостаток железа", "Переувлажнение", "Недостаток азота"],
        "solutions": ["Добавить железосодержащие удобрения", "Уменьшить полив", "Внести азотные удобрения"]
    },
    "brown_spots": {
        "name": "Грибковое заболевание",
        "description": "Коричневые пятна на листьях",
        "causes": ["Грибковая инфекция", "Избыточная влажность", "Плохая вентиляция"],
        "solutions": ["Обработать фунгицидами", "Улучшить вентиляцию", "Удалить пораженные листья"]
    },
    "white_powder": {
        "name": "Мучнистая роса",
        "description": "Белый налет на листьях",
        "causes": ["Грибковая инфекция", "Высокая влажность", "Резкие перепады температуры"],
        "solutions": ["Обработать фунгицидами", "Снизить влажность воздуха", "Обеспечить стабильную температуру"]
    },
    "leaf_curl": {
        "name": "Курчавость листьев",
        "description": "Деформация и скручивание листьев",
        "causes": ["Вирусная инфекция", "Недостаток кальция", "Повреждение насекомыми"],
        "solutions": ["Удалить пораженные части", "Внести кальциевые удобрения", "Обработать инсектицидами"]
    },
    "black_spots": {
        "name": "Черная пятнистость",
        "description": "Черные пятна на листьях",
        "causes": ["Грибковая инфекция", "Высокая влажность", "Недостаточная циркуляция воздуха"],
        "solutions": ["Обработать фунгицидами", "Улучшить проветривание", "Удалить пораженные листья"]
    },
    "wilting": {
        "name": "Увядание",
        "description": "Общее увядание растения",
        "causes": ["Недостаток воды", "Корневая гниль", "Бактериальная инфекция"],
        "solutions": ["Проверить режим полива", "Проверить корневую систему", "Обработать фунгицидами"]
    },
    "mosaic": {
        "name": "Мозаичная болезнь",
        "description": "Мозаичный узор на листьях",
        "causes": ["Вирусная инфекция", "Переносчики вирусов"],
        "solutions": ["Удалить пораженные растения", "Бороться с насекомыми-переносчиками"]
    }
}
PESTS_DB = {
    "aphids": {
        "name": "Тля",
        "description": "Мелкие насекомые на листьях и стеблях",
        "damage": "Высасывают сок из растения, вызывают деформацию листьев",
        "solutions": ["Обработать инсектицидами", "Использовать мыльный раствор", "Привлечь естественных хищников"]
    },
    "whitefly": {
        "name": "Белокрылка",
        "description": "Мелкие белые летающие насекомые",
        "damage": "Высасывают сок, выделяют медвяную росу, переносят вирусы",
        "solutions": ["Использовать желтые липкие ловушки", "Обработать инсектицидами", "Регулярно осматривать нижнюю сторону листьев"]
    },
    "thrips": {
        "name": "Трипсы",
        "description": "Мелкие удлиненные насекомые",
        "damage": "Повреждают листья и цветы, переносят вирусы",
        "solutions": ["Обработать инсектицидами", "Использовать синие липкие ловушки", "Удалять сорняки"]
    },
    "mealybugs": {
        "name": "Мучнистые червецы",
        "description": "Белые пушистые насекомые",
        "damage": "Высасывают сок, выделяют медвяную росу",
        "solutions": ["Обработать спиртовым раствором", "Использовать системные инсектициды", "Изолировать пораженные растения"]
    },
    "scale_insects": {
        "name": "Щитовки",
        "description": "Неподвижные насекомые под защитным щитком",
        "damage": "Высасывают сок, ослабляют растение",
        "solutions": ["Механически удалить", "Обработать масляными препаратами", "Использовать системные инсектициды"]
    },
    "caterpillars": {
        "name": "Гусеницы",
        "description": "Личинки бабочек различных размеров",
        "damage": "Объедают листья, стебли и плоды",
        "solutions": ["Собирать вручную", "Использовать биологические препараты", "Обработать инсектицидами"]
    }
}
LEAF_COLORS = {
    "healthy_green": {"lower": np.array([35, 30, 30]), "upper": np.array([85, 255, 255]),
                     "name": "здоровый зеленый"},
    "yellow": {"lower": np.array([20, 30, 30]), "upper": np.array([35, 255, 255]),
               "name": "желтый"},
    "brown": {"lower": np.array([10, 30, 10]), "upper": np.array([20, 255, 255]),
              "name": "коричневый"},
    "light_green": {"lower": np.array([35, 30, 30]), "upper": np.array([85, 100, 255]),
                    "name": "светло-зеленый"}
}
class PlantAnalyzer:
    def __init__(self, token=None):
        self.camera = None
        self.camera_index = 0
        self.output_dir = "analysis_results"
        self.api_token = token
        self.color_percentages = {}
        self.detected_diseases = []
        self.detected_pests = []
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    def set_api_token(self, token):
        self.api_token = token
    def initialize_camera(self, camera_index=0):
        self.camera_index = camera_index
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            if not self.camera.isOpened():
                raise Exception("Не удалось открыть камеру")
            return True
        except Exception as e:
            return False
    def upload_to_server(self, original_image, detection_image, analysis, text="Анализ состояния растений"):
        if not self.api_token:
            return False
        orig_filename = None
        analysis_filename = None
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            orig_filename = f"farm_photo_{timestamp}.jpg"
            analysis_filename = f"farm_analysis_{timestamp}.jpg"
            cv2.imwrite(orig_filename, original_image)
            cv2.imwrite(analysis_filename, detection_image)
            if not os.path.exists(orig_filename) or not os.path.exists(analysis_filename):
                return False
            data = {
                'text': text,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'has_analysis': 'true'
            }
            headers = {
                'X-Auth-Token': self.api_token
            }
            try:
                with open(orig_filename, 'rb') as orig_file, open(analysis_filename, 'rb') as analysis_file:
                    files = {
                        'image': ('original.jpg', orig_file.read(), 'image/jpeg'),
                        'analysis_image': ('analysis.jpg', analysis_file.read(), 'image/jpeg')
                    }
                    response = requests.post(
                        "https://fitodomik.online/api/upload-image.php",
                        data=data,
                        files=files,
                        headers=headers,
                        timeout=60,
                        verify=os.environ.get('REQUESTS_CA_BUNDLE', True)
                    )
                    if response.status_code != 200:
                        return False
                    try:
                        response_data = response.json()
                        if not response_data.get('success'):
                            return False
                        self.cleanup_analysis_folder()
                        return True
                    except:
                        return False
            except:
                return False
        except:
            return False
        finally:
            for filename in [orig_filename, analysis_filename]:
                if filename and os.path.exists(filename):
                    try:
                        os.remove(filename)
                    except:
                        pass
    def cleanup_analysis_folder(self):
        try:
            if os.path.exists(self.output_dir):
                for filename in os.listdir(self.output_dir):
                    file_path = os.path.join(self.output_dir, filename)
                    if os.path.isfile(file_path):
                        try:
                            os.remove(file_path)
                        except:
                            pass
        except:
            pass
    def capture_image(self):
        if self.camera is None:
            if not self.initialize_camera():
                return None
        try:
            ret, frame = self.camera.read()
            if not ret:
                return None
            frame_copy = frame.copy()
            return frame_copy
        finally:
            if self.camera and hasattr(self.camera, 'grab'):
                try:
                    self.camera.grab()
                except:
                    pass
    def release_camera(self):
        if self.camera is not None:
            self.camera.release()
            self.camera = None
    def detect_plant(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        detection_image = image.copy()
        total_mask = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
        for color_name, color_range in LEAF_COLORS.items():
            mask = cv2.inRange(hsv, color_range["lower"], color_range["upper"])
            kernel = np.ones((3,3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            total_mask = cv2.bitwise_or(total_mask, mask)
        contours, _ = cv2.findContours(total_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filtered_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:
                filtered_contours.append(contour)
        cv2.drawContours(detection_image, filtered_contours, -1, (0, 255, 0), 2)
        plant_mask = np.zeros_like(total_mask)
        cv2.drawContours(plant_mask, filtered_contours, -1, 255, -1)
        plant_pixels = np.count_nonzero(plant_mask)
        if plant_pixels > 0:
            for color_name, color_range in LEAF_COLORS.items():
                mask = cv2.inRange(hsv, color_range["lower"], color_range["upper"])
                color_pixels = cv2.countNonZero(cv2.bitwise_and(mask, plant_mask))
                self.color_percentages[color_name] = (color_pixels / plant_pixels) * 100
        return detection_image, filtered_contours
    def detect_diseases(self):
        self.detected_diseases = []
        if self.color_percentages.get("yellow", 0) > 10:
            self.detected_diseases.append(DISEASES_DB["yellow_leaves"])
        if self.color_percentages.get("brown", 0) > 5:
            self.detected_diseases.append(DISEASES_DB["brown_spots"])
        if self.color_percentages.get("light_green", 0) > 15:
            self.detected_diseases.append(DISEASES_DB["white_powder"])
        if (self.color_percentages.get("yellow", 0) > 20 and 
            self.color_percentages.get("brown", 0) > 10):
            self.detected_diseases.append(DISEASES_DB["wilting"])
    def detect_pests(self):
        self.detected_pests = []
        if (self.color_percentages.get("yellow", 0) > 15 and 
            self.color_percentages.get("brown", 0) > 5):
            self.detected_pests.append(PESTS_DB["aphids"])
        if self.color_percentages.get("brown", 0) > 10:
            self.detected_pests.append(PESTS_DB["thrips"])
        if (self.color_percentages.get("light_green", 0) > 20 and 
            self.color_percentages.get("yellow", 0) > 10):
            self.detected_pests.append(PESTS_DB["whitefly"])
    def analyze_health(self, image, contours):
        self.detect_diseases()
        self.detect_pests()
        status = "нормальное"
        details = []
        recommendations = []
        if self.color_percentages.get("yellow", 0) > 10:
            status = "требует внимания"
            details.append("Обнаружено значительное пожелтение листьев")
            recommendations.append("Проверьте режим полива")
            recommendations.append("Проверьте уровень освещенности")
        if self.color_percentages.get("brown", 0) > 5:
            status = "требует внимания"
            details.append("Обнаружены коричневые участки на листьях")
            recommendations.append("Проверьте на наличие заболеваний")
            recommendations.append("Удалите поврежденные листья")
        for disease in self.detected_diseases:
            details.append(f"{disease['name']}: {disease['description']}")
            recommendations.extend(disease['solutions'])
        for pest in self.detected_pests:
            details.append(f"{pest['name']}: {pest['description']}")
            recommendations.extend(pest['solutions'])
        if not details:
            recommendations.append("Поддерживайте текущий режим ухода")
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "состояние": status,
            "распределение цветов": "; ".join([f"{LEAF_COLORS[k]['name']}: {v:.1f}%" 
                                              for k, v in self.color_percentages.items() if v > 1]),
            "детали": "; ".join(details) if details else "отклонений не выявлено",
            "рекомендации": "; ".join(recommendations)
        }
    def create_report(self, original_image, detection_image, analysis):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_path = os.path.join(self.output_dir, f"original_{timestamp}.jpg")
        detection_path = os.path.join(self.output_dir, f"detection_{timestamp}.jpg")
        cv2.imwrite(original_path, original_image)
        cv2.imwrite(detection_path, detection_image)
        report_path = os.path.join(self.output_dir, f"analysis_{timestamp}.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"АНАЛИЗ СОСТОЯНИЯ РАСТЕНИЯ\n")
            f.write(f"Дата анализа: {analysis['timestamp']}\n\n")
            f.write(f"СОСТОЯНИЕ: {analysis['состояние']}\n\n")
            f.write("РАСПРЕДЕЛЕНИЕ ЦВЕТОВ:\n")
            if self.color_percentages:
                for color_key, color_info in LEAF_COLORS.items():
                    percent = self.color_percentages.get(color_key, 0.0)
                    f.write(f"- {color_info['name']}: {percent:.2f}%\n")
            else:
                f.write("- Нет данных по цветам\n")
            f.write("\n")
            f.write("ДЕТАЛИ АНАЛИЗА:\n")
            if self.detected_diseases or self.detected_pests:
                for disease in self.detected_diseases:
                    f.write(f"\nБолезнь: {disease['name']}\n")
                    f.write(f"Описание: {disease['description']}\n")
                    f.write("Возможные причины:\n")
                    for cause in disease['causes']:
                        f.write(f"  - {cause}\n")
                    f.write("Рекомендации по лечению:\n")
                    for sol in disease['solutions']:
                        f.write(f"  - {sol}\n")
                for pest in self.detected_pests:
                    f.write(f"\nВредитель: {pest['name']}\n")
                    f.write(f"Описание: {pest['description']}\n")
                    if 'damage' in pest:
                        f.write(f"Тип повреждений: {pest['damage']}\n")
                    f.write("Рекомендации по борьбе:\n")
                    for sol in pest['solutions']:
                        f.write(f"  - {sol}\n")
            else:
                f.write("отклонений не выявлено\n")
            f.write("\n")
            f.write("РЕКОМЕНДАЦИИ:\n")
            if analysis['рекомендации']:
                for rec in analysis['рекомендации'].split('; '):
                    f.write(f"- {rec}\n")
            else:
                f.write("- Нет рекомендаций\n")
        return original_path, detection_path, report_path
    def run_analysis(self, callback=None):
        if not self.initialize_camera():
            if callback:
                callback(None, None, None, "Ошибка инициализации камеры")
            return
        try:
            image = self.capture_image()
            if image is None:
                if callback:
                    callback(None, None, None, "Не удалось получить изображение")
                return
            detection_image, contours = self.detect_plant(image)
            analysis = self.analyze_health(image, contours)
            original_path, detection_path, report_path = self.create_report(
                image, detection_image, analysis
            )
            with open(report_path, 'r', encoding='utf-8') as f:
                full_analysis_text = f.read()
            if callback:
                callback(image, detection_image, analysis, None)
            if self.api_token:
                self.upload_to_server(image, detection_image, analysis, text=full_analysis_text)
            return image, detection_image, analysis
        finally:
            self.release_camera()
class SensorHistory:
    def __init__(self, max_points=300):
        self.max_points = max_points
        self.timestamps = deque(maxlen=max_points)
        self.temperature = deque(maxlen=max_points)
        self.humidity = deque(maxlen=max_points)
        self.soil_moisture = deque(maxlen=max_points)
        self.light_level = deque(maxlen=max_points)
        self.co2 = deque(maxlen=max_points)
        self.pressure = deque(maxlen=max_points)
    def add_data(self, timestamp, temp, humidity, soil, light, co2, pressure):
        self.timestamps.append(timestamp)
        try:
            self.temperature.append(float(temp) if temp != "--" else (self.temperature[-1] if self.temperature else 0))
        except (ValueError, IndexError):
            self.temperature.append(self.temperature[-1] if self.temperature else 0)
        try:
            self.humidity.append(float(humidity) if humidity != "--" else (self.humidity[-1] if self.humidity else 0))
        except (ValueError, IndexError):
            self.humidity.append(self.humidity[-1] if self.humidity else 0)
        try:
            self.soil_moisture.append(float(soil) if soil != "--" else (self.soil_moisture[-1] if self.soil_moisture else 0))
        except (ValueError, IndexError):
            self.soil_moisture.append(self.soil_moisture[-1] if self.soil_moisture else 0)
        try:
            self.co2.append(float(co2) if co2 != "--" else (self.co2[-1] if self.co2 else 400))
        except (ValueError, IndexError):
            self.co2.append(self.co2[-1] if self.co2 else 400)
        try:
            self.pressure.append(float(pressure) if pressure != "--" else (self.pressure[-1] if self.pressure else 750))
        except (ValueError, IndexError):
            self.pressure.append(self.pressure[-1] if self.pressure else 750)
class ArduinoHandler:
    def __init__(self):
        self.port = None
        self.serial_connection = None
        self.polling_interval = 5
        self.is_connected = False
        self.running = False
        self.monitoring_thread = None
        self.update_callback = None
        self.temperature = "--"
        self.humidity = "--"
        self.soil_moisture = "--"
        self.co2 = "--"
        self.pressure = "--"
        self.relay1_state = 0  
        self.relay2_state = 0  
        self.relay3_state = 0  
        self.relay4_state = 0  
        self.led_state = 0
        self.curtains_state = 0
        self.pump_state = 0
        self.fan_state = 0
    def connect(self):
        if self.is_connected:
            return True
        try:
            self.serial_connection = serial.Serial(self.port, 9600, timeout=3)
            time_module.sleep(2)
            self.is_connected = True
            return True
        except Exception as e:
            self.is_connected = False
            return False
    def disconnect(self):
        if self.serial_connection and self.is_connected:
            self.serial_connection.close()
            self.is_connected = False
    def start_monitoring(self):
        if not self.is_connected:
            if not self.connect():
                return False
        if self.running:
            return True
        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        return True
    def stop_monitoring(self):
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
        self.disconnect()
    def _monitoring_loop(self):
        while self.running:
            try:
                if self.is_connected and self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8', errors='replace').strip()
                    if line:
                        if self.parse_sensor_response(line):
                            continue
                time_module.sleep(0.1)
            except Exception as e:
                time_module.sleep(2)
    def parse_sensor_response(self, response):
        try:
            if response.startswith('{') and response.endswith('}'):
                import json
                data = json.loads(response)
                self.co2 = str(data.get('co2', '--'))
                self.temperature = str(data.get('temp', '--'))
                self.humidity = str(data.get('humidity', '--'))
                pressure_hpa = data.get('pressure', '--')
                if pressure_hpa != '--':
                    try:
                        pressure_mmhg = float(pressure_hpa) * 0.75006
                        self.pressure = f"{pressure_mmhg:.1f}"
                    except:
                        self.pressure = '--'
                else:
                    self.pressure = '--'
                self.soil_moisture = str(data.get('soil', '--'))
                self.relay1_state = 1 if data.get('relay1') == True else 0  
                self.relay2_state = 1 if data.get('relay2') == True else 0  
                self.relay3_state = 1 if data.get('relay3') == True else 0  
                self.relay4_state = 1 if data.get('relay4') == True else 0  
                self.fan_state = self.relay1_state
                self.pump_state = self.relay2_state
                self.curtains_state = self.relay3_state
                self.led_state = self.relay4_state
                if self.update_callback:
                    self.update_callback()
                return True
            elif response.startswith("Status:"):
                return self.parse_relay_status(response)
            return False
        except Exception as e:
            return False
    def parse_relay_status(self, response):
        try:
            parts = response.split(" ")
            for part in parts[1:]:  
                if ":" in part:
                    relay_info = part.split(":")
                    relay_num = relay_info[0]
                    relay_state = relay_info[1] == "ON"
                    if relay_num == "R1":
                        self.relay1_state = 1 if relay_state else 0
                        self.fan_state = self.relay1_state
                    elif relay_num == "R2":
                        self.relay2_state = 1 if relay_state else 0
                        self.pump_state = self.relay2_state
                    elif relay_num == "R3":
                        self.relay3_state = 1 if relay_state else 0
                        self.curtains_state = self.relay3_state
                    elif relay_num == "R4":
                        self.relay4_state = 1 if relay_state else 0
                        self.led_state = self.relay4_state
            if self.update_callback:
                self.update_callback()
            return True
        except Exception as e:
            return False
    def send_command(self, device_type, state):
        if not self.is_connected:
            if not self.connect():
                return False
        try:
            command = ""
            if device_type == "LED" or device_type == "LAMP":
                command = "4"  
            elif device_type == "CURTAINS":
                command = "3"  
            elif device_type == "RELAY3" or device_type == "PUMP":
                command = "2"  
            elif device_type == "RELAY4" or device_type == "FAN":
                command = "1"  
            elif device_type == "ALL_ON":
                command = "A+"
            elif device_type == "ALL_OFF":
                command = "A-"
            elif device_type == "STATUS":
                command = "S"
            if command:
                self.serial_connection.reset_input_buffer()
                self.serial_connection.write((command + '\n').encode('utf-8'))
                time_module.sleep(0.5)
                if self.serial_connection.in_waiting > 0:
                    response = self.serial_connection.readline().decode('utf-8', errors='replace').strip()
                    if response:
                        self.parse_relay_status(response)
                return True
            return False
        except Exception as e:
            self.is_connected = False
            return False
    def send_schedule_data(self, data):
        if not self.is_connected:
            if not self.connect():
                return False
        try:
            self.serial_connection.reset_input_buffer()
            self.serial_connection.write((data + '\n').encode('utf-8'))
            time_module.sleep(2)
            response_lines = []
            timeout_start = time_module.time()
            while time_module.time() - timeout_start < 5:  
                if self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8', errors='replace').strip()
                    if line:
                        response_lines.append(line)
                        if "Data loaded successfully" in line:
                            return True
                time_module.sleep(0.1)
            return len(response_lines) > 0
        except Exception as e:
            return False
    def request_sensor_data(self):
        return True
    def request_device_states(self):
        return self.send_command("STATUS", None)
class DataSender:
    def __init__(self, token=""):
        self.token = token
        self.server_url = "https://fitodomik.online/api/save-sensor-data.php"
        self.max_id_url = "https://fitodomik.online/api/get-max-sensor-id.php"
        self.headers = {"X-Auth-Token": f"{self.token}"}
        self.last_used_id = 0
        self.sending_thread = None
        self.sending_queue = []
        self.queue_lock = threading.Lock()
        self.sending_active = False
        self.start_sender_thread()
    def start_sender_thread(self):
        if self.sending_thread is None or not self.sending_thread.is_alive():
            self.sending_active = True
            self.sending_thread = threading.Thread(target=self._sender_thread_loop, daemon=True)
            self.sending_thread.start()
    def stop_sender_thread(self):
        self.sending_active = False
        if self.sending_thread and self.sending_thread.is_alive():
            self.sending_thread.join(timeout=1.0)
    def _sender_thread_loop(self):
        while self.sending_active:
            data_to_send = None
            with self.queue_lock:
                if self.sending_queue:
                    data_to_send = self.sending_queue.pop(0)
            if data_to_send:
                self._send_data_internal(*data_to_send)
            time_module.sleep(0.1)
    def set_token(self, token):
        self.token = token
        self.headers = {"X-Auth-Token": f"{self.token}"}
    def get_max_sensor_id(self):
        try:
            response = requests.get(self.max_id_url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'max_id' in data:
                    return int(data['max_id'])
                else:
                    return self.last_used_id
            elif response.status_code == 401:
                return self.last_used_id
            else:
                return self.last_used_id
        except Exception as e:
            return self.last_used_id
    def send_data(self, temp, humidity, soil, light, co2, pressure, 
                  led_state, curtains_state, pump_state, fan_state):
        if not self.token:
            return False
        if not self.sending_active or not self.sending_thread or not self.sending_thread.is_alive():
            self.start_sender_thread()
        try:
            try:
                temp_val = float(temp) if temp != "--" else None
                humidity_val = float(humidity) if humidity != "--" else None
                soil_val = float(soil) if soil != "--" else None
                light_val = float(light) if light != "--" else None
                co2_val = int(float(co2)) if co2 != "--" else None
                pressure_val = float(pressure) if pressure != "--" else None
            except (ValueError, TypeError):
                return False
            with self.queue_lock:
                self.sending_queue.append((temp, humidity, soil, light, co2, pressure, 
                                          led_state, curtains_state, pump_state, fan_state))
            return True
        except Exception:
            return False
    def _send_data_internal(self, temp, humidity, soil, light, co2, pressure, 
                           led_state, curtains_state, pump_state, fan_state):
        try:
            max_id = self.get_max_sensor_id()
            next_id = max(max_id + 1, self.last_used_id + 1)
            try:
                temp_val = float(temp) if temp != "--" else None
                humidity_val = float(humidity) if humidity != "--" else None
                soil_val = float(soil) if soil != "--" else None
                light_val = float(light) if light != "--" else None
                co2_val = int(float(co2)) if co2 != "--" else None
                pressure_val = float(pressure) if pressure != "--" else None
            except (ValueError, TypeError):
                return False
            data = {
                'id': next_id,
                'user_id': 1,  
                'temperature': temp_val,
                'humidity': humidity_val,
                'soil_moisture': soil_val,
                'light_level': light_val,
                'co2': co2_val,
                'pressure': pressure_val,
                'lamp_state': int(led_state) if led_state is not None else 0,
                'curtains_state': int(curtains_state) if curtains_state is not None else 0
            }
            try:
                response = requests.post(
                    self.server_url, 
                    data=data, 
                    headers=self.headers,
                    timeout=10,
                    verify=os.environ.get('REQUESTS_CA_BUNDLE', True)
                )
                if response.status_code == 200:
                    try:
                        resp_data = response.json()
                        if resp_data.get('success'):
                            self.last_used_id = next_id
                            return True
                        else:
                            return False
                    except:
                        return False
                else:
                    return False
            except:
                return False
        except:
            return False
class ThresholdManager:
    def __init__(self, token=""):
        self.token = token
        self.thresholds_url = "https://fitodomik.online/api/get-thresholds.php"
        self.schedule_url = "https://fitodomik.online/api/get-schedule.php"
        self.headers = {"X-Auth-Token": f"{self.token}"}
        self.thresholds = None
        self.schedule = None
    def set_token(self, token):
        self.token = token
        self.headers = {"X-Auth-Token": f"{self.token}"}
    def get_thresholds(self):
        if not self.token:
            return None
        try:
            try:
                response = requests.get(
                    self.thresholds_url, 
                    headers=self.headers,
                    timeout=10,
                    verify=os.environ.get('REQUESTS_CA_BUNDLE', True)
                )
                if response.status_code == 200:
                    try:
                        data = response.json()
                        self.thresholds = data
                        return data
                    except:
                        return None
                else:
                    return None
            except:
                return None
        except:
            return None
    def get_schedule(self):
        if not self.token:
            return None
        try:
            try:
                response = requests.get(
                    self.schedule_url, 
                    headers=self.headers,
                    timeout=10,
                    verify=os.environ.get('REQUESTS_CA_BUNDLE', True)
                )
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get('success'):
                            self.schedule = data.get('data', [])
                            return self.schedule
                        else:
                            return None
                    except:
                        return None
                else:
                    return None
            except:
                return None
        except:
            return None
    def format_schedule(self, data=None):
        if data is None:
            data = self.schedule
        if not data:
            return "Расписание не получено"
        if isinstance(data, dict) and 'schedule' in data:
            data = data['schedule']
        if not isinstance(data, list):
            return "Ошибка формата расписания"
        lamp_intervals = []
        curtains_intervals = []
        lamp_hours = [False] * 24
        curtains_hours = [False] * 24
        for item in data:
            try:
                hour = int(item.get('time_interval', '0:').split(':')[0])
                if 0 <= hour < 24:
                    lamp_hours[hour] = bool(item.get('lighting_active', False))
                    curtains_hours[hour] = bool(item.get('curtains_active', False))
            except (ValueError, IndexError):
                continue
        start_hour = None
        for hour in range(25):  
            h = hour % 24
            if hour < 24 and lamp_hours[h]:
                if start_hour is None:
                    start_hour = h
            elif start_hour is not None:
                lamp_intervals.append(f"{start_hour:02d}:00-{h:02d}:00")
                start_hour = None
        start_hour = None
        for hour in range(25):  
            h = hour % 24
            if hour < 24 and curtains_hours[h]:
                if start_hour is None:
                    start_hour = h
            elif start_hour is not None:
                curtains_intervals.append(f"{start_hour:02d}:00-{h:02d}:00")
                start_hour = None
        result = {
            "lamp": ", ".join(lamp_intervals) if lamp_intervals else "Нет активных периодов",
            "curtains": ", ".join(curtains_intervals) if curtains_intervals else "Нет активных периодов"
        }
        return result
    def format_thresholds(self, data=None):
        if data is None:
            data = self.thresholds
        if not data:
            return "Пороговые значения не получены"
        result = []
        for param_type, values in data.items():
            if not isinstance(values, dict):
                continue
            param_name = {
                'temperature': 'Температура',
                'humidity_air': 'Влажность воздуха',
                'humidity_soil': 'Влажность почвы',
                'co2': 'CO2'
            }.get(param_type, param_type)
            unit = {
                'temperature': '°C',
                'humidity_air': '%',
                'humidity_soil': '%',
                'co2': 'ppm'
            }.get(param_type, '')
            min_val = values.get('min_limit', 'Н/Д')
            max_val = values.get('max_limit', 'Н/Д')
            target = values.get('target_value', 'Н/Д')
            tolerance = values.get('tolerance', 'Н/Д')
            result.append({
                'name': param_name,
                'range': f"{min_val} - {max_val} {unit}",
                'target': f"{target} {unit}",
                'tolerance': f"±{tolerance} {unit}",
                'param_type': param_type,
                'min': min_val,
                'max': max_val,
                'target_value': target,
                'unit': unit
            })
        return result
class FitoDomikApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ФитоДомик")
        self.root.attributes('-fullscreen', True)
        self.root.overrideredirect(True)
        self.root.bind('<Escape>', lambda e: self.on_close())
        self.root.bind('<Alt-F4>', lambda e: self.on_close())
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.root.focus_set()
        self.arduino = ArduinoHandler()
        self.data_sender = DataSender()
        self.threshold_manager = ThresholdManager()
        self.plant_analyzer = PlantAnalyzer()
        self.sensor_history = SensorHistory()
        self.last_update_time = datetime.now()
        self.chart_update_interval = 30  
        self.data_send_interval = 1800   
        self.last_send_time = datetime.now() - timedelta(seconds=self.data_send_interval)  
        self.next_photo_check_time = datetime.now()
        self.photo_check_interval = 60  
        self.last_auto_photo_date = None
        self.last_photo_hour = None  
        self.themes = {
            "light": {
                "bg_primary": "#F5F5F5",
                "bg_secondary": "#E0E0E0",
                "fg_primary": "#212121",
                "fg_secondary": "#757575",
                "accent1": "#4CAF50",
                "accent2": "#F44336",
                "block1": "#90CAF9",
                "block2": "#A5D6A7",
                "block3": "#FFCC80",
                "block4": "#E1BEE7",
                "info": "#2196F3",
                "warning": "#FF9800",
                "error": "#F44336"
            },
            "dark": {
                "bg_primary": "#212121",
                "bg_secondary": "#303030",
                "fg_primary": "#FFFFFF",
                "fg_secondary": "#B0BEC5",
                "accent1": "#66BB6A",
                "accent2": "#EF5350",
                "block1": "#42A5F5",
                "block2": "#66BB6A",
                "block3": "#FFA726",
                "block4": "#AB47BC",
                "info": "#42A5F5",
                "warning": "#FFA726",
                "error": "#EF5350"
            }
        }
        self.current_theme = "light"
        self.token = ""
        self.port = "COM10"
        self.polling_interval = 5
        self.photo_time = 12
        self.photo_count = 1
        self.photo_time2 = 18  
        self.control_mode = tk.StringVar(value="manual")  
        self.thresholds_mode = tk.StringVar(value="auto")  
        self.photo_count_var = tk.IntVar(value=1)  
        self.load_settings()
        self.photo_count_var.set(self.photo_count)
        self.auto_thresholds = {}
        self.manual_thresholds = {}  
        self.manual_schedule = {}    
        self.auto_mode_running = False
        self.auto_mode_thread = None
        self.arduino.update_callback = lambda: self.root.after(0, self.update_monitoring_display)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        self.tab_weather = ttk.Frame(self.notebook)
        self.tab_monitoring = ttk.Frame(self.notebook)
        self.tab_charts = ttk.Frame(self.notebook)
        self.tab_control = ttk.Frame(self.notebook)  
        self.tab_analysis = ttk.Frame(self.notebook)  
        self.tab_thresholds = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_weather, text='Часы и погода')
        self.notebook.add(self.tab_monitoring, text='Мониторинг')
        self.notebook.add(self.tab_charts, text='Графики')
        self.notebook.add(self.tab_control, text='Управление')
        self.notebook.add(self.tab_analysis, text='Анализ растения')
        self.notebook.add(self.tab_thresholds, text='Пороги')
        self.notebook.add(self.tab_settings, text='Настройки')
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        self.init_weather_tab()
        self.init_monitoring_tab()
        self.init_charts_tab()
        self.init_control_tab()
        self.init_analysis_tab()
        self.init_thresholds_tab()
        self.init_settings_tab()
        self.apply_theme()
        self.update_time_thread = threading.Thread(target=self.update_time_loop, daemon=True)
        self.update_time_thread.start()
        self.check_photo_time()
        self.root.after(2000, self.auto_start_system)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    def update_control_mode(self):
        mode = self.control_mode.get()
        self.save_settings()
        self.update_control_display()
        if mode == "auto":
            self.start_auto_mode()
        else:
            self.stop_auto_mode()
            if self.thresholds_mode.get() == "manual":
                self.load_manual_data_to_arduino()
    def load_data_to_arduino(self):
        if self.thresholds_mode.get() == "auto":
            self.load_auto_data_to_arduino()
        else:
            self.load_manual_data_to_arduino()
    def load_auto_data_to_arduino(self):
        threading.Thread(target=self._load_auto_data_thread, daemon=True).start()
    def _load_auto_data_thread(self):
        try:
            if not self.token:
                return
            data = self.get_fitodomik_data(self.token)
            if data and data != "0-0;0-0;0-0;0-0|0,0|0;0":
                success = self.arduino.send_schedule_data(data)
                if success:
                    self.root.after(0, lambda: self.threshold_status_var.set(
                        f"Данные с сервера загружены в Arduino ({datetime.now().strftime('%H:%M:%S')})"
                    ))
                else:
                    self.root.after(0, lambda: self.threshold_status_var.set(
                        "Ошибка загрузки данных в Arduino"
                    ))
            else:
                pass
                self.root.after(0, lambda: self.threshold_status_var.set(
                    "Ошибка получения данных с сервера"
                ))
        except Exception as e:
            self.root.after(0, lambda: self.threshold_status_var.set(f"Ошибка: {e}"))
    def get_fitodomik_data(self, token):
        try:
            base_url = 'https://fitodomik.online/api'
            headers = {'X-Auth-Token': token} if token else {}
            t = requests.get(f"{base_url}/get-thresholds.php", headers=headers, timeout=10).json()
            d = requests.get(f"{base_url}/get-sensor-data.php", headers=headers, timeout=10).json()
            s = requests.get(f"{base_url}/get-schedule.php", headers=headers, timeout=10).json()
            order = ['temperature', 'humidity_air', 'humidity_soil', 'co2']
            thresholds = ";".join(f"{t[k]['min_limit']}-{t[k]['max_limit']}" 
                                 for k in order if k in t) or "0-0;0-0;0-0;0-0"
            data = d.get('data', {})
            devices = f"{int(data.get('lamp_state',0))},{int(data.get('curtains_state',0))}"
            sched = s.get('data', {}).get('schedule', [])
            lamp_hours = [h for h in range(24) for item in sched 
                         if item.get('time_interval','').startswith(f'{h}:') and item.get('lighting_active')]
            curtain_hours = [h for h in range(24) for item in sched 
                            if item.get('time_interval','').startswith(f'{h}:') and item.get('curtains_active')]
            def group(hours):
                if not hours: return "0"
                hours = sorted(set(hours))
                result = []
                start = end = hours[0]
                for h in hours[1:]:
                    if h == end + 1:
                        end = h
                    else:
                        result.append(f"{start}-{end}" if start != end else str(start))
                        start = end = h
                result.append(f"{start}-{end}" if start != end else str(start))
                return ",".join(result)
            schedule = f"{group(lamp_hours)};{group(curtain_hours)}"
            return f"{thresholds}|{devices}|{schedule}"
        except:
            return "0-0;0-0;0-0;0-0|0,0|0;0"
    def load_manual_data_to_arduino(self):
        try:
            thresholds_parts = []
            param_keys = ['temperature', 'humidity_air', 'humidity_soil', 'co2']
            for key in param_keys:
                if key in self.manual_thresholds:
                    thresh = self.manual_thresholds[key]
                    min_val = thresh.get('min', 0)
                    max_val = thresh.get('max', 0)
                    thresholds_parts.append(f"{min_val}-{max_val}")
                else:
                    thresholds_parts.append("0-0")
            thresholds_str = ";".join(thresholds_parts)
            devices_str = "0,0"
            lamp_schedule = "0"
            curtain_schedule = "0"
            if self.manual_schedule:
                if 'lamp' in self.manual_schedule and 'active_hours' in self.manual_schedule['lamp']:
                    lamp_hours = self.manual_schedule['lamp']['active_hours']
                    if lamp_hours:
                        lamp_schedule = self.format_hours_to_schedule(lamp_hours)
                if 'curtains' in self.manual_schedule and 'active_hours' in self.manual_schedule['curtains']:
                    curtain_hours = self.manual_schedule['curtains']['active_hours']
                    if curtain_hours:
                        curtain_schedule = self.format_hours_to_schedule(curtain_hours)
            schedule_str = f"{lamp_schedule};{curtain_schedule}"
            data = f"{thresholds_str}|{devices_str}|{schedule_str}"
            success = self.arduino.send_schedule_data(data)
            if success:
                self.threshold_status_var.set(
                    f"Ручные данные загружены в Arduino ({datetime.now().strftime('%H:%M:%S')})"
                )
            else:
                self.threshold_status_var.set("Ошибка загрузки ручных данных в Arduino")
        except Exception as e:
            self.threshold_status_var.set(f"Ошибка загрузки ручных данных: {e}")
    def format_hours_to_schedule(self, hours):
        if not hours:
            return "0"
        hours = sorted(set(hours))
        result = []
        start = end = hours[0]
        for h in hours[1:]:
            if h == end + 1:
                end = h
            else:
                result.append(f"{start}-{end}" if start != end else str(start))
                start = end = h
        result.append(f"{start}-{end}" if start != end else str(start))
        return ",".join(result)
    def start_auto_mode(self):
        if self.auto_mode_running:
            return
        if self.arduino.running:
            self.load_data_to_arduino()
        self.auto_mode_running = True
        self.auto_mode_thread = threading.Thread(target=self.auto_mode_loop, daemon=True)
        self.auto_mode_thread.start()
    def stop_auto_mode(self):
        self.auto_mode_running = False
        if self.auto_mode_thread and self.auto_mode_thread.is_alive():
            self.auto_mode_thread.join(timeout=1.0)
    def auto_mode_loop(self):
        while self.auto_mode_running:
            try:
                self.root.after(0, self.update_control_display)
                time_module.sleep(30)
                if self.thresholds_mode.get() == "auto":
                    current_time = datetime.now()
                    if current_time.minute % 10 == 0 and current_time.second < 30:
                        self.load_auto_data_to_arduino()
            except Exception as e:
                pass
                time_module.sleep(10)
    def update_auto_thresholds(self):
        pass
    def load_settings(self):
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.current_theme = settings.get('theme', 'light')
                    self.token = settings.get('token', '')
                    self.port = settings.get('port', 'COM10')
                    self.polling_interval = settings.get('polling_interval', 5)
                    if 'data_send_interval' in settings:
                        self.data_send_interval = settings.get('data_send_interval')
                    if self.data_send_interval < 300:  
                        self.data_send_interval = 300
                    self.photo_time = settings.get('photo_time', 12)
                    self.plant_analyzer.camera_index = settings.get('camera_index', 0)
                    self.photo_count = settings.get('photo_count', 1)
                    if 'photo_time2' in settings:
                        self.photo_time2 = settings.get('photo_time2')
                    if 'control_mode' in settings:
                        control_mode = settings.get('control_mode')
                        self.control_mode.set(control_mode)
                    if 'thresholds_mode' in settings:
                        thresholds_mode = settings.get('thresholds_mode')
                        self.thresholds_mode.set(thresholds_mode)
                    if 'manual_thresholds' in settings:
                        self.manual_thresholds = settings.get('manual_thresholds', {})
                    if 'manual_schedule' in settings:
                        self.manual_schedule = settings.get('manual_schedule', {})
                    if self.token:
                        self.data_sender.set_token(self.token)
                        self.threshold_manager.set_token(self.token)
                        self.plant_analyzer.set_api_token(self.token)
        except:
            pass
    def save_settings(self):
        try:
            settings = {
                'theme': self.current_theme,
                'token': self.token,
                'port': self.port,
                'polling_interval': self.polling_interval,
                'data_send_interval': self.data_send_interval,
                'photo_time': self.photo_time,
                'control_mode': self.control_mode.get(),
                'thresholds_mode': self.thresholds_mode.get(),
                'camera_index': self.plant_analyzer.camera_index,
                'photo_count': getattr(self, 'photo_count', 1),
                'manual_thresholds': self.manual_thresholds,
                'manual_schedule': self.manual_schedule
            }
            if getattr(self, 'photo_count', 1) == 2:
                settings['photo_time2'] = getattr(self, 'photo_time2', 18)
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        except:
            pass
    def on_close(self):
        if self.auto_mode_running:
            self.stop_auto_mode()
        if self.arduino.running:
            self.arduino.stop_monitoring()
        if hasattr(self.data_sender, 'stop_sender_thread'):
            self.data_sender.stop_sender_thread()
        self.root.destroy()
    def apply_theme(self):
        if hasattr(self, '_theme_applying'):
            return
        self._theme_applying = True       
        try:
            theme = self.themes[self.current_theme]
            self.root.configure(bg=theme["bg_primary"])
            style = ttk.Style()
            style.theme_use('default')
            style.configure('TNotebook', background=theme["bg_primary"])
            style.configure('TNotebook.Tab', background=theme["bg_secondary"], 
                            foreground=theme["fg_primary"], padding=[10, 5])
            style.map('TNotebook.Tab', background=[('selected', theme["bg_primary"])])
            style.configure('TButton', background=theme["bg_secondary"], 
                            foreground=theme["fg_primary"])
            style.configure('TFrame', background=theme["bg_primary"])
            style.configure('TLabelframe', background=theme["bg_primary"])
            style.configure('TLabelframe.Label', background=theme["bg_primary"], 
                           foreground=theme["fg_primary"], font=("Arial", 10, "bold"))
            style.configure('TEntry', 
                          fieldbackground=theme["bg_secondary"],
                          foreground=theme["fg_primary"],
                          insertcolor=theme["fg_primary"],  
                          borderwidth=1)
            style.configure('TSpinbox', 
                          fieldbackground=theme["bg_secondary"],
                          foreground=theme["fg_primary"],
                          arrowcolor=theme["fg_primary"],
                          borderwidth=1)
            style.configure('TCombobox', 
                          fieldbackground=theme["bg_secondary"],
                          foreground=theme["fg_primary"],
                          arrowcolor=theme["fg_primary"],
                          borderwidth=1)
            style.map('TEntry', 
                     fieldbackground=[('readonly', theme["bg_secondary"]),
                                      ('disabled', theme["bg_secondary"]),
                                      ('!invalid', theme["bg_secondary"]),
                                      ('active', theme["bg_secondary"])],
                     foreground=[('readonly', theme["fg_primary"]),
                                ('disabled', theme["fg_secondary"]),
                                ('active', theme["fg_primary"])])
            style.map('TSpinbox', 
                     fieldbackground=[('readonly', theme["bg_secondary"]),
                                     ('disabled', theme["bg_secondary"]),
                                     ('!invalid', theme["bg_secondary"]),
                                     ('active', theme["bg_secondary"])],
                     foreground=[('readonly', theme["fg_primary"]),
                                ('disabled', theme["fg_secondary"]),
                                ('active', theme["fg_primary"])])
            style.map('TCombobox', 
                     fieldbackground=[('readonly', theme["bg_secondary"]),
                                     ('disabled', theme["bg_secondary"]),
                                     ('!invalid', theme["bg_secondary"]),
                                     ('active', theme["bg_secondary"])],
                     foreground=[('readonly', theme["fg_primary"]),
                                ('disabled', theme["fg_secondary"]),
                                ('active', theme["fg_primary"])])
            self.root.option_add('*TCombobox*Listbox.background', theme["bg_secondary"])
            self.root.option_add('*TCombobox*Listbox.foreground', theme["fg_primary"])
            self.root.option_add('*TCombobox*Listbox.selectBackground', theme["accent1"])
            self.root.option_add('*TCombobox*Listbox.selectForeground', theme["fg_primary"])
            style.configure('Green.TButton', foreground=theme["fg_primary"], background=theme["accent1"])
            style.configure('Card.TFrame', background=theme["bg_secondary"])
            style.configure('Device.TFrame', background=theme["bg_secondary"])
            for tab in [self.tab_weather, self.tab_monitoring, self.tab_charts, 
                       self.tab_thresholds, self.tab_settings]:
                for widget in tab.winfo_children():
                    self.apply_theme_to_widget(widget, theme)
            self._update_entry_widgets_colors(theme)
            if hasattr(self, 'ax_temp'):
                if self.sensor_history.timestamps:
                    self.update_charts()
                else:
                    self._update_chart_appearance(self.ax_temp, self.canvas_temp)
                    self._update_chart_appearance(self.ax_humidity, self.canvas_humidity)
                    self._update_chart_appearance(self.ax_soil, self.canvas_soil)
                    self._update_chart_appearance(self.ax_co2, self.canvas_co2)
                    self._update_chart_appearance(self.ax_pressure, self.canvas_pressure)
        finally:
            if hasattr(self, '_theme_applying'):
                del self._theme_applying
    def _update_entry_widgets_colors(self, theme):
        if hasattr(self, 'token_entry'):
            self.token_entry.config(style='TEntry')
        if hasattr(self, 'port_combobox'):
            self.port_combobox.config(style='TCombobox')
        if hasattr(self, 'camera_index_spinbox'):
            self.camera_index_spinbox.config(style='TSpinbox')
        if hasattr(self, 'interval_spinbox'):
            self.interval_spinbox.config(style='TSpinbox')
        if hasattr(self, 'send_interval_spinbox'):
            self.send_interval_spinbox.config(style='TSpinbox')
        if hasattr(self, 'photo_time_spinbox'):
            self.photo_time_spinbox.config(style='TSpinbox')
        if hasattr(self, 'photo_time2_spinbox'):
            self.photo_time2_spinbox.config(style='TSpinbox')
    def apply_theme_to_widget(self, widget, theme):
        if isinstance(widget, ttk.Frame) or isinstance(widget, ttk.LabelFrame):
            pass
        elif isinstance(widget, tk.Frame):
            widget.configure(bg=theme["bg_primary"])
        elif isinstance(widget, tk.Label):
            widget.configure(bg=theme["bg_primary"], fg=theme["fg_primary"])
        elif isinstance(widget, tk.Button):
            widget.configure(bg=theme["bg_secondary"], fg=theme["fg_primary"],
                            activebackground=theme["bg_primary"],
                            activeforeground=theme["fg_primary"])
        for child in widget.winfo_children():
            self.apply_theme_to_widget(child, theme)
    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        self.save_settings()
        if hasattr(self, 'theme_button'):
            self.theme_button.config(text="Переключить на темную" if self.current_theme == "light" else "Переключить на светлую")
    def update_time_loop(self):
        while True:
            self.update_time()
            time_module.sleep(1)
    def update_time(self):
        if hasattr(self, 'time_label'):
            now = datetime.now()
            time_str = now.strftime("%H:%M:%S")
            date_str = now.strftime("%d.%m.%Y")
            self.root.after(0, lambda: self.time_label.config(text=time_str))
            self.root.after(0, lambda: self.date_label.config(text=date_str))
    def start_system(self):
        if self.arduino.running:
            messagebox.showinfo("Информация", "Система уже запущена")
            return
        self.arduino.port = self.port
        self.arduino.polling_interval = self.polling_interval
        success = self.arduino.start_monitoring()
        if success:
            self.start_button.config(text="Система запущена", state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.root.after(1000, self.load_data_to_arduino)
            if self.control_mode.get() == "auto":
                self.root.after(2000, self.start_auto_mode)
        else:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к порту {self.arduino.port}")
    def stop_system(self):
        self.arduino.stop_monitoring()
        self.start_button.config(text="Запустить систему", state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    def auto_start_system(self):
        if not self.arduino.running:
            self.arduino.port = self.port
            self.arduino.polling_interval = self.polling_interval
            success = self.arduino.start_monitoring()
            if success:
                self.start_button.config(text="Система запущена", state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
                self.root.after(1000, self.load_data_to_arduino)
                if self.control_mode.get() == "auto":
                    self.root.after(2000, self.start_auto_mode)
    def update_monitoring_display(self):
        if hasattr(self, '_update_pending'):
            return
        self._update_pending = True
        self.root.after(100, self._do_update_monitoring)
    def _do_update_monitoring(self):
        if not hasattr(self, 'temperature_value'):
            if hasattr(self, '_update_pending'):
                del self._update_pending
            return
        try:
            try:
                temp = float(self.arduino.temperature)
                self.temperature_value.config(text=f"{temp:.1f} °C")
            except (ValueError, TypeError):
                self.temperature_value.config(text=f"{self.arduino.temperature} °C")
            try:
                humidity = float(self.arduino.humidity)
                self.humidity_value.config(text=f"{humidity:.1f} %")
            except (ValueError, TypeError):
                self.humidity_value.config(text=f"{self.arduino.humidity} %")
            try:
                soil = float(self.arduino.soil_moisture)
                self.soil_moisture_value.config(text=f"{soil:.1f} %")
            except (ValueError, TypeError):
                self.soil_moisture_value.config(text=f"{self.arduino.soil_moisture} %")
            try:
                co2 = float(self.arduino.co2)
                self.co2_value.config(text=f"{co2:.0f} ppm")
            except (ValueError, TypeError):
                self.co2_value.config(text=f"{self.arduino.co2} ppm")
            try:
                pressure = float(self.arduino.pressure)
                self.pressure_value.config(text=f"{pressure:.1f} мм рт. ст.")
            except (ValueError, TypeError):
                self.pressure_value.config(text=f"{self.arduino.pressure} мм рт. ст.")
            led_status = "✅" if self.arduino.led_state == 1 else "❌"
            curtains_status = "✅" if self.arduino.curtains_state == 1 else "❌"
            pump_status = "✅" if self.arduino.pump_state == 1 else "❌"
            fan_status = "✅" if self.arduino.fan_state == 1 else "❌"
            self.lamp_status.config(text=led_status)
            self.curtains_status.config(text=curtains_status)
            self.pump_status.config(text=pump_status)
            self.fan_status.config(text=fan_status)
            current_time = datetime.now()
            if (current_time - self.last_update_time).total_seconds() > self.chart_update_interval:
                has_valid_data = False
                for value in [self.arduino.temperature, self.arduino.humidity, 
                              self.arduino.soil_moisture, self.arduino.co2, 
                              self.arduino.pressure]:
                    try:
                        float(value)
                        has_valid_data = True
                        break
                    except (ValueError, TypeError):
                        pass
                if has_valid_data:
                    self.sensor_history.add_data(
                        current_time,
                        self.arduino.temperature,
                        self.arduino.humidity,
                        self.arduino.soil_moisture,
                        0,  
                        self.arduino.co2,
                        self.arduino.pressure
                    )
                    self.last_update_time = current_time
                    if self.notebook.index("current") == 2:
                        self.update_charts()
            if (current_time - self.last_send_time).total_seconds() > self.data_send_interval:
                has_valid_data = False
                try:
                    float(self.arduino.temperature)
                    float(self.arduino.humidity)
                    has_valid_data = True
                except (ValueError, TypeError):
                    has_valid_data = False
                if has_valid_data:
                    try:
                        success = self.data_sender.send_data(
                            self.arduino.temperature,
                            self.arduino.humidity,
                            self.arduino.soil_moisture,
                            0,  
                            self.arduino.co2,
                            self.arduino.pressure,  
                            self.arduino.led_state,
                            self.arduino.curtains_state,
                            self.arduino.pump_state,
                            self.arduino.fan_state
                        )
                        self.last_send_time = current_time
                        if not success:
                            self.last_send_time = current_time - timedelta(seconds=(self.data_send_interval - 60))
                    except:
                        self.last_send_time = current_time - timedelta(seconds=(self.data_send_interval - 60))
        except:
            pass
        finally:
            if hasattr(self, '_update_pending'):
                del self._update_pending
    def init_weather_tab(self):
        frame = ttk.Frame(self.tab_weather)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.weather_api_key = '7124ee85d3cb4314a6032714251303'
        self.last_weather_update = None
        time_frame = ttk.Frame(frame)
        time_frame.pack(pady=10, fill='x')
        self.time_label = tk.Label(time_frame, text="00:00:00", font=("Arial", 48))
        self.time_label.pack(pady=10)
        self.date_label = tk.Label(time_frame, text="01.01.2023", font=("Arial", 24))
        self.date_label.pack(pady=5)
        separator = tk.Label(frame, text="─" * 50)
        separator.pack(pady=10)
        weather_frame = ttk.Frame(frame)
        weather_frame.pack(pady=10, fill='both', expand=True)
        weather_header = tk.Label(weather_frame, text="Погода в Москве", font=("Arial", 24, "bold"))
        weather_header.pack(pady=10)
        self.weather_icon_label = tk.Label(weather_frame, text="")
        self.weather_icon_label.pack(pady=5)
        self.temp_label = tk.Label(weather_frame, text="--°C", font=("Arial", 36, "bold"))
        self.temp_label.pack(pady=5)
        self.desc_label = tk.Label(weather_frame, text="Загрузка...", font=("Arial", 14))
        self.desc_label.pack(pady=5)
        details_frame = ttk.Frame(weather_frame)
        details_frame.pack(pady=10, fill='x')
        humidity_frame = ttk.Frame(details_frame)
        humidity_frame.pack(side='left', expand=True, fill='both', padx=20)
        humidity_label = tk.Label(humidity_frame, text="Влажность", font=("Arial", 12))
        humidity_label.pack()
        self.weather_humidity_value = tk.Label(humidity_frame, text="--%", font=("Arial", 14, "bold"))
        self.weather_humidity_value.pack()
        wind_frame = ttk.Frame(details_frame)
        wind_frame.pack(side='right', expand=True, fill='both', padx=20)
        wind_label = tk.Label(wind_frame, text="Ветер", font=("Arial", 12))
        wind_label.pack()
        self.wind_value = tk.Label(wind_frame, text="-- м/с", font=("Arial", 14, "bold"))
        self.wind_value.pack()
        self.get_weather()
        self.schedule_weather_updates()
        self.update_time()
    def schedule_weather_updates(self):
        self.get_weather()
        now = datetime.now()
        next_hour = (now.replace(microsecond=0, second=0, minute=0) + timedelta(hours=1))
        delay_ms = int((next_hour - now).total_seconds() * 1000)
        self.root.after(delay_ms, self.schedule_weather_updates)
    def get_weather(self):
        threading.Thread(target=self._fetch_weather_data, daemon=True).start()
    def _fetch_weather_data(self):
        try:
            api_url = f'https://api.weatherapi.com/v1/current.json?key={self.weather_api_key}&q=Moscow&lang=ru'
            try:
                response = requests.get(
                    api_url,
                    timeout=10,
                    verify=os.environ.get('REQUESTS_CA_BUNDLE', True)
                )
                if response.status_code == 200:
                    data = response.json()
                    temp = data['current']['temp_c']
                    condition = data['current']['condition']['text']
                    humidity = data['current']['humidity']
                    wind_kph = data['current']['wind_kph']
                    icon_url = data['current']['condition']['icon']
                    wind_ms = round(wind_kph * 0.277778, 1)
                    try:
                        icon_response = requests.get(
                            f"https:{icon_url}",
                            timeout=10,
                            verify=os.environ.get('REQUESTS_CA_BUNDLE', True)
                        )
                        if icon_response.status_code == 200:
                            self.root.after(0, lambda: self._update_weather_ui(
                                temp, condition, humidity, wind_ms, icon_response.content
                            ))
                        else:
                            self.root.after(0, lambda: self._update_weather_ui(
                                temp, condition, humidity, wind_ms, None
                            ))
                    except:
                        self.root.after(0, lambda: self._update_weather_ui(
                            temp, condition, humidity, wind_ms, None
                        ))
                    self.last_weather_update = datetime.now()
                else:
                    self.root.after(0, lambda: self._update_weather_ui_error())
            except:
                self.root.after(0, lambda: self._update_weather_ui_error())
        except:
            self.root.after(0, lambda: self._update_weather_ui_error())
    def _update_weather_ui(self, temp, condition, humidity, wind_ms, icon_data):
        self.temp_label.config(text=f"{temp}°C")
        self.desc_label.config(text=condition)
        self.weather_humidity_value.config(text=f"{humidity}%")
        self.wind_value.config(text=f"{wind_ms} м/с")
        if icon_data:
            try:
                image = Image.open(io.BytesIO(icon_data))
                photo = ImageTk.PhotoImage(image)
                self.weather_icon = photo
                self.weather_icon_label.config(image=photo)
            except Exception as e:
                self.weather_icon_label.config(text="*")
        else:
            self.weather_icon_label.config(text="*", image="")
    def _update_weather_ui_error(self):
        self.temp_label.config(text="--°C")
        self.desc_label.config(text="Ошибка получения данных")
        self.weather_humidity_value.config(text="--%")
        self.wind_value.config(text="-- м/с")
    def init_monitoring_tab(self):
        main_frame = ttk.Frame(self.tab_monitoring)
        main_frame.pack(fill='both', expand=True)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill='x', padx=10, pady=5)
        header = tk.Label(top_frame, text="Мониторинг системы", font=("Arial", 14, "bold"))
        header.pack(side='left', pady=5)
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(side='right')
        self.start_button = ttk.Button(
            button_frame, 
            text="Запустить систему", 
            command=self.start_system,
            style='Green.TButton'
        )
        self.start_button.pack(side='left', padx=5)
        self.stop_button = ttk.Button(
            button_frame, 
            text="Остановить", 
            command=self.stop_system,
            state=tk.DISABLED
        )
        self.stop_button.pack(side='left', padx=5)
        lower_frame = ttk.Frame(main_frame)
        lower_frame.pack(fill='both', expand=True, padx=10, pady=5)
        lower_frame.grid_columnconfigure(0, weight=1)
        for i in range(4):
            lower_frame.grid_rowconfigure(i, weight=1)
        sensors_label = tk.Label(lower_frame, text="Показания датчиков", font=("Arial", 12, "bold"))
        sensors_label.grid(row=0, column=0, sticky='w', pady=(0, 3))
        self.create_sensor_cards(lower_frame)
    def create_sensor_cards(self, parent_frame):
        sensors_frame = ttk.Frame(parent_frame)
        sensors_frame.grid(row=0, column=0, rowspan=2, columnspan=3, padx=5, pady=5, sticky='nsew')
        for i in range(2):
            sensors_frame.grid_rowconfigure(i, weight=1)
        for i in range(3):
            sensors_frame.grid_columnconfigure(i, weight=1)
        temp_frame = self.create_sensor_card(sensors_frame, "", "Температура", 0, 0)
        self.temperature_value = tk.Label(temp_frame, text="-- °C", font=("Arial", 20, "bold"))
        self.temperature_value.pack(expand=True, fill='both', pady=10)
        humidity_frame = self.create_sensor_card(sensors_frame, "", "Влажность", 0, 1)
        self.humidity_value = tk.Label(humidity_frame, text="-- %", font=("Arial", 20, "bold"))
        self.humidity_value.pack(expand=True, fill='both', pady=10)
        soil_frame = self.create_sensor_card(sensors_frame, "", "Влажность почвы", 0, 2)
        self.soil_moisture_value = tk.Label(soil_frame, text="-- %", font=("Arial", 20, "bold"))
        self.soil_moisture_value.pack(expand=True, fill='both', pady=10)
        co2_frame = self.create_sensor_card(sensors_frame, "", "CO₂", 1, 0)
        self.co2_value = tk.Label(co2_frame, text="-- ppm", font=("Arial", 20, "bold"))
        self.co2_value.pack(expand=True, fill='both', pady=10)
        pressure_frame = self.create_sensor_card(sensors_frame, "", "Давление", 1, 1)
        self.pressure_value = tk.Label(pressure_frame, text="-- мм рт. ст.", font=("Arial", 20, "bold"))
        self.pressure_value.pack(expand=True, fill='both', pady=10)
        devices_label = tk.Label(parent_frame, text="Состояние устройств", font=("Arial", 12, "bold"))
        devices_label.grid(row=2, column=0, columnspan=3, padx=5, pady=(10, 3), sticky='w')
        devices_frame = ttk.Frame(parent_frame)
        devices_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=3, sticky='nsew')
        for i in range(2):
            devices_frame.grid_columnconfigure(i, weight=1)
        lamp_frame = self.create_device_card(devices_frame, "", "Освещение", 0, 0)
        self.lamp_status = tk.Label(lamp_frame, text="❌", font=("Arial", 16))
        self.lamp_status.pack(pady=2)
        curtains_frame = self.create_device_card(devices_frame, "", "Шторы", 0, 1)
        self.curtains_status = tk.Label(curtains_frame, text="❌", font=("Arial", 16))
        self.curtains_status.pack(pady=2)
        pump_frame = self.create_device_card(devices_frame, "", "Насос", 1, 0)
        self.pump_status = tk.Label(pump_frame, text="❌", font=("Arial", 16))
        self.pump_status.pack(pady=2)
        fan_frame = self.create_device_card(devices_frame, "", "Вентилятор", 1, 1)
        self.fan_status = tk.Label(fan_frame, text="❌", font=("Arial", 16))
        self.fan_status.pack(pady=2)
    def create_sensor_card(self, parent, icon, title, row, col):
        theme = self.themes[self.current_theme]
        frame = ttk.Frame(parent, style='Card.TFrame')
        frame.grid(row=row, column=col, padx=3, pady=3, sticky='nsew')
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill='x', pady=5)
        if icon and icon.strip():
            icon_label = tk.Label(header_frame, text=icon, font=("Arial", 12))
            icon_label.pack(side='left', padx=5)
            title_label = tk.Label(header_frame, text=title, font=("Arial", 10))
            title_label.pack(side='left')
        else:
            title_label = tk.Label(header_frame, text=title, font=("Arial", 12, "bold"))
            title_label.pack(anchor='center')
        return frame
    def create_device_card(self, parent, icon, title, row, col):
        theme = self.themes[self.current_theme]
        frame = ttk.Frame(parent, style='Device.TFrame')
        frame.grid(row=row, column=col, padx=4, pady=4, sticky='nsew')
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill='x', pady=5)
        if icon and icon.strip():
            icon_label = tk.Label(header_frame, text=icon, font=("Arial", 14))
            icon_label.pack(side='left', padx=5)
            title_label = tk.Label(header_frame, text=title, font=("Arial", 12, "bold"))
            title_label.pack(side='left')
        else:
            title_label = tk.Label(header_frame, text=title, font=("Arial", 14, "bold"))
            title_label.pack(anchor='center')
        return frame
    def init_charts_tab(self):
        main_frame = ttk.Frame(self.tab_charts)
        main_frame.pack(fill='both', expand=True)
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', padx=10, pady=5)
        header = tk.Label(header_frame, text="Графики показателей", font=("Arial", 14, "bold"))
        header.pack(side='left', pady=5)
        period_frame = ttk.Frame(header_frame)
        period_frame.pack(side='right')
        period_label = tk.Label(period_frame, text="Период:", font=("Arial", 10))
        period_label.pack(side='left', padx=5)
        self.period_combobox = ttk.Combobox(period_frame, values=["Последний час", "Последние 3 часа", "Последние 6 часов", "Сутки"], width=13)
        self.period_combobox.pack(side='left', padx=5)
        self.period_combobox.current(0)
        self.period_combobox.bind("<<ComboboxSelected>>", lambda e: self.update_charts())
        charts_container = ttk.Frame(main_frame)
        charts_container.pack(fill='both', expand=True, padx=5, pady=5)
        for i in range(2):
            charts_container.grid_rowconfigure(i, weight=1)
        for i in range(3):
            charts_container.grid_columnconfigure(i, weight=1)
        theme = self.themes[self.current_theme]
        bg_color = theme["bg_secondary"]
        self.fig_temp = plt.Figure(figsize=(3.5, 2.5), dpi=100, tight_layout=True, facecolor=bg_color)
        self.ax_temp = self.fig_temp.add_subplot(111)
        self.ax_temp.set_title("Температура")
        self.canvas_temp = FigureCanvasTkAgg(self.fig_temp, master=charts_container)
        self.canvas_temp.get_tk_widget().configure(bg=bg_color, highlightbackground=bg_color, highlightcolor=bg_color)
        self.canvas_temp.get_tk_widget().grid(row=0, column=0, padx=3, pady=3, sticky='nsew')
        self.fig_humidity = plt.Figure(figsize=(3.5, 2.5), dpi=100, tight_layout=True, facecolor=bg_color)
        self.ax_humidity = self.fig_humidity.add_subplot(111)
        self.ax_humidity.set_title("Влажность")
        self.canvas_humidity = FigureCanvasTkAgg(self.fig_humidity, master=charts_container)
        self.canvas_humidity.get_tk_widget().configure(bg=bg_color, highlightbackground=bg_color, highlightcolor=bg_color)
        self.canvas_humidity.get_tk_widget().grid(row=0, column=1, padx=3, pady=3, sticky='nsew')
        self.fig_soil = plt.Figure(figsize=(3.5, 2.5), dpi=100, tight_layout=True, facecolor=bg_color)
        self.ax_soil = self.fig_soil.add_subplot(111)
        self.ax_soil.set_title("Влажность почвы")
        self.canvas_soil = FigureCanvasTkAgg(self.fig_soil, master=charts_container)
        self.canvas_soil.get_tk_widget().configure(bg=bg_color, highlightbackground=bg_color, highlightcolor=bg_color)
        self.canvas_soil.get_tk_widget().grid(row=0, column=2, padx=3, pady=3, sticky='nsew')
        self.fig_co2 = plt.Figure(figsize=(3.5, 2.5), dpi=100, tight_layout=True, facecolor=bg_color)
        self.ax_co2 = self.fig_co2.add_subplot(111)
        self.ax_co2.set_title("CO₂")
        self.canvas_co2 = FigureCanvasTkAgg(self.fig_co2, master=charts_container)
        self.canvas_co2.get_tk_widget().configure(bg=bg_color, highlightbackground=bg_color, highlightcolor=bg_color)
        self.canvas_co2.get_tk_widget().grid(row=1, column=0, padx=3, pady=3, sticky='nsew')
        self.fig_pressure = plt.Figure(figsize=(3.5, 2.5), dpi=100, tight_layout=True, facecolor=bg_color)
        self.ax_pressure = self.fig_pressure.add_subplot(111)
        self.ax_pressure.set_title("Давление")
        self.canvas_pressure = FigureCanvasTkAgg(self.fig_pressure, master=charts_container)
        self.canvas_pressure.get_tk_widget().configure(bg=bg_color, highlightbackground=bg_color, highlightcolor=bg_color)
        self.canvas_pressure.get_tk_widget().grid(row=1, column=1, padx=3, pady=3, sticky='nsew')
    def _update_chart_appearance(self, ax, canvas):
        theme = self.themes[self.current_theme]
        bg_color = theme["bg_secondary"]
        fig = ax.figure
        fig.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        ax.tick_params(colors=theme["fg_primary"])
        ax.xaxis.label.set_color(theme["fg_primary"])
        ax.yaxis.label.set_color(theme["fg_primary"])
        ax.title.set_color(theme["fg_primary"])
        for spine in ax.spines.values():
            spine.set_color(theme["fg_secondary"])
        canvas.get_tk_widget().configure(
            bg=bg_color, 
            highlightbackground=bg_color, 
            highlightcolor=bg_color
        )
        canvas.draw()
    def update_charts(self):
        try:
            if self.notebook.index("current") != 2:
                return
        except:
            pass 
        if not self.sensor_history.timestamps:
            return
        period_text = self.period_combobox.get() if hasattr(self, 'period_combobox') else "Последний час"
        if period_text == "Последний час":
            hours = 1
        elif period_text == "Последние 3 часа":
            hours = 3
        elif period_text == "Последние 6 часов":
            hours = 6
        elif period_text == "Сутки":
            hours = 24
        else:
            hours = 1  
        start_time = datetime.now() - timedelta(hours=hours)
        timestamps = list(self.sensor_history.timestamps)
        temperatures = list(self.sensor_history.temperature)
        humidities = list(self.sensor_history.humidity)
        soil_moistures = list(self.sensor_history.soil_moisture)
        co2_levels = list(self.sensor_history.co2)
        pressures = list(self.sensor_history.pressure)
        if not timestamps:
            return
        filtered_data = [
            (ts, temp, hum, soil, co2, press)
            for ts, temp, hum, soil, co2, press in zip(
                timestamps, temperatures, humidities, soil_moistures, co2_levels, pressures
            )
            if ts >= start_time
        ]
        if not filtered_data:
            return
        timestamps_filtered, temps_filtered, hums_filtered, soils_filtered, co2s_filtered, pressures_filtered = zip(*filtered_data)
        theme = self.themes[self.current_theme]
        current_time = datetime.now().strftime('%H:%M')
        temp_title = f"Температура: {self.arduino.temperature}°C ({current_time})"
        hum_title = f"Влажность: {self.arduino.humidity}% ({current_time})"
        soil_title = f"Влажность почвы: {self.arduino.soil_moisture}% ({current_time})"
        co2_title = f"CO₂: {self.arduino.co2}ppm ({current_time})"
        press_title = f"Давление: {self.arduino.pressure}мм рт.ст. ({current_time})"
        self._update_chart(self.ax_temp, self.canvas_temp, timestamps_filtered, temps_filtered, 
                          temp_title, "°C", theme["block1"])
        self._update_chart(self.ax_humidity, self.canvas_humidity, timestamps_filtered, hums_filtered, 
                          hum_title, "%", theme["block2"])
        self._update_chart(self.ax_soil, self.canvas_soil, timestamps_filtered, soils_filtered, 
                          soil_title, "%", theme["block3"])
        self._update_chart(self.ax_co2, self.canvas_co2, timestamps_filtered, co2s_filtered, 
                          co2_title, "ppm", theme["block4"])
        self._update_chart(self.ax_pressure, self.canvas_pressure, timestamps_filtered, pressures_filtered, 
                          press_title, "мм рт. ст.", theme["accent1"])
    def _update_chart(self, ax, canvas, x_data, y_data, title, y_label, color):
        theme = self.themes[self.current_theme]
        ax.clear()
        ax.plot(x_data, y_data, color=color, linewidth=2)
        ax.set_title(title, fontsize=10, color=theme["fg_primary"])
        ax.set_ylabel(y_label, fontsize=9, color=theme["fg_primary"])
        ax.set_xlabel("Время", fontsize=9, color=theme["fg_primary"])
        ax.grid(True, linestyle='--', alpha=0.7, color=theme["fg_secondary"])
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.tick_params(axis='x', rotation=45, labelsize=8, colors=theme["fg_primary"])
        ax.tick_params(axis='y', labelsize=8, colors=theme["fg_primary"])
        if len(x_data) > 10:
            ax.xaxis.set_major_locator(mdates.HourLocator())
            ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=[0, 15, 30, 45]))
        if y_data:
            min_val = min(y_data)
            max_val = max(y_data)
            ax.text(0.02, 0.98, f"Макс: {max_val:.1f}", 
                    transform=ax.transAxes, fontsize=8, 
                    verticalalignment='top', color=theme["fg_primary"])
            ax.text(0.02, 0.91, f"Мин: {min_val:.1f}", 
                    transform=ax.transAxes, fontsize=8, 
                    verticalalignment='top', color=theme["fg_primary"])
        ax.set_facecolor(theme["bg_secondary"])
        canvas.figure.patch.set_facecolor(theme["bg_secondary"])
        for spine in ax.spines.values():
            spine.set_color(theme["fg_secondary"])
        ax.margins(x=0.05, y=0.1)
        canvas.get_tk_widget().configure(
            bg=theme["bg_secondary"], 
            highlightbackground=theme["bg_secondary"], 
            highlightcolor=theme["bg_secondary"]
        )
        canvas.draw()
    def on_tab_changed(self, event):
        try:
            if self.notebook.index("current") == 2:
                if hasattr(self, 'ax_temp') and self.sensor_history.timestamps:
                    self.update_charts()
        except:
            pass
    def init_thresholds_tab(self):
        main_frame = ttk.Frame(self.tab_thresholds)
        main_frame.pack(fill='both', expand=True)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill='x', padx=10, pady=5)
        header = tk.Label(top_frame, text="Пороговые значения и расписание", font=("Arial", 14, "bold"))
        header.pack(side='left', pady=5)
        mode_frame = ttk.Frame(top_frame)
        mode_frame.pack(side='right', padx=5)
        mode_label = tk.Label(mode_frame, text="Режим:", font=("Arial", 12))
        mode_label.pack(side='left', padx=5)
        auto_radio = ttk.Radiobutton(mode_frame, text="Автоматический", 
                                    variable=self.thresholds_mode, value="auto",
                                    command=self.update_thresholds_mode)
        auto_radio.pack(side='left', padx=5)
        manual_radio = ttk.Radiobutton(mode_frame, text="Ручной", 
                                      variable=self.thresholds_mode, value="manual",
                                      command=self.update_thresholds_mode)
        manual_radio.pack(side='left', padx=5)
        refresh_button = ttk.Button(top_frame, text="Обновить данные", command=self.update_thresholds_and_schedule)
        refresh_button.pack(side='right', padx=5)
        load_arduino_button = ttk.Button(top_frame, text="Загрузить в Arduino", command=self.load_data_to_arduino)
        load_arduino_button.pack(side='right', padx=5)
        inner_notebook = ttk.Notebook(main_frame)
        inner_notebook.pack(fill='both', expand=True, padx=10, pady=5)
        self.thresholds_tab = ttk.Frame(inner_notebook)
        inner_notebook.add(self.thresholds_tab, text='Пороги')
        self.schedule_tab = ttk.Frame(inner_notebook)
        inner_notebook.add(self.schedule_tab, text='Расписание')
        self.thresholds_container = ttk.Frame(self.thresholds_tab)
        self.thresholds_container.pack(fill='both', expand=True, padx=10, pady=10)
        self.schedule_container = ttk.Frame(self.schedule_tab)
        self.schedule_container.pack(fill='both', expand=True, padx=10, pady=10)
        self.threshold_status_var = tk.StringVar(value="Нажмите 'Обновить данные' для загрузки с сервера")
        status_label = tk.Label(main_frame, textvariable=self.threshold_status_var, font=("Arial", 10, "italic"))
        status_label.pack(pady=5)
        if self.thresholds_mode.get() == "auto":
            self.create_threshold_placeholders()
            self.create_schedule_placeholders()
            if self.token:
                self.root.after(1000, self.update_thresholds_and_schedule)
        else:
            self.create_manual_threshold_inputs()
            self.create_manual_schedule_inputs()
    def create_threshold_placeholders(self):
        for widget in self.thresholds_container.winfo_children():
            widget.destroy()
        header_frame = ttk.Frame(self.thresholds_container)
        header_frame.pack(fill='x', pady=5)
        headers = ["Параметр", "Диапазон", "Целевое значение", "Допустимое отклонение"]
        for i, header_text in enumerate(headers):
            header_label = tk.Label(header_frame, text=header_text, font=("Arial", 12, "bold"))
            header_label.grid(row=0, column=i, padx=10, pady=5, sticky='w')
        parameters = ["Температура", "Влажность воздуха", "Влажность почвы", "CO2"]
        for i, param in enumerate(parameters):
            param_frame = ttk.Frame(self.thresholds_container, style='Card.TFrame')
            param_frame.pack(fill='x', pady=5)
            param_label = tk.Label(param_frame, text=param, font=("Arial", 11))
            param_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')
            for j in range(1, 4):
                placeholder = tk.Label(param_frame, text="Загрузка...", font=("Arial", 11))
                placeholder.grid(row=0, column=j, padx=10, pady=10, sticky='w')
    def create_schedule_placeholders(self):
        for widget in self.schedule_container.winfo_children():
            widget.destroy()
        schedule_header = tk.Label(self.schedule_container, text="Расписание работы устройств", 
                                 font=("Arial", 12, "bold"))
        schedule_header.pack(fill='x', pady=5)
        devices_frame = ttk.Frame(self.schedule_container)
        devices_frame.pack(fill='x', pady=10)
        lamp_frame = ttk.LabelFrame(devices_frame, text="Лампа освещения")
        lamp_frame.pack(fill='x', pady=5)
        self.lamp_schedule_label = tk.Label(lamp_frame, text="Загрузка расписания...", 
                                         font=("Arial", 11), wraplength=800)
        self.lamp_schedule_label.pack(fill='x', padx=10, pady=10)
        curtains_frame = ttk.LabelFrame(devices_frame, text="Шторы")
        curtains_frame.pack(fill='x', pady=5)
        self.curtains_schedule_label = tk.Label(curtains_frame, text="Загрузка расписания...", 
                                             font=("Arial", 11), wraplength=800)
        self.curtains_schedule_label.pack(fill='x', padx=10, pady=10)
    def update_thresholds_and_schedule(self):
        self.threshold_status_var.set("Загрузка данных с сервера...")
        threading.Thread(target=self._fetch_thresholds_and_schedule, daemon=True).start()
    def _fetch_thresholds_and_schedule(self):
        try:
            thresholds = self.threshold_manager.get_thresholds()
            schedule = self.threshold_manager.get_schedule()
            self.root.after(0, lambda: self._update_thresholds_ui(thresholds))
            self.root.after(0, lambda: self._update_schedule_ui(schedule))
            if self.control_mode.get() == "auto" and self.thresholds_mode.get() == "auto":
                self.load_auto_data_to_arduino()
        except Exception as e:
            error_msg = f"Ошибка при получении данных: {str(e)}"
            print(error_msg)
            self.root.after(0, lambda: self.threshold_status_var.set(error_msg))
    def _update_schedule_ui(self, schedule_data):
        if not schedule_data:
            self.lamp_schedule_label.config(text="Не удалось получить расписание")
            self.curtains_schedule_label.config(text="Не удалось получить расписание")
            return
        schedule = None
        if isinstance(schedule_data, dict) and 'schedule' in schedule_data:
            schedule = schedule_data['schedule']
        else:
            schedule = schedule_data
        formatted_schedule = self.threshold_manager.format_schedule(schedule_data)
        if isinstance(formatted_schedule, dict):
            lamp_intervals = formatted_schedule.get('lamp', "Нет активных периодов")
            curtains_intervals = formatted_schedule.get('curtains', "Нет активных периодов")
            self.lamp_schedule_label.config(text=f"Лампа включена: {lamp_intervals}")
            self.curtains_schedule_label.config(text=f"Шторы открыты: {curtains_intervals}")
        else:
            self.lamp_schedule_label.config(text="Ошибка форматирования расписания")
            self.curtains_schedule_label.config(text="Ошибка форматирования расписания")
        current_time = datetime.now().strftime("%H:%M:%S")
        self.threshold_status_var.set(f"Данные успешно обновлены в {current_time}")
        self.apply_theme()
    def init_settings_tab(self):
        main_frame = ttk.Frame(self.tab_settings)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)  
        header = tk.Label(main_frame, text="Настройки приложения", font=("Arial", 14, "bold"))
        header.pack(pady=5)  
        theme_frame = ttk.LabelFrame(main_frame, text="Тема интерфейса")
        theme_frame.pack(fill='x', pady=5)  
        theme_buttons_frame = ttk.Frame(theme_frame)
        theme_buttons_frame.pack(fill='x', padx=10, pady=5)  
        self.theme_var = tk.StringVar(value=self.current_theme)
        light_radio = ttk.Radiobutton(theme_buttons_frame, text="Светлая", 
                                      variable=self.theme_var, value="light",
                                      command=lambda: self.change_theme("light"))
        light_radio.pack(side='left', padx=20)
        dark_radio = ttk.Radiobutton(theme_buttons_frame, text="Темная", 
                                     variable=self.theme_var, value="dark",
                                     command=lambda: self.change_theme("dark"))
        dark_radio.pack(side='left', padx=20)
        api_frame = ttk.LabelFrame(main_frame, text="Настройки API")
        api_frame.pack(fill='x', pady=5)  
        token_frame = ttk.Frame(api_frame)
        token_frame.pack(fill='x', padx=10, pady=5)  
        token_label = tk.Label(token_frame, text="API токен:", font=("Arial", 12))
        token_label.pack(side='left', padx=5)  
        self.token_entry = ttk.Entry(token_frame, width=40)  
        self.token_entry.pack(side='left', padx=5, fill='x', expand=True)  
        self.token_entry.insert(0, self.token)
        self.token_entry.bind("<FocusOut>", lambda e: self.auto_save_settings())
        paste_token_button = ttk.Button(token_frame, text="Вставить", 
                                     command=self.paste_token)
        paste_token_button.pack(side='left', padx=5)
        api_buttons_frame = ttk.Frame(api_frame)
        api_buttons_frame.pack(fill='x', padx=10, pady=5)  
        get_token_button = ttk.Button(api_buttons_frame, text="Получить токен",
                                     command=self.open_token_page)
        get_token_button.pack(side='left', padx=5)  
        arduino_frame = ttk.LabelFrame(main_frame, text="Настройки Arduino")
        arduino_frame.pack(fill='x', pady=5)  
        port_frame = ttk.Frame(arduino_frame)
        port_frame.pack(fill='x', padx=10, pady=5)  
        port_label = tk.Label(port_frame, text="COM порт:", font=("Arial", 12))
        port_label.pack(side='left', padx=5)  
        self.port_combobox = ttk.Combobox(port_frame, values=self.list_ports(), width=10)  
        self.port_combobox.pack(side='left', padx=5)  
        self.port_combobox.set(self.port)
        self.port_combobox.bind("<<ComboboxSelected>>", lambda e: self.auto_save_settings())
        refresh_port_button = ttk.Button(port_frame, text="Обновить", 
                                         command=lambda: self.port_combobox.configure(values=self.list_ports()))
        refresh_port_button.pack(side='left', padx=5)  
        connect_button = ttk.Button(port_frame, text="Подключить Arduino", 
                                   command=self.connect_arduino)
        connect_button.pack(side='left', padx=5)  
        camera_frame = ttk.LabelFrame(main_frame, text="Настройки камеры")
        camera_frame.pack(fill='x', pady=5)  
        camera_index_frame = ttk.Frame(camera_frame)
        camera_index_frame.pack(fill='x', padx=10, pady=5)  
        camera_index_label = tk.Label(camera_index_frame, text="Индекс:", font=("Arial", 12))
        camera_index_label.pack(side='left', padx=5)  
        self.camera_index_spinbox = ttk.Spinbox(camera_index_frame, from_=0, to=10, width=3)  
        self.camera_index_spinbox.pack(side='left', padx=5)  
        self.camera_index_spinbox.set(self.plant_analyzer.camera_index)
        self.camera_index_spinbox.bind("<FocusOut>", lambda e: self.auto_save_settings())
        self.camera_index_spinbox.bind("<<Increment>>", lambda e: self.auto_save_settings())
        self.camera_index_spinbox.bind("<<Decrement>>", lambda e: self.auto_save_settings())
        test_camera_button = ttk.Button(camera_index_frame, text="Проверить камеру", 
                                       command=self.test_camera)
        test_camera_button.pack(side='left', padx=5)  
        intervals_frame = ttk.LabelFrame(main_frame, text="Настройки интервалов")
        intervals_frame.pack(fill='x', pady=5)  
        polling_frame = ttk.Frame(intervals_frame)
        polling_frame.pack(fill='x', padx=10, pady=5)  
        polling_label = tk.Label(polling_frame, text="Опрос Arduino:", font=("Arial", 12))
        polling_label.pack(side='left', padx=5)  
        self.interval_spinbox = ttk.Spinbox(polling_frame, from_=1, to=60, width=3)  
        self.interval_spinbox.pack(side='left', padx=5)  
        self.interval_spinbox.set(self.polling_interval)
        self.interval_spinbox.bind("<FocusOut>", lambda e: self.auto_save_settings())
        self.interval_spinbox.bind("<<Increment>>", lambda e: self.auto_save_settings())
        self.interval_spinbox.bind("<<Decrement>>", lambda e: self.auto_save_settings())
        interval_units = tk.Label(polling_frame, text="секунд", font=("Arial", 12))
        interval_units.pack(side='left')
        send_interval_frame = ttk.Frame(intervals_frame)
        send_interval_frame.pack(fill='x', padx=10, pady=5)
        send_interval_label = tk.Label(send_interval_frame, text="Отправка данных:", font=("Arial", 12))
        send_interval_label.pack(side='left', padx=5)
        self.send_interval_spinbox = ttk.Spinbox(send_interval_frame, from_=300, to=7200, width=4)  
        self.send_interval_spinbox.pack(side='left', padx=5)
        self.send_interval_spinbox.set(self.data_send_interval)
        self.send_interval_spinbox.bind("<FocusOut>", lambda e: self.auto_save_settings())
        self.send_interval_spinbox.bind("<<Increment>>", lambda e: self.auto_save_settings())
        self.send_interval_spinbox.bind("<<Decrement>>", lambda e: self.auto_save_settings())
        send_interval_units = tk.Label(send_interval_frame, text="секунд", font=("Arial", 12))
        send_interval_units.pack(side='left')
        photo_count_frame = ttk.Frame(intervals_frame)
        photo_count_frame.pack(fill='x', padx=10, pady=5)  
        photo_count_label = tk.Label(photo_count_frame, text="Фото в день:", font=("Arial", 12))
        photo_count_label.pack(side='left', padx=5)  
        self.photo_count_var = tk.IntVar(value=1)
        self.photo_count_var.trace_add("write", self.auto_save_on_change)
        photo_one = ttk.Radiobutton(photo_count_frame, text="1 фото", 
                                   variable=self.photo_count_var, value=1)
        photo_one.pack(side='left', padx=5)  
        photo_two = ttk.Radiobutton(photo_count_frame, text="2 фото", 
                                   variable=self.photo_count_var, value=2)
        photo_two.pack(side='left', padx=5)  
        photo_time_frame = ttk.Frame(intervals_frame)
        photo_time_frame.pack(fill='x', padx=10, pady=5)  
        photo_time_label = tk.Label(photo_time_frame, text="Время фото:", font=("Arial", 12))
        photo_time_label.pack(side='left', padx=5)  
        self.photo_time_spinbox = ttk.Spinbox(photo_time_frame, from_=1, to=24, width=3)  
        self.photo_time_spinbox.pack(side='left', padx=5)  
        self.photo_time_spinbox.set(self.photo_time if hasattr(self, 'photo_time') else 12)
        self.photo_time_spinbox.bind("<FocusOut>", lambda e: self.auto_save_settings())
        self.photo_time_spinbox.bind("<<Increment>>", lambda e: self.auto_save_settings())
        self.photo_time_spinbox.bind("<<Decrement>>", lambda e: self.auto_save_settings())
        time_units = tk.Label(photo_time_frame, text="час дня", font=("Arial", 12))
        time_units.pack(side='left')
        self.photo_time2_frame = ttk.Frame(intervals_frame)
        self.photo_time2_frame.pack(fill='x', padx=10, pady=5)  
        photo_time2_label = tk.Label(self.photo_time2_frame, text="Время фото 2:", font=("Arial", 12))
        photo_time2_label.pack(side='left', padx=5)  
        self.photo_time2_spinbox = ttk.Spinbox(self.photo_time2_frame, from_=1, to=24, width=3)  
        self.photo_time2_spinbox.pack(side='left', padx=5)  
        self.photo_time2_spinbox.set(getattr(self, 'photo_time2', 18))  
        self.photo_time2_spinbox.bind("<FocusOut>", lambda e: self.auto_save_settings())
        self.photo_time2_spinbox.bind("<<Increment>>", lambda e: self.auto_save_settings())
        self.photo_time2_spinbox.bind("<<Decrement>>", lambda e: self.auto_save_settings())
        time2_units = tk.Label(self.photo_time2_frame, text="час дня", font=("Arial", 12))
        time2_units.pack(side='left')
        if self.photo_count_var.get() == 1:
            self.photo_time2_frame.pack_forget()
        self.photo_count_var.trace_add("write", self.toggle_second_photo_time)
        app_control_frame = ttk.LabelFrame(main_frame, text="Управление приложением")
        app_control_frame.pack(fill='x', pady=5)
        control_buttons_frame = ttk.Frame(app_control_frame)
        control_buttons_frame.pack(fill='x', padx=10, pady=5)
        fullscreen_button = ttk.Button(control_buttons_frame, text="Выйти из полноэкранного режима", 
                                      command=self.toggle_fullscreen)
        fullscreen_button.pack(side='left', padx=5)
        close_button = ttk.Button(control_buttons_frame, text="Закрыть приложение", 
                                command=self.close_app)
        close_button.pack(side='left', padx=5)
    def auto_save_on_change(self, *args):
        self.toggle_second_photo_time(*args)
        self.auto_save_settings()
    def auto_save_settings(self):
        self.save_settings_from_ui()
    def paste_token(self):
        try:
            self.token_entry.delete(0, tk.END)
            self.token_entry.insert(0, self.root.clipboard_get())
            self.auto_save_settings()
        except:
            pass
    def change_theme(self, theme_name):
        if theme_name != self.current_theme:
            self.current_theme = theme_name
            self.apply_theme()
            self.save_settings()
    def toggle_fullscreen(self):
        try:
            current_fullscreen = self.root.attributes('-fullscreen')
            if current_fullscreen:
                self.root.attributes('-fullscreen', False)
                self.root.overrideredirect(False)
                self.root.geometry("1200x800")
                self.root.title("ФитоДомик")
            else:
                self.root.attributes('-fullscreen', True)
                self.root.overrideredirect(True)
        except Exception as e:
            print(f"Ошибка переключения полноэкранного режима: {e}")
    
    def close_app(self):
        self.on_close()
    def toggle_second_photo_time(self, *args):
        if self.photo_count_var.get() == 1:
            self.photo_time2_frame.pack_forget()
        else:
            self.photo_time2_frame.pack(fill='x', padx=10, pady=5)
    def open_token_page(self):
        import webbrowser
        webbrowser.open("https://fitodomik.online/get_token.php")
    def connect_arduino(self):
        self.port = self.port_combobox.get()
        self.arduino.port = self.port
        success = self.arduino.connect()
        if success:
            messagebox.showinfo("Arduino", "Подключение к Arduino успешно установлено")
        else:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к порту {self.port}")
    def save_settings_from_ui(self):
        self.token = self.token_entry.get()
        self.port = self.port_combobox.get()
        try:
            self.polling_interval = int(self.interval_spinbox.get())
        except ValueError:
            self.polling_interval = 5  
        try:
            self.data_send_interval = int(self.send_interval_spinbox.get())
            if self.data_send_interval < 300:  
                self.data_send_interval = 300
        except ValueError:
            self.data_send_interval = 300
        try:
            self.photo_time = int(self.photo_time_spinbox.get())
            if self.photo_time < 1 or self.photo_time > 24:
                self.photo_time = 12  
        except ValueError:
            self.photo_time = 12  
        try:
            camera_index = int(self.camera_index_spinbox.get())
            if 0 <= camera_index <= 10:
                self.plant_analyzer.camera_index = camera_index
        except ValueError:
            pass
        self.photo_count = self.photo_count_var.get()
        if self.photo_count == 2:
            try:
                self.photo_time2 = int(self.photo_time2_spinbox.get())
                if self.photo_time2 < 1 or self.photo_time2 > 24:
                    self.photo_time2 = 18  
            except ValueError:
                self.photo_time2 = 18
        self.data_sender.set_token(self.token)
        self.threshold_manager.set_token(self.token)
        self.plant_analyzer.set_api_token(self.token)
        self.save_settings()
    def init_control_tab(self):
        main_frame = ttk.Frame(self.tab_control)
        main_frame.pack(fill='both', expand=True)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill='x', padx=10, pady=5)
        header = tk.Label(top_frame, text="Управление устройствами", font=("Arial", 14, "bold"))
        header.pack(side='left', pady=5)
        mode_frame = ttk.Frame(top_frame)
        mode_frame.pack(side='right', padx=5)
        mode_label = tk.Label(mode_frame, text="Режим:", font=("Arial", 12))
        mode_label.pack(side='left', padx=5)
        manual_radio = ttk.Radiobutton(mode_frame, text="Ручной", variable=self.control_mode, value="manual", 
                                      command=self.update_control_mode)
        manual_radio.pack(side='left', padx=5)
        auto_radio = ttk.Radiobutton(mode_frame, text="Автоматический", variable=self.control_mode, value="auto", 
                                    command=self.update_control_mode)
        auto_radio.pack(side='left', padx=5)
        devices_frame = ttk.Frame(main_frame)
        devices_frame.pack(fill='both', expand=True, padx=10, pady=5)
        for i in range(2):
            devices_frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            devices_frame.grid_columnconfigure(i, weight=1)
        self.create_device_control_cards(devices_frame)
    def init_analysis_tab(self):
        main_frame = ttk.Frame(self.tab_analysis)
        main_frame.pack(fill='both', expand=True)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill='x', padx=10, pady=5)
        header = tk.Label(top_frame, text="Анализ состояния растения", font=("Arial", 14, "bold"))
        header.pack(side='left', pady=5)
        self.next_photo_info_label = tk.Label(top_frame, text="", font=("Arial", 10))
        self.next_photo_info_label.pack(side='right', padx=10)
        self.update_next_photo_time()
        photo_frame = ttk.Frame(main_frame)
        photo_frame.pack(fill='x', padx=10, pady=5)
        photo_button = ttk.Button(photo_frame, text="Сделать фото и анализ", command=self.take_photo_and_analyze)
        photo_button.pack(pady=5, ipadx=20, ipady=5)
        photo_settings_frame = ttk.Frame(photo_frame)
        photo_settings_frame.pack(fill='x', pady=3)
        if self.photo_count == 1:
            photo_settings_text = f"Настроено автоматическое фото в {self.photo_time}:00"
        else:
            photo_settings_text = f"Настроено автоматическое фото в {self.photo_time}:00 и {self.photo_time2}:00"
        photo_settings_label = tk.Label(photo_settings_frame, text=photo_settings_text, font=("Arial", 10))
        photo_settings_label.pack(anchor='center')
        images_frame = ttk.Frame(main_frame)
        images_frame.pack(fill='both', expand=True, padx=10, pady=5)
        images_frame.columnconfigure(0, weight=1)
        images_frame.columnconfigure(1, weight=1)
        images_frame.rowconfigure(0, weight=0)  
        images_frame.rowconfigure(1, weight=0)
        left_image_label = tk.Label(images_frame, text="Оригинальное фото:", anchor='w', font=("Arial", 10, "bold"))
        left_image_label.grid(row=0, column=0, sticky='w', padx=5, pady=(0, 2))
        right_image_label = tk.Label(images_frame, text="Анализ:", anchor='w', font=("Arial", 10, "bold"))
        right_image_label.grid(row=0, column=1, sticky='w', padx=5, pady=(0, 2))
        image_height = 170  
        left_frame = ttk.Frame(images_frame, style='Card.TFrame')
        left_frame.grid(row=1, column=0, padx=5, pady=2, sticky='nsew')
        self.control_original_image = tk.Label(left_frame, text="Нет изображения", 
                                     relief="solid", background="#222222", foreground="white",
                                     anchor='center')
        self.control_original_image.pack(fill='both', expand=True, padx=5, pady=5)
        right_frame = ttk.Frame(images_frame, style='Card.TFrame')
        right_frame.grid(row=1, column=1, padx=5, pady=2, sticky='nsew')
        self.control_processed_image = tk.Label(right_frame, text="Нет изображения", 
                                      relief="solid", background="#222222", foreground="white",
                                      anchor='center')
        self.control_processed_image.pack(fill='both', expand=True, padx=5, pady=5)
        left_frame.config(height=image_height, width=350)
        right_frame.config(height=image_height, width=350)
        result_frame = ttk.Frame(main_frame)
        result_frame.pack(fill='x', pady=5, padx=10)
        results_label = tk.Label(result_frame, text="Результаты анализа:", font=("Arial", 10, "bold"))
        results_label.pack(anchor='w', pady=3)
        self.control_analysis_results = tk.Label(result_frame, text="Нет данных", wraplength=900,
                                       justify=tk.LEFT, anchor='w')
        self.control_analysis_results.pack(fill='x', pady=3)
    def create_device_control_cards(self, parent):
        style = ttk.Style()
        style.configure('Device.TFrame', relief='raised', borderwidth=2, background='#333333')
        lamp_card = ttk.Frame(parent, style='Device.TFrame')
        lamp_card.grid(row=0, column=0, padx=15, pady=15, sticky='nsew')
        lamp_title = tk.Label(lamp_card, text="Освещение", font=("Arial", 16, "bold"))
        lamp_title.pack(pady=10)
        self.lamp_status_label = tk.Label(lamp_card, text="Состояние: Выключено", font=("Arial", 12))
        self.lamp_status_label.pack(pady=10)
        self.lamp_button = ttk.Button(lamp_card, text="Включить", 
                              command=lambda: self.toggle_device("LED"))
        self.lamp_button.pack(pady=15, ipadx=20, ipady=8)
        curtains_card = ttk.Frame(parent, style='Device.TFrame')
        curtains_card.grid(row=0, column=1, padx=15, pady=15, sticky='nsew')
        curtains_title = tk.Label(curtains_card, text="Шторы", font=("Arial", 16, "bold"))
        curtains_title.pack(pady=10)
        self.curtains_status_label = tk.Label(curtains_card, text="Состояние: Закрыты", font=("Arial", 12))
        self.curtains_status_label.pack(pady=10)
        self.curtains_button = ttk.Button(curtains_card, text="Открыть", 
                                  command=lambda: self.toggle_device("CURTAINS"))
        self.curtains_button.pack(pady=15, ipadx=20, ipady=8)
        pump_card = ttk.Frame(parent, style='Device.TFrame')
        pump_card.grid(row=1, column=0, padx=15, pady=15, sticky='nsew')
        pump_title = tk.Label(pump_card, text="Насос", font=("Arial", 16, "bold"))
        pump_title.pack(pady=10)
        self.pump_status_label = tk.Label(pump_card, text="Состояние: Выключен", font=("Arial", 12))
        self.pump_status_label.pack(pady=10)
        self.pump_button = ttk.Button(pump_card, text="Включить", 
                              command=lambda: self.toggle_device("RELAY3"))
        self.pump_button.pack(pady=15, ipadx=20, ipady=8)
        fan_card = ttk.Frame(parent, style='Device.TFrame')
        fan_card.grid(row=1, column=1, padx=15, pady=15, sticky='nsew')
        fan_title = tk.Label(fan_card, text="Вентилятор", font=("Arial", 16, "bold"))
        fan_title.pack(pady=10)
        self.fan_status_label = tk.Label(fan_card, text="Состояние: Выключен", font=("Arial", 12))
        self.fan_status_label.pack(pady=10)
        self.fan_button = ttk.Button(fan_card, text="Включить", 
                             command=lambda: self.toggle_device("RELAY4"))
        self.fan_button.pack(pady=15, ipadx=20, ipady=8)
        self.update_control_display()
    def toggle_device(self, device_type):
        if self.control_mode.get() == "auto":
            messagebox.showinfo("Режим", "В автоматическом режиме управление недоступно. Переключите в ручной режим.")
            return
        if not self.arduino.is_connected:
            success = self.arduino.connect()
            if not success:
                messagebox.showerror("Ошибка", "Не удалось подключиться к Arduino")
                return
        device_names = {
            "LED": "Лампа",
            "CURTAINS": "Шторы", 
            "RELAY3": "Насос",
            "RELAY4": "Вентилятор"
        }
        device_name = device_names.get(device_type, device_type)
        success = self.arduino.send_command(device_type, None)  
        if not success:
            messagebox.showerror("Ошибка", "Не удалось отправить команду")
            return
        self.arduino.request_device_states()
        self.update_control_display()
    def get_device_state(self, device_type):
        if device_type == "LED":
            return self.arduino.led_state
        elif device_type == "CURTAINS":
            return self.arduino.curtains_state
        elif device_type == "RELAY3":
            return self.arduino.pump_state
        elif device_type == "RELAY4":
            return self.arduino.fan_state
        return 0
    def update_device_state(self, device_type, state):
        pass
    def update_control_display(self):
        mode = self.control_mode.get()
        state = tk.NORMAL if mode == "manual" else tk.DISABLED
        lamp_text = "Выключить лампу" if self.arduino.led_state == 1 else "Включить лампу"
        curtains_text = "Закрыть шторы" if self.arduino.curtains_state == 1 else "Открыть шторы"
        pump_text = "Выключить насос" if self.arduino.pump_state == 1 else "Включить насос"
        fan_text = "Выключить вентилятор" if self.arduino.fan_state == 1 else "Включить вентилятор"
        self.lamp_button.config(text=lamp_text, state=state)
        self.curtains_button.config(text=curtains_text, state=state)
        self.pump_button.config(text=pump_text, state=state)
        self.fan_button.config(text=fan_text, state=state)
        self.update_device_indicator("lamp", self.arduino.led_state)
        self.update_device_indicator("curtains", self.arduino.curtains_state)
        self.update_device_indicator("pump", self.arduino.pump_state)
        self.update_device_indicator("fan", self.arduino.fan_state)
    def update_device_indicator(self, device, state):
        theme = self.themes[self.current_theme]
        active_color = theme["accent1"]  
        inactive_color = theme["fg_secondary"]  
        color = active_color if state == 1 else inactive_color
        if device == "lamp":
            if hasattr(self, 'lamp_indicator'):
                self.lamp_indicator.config(bg=color)
            if hasattr(self, 'lamp_status_label'):
                status_text = "Состояние: Включено" if state == 1 else "Состояние: Выключено"
                self.lamp_status_label.config(text=status_text)
        elif device == "curtains":
            if hasattr(self, 'curtains_indicator'):
                self.curtains_indicator.config(bg=color)
            if hasattr(self, 'curtains_status_label'):
                status_text = "Состояние: Открыты" if state == 1 else "Состояние: Закрыты"
                self.curtains_status_label.config(text=status_text)
        elif device == "pump":
            if hasattr(self, 'pump_indicator'):
                self.pump_indicator.config(bg=color)
            if hasattr(self, 'pump_status_label'):
                status_text = "Состояние: Включен" if state == 1 else "Состояние: Выключен"
                self.pump_status_label.config(text=status_text)
        elif device == "fan":
            if hasattr(self, 'fan_indicator'):
                self.fan_indicator.config(bg=color)
            if hasattr(self, 'fan_status_label'):
                status_text = "Состояние: Включен" if state == 1 else "Состояние: Выключен"
                self.fan_status_label.config(text=status_text)
    def take_photo_and_analyze(self, is_auto=False):
        self.plant_analyzer.set_api_token(self.token)
        self.control_original_image.config(text="Идет анализ...")
        self.control_processed_image.config(text="Пожалуйста, подождите...")
        self.control_analysis_results.config(text="Обработка изображения...")
        threading.Thread(target=lambda: self._run_analysis(is_auto), daemon=True).start()
    def _run_analysis(self, is_auto=False):
        results = self.plant_analyzer.run_analysis(callback=lambda *args: self._analysis_callback(*args, is_auto=is_auto))
    def _analysis_callback(self, original_image, detection_image, analysis, error, is_auto=False):
        if error:
            self.root.after(0, lambda: self.control_analysis_results.config(text=f"Ошибка: {error}"))
            return
        if original_image is None or detection_image is None or analysis is None:
            self.root.after(0, lambda: self.control_analysis_results.config(text="Не удалось получить результаты анализа"))
            return
        original_tk = self.cv2_to_tkinter(original_image)
        detection_tk = self.cv2_to_tkinter(detection_image)
        self.root.after(0, lambda: self._update_analysis_ui(original_tk, detection_tk, analysis, is_auto))
    def _update_analysis_ui(self, original_tk, detection_tk, analysis, is_auto=False):
        self.original_tk_image = original_tk
        self.detection_tk_image = detection_tk
        self.control_original_image.config(image=original_tk, text="")
        self.control_processed_image.config(image=detection_tk, text="")
        result_text = f"Дата анализа: {analysis['timestamp']}\n"
        if is_auto:
            result_text += "Фото сделано автоматически по расписанию\n"
        result_text += f"Состояние: {analysis['состояние']}\n"
        result_text += f"Цвета: {analysis['распределение цветов']}\n"
        result_text += f"Детали: {analysis['детали']}\n"
        result_text += f"Рекомендации: {analysis['рекомендации']}"
        self.control_analysis_results.config(text=result_text)
    def cv2_to_tkinter(self, image):
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        max_width = 350
        max_height = 200
        height, width = rgb_image.shape[:2]
        if width > max_width or height > max_height:
            scale = min(max_width/width, max_height/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            rgb_image = cv2.resize(rgb_image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        pil_image = Image.fromarray(rgb_image)
        tk_image = ImageTk.PhotoImage(image=pil_image)
        return tk_image
    def list_ports(self):
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.device)
        return ports
    def test_camera(self):
        try:
            if self.plant_analyzer.initialize_camera():
                image = self.plant_analyzer.capture_image()
                if image is not None:
                    tk_image = self.cv2_to_tkinter(image)
                    preview_window = tk.Toplevel(self.root)
                    preview_window.title("Тест камеры")
                    preview_window.geometry("500x400")
                    image_label = tk.Label(preview_window)
                    image_label.pack(fill='both', expand=True, padx=10, pady=10)
                    image_label.config(image=tk_image)
                    image_label.image = tk_image  
                    close_button = ttk.Button(preview_window, text="Закрыть", 
                                             command=preview_window.destroy)
                    close_button.pack(pady=10)
                else:
                    messagebox.showerror("Ошибка", "Не удалось получить изображение с камеры")
            else:
                messagebox.showerror("Ошибка", "Не удалось инициализировать камеру")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при тестировании камеры: {str(e)}")
        finally:
            self.plant_analyzer.release_camera()
    def _update_thresholds_ui(self, thresholds):
        if not thresholds:
            self.threshold_status_var.set("Не удалось получить пороговые значения. Проверьте подключение и API токен.")
            return
        for widget in self.thresholds_container.winfo_children():
            widget.destroy()
        header_frame = ttk.Frame(self.thresholds_container)
        header_frame.pack(fill='x', pady=5)
        headers = ["Параметр", "Диапазон", "Целевое значение", "Допустимое отклонение"]
        for i, header_text in enumerate(headers):
            header_label = tk.Label(header_frame, text=header_text, font=("Arial", 12, "bold"))
            header_label.grid(row=0, column=i, padx=10, pady=5, sticky='w')
        formatted_thresholds = self.threshold_manager.format_thresholds(thresholds)
        if isinstance(formatted_thresholds, str):
            self.threshold_status_var.set(formatted_thresholds)
            return
        for i, threshold in enumerate(formatted_thresholds):
            param_frame = ttk.Frame(self.thresholds_container, style='Card.TFrame')
            param_frame.pack(fill='x', pady=5)
            theme = self.themes[self.current_theme]
            colors = [theme["block1"], theme["block2"], theme["block3"], theme["block4"]]
            color_index = i % len(colors)
            param_label = tk.Label(param_frame, text=threshold['name'], font=("Arial", 11, "bold"))
            param_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')
            range_label = tk.Label(param_frame, text=threshold['range'], font=("Arial", 11))
            range_label.grid(row=0, column=1, padx=10, pady=10, sticky='w')
            target_label = tk.Label(param_frame, text=threshold['target'], font=("Arial", 11, "bold"), fg=colors[color_index])
            target_label.grid(row=0, column=2, padx=10, pady=10, sticky='w')
            tolerance_label = tk.Label(param_frame, text=threshold['tolerance'], font=("Arial", 11))
            tolerance_label.grid(row=0, column=3, padx=10, pady=10, sticky='w')
        self.apply_theme()
    def check_photo_time(self):
        now = datetime.now()
        current_date = now.date()
        current_hour = now.hour
        current_minute = now.minute
        today_date_str = current_date.strftime("%Y-%m-%d")
        last_photo_date_str = self.last_auto_photo_date.strftime("%Y-%m-%d") if self.last_auto_photo_date else None
        if last_photo_date_str != today_date_str or (self.photo_count == 2 and hasattr(self, 'last_photo_hour') and self.last_photo_hour == self.photo_time and current_hour == self.photo_time2):
            if current_hour == self.photo_time and current_minute < 5:
                self.take_photo_and_analyze(is_auto=True)
                self.last_auto_photo_date = current_date
                self.last_photo_hour = self.photo_time
            elif self.photo_count == 2 and current_hour == self.photo_time2 and current_minute < 5:
                if not hasattr(self, 'last_photo_hour') or self.last_photo_hour != self.photo_time2:
                    self.take_photo_and_analyze(is_auto=True)
                    self.last_auto_photo_date = current_date
                    self.last_photo_hour = self.photo_time2
        self.update_next_photo_time()
        self.root.after(60000, self.check_photo_time)
    def update_next_photo_time(self):
        if not hasattr(self, 'next_photo_info_label'):
            return
        now = datetime.now()
        current_date = now.date()
        photo_time1 = datetime.combine(current_date, datetime_time(hour=self.photo_time, minute=0))
        times = [photo_time1]
        if self.photo_count == 2:
            photo_time2 = datetime.combine(current_date, datetime_time(hour=self.photo_time2, minute=0))
            times.append(photo_time2)
        tomorrow = current_date + timedelta(days=1)
        tomorrow_photo1 = datetime.combine(tomorrow, datetime_time(hour=self.photo_time, minute=0))
        times.append(tomorrow_photo1)
        if self.photo_count == 2:
            tomorrow_photo2 = datetime.combine(tomorrow, datetime_time(hour=self.photo_time2, minute=0))
            times.append(tomorrow_photo2)
        future_times = [t for t in times if t > now]
        next_photo_time = min(future_times) if future_times else tomorrow_photo1
        time_diff = next_photo_time - now
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        time_str = ""
        if time_diff.days > 0:
            time_str = f"До следующего фото: {time_diff.days} д. {hours} ч. {minutes} мин."
        elif hours > 0:
            time_str = f"До следующего фото: {hours} ч. {minutes} мин."
        else:
            time_str = f"До следующего фото: {minutes} мин."
        next_photo_hour = next_photo_time.hour
        time_str += f" ({next_photo_hour}:00)"
        self.next_photo_info_label.config(text=time_str)
    def update_thresholds_mode(self):
        mode = self.thresholds_mode.get()
        for widget in self.thresholds_container.winfo_children():
            widget.destroy()
        for widget in self.schedule_container.winfo_children():
            widget.destroy()
        if mode == "auto":
            self.create_threshold_placeholders()
            self.create_schedule_placeholders()
            if self.token:
                self.update_thresholds_and_schedule()
                if self.control_mode.get() == "auto":
                    self.root.after(3000, self.load_data_to_arduino)
        else:
            self.create_manual_threshold_inputs()
            self.create_manual_schedule_inputs()
            if self.control_mode.get() == "auto":
                self.root.after(1000, self.load_data_to_arduino)
        self.save_settings()
    def save_manual_thresholds(self, param_key=None):
        if not hasattr(self, 'manual_input_fields'):
            return
        try:
            if param_key:
                fields = self.manual_input_fields.get(param_key)
                if fields:
                    self.manual_thresholds[param_key] = {
                        "min": float(fields["min"].get()),
                        "max": float(fields["max"].get()),
                        "target": float(fields["target"].get()),
                        "tolerance": float(fields["tolerance"].get())
                    }
            else:
                for key, fields in self.manual_input_fields.items():
                    self.manual_thresholds[key] = {
                        "min": float(fields["min"].get()),
                        "max": float(fields["max"].get()),
                        "target": float(fields["target"].get()),
                        "tolerance": float(fields["tolerance"].get())
                    }
            self.save_settings()
            if self.control_mode.get() == "auto":
                self.load_data_to_arduino()
            self.threshold_status_var.set(f"Пороговые значения сохранены ({datetime.now().strftime('%H:%M:%S')})")
        except ValueError as e:
            self.threshold_status_var.set(f"Ошибка: введите корректные числовые значения")
        except Exception as e:
            self.threshold_status_var.set(f"Ошибка сохранения: {str(e)}")
    def save_manual_schedule(self):
        if not hasattr(self, 'lamp_hour_vars') or not hasattr(self, 'curtains_hour_vars'):
            return
        try:
            lamp_active_hours = []
            for hour, var in self.lamp_hour_vars.items():
                if var.get():
                    lamp_active_hours.append(hour)
            curtains_active_hours = []
            for hour, var in self.curtains_hour_vars.items():
                if var.get():
                    curtains_active_hours.append(hour)
            self.manual_schedule = {
                "lamp": {"active_hours": lamp_active_hours},
                "curtains": {"active_hours": curtains_active_hours}
            }
            self.save_settings()
            if self.control_mode.get() == "auto":
                self.load_data_to_arduino()
            self.threshold_status_var.set(f"Расписание сохранено ({datetime.now().strftime('%H:%M:%S')})")
        except Exception as e:
            self.threshold_status_var.set(f"Ошибка сохранения расписания: {str(e)}")
    def update_thresholds_and_schedule(self):
        self.threshold_status_var.set("Загрузка данных с сервера...")
        threading.Thread(target=self._fetch_thresholds_and_schedule, daemon=True).start()
    def _fetch_thresholds_and_schedule(self):
        try:
            thresholds = self.threshold_manager.get_thresholds()
            schedule = self.threshold_manager.get_schedule()
            self.root.after(0, lambda: self._update_thresholds_ui(thresholds))
            self.root.after(0, lambda: self._update_schedule_ui(schedule))
            if self.control_mode.get() == "auto" and self.thresholds_mode.get() == "auto":
                self.load_auto_data_to_arduino()
        except Exception as e:
            error_msg = f"Ошибка при получении данных: {str(e)}"
            print(error_msg)
            self.root.after(0, lambda: self.threshold_status_var.set(error_msg))
    def create_manual_threshold_inputs(self):
        header_frame = ttk.Frame(self.thresholds_container)
        header_frame.pack(fill='x', pady=5)
        headers = ["Параметр", "Мин. значение", "Макс. значение", "Целевое значение", "Допуск"]
        for i, header_text in enumerate(headers):
            header_label = tk.Label(header_frame, text=header_text, font=("Arial", 12, "bold"))
            header_label.grid(row=0, column=i, padx=10, pady=5, sticky='w')
        parameters = [
            {"name": "Температура", "key": "temperature", "unit": "°C"},
            {"name": "Влажность воздуха", "key": "humidity_air", "unit": "%"},
            {"name": "Влажность почвы", "key": "humidity_soil", "unit": "%"},
            {"name": "CO2", "key": "co2", "unit": "ppm"}
        ]
        self.manual_input_fields = {}
        for i, param in enumerate(parameters):
            param_frame = ttk.Frame(self.thresholds_container, style='Card.TFrame')
            param_frame.pack(fill='x', pady=5)
            param_label = tk.Label(param_frame, text=param["name"], font=("Arial", 11, "bold"))
            param_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')
            default_values = {
                "temperature": {"min": 18, "max": 28, "target": 23, "tolerance": 2},
                "humidity_air": {"min": 40, "max": 80, "target": 60, "tolerance": 5},
                "humidity_soil": {"min": 30, "max": 70, "target": 50, "tolerance": 10},
                "co2": {"min": 400, "max": 1200, "target": 800, "tolerance": 100}
            }
            saved_values = self.manual_thresholds.get(param["key"], default_values[param["key"]])
            min_var = tk.StringVar(value=str(saved_values.get("min", default_values[param["key"]]["min"])))
            max_var = tk.StringVar(value=str(saved_values.get("max", default_values[param["key"]]["max"])))
            target_var = tk.StringVar(value=str(saved_values.get("target", default_values[param["key"]]["target"])))
            tolerance_var = tk.StringVar(value=str(saved_values.get("tolerance", default_values[param["key"]]["tolerance"])))
            min_entry = ttk.Entry(param_frame, width=8, textvariable=min_var)
            min_entry.grid(row=0, column=1, padx=10, pady=10)
            max_entry = ttk.Entry(param_frame, width=8, textvariable=max_var)
            max_entry.grid(row=0, column=2, padx=10, pady=10)
            target_entry = ttk.Entry(param_frame, width=8, textvariable=target_var)
            target_entry.grid(row=0, column=3, padx=10, pady=10)
            tolerance_entry = ttk.Entry(param_frame, width=8, textvariable=tolerance_var)
            tolerance_entry.grid(row=0, column=4, padx=10, pady=10)
            unit_label1 = tk.Label(param_frame, text=param["unit"], font=("Arial", 10))
            unit_label1.grid(row=0, column=1, padx=(50, 0), pady=10, sticky='w')
            unit_label2 = tk.Label(param_frame, text=param["unit"], font=("Arial", 10))
            unit_label2.grid(row=0, column=2, padx=(50, 0), pady=10, sticky='w')
            unit_label3 = tk.Label(param_frame, text=param["unit"], font=("Arial", 10))
            unit_label3.grid(row=0, column=3, padx=(50, 0), pady=10, sticky='w')
            unit_label4 = tk.Label(param_frame, text=param["unit"], font=("Arial", 10))
            unit_label4.grid(row=0, column=4, padx=(50, 0), pady=10, sticky='w')
            self.manual_input_fields[param["key"]] = {
                "min": min_var,
                "max": max_var,
                "target": target_var,
                "tolerance": tolerance_var
            }
            min_var.trace_add("write", lambda *args, key=param["key"]: self.save_manual_thresholds(key))
            max_var.trace_add("write", lambda *args, key=param["key"]: self.save_manual_thresholds(key))
            target_var.trace_add("write", lambda *args, key=param["key"]: self.save_manual_thresholds(key))
            tolerance_var.trace_add("write", lambda *args, key=param["key"]: self.save_manual_thresholds(key))
        save_frame = ttk.Frame(self.thresholds_container)
        save_frame.pack(fill='x', pady=10)
        save_button = ttk.Button(save_frame, text="Сохранить пороговые значения", 
                               command=self.save_all_manual_thresholds)
        save_button.pack(side='right', padx=10)
        self.threshold_status_var.set("Ручной режим: введите пороговые значения")
    def create_manual_schedule_inputs(self):
        schedule_header = tk.Label(self.schedule_container, text="Расписание работы устройств", 
                                 font=("Arial", 12, "bold"))
        schedule_header.pack(fill='x', pady=5)
        default_schedule = {
            "lamp": {"active_hours": [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]},
            "curtains": {"active_hours": [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}
        }
        saved_schedule = self.manual_schedule or default_schedule
        devices_frame = ttk.Frame(self.schedule_container)
        devices_frame.pack(fill='x', pady=10)
        lamp_frame = ttk.LabelFrame(devices_frame, text="Лампа освещения")
        lamp_frame.pack(fill='x', pady=5)
        lamp_hours_frame = ttk.Frame(lamp_frame)
        lamp_hours_frame.pack(fill='x', padx=10, pady=10)
        self.lamp_hour_vars = {}
        lamp_active_hours = saved_schedule.get("lamp", {}).get("active_hours", default_schedule["lamp"]["active_hours"])
        for hour in range(24):
            hour_var = tk.BooleanVar(value=hour in lamp_active_hours)
            hour_check = ttk.Checkbutton(lamp_hours_frame, text=f"{hour}:00", 
                                       variable=hour_var,
                                       command=lambda h=hour: self.save_manual_schedule())
            hour_check.grid(row=hour // 8, column=hour % 8, padx=5, pady=2, sticky='w')
            self.lamp_hour_vars[hour] = hour_var
        curtains_frame = ttk.LabelFrame(devices_frame, text="Шторы")
        curtains_frame.pack(fill='x', pady=5)
        curtains_hours_frame = ttk.Frame(curtains_frame)
        curtains_hours_frame.pack(fill='x', padx=10, pady=10)
        self.curtains_hour_vars = {}
        curtains_active_hours = saved_schedule.get("curtains", {}).get("active_hours", default_schedule["curtains"]["active_hours"])
        for hour in range(24):
            hour_var = tk.BooleanVar(value=hour in curtains_active_hours)
            hour_check = ttk.Checkbutton(curtains_hours_frame, text=f"{hour}:00", 
                                       variable=hour_var,
                                       command=lambda h=hour: self.save_manual_schedule())
            hour_check.grid(row=hour // 8, column=hour % 8, padx=5, pady=2, sticky='w')
            self.curtains_hour_vars[hour] = hour_var
        save_frame = ttk.Frame(self.schedule_container)
        save_frame.pack(fill='x', pady=10)
        save_button = ttk.Button(save_frame, text="Сохранить расписание", 
                               command=self.save_manual_schedule)
        save_button.pack(side='right', padx=10)
    def save_all_manual_thresholds(self):
        for key, fields in self.manual_input_fields.items():
            self.save_manual_thresholds(key)
if __name__ == "__main__":
    root = tk.Tk()
    app = FitoDomikApp(root)
    root.mainloop() 