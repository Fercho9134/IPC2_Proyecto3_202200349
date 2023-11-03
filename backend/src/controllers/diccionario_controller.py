import xml.etree.ElementTree as ET
import os
import unicodedata
from unidecode import unidecode
import re
import shutil
from src.models.Fecha import Fecha
from src.models.hashtag_fecha import hashtag_fecha
import xml.dom.minidom as minidom
from datetime import datetime
from src.models.hashtag_cantidad import hashtag_cantidad
from src.models.usuario_cantidad import usuario_cantidad
from src.models.usuarios_fecha import usuarios_fecha
from src.models.Sentimientos_Fecha import Sentimientos_Fecha
import random

#Funcion para generar una cadena de 6 caracteres aleatorios
def generar_cadena_aleatoria():
    caracteres = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    longitud = 6
    cadena = ''.join(random.choice(caracteres) for i in range(longitud))
    return cadena



def normalizar_palabra(palabra):
    return ''.join((c for c in unicodedata.normalize('NFD', palabra) if unicodedata.category(c) != 'Mn')).lower()

def cargar_diccionario(request, directorio_base):

    try:
        if 'archivo_configuracion' not in request.files:
            print({"Success": False, "Mensaje": "No se envió ningun archivo en la petición"})
            return {"Success": False, "Mensaje": "No se envió ningun archivo en la petición"}, 400
            

        archivo_xml = request.files['archivo_configuracion']

        # Verifica si el archivo tiene una extensión válida
        if archivo_xml and allowed_file(archivo_xml.filename):
            # Parsea el archivo XML del usuario
            tree = ET.parse(archivo_xml)
            root = tree.getroot()

            # Extrae las palabras positivas y negativas del archivo del usuario
            if root.find("sentimientos_positivos") is None:
                palabras_positivas = []
            else:
                palabras_positivas = [normalizar_palabra(palabra_element.text) for palabra_element in root.find("sentimientos_positivos").iter("palabra")]

            if root.find("sentimientos_negativos") is None:
                palabras_negativas = []
            else:
                palabras_negativas = [normalizar_palabra(palabra_element.text) for palabra_element in root.find("sentimientos_negativos").iter("palabra")]


            # Abre el archivo XML de palabras positivas y negativas
            archivo_positivas = os.path.join(directorio_base, "src", "data", "palabrasPositivas.xml")

            archivo_negativas = os.path.join(directorio_base, "src", "data", "palabrasNegativas.xml")

            #Creamos una copia del archivo de resumen config y obtenemos su root
            
            archivo_resumen = os.path.join(directorio_base, "src", "data", "resumenConfig.xml")

            nombre_archivo_xml_copia = f"resumenConfig{generar_cadena_aleatoria()}.xml"

            archivo_resumen_copia = os.path.join(directorio_base, "src", "data", nombre_archivo_xml_copia)

            shutil.copyfile(archivo_resumen, archivo_resumen_copia)

            archivo_positivas_rechazadas = os.path.join(directorio_base, "src", "data", "palabrasPositivasRechazadas.xml")

            archivo_negativas_rechazadas = os.path.join(directorio_base, "src", "data", "palabrasNegativasRechazadas.xml")

            tree_positivas = ET.parse(archivo_positivas)

            tree_negativas = ET.parse(archivo_negativas)

            root_positivas = tree_positivas.getroot()

            root_negativas = tree_negativas.getroot()

            tree_resumen = ET.parse(archivo_resumen_copia)

            root_resumen = tree_resumen.getroot()

            tree_positivas_rechazadas = ET.parse(archivo_positivas_rechazadas)

            tree_negativas_rechazadas = ET.parse(archivo_negativas_rechazadas)

            root_positivas_rechazadas = tree_positivas_rechazadas.getroot()

            root_negativas_rechazadas = tree_negativas_rechazadas.getroot()

            palabras_positivas_rechazadas = 0

            palabras_negativas_rechazadas = 0

            palabras_positivas_agregadas = 0

            palabras_negativas_agregadas = 0

            #Obtenemos un arreglo con las palabras que ya existen en el diccionario de palabras positivas y otro con las palabras que ya existen en el diccionario de palabras negativas, este se actualizará conforme se vayan agregando las palabras del usuario
            if root_positivas is None:
                palabras_positivas_existentes = []
            else:
                palabras_positivas_existentes = [palabra_element.text for palabra_element in root_positivas.iter("palabra")]

            if root_negativas is None:
                palabras_negativas_existentes = []
            else:
                palabras_negativas_existentes = [palabra_element.text for palabra_element in root_negativas.iter("palabra")]

            palabras_positivas_rechazadas_existentes = []
            
            palabras_negativas_rechazadas_existentes = []


            #Se deben verificar que las palabras que se van a agregar no existan en el diccionario contrario, es decir, si se va a agregar una palabra positiva, esta no debe existir en el diccionario de palabras negativas y viceversa. Si la palabra existe en el diccionario contrario, se contabilizara como una palabra rechazada y no se agregara al diccionario
            #Por otro lado, tambien se debe verificar que la palabra no exista en su propio diccionario, es decir, si se va a agregar una palabra positiva, esta no debe existir en el diccionario de palabras positivas y viceversa. Si la palabra existe en su propio diccionario, solo se omitira y no se contabilizara como una palabra rechazada

            #Se recorre el arreglo de palabras positivas del usuario
            for palabra in palabras_positivas:
                #Se verifica que la palabra no exista en el diccionario de palabras negativas
                if palabra in palabras_negativas_existentes:
                    #Verificamos que la palabra no exista en el diccionario de palabras positivas rechazadas si no existe, se agrega al diccionario de palabras positivas rechazadas y se contabiliza como una palabra positiva rechazada y si ya existe solo se omite
                    if palabra not in palabras_positivas_rechazadas_existentes:
                        palabras_positivas_rechazadas_existentes.append(palabra)
                        palabras_positivas_rechazadas += 1
                    else:
                        continue
                    
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
                    #Verificamos que la palabra no exista en el diccionario de palabras negativas rechazadas si no existe, se agrega al diccionario de palabras negativas rechazadas y se contabiliza como una palabra negativa rechazada y si ya existe solo se omite
                    if palabra not in palabras_negativas_rechazadas_existentes:
                        palabras_negativas_rechazadas_existentes.append(palabra)
                        palabras_negativas_rechazadas += 1
                    else:
                        continue
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
            tree_resumen.write(archivo_resumen_copia)

            # Guarda los cambios en los archivos XML existentes
            tree_positivas.write(archivo_positivas)

            tree_negativas.write(archivo_negativas)

            tree_positivas_rechazadas.write(archivo_positivas_rechazadas)

            tree_negativas_rechazadas.write(archivo_negativas_rechazadas)

            #actualizamos mensajes
            actualizar_mensajes(directorio_base)

            #Obtenemos el contenido como cadena del archivo de resumen y lo devolvemos como respuesta
            #El string no debe llevar saltos de linea ni espacios en blanco
            xml_string_resumen_config = minidom.parseString(ET.tostring(root_resumen)).toxml()
            #eliminamos los signos #\n# y #\t# del string
            xml_string_resumen_config = re.sub(r'\n|\t', '', xml_string_resumen_config)

            return {"Success": True, "Mensaje": "Diccionario cargado con éxito", "resumenConfig.xml": xml_string_resumen_config, "nombre_archivo_xml": nombre_archivo_xml_copia}, 200
        else:
            print("Archivo no valido", str(archivo_xml.filename))
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
        archivo_positivas_rechazadas = os.path.join(directorio_base, "src", "data", "palabrasPositivasRechazadas.xml")
        archivo_negativas_rechazadas = os.path.join(directorio_base, "src", "data", "palabrasNegativasRechazadas.xml")
        archivo_mensajes = os.path.join(directorio_base, "src", "data", "mensajes.xml")
        archivo_resumen_mensajes = os.path.join(directorio_base, "src", "data", "resumenMensajes.xml")


        # Limpiar el archivo de palabras positivas
        with open(archivo_positivas, 'w', encoding='utf-8') as file:
            file.write('<palabrasPositivas></palabrasPositivas>')

        # Limpiar el archivo de palabras negativas
        with open(archivo_negativas, 'w', encoding='utf-8') as file:
            file.write('<palabrasNegativas></palabrasNegativas>')
        
        with open(archivo_resumen_mensajes, 'w', encoding='utf-8') as file:
            file.write('<MENSAJES_RECIBIDOS></MENSAJES_RECIBIDOS>')

        # Limpiar el archivo de palabras positivas rechazadas
        with open(archivo_positivas_rechazadas, 'w', encoding='utf-8') as file:
            file.write('<palabrasPositivasRechazadas></palabrasPositivasRechazadas>')

        # Limpiar el archivo de palabras negativas rechazadas
        with open(archivo_negativas_rechazadas, 'w', encoding='utf-8') as file:
            file.write('<palabrasNegativasRechazadas></palabrasNegativasRechazadas>')

        # Limpiar el archivo de mensajes
        with open(archivo_mensajes, 'w', encoding='utf-8') as file:
            file.write('<mensajes></mensajes>')

        # Reiniciar los datos del archivo resumenConfig.xml
        archivo_resumen = os.path.join(directorio_base, "src", "data", "resumenConfig.xml")
        tree_resumen = ET.parse(archivo_resumen)
        root_resumen = tree_resumen.getroot()

        for elemento in root_resumen:
            elemento.text = '0'

        tree_resumen.write(archivo_resumen)
        

        xml_string_resumen_config = minidom.parseString(ET.tostring(root_resumen)).toprettyxml(indent="   ")
        with open(archivo_resumen, "w", encoding='utf-8') as f:
            f.write(xml_string_resumen_config)

        
        tree_mensajes = ET.parse(archivo_mensajes)
        root_mensajes = tree_mensajes.getroot()


        xml_string_mensaje = minidom.parseString(ET.tostring(root_mensajes)).toprettyxml(indent="   ")
        with open(archivo_mensajes, "w", encoding='utf-8') as f:
            f.write(xml_string_mensaje)
        
        tree_resumen_mensajes = ET.parse(archivo_resumen_mensajes)
        root_resumen_mensajes = tree_resumen_mensajes.getroot()

        xml_string_resumen_mensajes = minidom.parseString(ET.tostring(root_resumen_mensajes)).toprettyxml(indent="   ")
        with open(archivo_resumen_mensajes, "w", encoding='utf-8') as f:
            f.write(xml_string_resumen_mensajes)
            

        return {"Success": True, "Mensaje": "Archivos limpiados"}, 200

    except Exception as e:
        return {"Success": False, "Mensaje": str(e)}, 500
    

