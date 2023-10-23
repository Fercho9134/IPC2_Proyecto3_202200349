import xml.etree.ElementTree as ET

def procesar_diccionario_usuario(archivo_usuario):
    tree = ET.parse(archivo_usuario)
    root = tree.getroot()
    diccionario = root.find("diccionario")

    palabras_positivas = [palabra_element.text for palabra_element in diccionario.find("sentimientos_positivos").iter("palabra")]
    palabras_negativas = [palabra_element.text for palabra_element in diccionario.find("sentimientos_negativos").iter("palabra")]

    return palabras_positivas, palabras_negativas

# Función para verificar si la extensión del archivo es válida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'xml'

