from controller import Robot, Motor, DistanceSensor, PositionSensor, Camera
import time

# Константы
TIME_STEP = 32
WAITING = 0
GRASPING = 1
ROTATING = 2
RELEASING = 3
ROTATING_BACK = 4

state = WAITING
counter = 0
a = 0
b = 0
c = 0

target_positions1 = [-1.88, 2.14, -2.38, -1.51]
target_positions2 = [-1.88, -1.14, -2.38, -1.51]
speed = 1.2
    
# Инициализация робота
robot = Robot()

# Функция для считывания цвета из файла
def read_color_from_file():
    try:
        with open("color.txt", "r", encoding="utf-8") as file:
            color = file.read().strip().lower()
            print(f"Color read from file: {color}")  # Печать для отладки
        return color
    except FileNotFoundError:
        print("File not found!")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

# Считывание цвета, заданного пользователем
required_color = read_color_from_file()

print(required_color)

if required_color not in ['green', 'red', 'blue']:
    print("Invalid color detected, exiting...")
    robot.cleanup()
    exit()

# Получение устройств
hand_motors = [
    robot.getDevice("finger_1_joint_1"),
    robot.getDevice("finger_2_joint_1"),
    robot.getDevice("finger_middle_joint_1")
]

ur_motors = [
    robot.getDevice("shoulder_lift_joint"),
    robot.getDevice("elbow_joint"),
    robot.getDevice("wrist_1_joint"),
    robot.getDevice("wrist_2_joint")
]

# Запуск камеры
camera = robot.getDevice("camera")
camera.enable(4 * TIME_STEP)
camera.recognitionEnable(4 * TIME_STEP)

# Инициализация скорости для руки и захвата
for motor in ur_motors:
    motor.setVelocity(speed)

# Запуск сенсора для определения расстояния
distance_sensor = robot.getDevice("distance sensor")
distance_sensor.enable(TIME_STEP)

# Запуск сенсора для определения позиции
position_sensor = robot.getDevice("wrist_1_joint_sensor")
position_sensor.enable(TIME_STEP)

while robot.step(TIME_STEP) != -1:
    number_of_objects = camera.getRecognitionNumberOfObjects()
    
    if number_of_objects > 0:
        objects = camera.getRecognitionObjects()

        for obj in objects:
            colors = obj.getColors()
            a = colors[0]
            b = colors[1]
            c = colors[2]

            # Определение цвета обнаруженного объекта
            if a == 0 and b == 1 and c == 0:  # Green
                detected_color = 'green'
                break
            elif a == 1.0 and b == 0.0 and c == 0.0:  # Red
                detected_color = 'red'
                break
            elif a == 0.0 and b == 0.0 and c == 1.0:  # Blue
                detected_color = 'blue'
                break
            else:  # Default (Other colors)
                detected_color = 'other'
                break

    # Основной цикл движения робота
    if counter <= 0:
        if state == WAITING:
            if distance_sensor.getValue() < 500:  
                state = GRASPING
                counter = 8
                print("Grasping object")
                for motor in hand_motors:
                    motor.setPosition(0.5)  # Захват

        elif state == GRASPING:
            print("Grasping complete, rotating arm")
            
            if detected_color == required_color:
                for i in range(4):
                    ur_motors[i].setPosition(target_positions2[i])
            else:
                for i in range(4):
                    ur_motors[i].setPosition(target_positions1[i])
            state = ROTATING

        elif state == ROTATING:
            if position_sensor.getValue() < -2.3:  
                counter = 8
                print("Releasing object")
                state = RELEASING
                for motor in hand_motors:
                    motor.setPosition(motor.getMinPosition())  # Разжимание

        elif state == RELEASING:
            for motor in ur_motors:
                motor.setPosition(0.0)  # Возвращение руки в исходное положение
            print("Rotating arm back")
            state = ROTATING_BACK

        elif state == ROTATING_BACK:
            if position_sensor.getValue() > -0.1:  
                state = WAITING
                print("Waiting for object")

    counter -= 1 

robot.cleanup() 