def analizar_mensajes(request, directorio_base):
    try:
        if 'archivo_xml' not in request.files:
            return {"Success": False, "Mensaje": "No se envió ningun archivo en la petición"}, 404
            

        archivo_xml = request.files['archivo_xml']

        # Verifica si el archivo tiene una extensión válida
        if archivo_xml and allowed_file(archivo_xml.filename):
            # Parsea el archivo XML del usuario
            tree = ET.parse(archivo_xml)
            root = tree.getroot()

            #Cargamos bd de mensajes
            mensajes_tree = ET.parse(os.path.join(directorio_base, "src", "data", "mensajes.xml"))
            mensajes_root = mensajes_tree.getroot()

            #Cargamos y limpiamos el xml temporal con los mensajes que se incluyen solo los mensajes que se acaban de analizar
            mensajes_temporal_archivo = os.path.join(directorio_base, "src", "data", "mensajes-temporal.xml")

            #Lo limpiamos
            with open(mensajes_temporal_archivo, 'w', encoding='utf-8') as file:
                file.write('<mensajes></mensajes>')

            mensajes_temporal_tree = ET.parse(os.path.join(directorio_base, "src", "data", "mensajes-temporal.xml"))
            mensajes_temporal_root = mensajes_temporal_tree.getroot()

            #cargamos en listas las palabras positivas y negativas
            palabras_positivas_tree = ET.parse(os.path.join(directorio_base, "src", "data", "palabrasPositivas.xml"))
            palabras_positivas_root = palabras_positivas_tree.getroot()

            if palabras_positivas_root is None:
                palabras_positivas = []
            else:
                palabras_positivas = [palabra_element.text for palabra_element in palabras_positivas_root.iter("palabra")]

            palabras_negativas_tree = ET.parse(os.path.join(directorio_base, "src", "data", "palabrasNegativas.xml"))
            palabras_negativas_root = palabras_negativas_tree.getroot()

            if palabras_negativas_root is None:
                palabras_negativas = []
            else:
                palabras_negativas = [palabra_element.text for palabra_element in palabras_negativas_root.iter("palabra")]
            
            #Iteramos sobre cada elemento MENSAJE del archivo XML del usuario
            '''
            Ejemplo del archivo de entrada:
            <?xml version="1.0"?>
            <MENSAJES>

            <MENSAJE>
            <FECHA> Guatemala, 15/01/2023 15:25 hrs. </FECHA>
            <TEXTO> Bienvenido a USAC @estudiante01 @estudiante02, es un gusto que seas parte de esta institución #bienvenidaUSAC#</TEXTO>
            </MENSAJE>

            <MENSAJE>
            <FECHA> Guatemala, 15/01/2023 15:25 hrs. </FECHA>
            <TEXTO> Mensaje 2 @juanito</TEXTO>
            </MENSAJE>

            </MENSAJES>
            '''

            #Se recorre el archivo XML del usuario
            for mensaje in root.findall("MENSAJE"):
                texto = mensaje.find("TEXTO").text
                fecha_texto = mensaje.find("FECHA").text
                menciones = []
                hashtags = []
                palabras_del_mensaje = []

                positivas = 0
                negativas = 0



                texto_normalizado = unidecode(texto).lower()

                menciones.extend(re.findall(r'@[\w\d_]+', texto_normalizado))

                #Si se repite un usuario en el mensaje, solo se contabiliza una vez, es decir, si un usuario es mencionado 2 o más veces en un mismo mensaje, solo se contabiliza como 1 usuario mencionado, se eliminan las repeticiones
                menciones = list(dict.fromkeys(menciones))

                hashtags.extend(re.findall(r'(#[^#]+#)', texto_normalizado))

                #Si se repite un hashtag en el mensaje, solo se contabiliza una vez, es decir, si un hashtag es incluido 2 o más veces en un mismo mensaje, solo se contabiliza como 1 hashtag incluido, se eliminan las repeticiones
                hashtags = list(dict.fromkeys(hashtags))

                texto_sin_menciones_ni_hashtags = re.sub(r'@[\w\d_]+|#\w+#', '', texto_normalizado)
                #quitamos comas, puntos, signos de exclamacion, signos de interrogacion, etc
                texto_sin_menciones_ni_hashtags = re.sub(r'[^\w\s]', '', texto_sin_menciones_ni_hashtags)
                #formamos una lista con las palabras que no son menciones ni hashtags
                palabras_del_mensaje.extend(texto_sin_menciones_ni_hashtags.split())

                # Extraer la fecha en el formato dd/mm/yyyy
                fecha_existe = re.search(r'\d{2}/\d{2}/\d{4}', fecha_texto)
                if fecha_existe:
                    fecha = fecha_existe.group()
                else:
                    fecha = ''
                
                # Verificamos el tipo de mensaje
                for palabra in palabras_del_mensaje:
                    if palabra in palabras_positivas:
                        positivas += 1
                    elif palabra in palabras_negativas:
                        negativas += 1
                
                if positivas > negativas:
                    tipo_mensaje = 'POSITIVO'
                elif positivas < negativas:
                    tipo_mensaje = 'NEGATIVO'
                else:
                    tipo_mensaje = 'NEUTRO'

                
                '''
                El archivo de salida debe tener el siguiente formato:
                <mensaje fecha="12/12/2023" sentimiento="neutro">
                    <contenido>Este es el contenido del mensaje @usuario1 @usuario2 #hastag1 #hastag2</contenido>
                    <menciones>
                        <mencion>@usuario1</mencion>
                        <mencion>@usuario2</mencion>
                    </menciones>
                    <hastags> 
                        <hastag>#hastag1</hastag> 
                        <hastag>#hastag2</hastag>
                    </hastags>
                </mensaje>
                '''

                # Se crea el elemento MENSAJE
                mensaje_element = ET.Element("mensaje")
                mensaje_element.set("fecha", fecha)
                mensaje_element.set("sentimiento", tipo_mensaje)

                # Se crea el elemento CONTENIDO
                contenido_element = ET.Element("contenido")
                contenido_element.text = texto_normalizado
                mensaje_element.append(contenido_element)

                # Se crea el elemento menciones
                menciones_element = ET.Element("menciones")
                for mencion in menciones:
                    mencion_element = ET.Element("mencion")
                    mencion_element.text = mencion
                    menciones_element.append(mencion_element)
                mensaje_element.append(menciones_element)

                # Se crea el elemento hashtags
                hashtags_element = ET.Element("hashtags")
                for hashtag in hashtags:
                    hashtag_element = ET.Element("hashtag")
                    hashtag_element.text = hashtag
                    hashtags_element.append(hashtag_element)
                mensaje_element.append(hashtags_element)

                # Se agrega el mensaje al archivo XML de mensajes
                mensajes_root.append(mensaje_element)
                mensajes_temporal_root.append(mensaje_element)


            # Se guarda el archivo XML de mensajes
            mensajes_tree.write(os.path.join(directorio_base, "src", "data", "mensajes.xml"))
            mensajes_temporal_tree.write(os.path.join(directorio_base, "src", "data", "mensajes-temporal.xml"))
                    

            xml_string = minidom.parseString(ET.tostring(mensajes_root)).toprettyxml(indent="   ")
            with open(os.path.join(directorio_base, "src", "data", "mensajes.xml"), "w", encoding='utf-8') as f:
                f.write(xml_string)

            xml_string_temporal = minidom.parseString(ET.tostring(mensajes_temporal_root)).toprettyxml(indent="   ")
            with open(os.path.join(directorio_base, "src", "data", "mensajes-temporal.xml"), "w", encoding='utf-8') as f:
                f.write(xml_string_temporal)


            nombre_resumen = actualizarResumenMensajes(directorio_base)
            tree_resumen_mensajes = ET.parse(os.path.join(directorio_base, "src", "data", nombre_resumen))
            root_resumen_mensajes = tree_resumen_mensajes.getroot()
            
            #obtenemos el contenido como cadena del archivo de resumen y lo devolvemos como respuesta
            #El string no debe llevar saltos de linea ni espacios en blanco

            xml_string_resumen_mensajes = minidom.parseString(ET.tostring(root_resumen_mensajes)).toxml()
            #eliminamos los signos #\n# y #\t# del string
            xml_string_resumen_mensajes = re.sub(r'\n|\t', '', xml_string_resumen_mensajes)



            return {"Success": True, "Mensaje": "Mensajes cargados con éxito", "resumenMensajes.xml": xml_string_resumen_mensajes, "nombre_archivo_xml": nombre_resumen}, 200
        else:
            print("Archivo no valido", str(archivo_xml.filename))
            return {"Success": False, "Mensaje": "Archivo no valido"}, 400
    except Exception as e:
        print(str(e))
        return {"Success": False, "Mensaje": str(e)}, 500

