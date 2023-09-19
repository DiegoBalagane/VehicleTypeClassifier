import cv2
import time
import sqlite3

# Inicjalizacja detektora samochodów
car_cascade = cv2.CascadeClassifier('haarcascade_car.xml')

# Inicjalizacja listy wykrytych samochodów
detected_cars = []

# Otwórz strumień wideo
ip_camera_address = 'IP_KAMERY'
cap = cv2.VideoCapture(ip_camera_address)
cap.set(3, 640)
cap.set(4, 480)

# Inicjalizacja czasu ostatniego wykrycia samochodu
last_detection_time = time.time()

# Inicjalizacja opóźnienia usunięcia prostokątów
rectangle_remove_delay = 2.0  # 2 sekundy

# Inicjalizacja sumy i liczby klatek od początku
total_cars = 0
total_frames = 0

# Inicjalizacja bazy danych SQLite
conn = sqlite3.connect('vehicle_data.db')
cursor = conn.cursor()

# Tworzenie tabeli do przechowywania średnich wyników
cursor.execute('''
    CREATE TABLE IF NOT EXISTS average_data (
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        time_interval INT,
        average_cars REAL
    )
''')

# Inicjalizacja zmiennej do określenia interwału czasowego
time_interval = 0

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Wykrywanie samochodów za pomocą kaskady Haara
    cars = car_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Aktualizacja listy wykrytych samochodów (eliminacja duplikatów)
    updated_detected_cars = []

    for (x, y, w, h) in cars:
        car_rect = [x, y, x + w, y + h]
        is_duplicate = False

        for existing_car in detected_cars:
            if abs(car_rect[0] - existing_car[0]) < 20 and abs(car_rect[1] - existing_car[1]) < 20:
                is_duplicate = True
                break

        if not is_duplicate:
            updated_detected_cars.append(car_rect)

    detected_cars = updated_detected_cars

    # Rysowanie prostokątów wokół wykrytych samochodów
    for (x1, y1, x2, y2) in detected_cars:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Wyświetlanie liczby wykrytych samochodów
    cv2.putText(frame, f'Liczba samochodow: {len(detected_cars)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                2)

    # Aktualizacja czasu ostatniego wykrycia samochodu
    last_detection_time = time.time()

    # Usunięcie prostokątów po opóźnieniu
    for rect in detected_cars.copy():
        if time.time() - last_detection_time >= rectangle_remove_delay:
            detected_cars.remove(rect)

    # Aktualizacja sumy i liczby klatek od początku
    total_cars += len(detected_cars)
    total_frames += 1

    # Wyświetlanie średniej liczby aut
    if total_frames > 0:
        average_cars = total_cars / total_frames
        cv2.putText(frame, f'Srednia liczba aut: {average_cars:.2f}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 255), 2)

    # Zapisywanie średniej liczby aut do bazy danych w określonych interwałach
    if time_interval % 10 == 0 and time_interval <= 60:
        cursor.execute('INSERT INTO average_data (time_interval, average_cars) VALUES (?, ?)',
                       (time_interval, average_cars))
        conn.commit()

    # Zwiększenie interwału czasowego
    time_interval += 1

    # Zerowanie interwału po 60 sekundach
    if time_interval > 60:
        time_interval = 0

    cv2.imshow('Kamera IP', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
conn.close()
