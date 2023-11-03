from django.shortcuts import render, redirect
import requests
from django.http import HttpResponse
from datetime import datetime
from django.http import JsonResponse
import json

def index(request):
    backend_url = 'http://127.0.0.1:5000/obtener-mensajes'

    try:
        response = requests.get(backend_url)

        if response.status_code == 200:
            mensajes = response.json()['Mensajes']
        else:
            mensajes = [] 

    except requests.exceptions.RequestException as e:
        print(f"Error de solicitud: {e}")
        mensajes = []  # En caso de error, muestra una lista vacía

    # Obtén el año actual para mostrarlo en el pie de página
    from datetime import datetime
    year = datetime.now().year

    return render(request, 'index.html', {'mensajes': mensajes, 'year': year})

def restaurar_datos(request):
    try:
        response = requests.get('http://127.0.0.1:5000/limpiar-archivos')
        if response.status_code == 200:
            
            return redirect('index')
        else:
            #Mostramos una notificación de error
            return redirect('index')
        
    except requests.exceptions.RequestException as e:
        # Maneja errores de solicitud
        return redirect('index')  # Reemplaza 'pagina_de_error' con el nombre de tu vista de error
    
def cargar_mensajes(request):
    if request.method == 'POST':
        archivo = request.FILES.get('archivo_xml')

        if archivo:
            # URL del servidor backend
            backend_url = 'http://127.0.0.1:5000/cargar-mensajes'

            # Configura el archivo XML como el cuerpo de la solicitud POST
            files = {'archivo_xml': archivo}

            try:
                response = requests.post(backend_url, files=files)

                if response.status_code == 200:
                    #obtenemos el nombre del archivo de resumen de la respuesta
                    nombre_archivo = response.json()['nombre_archivo_xml']
                    mensaje = f'Archivo de mensajes cargado correctamente. El nombre del archivo de resumen es: {nombre_archivo}'

                    return render(request, 'index.html', {'nombre_archivo': mensaje})
                else:
                    nombre_archivo = ''
                    return redirect('index')

            except requests.exceptions.RequestException as e:
                return HttpResponse(f"Error de solicitud: {e}")
        else:
            return HttpResponse("No se seleccionó ningún archivo XML")

    return HttpResponse("Error en la carga del archivo XML")

def cargar_configuracion(request):
    if request.method == 'POST':
        archivo = request.FILES.get('archivo_configuracion')
        print(archivo)

        if archivo:
            # URL del servidor backend
            backend_url = 'http://127.0.0.1:5000/cargar-diccionario'

            # Configura el archivo XML como el cuerpo de la solicitud POST
            files = {'archivo_configuracion': archivo}

            try:
                response = requests.post(backend_url, files=files)

                if response.status_code == 200:
                    #obtenemos el nombre del archivo de resumen de la respuesta
                    nombre_archivo = response.json()['nombre_archivo_xml']
                    mensaje = f"Archivo de diccionario cargado correctamente. El nombre del archivo de resumen es: {nombre_archivo}"
                    return render(request, 'index.html', {'nombre_archivo': mensaje})
                else:
                    nombre_archivo = ''
                    return redirect('index')

            except requests.exceptions.RequestException as e:
                return HttpResponse(f"Error de solicitud: {e}")
        else:
            return HttpResponse("No se seleccionó ningún archivo XML")

    return HttpResponse("Error en la carga del archivo XML")

