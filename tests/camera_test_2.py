import numpy as np
import imageio
from PIL import Image, ImageDraw, ImageFont
import time


def is_green_object_present(frame):
    # Convertire l'immagine in spazio colore HSV
    hsv_image = Image.fromarray(frame).convert("HSV")
    hsv_array = np.array(hsv_image)

    # Definire i limiti inferiori e superiori per il colore verde in HSV
    lower_green = np.array([35, 100, 100])
    upper_green = np.array([85, 255, 255])

    # Creare una maschera per il colore verde
    mask = ((hsv_array[:, :, 0] >= lower_green[0]) & (hsv_array[:, :, 0] <= upper_green[0]) &
            (hsv_array[:, :, 1] >= lower_green[1]) & (hsv_array[:, :, 1] <= upper_green[1]) &
            (hsv_array[:, :, 2] >= lower_green[2]) & (hsv_array[:, :, 2] <= upper_green[2]))

    # Verifica se ci sono abbastanza pixel verdi per essere considerato un oggetto
    green_pixel_count = np.sum(mask)
    return green_pixel_count > 500  # Soglia arbitraria per considerare un oggetto


# Aprire la connessione alla webcam
video_reader = imageio.get_reader('<video1>', 'ffmpeg')

while True:
    try:
        # Leggere un frame dalla webcam
        frame = video_reader.get_next_data()

        # Controllare se c'è un oggetto verde
        green_present = is_green_object_present(frame)
        print("Oggetto verde presente:", green_present)

        """
        # Mostrare il frame originale con un messaggio indicativo
        frame_pil = Image.fromarray(frame)
        draw = ImageDraw.Draw(frame_pil)
        font = ImageFont.load_default()
        if green_present:
            draw.text((10, 30), "Green Object Detected", font=font, fill=(0, 255, 0))
        else:
            draw.text((10, 30), "No Green Object", font=font, fill=(255, 0, 0))

        # Visualizzare l'immagine
        frame_pil.show()

        # Aggiungere un ritardo per evitare di sovraccaricare il sistema
        time.sleep(1)
        """
    except Exception as e:
        print("Errore nel ricevere frame dalla webcam:", e)
        break

# Chiudere il video_reader
video_reader.close()