def actualizarResumenMensajes(directorio_base):
    try:

        archivo_resumen = os.path.join(directorio_base, "src", "data", "resumenMensajes.xml")
        with open(archivo_resumen, 'w', encoding='utf-8') as file:
            file.write('<MENSAJES_RECIBIDOS></MENSAJES_RECIBIDOS>')
        
        nombre_archivo_copia = f"resumenMensajes{generar_cadena_aleatoria()}.xml"
        archivo_resumen_copia = os.path.join(directorio_base, "src", "data", nombre_archivo_copia)
        shutil.copyfile(archivo_resumen, archivo_resumen_copia)

        #Se carga el archivo XML de resumenConfig
        tree_resumen = ET.parse(archivo_resumen_copia)
        root_resumen = tree_resumen.getroot()

        #Se carga el archivo XML de mensajes que se acaba de analizar
        archivo_mensajes = os.path.join(directorio_base, "src", "data", "mensajes-temporal.xml")
        tree_mensajes = ET.parse(archivo_mensajes)
        root_mensajes = tree_mensajes.getroot()

        #Usaremos un archivo temporal que es una copia del archivo de mensajes, se irán eliminando los mensajes que ya se hayan contabilizado
        #Primero creamos una copia del archivo de mensajes


        #Vamos a recorrer el archivo XML de mensajes y vamos a contar la cantidad de mensajes positivos, negativos y neutros por cada fecha, el resumen de mensajes será por fecha
        '''
        Ejemplo resumeMensajes.xml
        <?xml version="1.0"?>
        <MENSAJES_RECIBIDOS>


        <TIEMPO>
        <FECHA>15/01/2023</FECHA>
        <MSJ_RECIBIDOS>1</MSJ_RECIBIDOS>
        <USR_MENCIONADOS>2</USR_MENCIONADOS>
        <HASH_INCLUIDOS>1</HASH_INCLUIDOS>
        </TIEMPO>

        </MENSAJES_RECIBIDOS>
        
        '''

        #Se creará un TAG TIEMPO por cada fecha que se encuentre en el archivo XML de mensajes, si ya existe un TAG TIEMPO con esa fecha, solo se actualizará la cantidad de mensajes recibidos, usuarios mencionados y hashtags incluidos
        #Solo se contarán usuarios mencionados y hastags dstintos por fecha, es decir, si un usuario es mencionado 2 o más veces en una misma fecha aunque sean mensajes distintos, solo se contabilizará como 1 usuario mencionado, al igual que los hashtags, si un hashtag es incluido 2 o más veces en una misma fecha aunque sean mensajes distintos, solo se contabilizará como 1 hashtag incluido
                        

        lista_fechas = []

        for mensaje in root_mensajes.iter("mensaje"):

            #paso 1 obtener la fecha del mensaje
            fecha_doc = mensaje.get("fecha")

            fecha_actual = None

            #paso 2 verificar si la fecha ya existe en la lista de fechas, si no existe, se agrega a la lista de fechas, si ya existe s obtiene su lista de usuarios mencionados y hashtags incluidos
            for fecha_iter in lista_fechas:
                if fecha_iter.fecha == fecha_doc:
                    fecha_actual = fecha_iter
                    break

            if fecha_actual is None:
                fecha_actual = Fecha(fecha_doc)
                lista_fechas.append(fecha_actual)

            #Se obtienen los datos del mensaje actual menciones y hashtags
            menciones = mensaje.find("menciones")
            for mencion in menciones.iter("mencion"):
                if mencion.text not in fecha_actual.lista_menciones:
                    fecha_actual.lista_menciones.append(mencion.text)
            
            hashtags = mensaje.find("hashtags")
            for hashtag in hashtags.iter("hashtag"):
                if hashtag.text not in fecha_actual.lista_hashtags:
                    fecha_actual.lista_hashtags.append(hashtag.text)
            

            #paso 4 verificar si ya existe un TAG TIEMPO con esa fecha, si existe, se actualiza la cantidad de mensajes recibidos, usuarios mencionados y hashtags incluidos, si no existe, se crea un nuevo TAG TIEMPO con esa fecha y se actualiza la cantidad de mensajes recibidos, usuarios mencionados y hashtags incluidos
            #Se recorre el archivo XML de resumenMensajes
            fecha_encotrada = False
            
            for tiempo in root_resumen.iter("TIEMPO"):
                if tiempo.find("FECHA").text == fecha_actual.fecha:
                    fecha_encotrada = True
                    tiempo.find("MSJ_RECIBIDOS").text = str(int(tiempo.find("MSJ_RECIBIDOS").text) + 1)
                    tiempo.find("USR_MENCIONADOS").text = str(len(fecha_actual.lista_menciones))
                    tiempo.find("HASH_INCLUIDOS").text = str(len(fecha_actual.lista_hashtags))
                    break

            if fecha_encotrada == False:
                nuevo_tiempo = ET.Element("TIEMPO")
                nueva_fecha = ET.Element("FECHA")
                nueva_fecha.text = fecha_actual.fecha
                nuevo_tiempo.append(nueva_fecha)
                msj_recibidos = ET.Element("MSJ_RECIBIDOS")
                msj_recibidos.text = "1"
                nuevo_tiempo.append(msj_recibidos)
                usr_mencionados = ET.Element("USR_MENCIONADOS")
                usr_mencionados.text = str(len(fecha_actual.lista_menciones))
                nuevo_tiempo.append(usr_mencionados)
                hash_incluidos = ET.Element("HASH_INCLUIDOS")
                hash_incluidos.text = str(len(fecha_actual.lista_hashtags))
                nuevo_tiempo.append(hash_incluidos)
                root_resumen.append(nuevo_tiempo)

            #Guardar los cambios en el archivo XML de resumenMensajes
            tree_resumen.write(archivo_resumen_copia)


        xml_string = minidom.parseString(ET.tostring(root_resumen)).toprettyxml(indent="   ")
        with open(archivo_resumen_copia, "w", encoding='utf-8') as f:
            f.write(xml_string)

        
        return nombre_archivo_copia

    except Exception as e:
        return {"Success": False, "Mensaje": str(e)}, 500
    


