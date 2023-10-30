from flask import Flask, request
from src.controllers.diccionario_controller import *
import os
import unicodedata

app = Flask(__name__)

directorio_base = os.path.dirname(os.path.abspath(__file__))



@app.route('/cargar-diccionario', methods=['POST'])
def cargar_diccionario_endpoint():
    return cargar_diccionario(request, directorio_base)

@app.route('/limpiar-archivos', methods=['POST'])
def limpiar_archivos_endpoint():
    return limpiar_datos(directorio_base)

    





if __name__ == '__main__':
    app.run()

