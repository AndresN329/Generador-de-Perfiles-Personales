"""
Servidor mínimo que sirve:
  • GET /            → formulario HTML
  • GET /tarjeta?... → página generada con los datos del usuario
  • Archivos dentro de /static (CSS, imágenes…)
"""

# Importamos los módulos necesarios
from http.server import SimpleHTTPRequestHandler, HTTPServer  # Para crear el servidor web
import urllib.parse as up  # Para analizar las URLs y sus parámetros
import html  # Para escapar caracteres especiales y prevenir inyecciones HTML
from pathlib import Path  # Para manejar rutas de archivos de forma segura
from textwrap import dedent  # Para quitar la indentación de las cadenas multilínea

# Configuración del servidor
PORT = 8000  # Puerto en el que escuchará el servidor
ROOT = Path(__file__).parent.resolve()  # Directorio raíz donde se encuentra este archivo

# --- Plantillas HTML ---------------------------------------------

# Plantilla HTML para el formulario inicial
# dedent() elimina la indentación para que el código sea más legible en el editor
FORM_HTML = dedent("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <title>Genera tu perfil profesional</title>
        <style>
            .formulario{
                   
                text-align: center;
                border-radius: 25px;
                border-style: 1px solid;
                background-color: white;
                padding: 30px;
                max-width: 520px;
                margin: 300px auto;
                background: #17202a;
                color: white;
                   }

            input{
                padding:8px;
                border-radius: 5px;
                margin-bottom: 5px;
                
                   }

            select{
                padding:5px;
                width: 195px;
                border-radius: 5px;
                margin-bottom: 5px;
                   
                   }

            button{
                margin-top: 3px;
                border-radius: 5px;
                padding: 2px;
                width: 120px;
                   
                   }
        </style>
    </head>
    <body>
        <section class="formulario" >
            <h1>Generador de perfiles profesionales</h1>
            <form action="/tarjeta" method="get">
                <input placeholder="Ingrese su nombre" name="nombre" required><br>
                <input placeholder="Ingrese su apellido" name="Apellido" required><br>
                <input placeholder="Ingrese su edad" name="Edad" required><br>
                <select name="habilidades" id="habilidades" >
                <option value="nego">Negociacion</option>
                <option value="comu">Comunicacion</option>
                <option value="escu">Escucha activa</option>
                <option value="pens">Pensamiento critico</option>
                <option value="crea">Creatividad</option>
                <option value="lide">Liderazgo</option>
                <option value="estra">Estrategia</option>
                </select></label><br>
                <input placeholder="Ingrese su ocupacion" name="Ocupacion" required><br>
                <input placeholder="Ingrese su red social" name="LinkedIn, instagram..."  required><br>
                <input placeholder="Ingrese su red social" name="Red Social #2" required><br>   
                <input type = "url" placeholder="Ingrese su link de foto" name="Url foto de perfil" required><br>
                <button>Crear tarjeta</button>
            </form>
        <section>
    </body>
    </html>
""")

# Plantilla HTML para la tarjeta generada
# Las llaves dobles {{}} son para escapar las llaves en un formato de cadena
# Las llaves simples {nombre} serán reemplazadas por los valores reales
CARD_HTML = dedent("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <title>Perfil de {nombre}</title>
        <link rel="stylesheet" href="/static/style.css">
        <style>
            .card {{
                padding: 2rem 3rem;
                border-radius: 1rem;
                box-shadow: 0 10px 25px rgba(0,0,0,.1);
                text-align: center;
                background: white;
                max-width: 320px;
                margin: 4rem auto;
            }}
            h1 {{ edad: {edad}; margin: 0 0 .5rem }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>{nombre} {apellido}</h1>
            <p>{edad} años</p>
            <p>{habilidad}</p>
                   
                   
            <p><a href="/">← Crear otra</a></p>
        </div>
    </body>
    </html>
""")

# --- Manejador HTTP ---------------------------------------------

class TarjetaHandler(SimpleHTTPRequestHandler):
    # Esta clase hereda de SimpleHTTPRequestHandler para manejar las peticiones HTTP
    
    # Sobrescribimos el método translate_path para servir archivos estáticos
    def translate_path(self, path):
        # Si la ruta comienza con /static/, buscamos el archivo en el directorio raíz
        if path.startswith("/static/"):
            return ROOT / path.lstrip("/")  # Unimos ROOT con la ruta sin la barra inicial
        # Para otras rutas, usamos el comportamiento por defecto
        return super().translate_path(path)

    # Manejamos las peticiones GET
    def do_GET(self):
        # Analizamos la URL para obtener la ruta y los parámetros
        parsed = up.urlparse(self.path)
        
        # Si la ruta es "/", mostramos el formulario
        if parsed.path == "/":
            self._send_html(FORM_HTML)
        # Si la ruta es "/tarjeta", generamos una tarjeta con los datos recibidos
        elif parsed.path == "/tarjeta":
            # Obtenemos los parámetros de la URL (query string)
            datos = up.parse_qs(parsed.query)
            
            # Extraemos y sanitizamos los valores para prevenir inyecciones HTML
            # Si no existe el parámetro, usamos un valor por defecto
            # parse_qs devuelve listas, tomamos el primer elemento [0]
            nombre = html.escape(datos.get("nombre", ["Anónim@"])[0])
            apellido = html.escape(datos.get("Apellido",["Anonim@"])[0])
            edad  = html.escape(datos.get("Edad",  ["#000000"])[0])
            habilidad  = html.escape(datos.get("Habilidad",  ["#000000"])[0])
            # Generamos el HTML de la tarjeta con los datos del usuario
            self._send_html(CARD_HTML.format(nombre=nombre, apellido=apellido, edad=edad, habilidad=habilidad))
        else:
            # Para cualquier otra ruta, intentamos servir archivos estáticos o devolvemos 404
            super().do_GET()

    # Método auxiliar para enviar respuestas HTML
    def _send_html(self, contenido, status=200):
        # Enviamos el código de estado (200 = OK por defecto)
        self.send_response(status)
        # Indicamos que el contenido es HTML con codificación UTF-8
        self.send_header("Content-Type", "text/html; charset=utf-8")
        # Finalizamos las cabeceras
        self.end_headers()
        # Enviamos el contenido HTML codificado en bytes (UTF-8)
        self.wfile.write(contenido.encode("utf-8"))


# Punto de entrada del programa
if __name__ == "__main__":
    # Creamos el servidor HTTP en el puerto especificado
    with HTTPServer(("", PORT), TarjetaHandler) as httpd:
        print(f"🚀  Servidor en http://localhost:{PORT}")
        try:
            # Iniciamos el servidor (se queda esperando peticiones indefinidamente)
            httpd.serve_forever()
        except KeyboardInterrupt:
            # Si el usuario presiona Ctrl+C, detenemos el servidor
            print("\n⏹️  Servidor detenido")