#Area de peticiones
#Consultar hasttags
#Esta funcion recibe como parametro una request y un directorio base, la request debe contener la fecha de inicio y la fecha de fin. La funcion retornará un Json con los hashtags que se utilizaron en los mensajes que se recibieron en el rango de fechas especificado. Se organizará por fecha y se mostrará la cantidad de veces que se utilizó cada hashtag en cada fecha
def consultar_hashtags(request, directorio_base):
    try:
        #Se obtienen los parametros de la request
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')

        #Se verifica que los parametros no sean nulos
        if fecha_inicio is None or fecha_fin is None:
            print("No se envió la fecha de inicio o la fecha de fin")
            return {"Success": False, "Mensaje": "No se envió la fecha de inicio o la fecha de fin"}, 400
            

        #Se verifica que las fechas tengan el formato correcto
        print(fecha_inicio)
        print(fecha_fin)
        fecha_inicio_valida = re.search(r'\d{2}/\d{2}/\d{4}', fecha_inicio)
        fecha_fin_valida = re.search(r'\d{2}/\d{2}/\d{4}', fecha_fin)

        if fecha_inicio_valida is None or fecha_fin_valida is None:
            print("El formato de la fecha de inicio o de la fecha de fin es incorrecto")
            return {"Success": False, "Mensaje": "El formato de la fecha de inicio o de la fecha de fin es incorrecto"}, 400

        #Se verifica que la fecha de inicio sea menor a la fecha de fin
        fecha_inicio = datetime.strptime(fecha_inicio, '%d/%m/%Y')
        fecha_fin = datetime.strptime(fecha_fin, '%d/%m/%Y')

        if fecha_inicio > fecha_fin:
            print("La fecha de inicio debe ser menor a la fecha de fin")
            return {"Success": False, "Mensaje": "La fecha de inicio debe ser menor a la fecha de fin"}, 400

        #Se carga el archivo XML de mensajes
        archivo_mensajes = os.path.join(directorio_base, "src", "data", "mensajes.xml")
        tree_mensajes = ET.parse(archivo_mensajes)
        root_mensajes = tree_mensajes.getroot()

        #Esta lista contendrá los objetos hashtag_fecha, cada objeto tendrá una fecha y una lista de hashtags con la cantidad de veces que se utilizó cada hashtag en esa fecha
        lista_fecha_hashtags = []

        for mensaje in root_mensajes.iter("mensaje"):
            fecha_doc = mensaje.get("fecha")

            #Se verifica que la fecha del mensaje este dentro del rango de fechas especificado
            fecha_doc = datetime.strptime(fecha_doc, '%d/%m/%Y')
            if fecha_doc < fecha_inicio or fecha_doc > fecha_fin:
                continue

            fecha_actual = None
            #Verificamos si ya tenemos un objeto con esa fecha, si ya existe, se agrega el hashtag a la lista de hashtags de ese objeto, si no existe, se crea un nuevo objeto hashtag_fecha con esa fecha y se agrega el hashtag a la lista de hashtags de ese objeto
            for fecha_hashtag_iter in lista_fecha_hashtags:
                if fecha_hashtag_iter.fecha == fecha_doc:
                    fecha_actual = fecha_hashtag_iter
                    break
            
            if fecha_actual is None:
                fecha_actual = hashtag_fecha(fecha_doc)
                lista_fecha_hashtags.append(fecha_actual)
                    

            #Analizamos los hastags del mensaje actual
            hashtags = mensaje.find("hashtags")
            for hashtag in hashtags.iter("hashtag"):

                hashtag_actual = None
                #Verificamos si ya existe un objeto hashtag con ese hashtag, si ya existe, se actualiza la cantidad de veces que se utilizó ese hashtag, si no existe, se crea un nuevo objeto hashtag con ese hashtag y se agrega a la lista de hashtags del objeto hashtag_fecha
                for hashtag_iter in fecha_actual.lista_hashtags:
                    if hashtag_iter.hashtag == hashtag.text:
                        hashtag_actual = hashtag_iter
                        break
                
                if hashtag_actual is None:
                    hashtag_actual = hashtag_cantidad(hashtag.text)
                    fecha_actual.lista_hashtags.append(hashtag_actual)
                
                hashtag_actual.cantidad += 1

        #Se crea el json de respuesta
        lista_json = []
        for fecha_hashtag in lista_fecha_hashtags:
            fecha_json = {}
            fecha_json["fecha"] = fecha_hashtag.fecha.strftime("%d/%m/%Y")
            fecha_json["hashtags"] = []
            for hashtag in fecha_hashtag.lista_hashtags:
                hashtag_json = {}
                hashtag_json["hashtag"] = hashtag.hashtag
                hashtag_json["cantidad"] = hashtag.cantidad
                fecha_json["hashtags"].append(hashtag_json)
            lista_json.append(fecha_json)

        return {"Success": True, "Mensaje": "Hashtags consultados con éxito", "Hashtags": lista_json}, 200
                

    except Exception as e:
        return {"Success": False, "Mensaje": str(e)}, 500
    

