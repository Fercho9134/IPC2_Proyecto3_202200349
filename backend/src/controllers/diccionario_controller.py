import xml.etree.ElementTree as ET
import os
import unicodedata



def normalizar_palabra(palabra):
    return ''.join((c for c in unicodedata.normalize('NFD', palabra) if unicodedata.category(c) != 'Mn')).lower()

def cargar_diccionario(request, directorio_base):

    try:
        if 'archivo_xml' not in request.files:
            print(request.files)
            print("Holaa")
            return {"Success": False, "Mensaje": "No se envió ningun archivo en la petición"}, 400
            

        archivo_xml = request.files['archivo_xml']

        # Verifica si el archivo tiene una extensión válida
        if archivo_xml and allowed_file(archivo_xml.filename):
            # Parsea el archivo XML del usuario
            tree = ET.parse(archivo_xml)
            root = tree.getroot()

            # Extrae las palabras positivas y negativas del archivo del usuario
            palabras_positivas = [normalizar_palabra(palabra_element.text) for palabra_element in root.find("sentimientos_positivos").iter("palabra")]

            palabras_negativas = [normalizar_palabra(palabra_element.text) for palabra_element in root.find("sentimientos_negativos").iter("palabra")]


            # Abre el archivo XML de palabras positivas y negativas
            archivo_positivas = os.path.join(directorio_base, "src", "data", "palabrasPositivas.xml")

            archivo_negativas = os.path.join(directorio_base, "src", "data", "palabrasNegativas.xml")

            archivo_resumen = os.path.join(directorio_base, "src", "data", "resumenConfig.xml")

            tree_positivas = ET.parse(archivo_positivas)

            tree_negativas = ET.parse(archivo_negativas)

            root_positivas = tree_positivas.getroot()

            root_negativas = tree_negativas.getroot()

            tree_resumen = ET.parse(archivo_resumen)

            root_resumen = tree_resumen.getroot()

            palabras_positivas_rechazadas = 0

            palabras_negativas_rechazadas = 0

            palabras_positivas_agregadas = 0

            palabras_negativas_agregadas = 0

            #Obtenemos un arreglo con las palabras que ya existen en el diccionario de palabras positivas y otro con las palabras que ya existen en el diccionario de palabras negativas, este se actualizará conforme se vayan agregando las palabras del usuario
            palabras_positivas_existentes = [palabra_element.text for palabra_element in root_positivas.iter("palabra")]
            palabras_negativas_existentes = [palabra_element.text for palabra_element in root_negativas.iter("palabra")]


            #Se deben verificar que las palabras que se van a agregar no existan en el diccionario contrario, es decir, si se va a agregar una palabra positiva, esta no debe existir en el diccionario de palabras negativas y viceversa. Si la palabra existe en el diccionario contrario, se contabilizara como una palabra rechazada y no se agregara al diccionario
            #Por otro lado, tambien se debe verificar que la palabra no exista en su propio diccionario, es decir, si se va a agregar una palabra positiva, esta no debe existir en el diccionario de palabras positivas y viceversa. Si la palabra existe en su propio diccionario, solo se omitira y no se contabilizara como una palabra rechazada

            #Se recorre el arreglo de palabras positivas del usuario
            for palabra in palabras_positivas:
                #Se verifica que la palabra no exista en el diccionario de palabras negativas
                if palabra in palabras_negativas_existentes:
                    palabras_positivas_rechazadas += 1
                #Se verifica que la palabra no exista en el diccionario de palabras positivas
                elif palabra in palabras_positivas_existentes:
                    continue
                #Si la palabra no existe en ninguno de los dos diccionarios, se agrega al diccionario de palabras positivas
                else:
                    nueva_palabra = ET.Element("palabra")
                    nueva_palabra.text = palabra
                    root_positivas.append(nueva_palabra)
                    palabras_positivas_existentes.append(palabra)
                    palabras_positivas_agregadas += 1

            


            #Se recorre el arreglo de palabras negativas del usuario
            for palabra in palabras_negativas:
                #Se verifica que la palabra no exista en el diccionario de palabras positivas
                if palabra in palabras_positivas_existentes:
                    palabras_negativas_rechazadas += 1
                #Se verifica que la palabra no exista en el diccionario de palabras negativas
                elif palabra in palabras_negativas_existentes:
                    continue
                #Si la palabra no existe en ninguno de los dos diccionarios, se agrega al diccionario de palabras negativas
                else:
                    nueva_palabra = ET.Element("palabra")
                    nueva_palabra.text = palabra
                    root_negativas.append(nueva_palabra)
                    palabras_negativas_existentes.append(palabra)
                    palabras_negativas_agregadas += 1
                    


            #Se actualiza el resumen del diccionario, se debe sumar al dato existenta la cantidad de palabras positivas, negativas, positivas rechazadas y negativas rechazadas
            root_resumen.find("PALABRAS_POSITIVAS").text = str(int(root_resumen.find("PALABRAS_POSITIVAS").text) + palabras_positivas_agregadas)
            root_resumen.find("PALABRAS_NEGATIVAS").text = str(int(root_resumen.find("PALABRAS_NEGATIVAS").text) + palabras_negativas_agregadas)
            root_resumen.find("PALABRAS_POSITIVAS_RECHAZADA").text = str(int(root_resumen.find("PALABRAS_POSITIVAS_RECHAZADA").text) + palabras_positivas_rechazadas)
            root_resumen.find("PALABRAS_NEGATIVAS_RECHAZADA").text = str(int(root_resumen.find("PALABRAS_NEGATIVAS_RECHAZADA").text) + palabras_negativas_rechazadas)
            
            #Se guardan los cambios en el archivo XML de resumen
            tree_resumen.write(archivo_resumen)

            # Guarda los cambios en los archivos XML existentes
            tree_positivas.write(archivo_positivas)

            tree_negativas.write(archivo_negativas)


            return {"Success": True, "Mensaje": "Diccionario cargado con éxito"}, 200
        else:
            return {"Success": False, "Mensaje": "Ocurrió un error"}, 400
    except Exception as e:
        return {"Success": False, "Mensaje": str(e)}, 500
    


# Función para verificar si la extensión del archivo es válida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'xml'


def limpiar_datos(directorio_base):
    try:
        # Ruta de los archivos de diccionario
        archivo_positivas = os.path.join(directorio_base, "src", "data", "palabrasPositivas.xml")
        archivo_negativas = os.path.join(directorio_base, "src", "data", "palabrasNegativas.xml")

        # Limpiar el archivo de palabras positivas
        with open(archivo_positivas, 'w', encoding='utf-8') as file:
            file.write('<palabrasPositivas></palabrasPositivas>')

        # Limpiar el archivo de palabras negativas
        with open(archivo_negativas, 'w', encoding='utf-8') as file:
            file.write('<palabrasNegativas></palabrasNegativas>')

        # Reiniciar los datos del archivo resumenConfig.xml
        archivo_resumen = os.path.join(directorio_base, "src", "data", "resumenConfig.xml")
        tree_resumen = ET.parse(archivo_resumen)
        root_resumen = tree_resumen.getroot()

        for elemento in root_resumen:
            elemento.text = '0'

        tree_resumen.write(archivo_resumen)

        return {"Success": True, "Mensaje": "Archivos limpiados"}, 200

    except Exception as e:
        return {"Success": False, "Mensaje": str(e)}, 500