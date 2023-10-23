from flask import Flask
from src.controllers.diccionario_controller import *
from flask import request
import os

app = Flask(__name__)

directorio_base = os.path.dirname(os.path.abspath(__file__))

@app.route('/', methods=['GET'])
def Home():
    return "¡Hola mundo!"

@app.route('/cargar-diccionario', methods=['POST'])
def cargar_diccionario():
    try:
        if 'archivo_xml' not in request.files:
            print(request.files)
            print("Holaa")
            return "Ningún archivo enviado", 400
            

        archivo_xml = request.files['archivo_xml']

        # Verifica si el archivo tiene una extensión válida
        if archivo_xml and allowed_file(archivo_xml.filename):
            # Parsea el archivo XML del usuario
            mensaje = ""
            tree = ET.parse(archivo_xml)
            mensaje += "Archivo XML parseado exitosamente\n"
            root = tree.getroot()
            mensaje += "Archivo XML obtenido exitosamente\n"

            # Extrae las palabras positivas y negativas del archivo del usuario
            palabras_positivas = [palabra_element.text for palabra_element in root.find("sentimientos_positivos").iter("palabra")]
            mensaje += "Palabras positivas obtenidas exitosamente\n"
            palabras_negativas = [palabra_element.text for palabra_element in root.find("sentimientos_negativos").iter("palabra")]
            mensaje += "Palabras negativas obtenidas exitosamente\n"

            # Abre el archivo XML de palabras positivas y negativas
            archivo_positivas = os.path.join(directorio_base, "src", "data", "palabrasPositivas.xml")
            mensaje += "Archivo XML de palabras positivas obtenido exitosamente\n"
            archivo_negativas = os.path.join(directorio_base, "src", "data", "palabrasNegativas.xml")
            mensaje += "Archivo XML de palabras negativas obtenido exitosamente\n"
            tree_positivas = ET.parse(archivo_positivas)
            mensaje += "Archivo XML de palabras positivas parseado exitosamente\n"
            tree_negativas = ET.parse(archivo_negativas)
            mensaje += "Archivo XML de palabras negativas parseado exitosamente\n"
            root_positivas = tree_positivas.getroot()
            mensaje += "Root de palabras positivas obtenido exitosamente\n"
            root_negativas = tree_negativas.getroot()
            mensaje += "Root de palabras negativas obtenido exitosamente\n"

            # Agrega las palabras del usuario a los archivos existentes
            for palabra in palabras_positivas:
                #Entramos a la etiqueta sentimientos_positivos y agregamos una nueva etiqueta palabra
                nueva_palabra = ET.Element("palabra")
                nueva_palabra.text = palabra
                root_positivas.append(nueva_palabra)
            
            mensaje += "Palabras positivas agregadas exitosamente\n"

            for palabra in palabras_negativas:
                nueva_palabra = ET.Element("palabra")
                nueva_palabra.text = palabra
                root_negativas.append(nueva_palabra)
            
            mensaje += "Palabras negativas agregadas exitosamente\n"

            # Guarda los cambios en los archivos XML existentes
            tree_positivas.write(archivo_positivas)
            mensaje += "Archivo XML de palabras positivas guardado exitosamente\n"
            tree_negativas.write(archivo_negativas)
            mensaje += "Archivo XML de palabras negativas guardado exitosamente\n"

            return "Diccionario cargado exitosamente", 200
        else:
            return "Archivo no válido", 400
    except Exception as e:
        return {"mensaje": mensaje, "error": str(e)}, 500


if __name__ == '__main__':
    app.run()