#Consultar usuarios, la función será similar a la de consultar hashtags, solo que en este caso se mostrarán los usuarios que fueron mencionados en los mensajes que se recibieron en el rango de fechas especificado. Se organizará por fecha y se mostrará la cantidad de veces que se mencionó a cada usuario en cada fecha
def consultar_usuarios(request, directorio_base):
    try:
        #Se obtienen los parametros de la request
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')

        #Se verifica que los parametros no sean nulos
        if fecha_inicio is None or fecha_fin is None:
            return {"Success": False, "Mensaje": "No se envió la fecha de inicio o la fecha de fin"}, 400

        #Se verifica que las fechas tengan el formato correcto
        fecha_inicio_valida = re.search(r'\d{2}/\d{2}/\d{4}', fecha_inicio)
        fecha_fin_valida = re.search(r'\d{2}/\d{2}/\d{4}', fecha_fin)

        if fecha_inicio_valida is None or fecha_fin_valida is None:
            return {"Success": False, "Mensaje": "El formato de la fecha de inicio o de la fecha de fin es incorrecto"}, 400

        #Se verifica que la fecha de inicio sea menor a la fecha de fin
        fecha_inicio = datetime.strptime(fecha_inicio, '%d/%m/%Y')
        fecha_fin = datetime.strptime(fecha_fin, '%d/%m/%Y')

        if fecha_inicio > fecha_fin:
            return {"Success": False, "Mensaje": "La fecha de inicio debe ser menor a la fecha de fin"}, 400

        #Se carga el archivo XML de mensajes
        archivo_mensajes = os.path.join(directorio_base, "src", "data", "mensajes.xml")
        tree_mensajes = ET.parse(archivo_mensajes)
        root_mensajes = tree_mensajes.getroot()

        #Esta lista contendrá los objetos usuario_fecha, cada objeto tendrá una fecha y una lista de usuarios con la cantidad de veces que se mencionó a cada usuario en esa fecha
        lista_fecha_usuarios = []

        for mensaje in root_mensajes.iter("mensaje"):
            fecha_doc = mensaje.get("fecha")

            #Se verifica que la fecha del mensaje este dentro del rango de fechas especificado
            fecha_doc = datetime.strptime(fecha_doc, '%d/%m/%Y')
            if fecha_doc < fecha_inicio or fecha_doc > fecha_fin:
                continue

            fecha_actual = None
            #Verificamos si ya tenemos un objeto con esa fecha, si ya existe, se agrega el usuario a la lista de usuarios de ese objeto, si no existe, se crea un nuevo objeto usuario_fecha con esa fecha y se agrega el usuario a la lista de usuarios de ese objeto
            for fecha_usuario_iter in lista_fecha_usuarios:
                if fecha_usuario_iter.fecha == fecha_doc:
                    fecha_actual = fecha_usuario_iter
                    break

            if fecha_actual is None:
                fecha_actual = usuarios_fecha(fecha_doc)
                lista_fecha_usuarios.append(fecha_actual)


            #Analizamos los usuarios del mensaje actual
            menciones = mensaje.find("menciones")
            for mencion in menciones.iter("mencion"):

                usuario_actual = None
                #Verificamos si ya existe un objeto usuario con ese usuario, si ya existe, se actualiza la cantidad de veces que se mencionó ese usuario, si no existe, se crea un nuevo objeto usuario con ese usuario y se agrega a la lista de usuarios del objeto usuario_fecha
                for usuario_iter in fecha_actual.lista_usuarios:
                    if usuario_iter.usuario == mencion.text:
                        usuario_actual = usuario_iter
                        break

                if usuario_actual is None:
                    usuario_actual = usuario_cantidad(mencion.text)
                    fecha_actual.lista_usuarios.append(usuario_actual)

                usuario_actual.cantidad += 1

        #Se crea el json de respuesta
        lista_json = []
        for fecha_usuario in lista_fecha_usuarios:
            fecha_json = {}
            fecha_json["fecha"] = fecha_usuario.fecha.strftime("%d/%m/%Y")
            fecha_json["usuarios"] = []
            for usuario in fecha_usuario.lista_usuarios:
                usuario_json = {}
                usuario_json["usuario"] = usuario.usuario
                usuario_json["cantidad"] = usuario.cantidad
                fecha_json["usuarios"].append(usuario_json)
            lista_json.append(fecha_json)

        return {"Success": True, "Mensaje": "Usuarios consultados con éxito", "Usuarios": lista_json}, 200
    
    except Exception as e:
        return {"Success": False, "Mensaje": str(e)}, 500
    

