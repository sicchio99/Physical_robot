import requests as r
import json
import time


url = 'http://192.168.0.112:8080/get'
what_to_get = {'magX': '', 'magY': '', 'magZ': '', 'mag': ''}


def phyphox_data():
    response = r.get(url + '&'.join(what_to_get)).text
    #data = response.json()
    print(response)
    data = {}

    # Verifica se 'buffer' è presente e non vuoto
    if 'buffer' in data and data['buffer']:
        for item in what_to_get:
            if item in data['buffer']:
                mag_data = data['buffer'][item]['buffer'][0]
                print(f'{item}: {mag_data:.7f}', end='\t')
            else:
                print(f'{item}: No data', end='\t')
        print()
    else:
        print("No data available")


if __name__ == '__main__':
    while True:
        phyphox_data()
        time.sleep(0.1)