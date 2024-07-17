from flask import Flask

app = Flask(__name__)


@app.route('/start', methods=['GET'])
def start_script():
    # Esegui qui il tuo script o operazione
    # Ad esempio, eseguire uno script shell
    import subprocess
    try:
        result = subprocess.run(['bash', 'start.sh'], check=True, universal_newlines=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        return f'Script avviato con successo: {result.stdout}', 200
    except subprocess.CalledProcessError as e:
        return f'Errore nell\'esecuzione dello script: {e.stderr}', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008)