#Funcion para contar la cantidad de mensajes positivos, negativos y neutros que se recibieron en el rango de fechas especificado, organizará por fecha y mostrará la cantidad de mensajes positivos, negativos y neutros que se recibieron en cada fecha
def consultar_sentimientos(request, directorio_base):
    try:
        #Se obtienen los parametros de la request
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')

        #Se verifica que los parametros no sean nulos
        if fecha_inicio is None or fecha_fin is None:
            return {"Success": False, "Mensaje": "No se envió la fecha de inicio o la fecha de fin"}, 400

        #Se verifica que las fechas tengan el formato correcto
        fecha_inicio_valida = re.search(r'\d{2}/\d{2}/\d{4}', fecha_inicio)
        fecha_fin_valida = re.search(r'\d{2}/\d{2}/\d{4}', fecha_fin)

        if fecha_inicio_valida is None or fecha_fin_valida is None:
            return {"Success": False, "Mensaje": "El formato de la fecha de inicio o de la fecha de fin es incorrecto"}, 400

        #Se verifica que la fecha de inicio sea menor a la fecha de fin
        fecha_inicio = datetime.strptime(fecha_inicio, '%d/%m/%Y')
        fecha_fin = datetime.strptime(fecha_fin, '%d/%m/%Y')

        if fecha_inicio > fecha_fin:
            return {"Success": False, "Mensaje": "La fecha de inicio debe ser menor a la fecha de fin"}, 400

        #Se carga el archivo XML de mensajes
        archivo_mensajes = os.path.join(directorio_base, "src", "data", "mensajes.xml")
        tree_mensajes = ET.parse(archivo_mensajes)
        root_mensajes = tree_mensajes.getroot()

        #Esta lista contendrá los objetos sentimiento_fecha, cada objeto tendrá una fecha y la cantidad de mensajes positivos, negativos y neutros que se recibieron en esa fecha
        lista_fecha_sentimientos = []

        for mensaje in root_mensajes.iter("mensaje"):
            fecha_doc = mensaje.get("fecha")

            #Se verifica que la fecha del mensaje este dentro del rango de fechas especificado
            fecha_doc = datetime.strptime(fecha_doc, '%d/%m/%Y')
            if fecha_doc < fecha_inicio or fecha_doc > fecha_fin:
                continue

            fecha_actual = None

            #Verificamos si ya tenemos un objeto con esa fecha, si ya existe, se actualiza la cantidad de mensajes positivos, negativos y neutros que se recibieron en esa fecha, si no existe, se crea un nuevo objeto sentimiento_fecha con esa fecha y se actualiza la cantidad de mensajes positivos, negativos y neutros que se recibieron en esa fecha
            for fecha_sentimiento_iter in lista_fecha_sentimientos:
                if fecha_sentimiento_iter.fecha == fecha_doc:
                    fecha_actual = fecha_sentimiento_iter
                    break

            if fecha_actual is None:
                fecha_actual = Sentimientos_Fecha(fecha_doc)
                lista_fecha_sentimientos.append(fecha_actual)

            #Analizamos el sentimiento del mensaje actual
            sentimiento = mensaje.get("sentimiento")
            if sentimiento == "POSITIVO":
                fecha_actual.positivos += 1
            elif sentimiento == "NEGATIVO":
                fecha_actual.negativos += 1
            else:
                fecha_actual.neutros += 1

        #Se crea el json de respuesta
        lista_json = []
        for fecha_sentimiento in lista_fecha_sentimientos:
            fecha_json = {}
            fecha_json["fecha"] = fecha_sentimiento.fecha.strftime("%d/%m/%Y")
            fecha_json["positivos"] = fecha_sentimiento.positivos
            fecha_json["negativos"] = fecha_sentimiento.negativos
            fecha_json["neutros"] = fecha_sentimiento.neutros
            lista_json.append(fecha_json)

        return {"Success": True, "Mensaje": "Sentimientos consultados con éxito", "Sentimientos": lista_json}, 200
    
    except Exception as e:
        return {"Success": False, "Mensaje": str(e)}, 500

    
#Peticion para graficar los hashtags, devolverá un Json con los hashtags que se utilizaron en los mensajes que se recibieron en el rango de fechas especificado. A diferencia de la petición de consultar hashtags, esta petición devolverá un Json con los hashtags que se utilizaron en los mensajes que se recibieron en el rango de fechas especificado, pero en este caso, se organizará por hashtag y se mostrará la cantidad de veces que se utilizó cada hashtag en el rango de fechas especificado.
#Es decir se mostrará la cantidad de veces que se utilizó cada hashtag en el rango de fechas especificado, sin importar la fecha en la que se utilizó cada hashtag mientras este dentro del rango de fechas especificado
def graficar_hashtags(request, directorio_base):
    try:
        #Se obtienen los parametros de la request
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')

        #Se verifica que los parametros no sean nulos
        if fecha_inicio is None or fecha_fin is None:
            return {"Success": False, "Mensaje": "No se envió la fecha de inicio o la fecha de fin"}, 400

        #Se verifica que las fechas tengan el formato correcto
        fecha_inicio_valida = re.search(r'\d{2}/\d{2}/\d{4}', fecha_inicio)
        fecha_fin_valida = re.search(r'\d{2}/\d{2}/\d{4}', fecha_fin)

        if fecha_inicio_valida is None or fecha_fin_valida is None:
            return {"Success": False, "Mensaje": "El formato de la fecha de inicio o de la fecha de fin es incorrecto"}, 400

        #Se verifica que la fecha de inicio sea menor a la fecha de fin
        fecha_inicio = datetime.strptime(fecha_inicio, '%d/%m/%Y')
        fecha_fin = datetime.strptime(fecha_fin, '%d/%m/%Y')

        if fecha_inicio > fecha_fin:
            return {"Success": False, "Mensaje": "La fecha de inicio debe ser menor a la fecha de fin"}, 400

        #Se carga el archivo XML de mensajes
        archivo_mensajes = os.path.join(directorio_base, "src", "data", "mensajes.xml")
        tree_mensajes = ET.parse(archivo_mensajes)
        root_mensajes = tree_mensajes.getroot()

        #Esta lista contendrá los objetos hashtag_cantidad, cada objeto tendrá un hashtag y la cantidad de veces que se utilizó ese hashtag en el rango de fechas especificado
        lista_hashtags = []

        for mensaje in root_mensajes.iter("mensaje"):
            fecha_doc = mensaje.get("fecha")

            #Se verifica que la fecha del mensaje este dentro del rango de fechas especificado
            fecha_doc = datetime.strptime(fecha_doc, '%d/%m/%Y')
            if fecha_doc < fecha_inicio or fecha_doc > fecha_fin:
                continue

            #Analizamos los hastags del mensaje actual
            hashtags = mensaje.find("hashtags")
            for hashtag in hashtags.iter("hashtag"):

                hashtag_actual = None
                #Verificamos si ya existe un objeto hashtag con ese hashtag, si ya existe, se actualiza la cantidad de veces que se utilizó ese hashtag, si no existe, se crea un nuevo objeto hashtag con ese hashtag y se agrega a la lista de hashtags
                for hashtag_iter in lista_hashtags:
                    if hashtag_iter.hashtag == hashtag.text:
                        hashtag_actual = hashtag_iter
                        break

                if hashtag_actual is None:
                    hashtag_actual = hashtag_cantidad(hashtag.text)
                    lista_hashtags.append(hashtag_actual)

                hashtag_actual.cantidad += 1
            
        #Se crea el json de respuesta
        lista_json = []
        for hashtag in lista_hashtags:
            hashtag_json = {}
            hashtag_json["hashtag"] = hashtag.hashtag
            hashtag_json["cantidad"] = hashtag.cantidad
            lista_json.append(hashtag_json)

        return {"Success": True, "Mensaje": "Hashtags consultados con éxito", "Hashtags": lista_json}, 200
    
    except Exception as e:
        return {"Success": False, "Mensaje": str(e)}, 500
    

