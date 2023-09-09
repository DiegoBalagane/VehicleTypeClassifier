import cv2

# Adres IP kamery na telefonie
ip_camera_address = 'ADRES_IP'

# Otwórz strumień wideo
cap = cv2.VideoCapture(ip_camera_address)

while True:
    # Odczytaj klatkę z kamery
    ret, frame = cap.read()

    if not ret:
        print("Nie można odczytać klatki.")
        break

    # Wyświetl klatkę (możesz użyć innej metody do wyświetlenia)
    cv2.imshow('Kamera IP', frame)

    # Przerwanie pętli po naciśnięciu klawisza 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Zwolnij zasoby
cap.release()
cv2.destroyAllWindows()
