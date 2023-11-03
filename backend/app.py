from flask import Flask, request
from src.controllers.diccionario_controller import *
import os
import unicodedata

app = Flask(__name__)

directorio_base = os.path.dirname(os.path.abspath(__file__))



@app.route('/cargar-diccionario', methods=['POST'])
def cargar_diccionario_endpoint():
    return cargar_diccionario(request, directorio_base)

@app.route('/limpiar-archivos', methods=['GET'])
def limpiar_archivos_endpoint():
    return limpiar_datos(directorio_base)

@app.route('/cargar-mensajes', methods=['POST'])
def cargar_mensajes_endpoint():
    return analizar_mensajes(request, directorio_base)

@app.route('/consultar-hashtags', methods=['POST'])
def consultar_hashtags_endpoint():
    return consultar_hashtags(request, directorio_base)

@app.route('/consultar-usuarios', methods=['POST'])
def consultar_usuarios_endpoint():
    return consultar_usuarios(request, directorio_base)

@app.route('/consultar-sentimientos', methods=['POST'])
def consultar_mensajes_endpoint():
    return consultar_sentimientos(request, directorio_base)

@app.route('/graficar-hashtags', methods=['POST'])
def graficar_hashtags_endpoint():
    return graficar_hashtags(request, directorio_base)

@app.route('/graficar-usuarios', methods=['POST'])
def graficar_usuarios_endpoint():
    return graficar_usuarios(request, directorio_base)

@app.route('/graficar-sentimientos', methods=['POST'])
def graficar_sentimientos_endpoint():
    return graficar_sentimientos(request, directorio_base)

@app.route('/informacion-estudiante', methods=['GET'])
def informacion_estudiante_endpoint():
    return informacion_estudiante()

@app.route('/documentacion', methods=['GET'])
def documentacion_endpoint():
    return mostrar_documentacion()

    
@app.route('/obtener-mensajes', methods=['GET'])
def obtener_todos_los_mensajes_endpoint():
    return obtener_mensajes(directorio_base)





if __name__ == '__main__':
    app.run()