#Peticion para graficar los usuarios, devolverá un Json con los usuarios que fueron mencionados en los mensajes que se recibieron en el rango de fechas especificado. A diferencia de la petición de consultar usuarios, esta petición devolverá un Json con los usuarios que fueron mencionados en los mensajes que se recibieron en el rango de fechas especificado, pero en este caso, se organizará por usuario y se mostrará la cantidad de veces que se mencionó a cada usuario en el rango de fechas especificado.
#Es decir se mostrará la cantidad de veces que se mencionó a cada usuario en el rango de fechas especificado, sin importar la fecha en la que se mencionó a cada usuario mientras este dentro del rango de fechas especificado
def graficar_usuarios(request, directorio_base):
    try:
        #Se obtienen los parametros de la request
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')

        #Se verifica que los parametros no sean nulos
        if fecha_inicio is None or fecha_fin is None:
            return {"Success": False, "Mensaje": "No se envió la fecha de inicio o la fecha de fin"}, 400

        #Se verifica que las fechas tengan el formato correcto
        fecha_inicio_valida = re.search(r'\d{2}/\d{2}/\d{4}', fecha_inicio)
        fecha_fin_valida = re.search(r'\d{2}/\d{2}/\d{4}', fecha_fin)

        if fecha_inicio_valida is None or fecha_fin_valida is None:
            return {"Success": False, "Mensaje": "El formato de la fecha de inicio o de la fecha de fin es incorrecto"}, 400

        #Se verifica que la fecha de inicio sea menor a la fecha de fin
        fecha_inicio = datetime.strptime(fecha_inicio, '%d/%m/%Y')
        fecha_fin = datetime.strptime(fecha_fin, '%d/%m/%Y')

        if fecha_inicio > fecha_fin:
            return {"Success": False, "Mensaje": "La fecha de inicio debe ser menor a la fecha de fin"}, 400

        #Se carga el archivo XML de mensajes
        archivo_mensajes = os.path.join(directorio_base, "src", "data", "mensajes.xml")
        tree_mensajes = ET.parse(archivo_mensajes)
        root_mensajes = tree_mensajes.getroot()

        #Esta lista contendrá los objetos usuario_cantidad, cada objeto tendrá un usuario y la cantidad de veces que se mencionó ese usuario en el rango de fechas especificado
        lista_usuarios = []

        for mensaje in root_mensajes.iter("mensaje"):
            fecha_doc = mensaje.get("fecha")

            #Se verifica que la fecha del mensaje este dentro del rango de fechas especificado
            fecha_doc = datetime.strptime(fecha_doc, '%d/%m/%Y')
            if fecha_doc < fecha_inicio or fecha_doc > fecha_fin:
                continue

            #Analizamos los usuarios del mensaje actual
            menciones = mensaje.find("menciones")
            for mencion in menciones.iter("mencion"):

                usuario_actual = None
                #Verificamos si ya existe un objeto usuario con ese usuario, si ya existe, se actualiza la cantidad de veces que se mencionó ese usuario, si no existe, se crea un nuevo objeto usuario con ese usuario y se agrega a la lista de usuarios
                for usuario_iter in lista_usuarios:
                    if usuario_iter.usuario == mencion.text:
                        usuario_actual = usuario_iter
                        break

                if usuario_actual is None:
                    usuario_actual = usuario_cantidad(mencion.text)
                    lista_usuarios.append(usuario_actual)

                usuario_actual.cantidad += 1

        #Se crea el json de respuesta
        lista_json = []
        for usuario in lista_usuarios:
            usuario_json = {}
            usuario_json["usuario"] = usuario.usuario
            usuario_json["cantidad"] = usuario.cantidad
            lista_json.append(usuario_json)

        return {"Success": True, "Mensaje": "Usuarios consultados con éxito", "Usuarios": lista_json}, 200
    
    except Exception as e:
        return {"Success": False, "Mensaje": str(e)}, 500
    

#Peticion para graficar los sentimientos, devolverá un Json con la cantidad de mensajes positivos, negativos y neutros que se recibieron en el rango de fechas especificado. A diferencia de la petición de consultar sentimientos, esta petición devolverá un Json con la cantidad de mensajes positivos, negativos y neutros que se recibieron en el rango de fechas especificado, pero en este caso, se organizará por sentimiento y se mostrará la cantidad de mensajes positivos, negativos y neutros que se recibieron en el rango de fechas especificado.
#Es decir se mostrará la cantidad de mensajes positivos, negativos y neutros que se recibieron en el rango de fechas especificado, sin importar la fecha en la que se recibieron los mensajes mientras este dentro del rango de fechas especificado
def graficar_sentimientos(request, directorio_base):
    try:
        #Se obtienen los parametros de la request
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')

        #Se verifica que los parametros no sean nulos
        if fecha_inicio is None or fecha_fin is None:
            return {"Success": False, "Mensaje": "No se envió la fecha de inicio o la fecha de fin"}, 400

        #Se verifica que las fechas tengan el formato correcto
        fecha_inicio_valida = re.search(r'\d{2}/\d{2}/\d{4}', fecha_inicio)
        fecha_fin_valida = re.search(r'\d{2}/\d{2}/\d{4}', fecha_fin)

        if fecha_inicio_valida is None or fecha_fin_valida is None:
            return {"Success": False, "Mensaje": "El formato de la fecha de inicio o de la fecha de fin es incorrecto"}, 400

        #Se verifica que la fecha de inicio sea menor a la fecha de fin
        fecha_inicio = datetime.strptime(fecha_inicio, '%d/%m/%Y')
        fecha_fin = datetime.strptime(fecha_fin, '%d/%m/%Y')

        if fecha_inicio > fecha_fin:
            return {"Success": False, "Mensaje": "La fecha de inicio debe ser menor a la fecha de fin"}, 400

        #Se carga el archivo XML de mensajes
        archivo_mensajes = os.path.join(directorio_base, "src", "data", "mensajes.xml")
        tree_mensajes = ET.parse(archivo_mensajes)
        root_mensajes = tree_mensajes.getroot()

        #Esta lista contendrá los objetos sentimiento_cantidad, cada objeto tendrá un sentimiento y la cantidad de mensajes positivos, negativos y neutros que se recibieron en el rango de fechas especificado
        lista_sentimientos = []
        cantidad_positivos = 0
        cantidad_negativos = 0
        cantidad_neutros = 0

        for mensaje in root_mensajes.iter("mensaje"):
            fecha_doc = mensaje.get("fecha")

            #Se verifica que la fecha del mensaje este dentro del rango de fechas especificado
            fecha_doc = datetime.strptime(fecha_doc, '%d/%m/%Y')
            if fecha_doc < fecha_inicio or fecha_doc > fecha_fin:
                continue

            #Analizamos el sentimiento del mensaje actual
            sentimiento = mensaje.get("sentimiento")

            if sentimiento == "POSITIVO":
                cantidad_positivos += 1
            elif sentimiento == "NEGATIVO":
                cantidad_negativos += 1
            else:
                cantidad_neutros += 1
            
        #Se crea el json de respuesta
        lista_json = []
        sentimiento_json = {}
        sentimiento_json["sentimiento"] = "POSITIVO"
        sentimiento_json["cantidad"] = cantidad_positivos
        lista_json.append(sentimiento_json)
        sentimiento_json = {}
        sentimiento_json["sentimiento"] = "NEGATIVO"
        sentimiento_json["cantidad"] = cantidad_negativos
        lista_json.append(sentimiento_json)
        sentimiento_json = {}
        sentimiento_json["sentimiento"] = "NEUTRO"
        sentimiento_json["cantidad"] = cantidad_neutros
        lista_json.append(sentimiento_json)

        return {"Success": True, "Mensaje": "Sentimientos consultados con éxito", "Sentimientos": lista_json}, 200
    
    except Exception as e:
        return {"Success": False, "Mensaje": str(e)}, 500


