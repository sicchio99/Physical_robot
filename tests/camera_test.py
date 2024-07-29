import cv2
import numpy as np


def is_green_object_present(frame):
    # Convertire il frame in spazio colore HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Definire i limiti inferiori e superiori per il colore verde in HSV
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])

    # Creare una maschera per il colore verde
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Trovare i contorni degli oggetti verdi
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Controllare se esiste almeno un contorno con una certa area minima
    for contour in contours:
        if cv2.contourArea(contour) > 500:  # Filtrare contorni piccoli
            return True

    return False


# Aprire la connessione alla webcam
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Errore nell'apertura della webcam")
    exit()

while True:
    # Leggere un frame dalla webcam
    ret, frame = cap.read()

    if not ret:
        print("Errore nel ricevere frame dalla webcam")
        break

    # Controllare se c'è un oggetto verde
    green_present = is_green_object_present(frame)
    print("Oggetto verde presente:", green_present)

    # Mostrare il frame originale con un messaggio indicativo
    if green_present:
        cv2.putText(frame, "Green Object Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "No Green Object", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # cv2.imshow('Webcam', frame)

    # Uscire dal loop quando si preme il tasto 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Rilasciare la connessione e chiudere le finestre
cap.release()
cv2.destroyAllWindows()
