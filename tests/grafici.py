"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Dati di esempio (puoi sostituirli con i tuoi valori)
valori = np.array([12.6,12.6,12.6,12.6,12.6,12.6,12.5,12.6,12.6,12.6,12.7,12.6,12.6,12.6,12.6,12.7])

# Creazione del grafico
plt.figure(figsize=(8, 6))

# Generazione dell'istogramma e della curva di densità
sns.histplot(valori, kde=True, stat="density", bins=10, color='skyblue', edgecolor='black')

# Aggiunta di etichette e titolo
plt.title("Distribuzione dei Valori e Curva di Densità")
plt.xlabel("Valori")
plt.ylabel("Densità")

# Visualizzazione del grafico
plt.show()
"""

import numpy as np
import matplotlib.pyplot as plt

# Valori di input (x) - Puoi modificarli con i tuoi valori
x = np.array([1, 5, 10, 15, 20, 25, 30])

# Valori di output (y) - Puoi modificarli con i tuoi valori o usare una funzione
y = np.array([0.8, 4.8, 12.6, 21.5, 31.2, 40.5, 50.5])

# Creazione del grafico
plt.figure(figsize=(8, 6))

# Tracciamento della curva
plt.plot(x, y, marker='o', color='b', label="Andamento della funzione")

# Aggiunta di etichette e titolo
plt.title("Distanza percorsa")
plt.xlabel("Numero di comandi move")
plt.ylabel("Distanza (cm)")

# Aggiunta di una legenda
plt.legend()

# Visualizzazione del grafico
plt.grid(True)
plt.show()