def consultar_hashtags(request):
    if request.method == 'POST':
        fecha_inicio_original = request.POST.get('fecha_inicio')
        fecha_fin_original = request.POST.get('fecha_fin')

        fecha_inicio = datetime.strptime(fecha_inicio_original, '%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_fin = datetime.strptime(fecha_fin_original, '%Y-%m-%d').strftime('%d/%m/%Y')

        # Enviar una solicitud POST al endpoint para consultar hashtags
        data = {'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin}
        response = requests.post('http://127.0.0.1:5000/consultar-hashtags', data=data)

        # Mandamos de una vez la de graficar
        response_graficar = requests.post('http://127.0.0.1:5000/graficar-hashtags', data=data)

        if response.status_code == 200 and response_graficar.status_code == 200:
            resultados = response.json()['Hashtags']
            resultados_graficar = response_graficar.json()['Hashtags']

            labels = [result['hashtag'] for result in resultados_graficar]
            data = [result['cantidad'] for result in resultados_graficar]

            labels_json = json.dumps(labels)
            data_json = json.dumps(data)

            return render(request, 'consultar_hashtags.html', {
            'resultados': resultados,
            'resultados_graficar': resultados_graficar,
            'fecha_inicio': fecha_inicio_original,
            'fecha_fin': fecha_fin_original,
            'labels_json': labels_json,
            'data_json': data_json,
        })

        else:
            resultados = []
            resultados_graficar = []
            return render(request, 'consultar_hashtags.html', {'fecha_inicio': '2023-01-01', 'fecha_fin': '2023-12-31'})


    return render(request, 'consultar_hashtags.html', {'fecha_inicio': '2023-01-01', 'fecha_fin': '2023-12-31'})

def consultar_menciones(request):
    if request.method == 'POST':
        fecha_inicio_original = request.POST.get('fecha_inicio')
        fecha_fin_original = request.POST.get('fecha_fin')

        fecha_inicio = datetime.strptime(fecha_inicio_original, '%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_fin = datetime.strptime(fecha_fin_original, '%Y-%m-%d').strftime('%d/%m/%Y')

        # Enviar una solicitud POST al endpoint para consultar hashtags
        data = {'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin}
        response = requests.post('http://127.0.0.1:5000/consultar-usuarios', data=data)


        response_graficar = requests.post('http://127.0.0.1:5000/graficar-usuarios', data=data)

        if response.status_code == 200 and response_graficar.status_code == 200:
            resultados = response.json()['Usuarios']
            resultados_graficar = response_graficar.json()['Usuarios']

            labels = [result['usuario'] for result in resultados_graficar]
            data = [result['cantidad'] for result in resultados_graficar]

            labels_json = json.dumps(labels)
            data_json = json.dumps(data)

            return render(request, 'consultar_menciones.html', {
            'resultados': resultados,
            'resultados_graficar': resultados_graficar,
            'fecha_inicio': fecha_inicio_original,
            'fecha_fin': fecha_fin_original,
            'labels_json': labels_json,
            'data_json': data_json,
            })

        else:
            resultados = []
            return render(request, 'consultar_menciones.html', {'fecha_inicio': '2023-01-01', 'fecha_fin': '2023-12-31'})


    return render(request, 'consultar_menciones.html', {'fecha_inicio': '2023-01-01', 'fecha_fin': '2023-12-31'})

def consultar_sentimientos(request):
    if request.method == 'POST':
        fecha_inicio_original = request.POST.get('fecha_inicio')
        fecha_fin_original = request.POST.get('fecha_fin')

        fecha_inicio = datetime.strptime(fecha_inicio_original, '%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_fin = datetime.strptime(fecha_fin_original, '%Y-%m-%d').strftime('%d/%m/%Y')

        # Enviar una solicitud POST al endpoint para consultar hashtags
        data = {'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin}
        response = requests.post('http://127.0.0.1:5000/consultar-sentimientos', data=data)

        response_graficar = requests.post('http://127.0.0.1:5000/graficar-sentimientos', data=data)

        if response.status_code == 200 and response_graficar.status_code == 200:
            resultados = response.json()['Sentimientos']
            resultados_graficar = response_graficar.json()['Sentimientos']

            labels = [result['sentimiento'] for result in resultados_graficar]
            data = [result['cantidad'] for result in resultados_graficar]

            labels_json = json.dumps(labels)
            data_json = json.dumps(data)

            return render(request, 'consultar_mensajes.html', {
            'resultados': resultados,
            'resultados_graficar': resultados_graficar,
            'fecha_inicio': fecha_inicio_original,
            'fecha_fin': fecha_fin_original,
            'labels_json': labels_json,
            'data_json': data_json,
            })
        else:
            resultados = []

            return render(request, 'consultar_mensajes.html', {'fecha_inicio': '2023-01-01', 'fecha_fin': '2023-12-31'})

    return render(request, 'consultar_mensajes.html', {'fecha_inicio': '2023-01-01', 'fecha_fin': '2023-12-31'})

def graficar_hashtags(request):
    if request.method == 'POST':
        fecha_inicio_original = request.POST.get('fecha_inicio')
        fecha_fin_original = request.POST.get('fecha_fin')

        fecha_inicio = datetime.strptime(fecha_inicio_original, '%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_fin = datetime.strptime(fecha_fin_original, '%Y-%m-%d').strftime('%d/%m/%Y')

        data = {'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin}

        # Mandamos de una vez la de graficar
        response_graficar = requests.post('http://127.0.0.1:5000/graficar-hashtags', data=data)

        if response_graficar.status_code == 200:
            resultados_graficar = response_graficar.json()['Hashtags']

            labels = [result['hashtag'] for result in resultados_graficar]
            data = [result['cantidad'] for result in resultados_graficar]

            labels_json = json.dumps(labels)
            data_json = json.dumps(data)

            return render(request, 'grafica_hashtags.html', {
            'resultados_graficar': resultados_graficar,
            'fecha_inicio': fecha_inicio_original,
            'fecha_fin': fecha_fin_original,
            'labels_json': labels_json,
            'data_json': data_json,
        })

        else:
            resultados_graficar = []
            return render(request, 'grafica_hashtags.html', {'fecha_inicio': '2023-01-01', 'fecha_fin': '2023-12-31'})


    return render(request, 'grafica_hashtags.html', {'fecha_inicio': '2023-01-01', 'fecha_fin': '2023-12-31'})

def graficar_menciones(request):
    if request.method == 'POST':
        fecha_inicio_original = request.POST.get('fecha_inicio')
        fecha_fin_original = request.POST.get('fecha_fin')

        fecha_inicio = datetime.strptime(fecha_inicio_original, '%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_fin = datetime.strptime(fecha_fin_original, '%Y-%m-%d').strftime('%d/%m/%Y')

        # Enviar una solicitud POST al endpoint para consultar hashtags
        data = {'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin}

        response_graficar = requests.post('http://127.0.0.1:5000/graficar-usuarios', data=data)

        if response_graficar.status_code == 200:
            resultados_graficar = response_graficar.json()['Usuarios']

            labels = [result['usuario'] for result in resultados_graficar]
            data = [result['cantidad'] for result in resultados_graficar]

            labels_json = json.dumps(labels)
            data_json = json.dumps(data)

            return render(request, 'grafica_menciones.html', {
            'resultados_graficar': resultados_graficar,
            'fecha_inicio': fecha_inicio_original,
            'fecha_fin': fecha_fin_original,
            'labels_json': labels_json,
            'data_json': data_json,
            })

        else:
            resultados = []
            return render(request, 'grafica_menciones.html', {'fecha_inicio': '2023-01-01', 'fecha_fin': '2023-12-31'})


    return render(request, 'grafica_menciones.html', {'fecha_inicio': '2023-01-01', 'fecha_fin': '2023-12-31'})

def graficar_sentimientos(request):
    if request.method == 'POST':
        fecha_inicio_original = request.POST.get('fecha_inicio')
        fecha_fin_original = request.POST.get('fecha_fin')

        fecha_inicio = datetime.strptime(fecha_inicio_original, '%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_fin = datetime.strptime(fecha_fin_original, '%Y-%m-%d').strftime('%d/%m/%Y')

        # Enviar una solicitud POST al endpoint para consultar hashtags
        data = {'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin}

        response_graficar = requests.post('http://127.0.0.1:5000/graficar-sentimientos', data=data)

        if response_graficar.status_code == 200:
            resultados_graficar = response_graficar.json()['Sentimientos']

            labels = [result['sentimiento'] for result in resultados_graficar]
            data = [result['cantidad'] for result in resultados_graficar]

            labels_json = json.dumps(labels)
            data_json = json.dumps(data)

            return render(request, 'grafica_mensajes.html', {
            'resultados_graficar': resultados_graficar,
            'fecha_inicio': fecha_inicio_original,
            'fecha_fin': fecha_fin_original,
            'labels_json': labels_json,
            'data_json': data_json,
            })
        else:
            resultados = []

            return render(request, 'grafica_mensajes.html', {'fecha_inicio': '2023-01-01', 'fecha_fin': '2023-12-31'})

    return render(request, 'grafica_mensajes.html', {'fecha_inicio': '2023-01-01', 'fecha_fin': '2023-12-31'})

def informacion_estudiante(request):
    backend_url = 'http://127.0.0.1:5000/informacion-estudiante'

    try:
        response = requests.get(backend_url)

        if response.status_code == 200:
            informacion = response.json()['Informacion']
        else:
            informacion = [] 

    except requests.exceptions.RequestException as e:
        print(f"Error de solicitud: {e}")
        mensajes = []  # En caso de error, muestra una lista vacía

    # Obtén el año actual para mostrarlo en el pie de página
    year = datetime.now().year

    return render(request, 'informacion.html', {'estudiante_info': informacion, 'year': year})

    