#Funcion para devolver informacion del estudiante. Es un get, no recibe nada, solo devuelve un Json con la informacion del estudiante
def informacion_estudiante():
    try:
        return {"Success": True, "Mensaje": "Información del estudiante consultada con éxito", "Informacion": {"Nombre": "Irving Fernando Alvarado Asensio", "Carnet": "202200349", "Curso": "Introducción a la programación y computación 2", "Semestre": 4}}, 200
    except Exception as e:
        return {"Success": False, "Mensaje": str(e)}, 500
    
def mostrar_documentacion():
    try:
        return {"Success": True, "Mensaje": "Documentación consultada con éxito", "Documentacion": "Link"}, 200
    except Exception as e:
        return {"Success": False, "Mensaje": str(e)}, 500
    

#Funcion para devolver todos los mensajes en un archivo json, no recibe nada, solo devuelve un Json con todos los mensajes
def obtener_mensajes(directorio_base):
    try:
        #Se carga el archivo XML de mensajes
        archivo_mensajes = os.path.join(directorio_base, "src", "data", "mensajes.xml")
        tree_mensajes = ET.parse(archivo_mensajes)
        root_mensajes = tree_mensajes.getroot()

        #Se crea el json de respuesta
        lista_json = []
        for mensaje in root_mensajes.iter("mensaje"):
            mensaje_json = {}
            mensaje_json["fecha"] = mensaje.get("fecha")
            mensaje_json["contenido"] = mensaje.find("contenido").text
            mensaje_json["sentimiento"] = mensaje.get("sentimiento")
            mensaje_json["hashtags"] = []
            mensaje_json["menciones"] = []
            hashtags = mensaje.find("hashtags")
            for hashtag in hashtags.iter("hashtag"):
                mensaje_json["hashtags"].append(hashtag.text)
            menciones = mensaje.find("menciones")
            for mencion in menciones.iter("mencion"):
                mensaje_json["menciones"].append(mencion.text)
            lista_json.append(mensaje_json)

        return {"Success": True, "Mensaje": "Mensajes consultados con éxito", "Mensajes": lista_json}, 200
    
    except Exception as e:
        return {"Success": False, "Mensaje": str(e)}, 500
            

#Funcion para volver a analizar todos los mensajes del archivo XML de mensajes, la fecha es la fecha que ya tenemos y el texto del mensaje es "contenido" del mensaje. Se ejecutará cada vez que se cargue u nuevo diccionario de palabras. Entonces el objetivo es actualizar el sentimiento de todos los mensajes del archivo XML de mensajes
#Solo modificaremos el sentimiento, a todos
def actualizar_mensajes(directorio_base):
    try:
         #Cargamos bd de mensajes
        mensajes_tree = ET.parse(os.path.join(directorio_base, "src", "data", "mensajes.xml"))
        mensajes_root = mensajes_tree.getroot()

        #cargamos en listas las palabras positivas y negativas
        palabras_positivas_tree = ET.parse(os.path.join(directorio_base, "src", "data", "palabrasPositivas.xml"))
        palabras_positivas_root = palabras_positivas_tree.getroot()

        if palabras_positivas_root is None:
            palabras_positivas = []
        else:
            palabras_positivas = [palabra_element.text for palabra_element in palabras_positivas_root.iter("palabra")]

        palabras_negativas_tree = ET.parse(os.path.join(directorio_base, "src", "data", "palabrasNegativas.xml"))
        palabras_negativas_root = palabras_negativas_tree.getroot()

        if palabras_negativas_root is None:
            palabras_negativas = []
        else:
            palabras_negativas = [palabra_element.text for palabra_element in palabras_negativas_root.iter("palabra")]

        #Se recorre el archivo XML de mensajes
        for mensaje in mensajes_root.iter("mensaje"):
            positivas = 0
            negativas = 0
            neutras = 0
            palabras_del_mensaje = []
            #Se obtiene el contenido del mensaje
            contenido = mensaje.find("contenido").text

            #Se obtiene el sentimiento del mensaje, usando las expresiones regulares y comparando palabras positivas y negativas:
            #Se obtienen las palabras del mensaje
            texto_sin_menciones_ni_hashtags = re.sub(r'@[\w\d_]+|#\w+#', '', contenido)
                #quitamos comas, puntos, signos de exclamacion, signos de interrogacion, etc
            texto_sin_menciones_ni_hashtags = re.sub(r'[^\w\s]', '', texto_sin_menciones_ni_hashtags)
                #formamos una lista con las palabras que no son menciones ni hashtags
            palabras_del_mensaje.extend(texto_sin_menciones_ni_hashtags.split())

            #Se obtiene el sentimiento del mensaje
            for palabra in palabras_del_mensaje:
                if palabra in palabras_positivas:
                    positivas += 1
                elif palabra in palabras_negativas:
                    negativas += 1
            
            if positivas > negativas:
                mensaje.set("sentimiento", "POSITIVO")
            elif positivas < negativas:
                mensaje.set("sentimiento", "NEGATIVO")
            else:
                mensaje.set("sentimiento", "NEUTRO")

        #Se guardan los cambios en el archivo XML de mensajes
        mensajes_tree.write(os.path.join(directorio_base, "src", "data", "mensajes.xml"))
        

    except Exception as e:
        return {"Success": False, "Mensaje": str(e)}, 500
