import http.server
import http.client
import socketserver
import json

# -- IP and the port of the server
IP = "localhost"  # Localhost means "I": your local machine
PORT = 8000
socketserver.TCPServer.allow_reuse_address = True
headers = {'User-Agent': 'http-client'}

# HTTPRequestHandler class
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

        def FDA_req(self, limit=10, solicitud=None, search_url=None):
            conn = http.client.HTTPSConnection("api.fda.gov")

            url = "https://api.fda.gov/drug/label.json?limit={}".format(limit)
            if solicitud:
                url+="&search={}:{}".format(search_url,solicitud)
            print(url)
            conn.request("GET", url, None, headers)
            r1 = conn.getresponse()
            print(r1.status, r1.reason)
            repos_raw = r1.read().decode("utf-8")
            conn.close()

            repos = json.loads(repos_raw)
            return repos

#----------------------------------------------------------------------------

        def OpenFDAHTML(self, lista_info):
            respuesta = ("""
            <!DOCTYPE html>
            <title>OpenFDA-results</title>
            <html lang="es">

            <head>
                <meta charset="UTF-8">
                <title>"FDA"</title>
            </head>
            <body style = "background-color: #AFA9C6">
              <fieldset>
                  <legend><h1>Resultados del buscador FDA:</h1></legend>
            </head>
            <body>
            <ol>
            """)+ lista_info + ("""
            </body>
            </html>""")
            return respuesta
#----------------------------------------------------
        def mensaje_error(self):
            mensaje=("""
            <!DOCTYPE html>
            <title>OpenFDA-results</title>
            <html lang="es">

            <head>
                <meta charset="UTF-8">
                <title>"FDA"</title>
            </head>
            <body style = "background-color: #AFA9C6">
              <fieldset>
                  <legend><h1>ERROR 404:</h1></legend>
            </head>
            <body><li>No se ha encontrado el recurso solicitado.</li>""")
            return  mensaje

#----------------------------------------------------------------

        def busca_info(self, limit=10, solicitud=None, search_url=None):
            info = self.FDA_req(limit,solicitud,search_url)
            medicamento = ""
            try:
                for i in range(len(info['results'])):
                    try:
                        nombre = info['results'][i]['openfda']['substance_name']
                        marca = info['results'][i]['openfda']['brand_name']
                        empresa = info['results'][i]['openfda']['manufacturer_name']
                        id = info['results'][i]['id']

                        medicamento += '<p><li>Nombre: {}.<br>Marca: {}.<br>Empresa: {}.<br>Id: {}: </li></p>\n'.format(nombre, marca, empresa, id)

                    except KeyError:
                        id = info['results'][i]['id']
                        medicamento += '<p><li>Id: {}.<br>No se han encontrado más datos del medicamento solicitado.</li></p>\n'.format(id)
                        continue
                return self.OpenFDAHTML(medicamento)

            except KeyError:
                return self.mensaje_error()
                self.wfile.write(bytes(mensaje, "utf8"))

#--------------------------------------------------------------------

        def busca_empresas(self, limit):
            info = self.FDA_req(limit)
            lista_empresas= ""
            for i in range(len(info['results'])):
                try:
                    empresa = info['results'][i]['openfda']['manufacturer_name'][0]
                    lista_empresas += '<p><li>{}</li></p>\n'.format(empresa)
                except KeyError:
                    lista_empresas += "<p><li>Desconocido</li><p/>"
                    continue

            return self.OpenFDAHTML(lista_empresas)

#----------------------------------------------------------------------------
        def busca_advertencias(self, limit):
            info = self.FDA_req(limit)
            lista_advertencias= ""
            for i in range(len(info['results'])):
                try:
                    advertencia = info['results'][i]['warnings'][0]
                    lista_advertencias += '<p><li>{}</li></p>\n'.format(advertencia)
                except KeyError:
                    lista_advertencias += "<li><p>Desconocido</li><p/>"
                    continue
            return self.OpenFDAHTML(lista_advertencias)
#-----------------------------------------------------------------------------
        def send_info(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            print(self.path)
            return
#----------------------------------------------------------------------------

        def do_GET(self):
            if self.path == "/":
                self.send_info()
                filename = "index.html"
                with open(filename, "r") as f:
                    content = f.read()
                    self.wfile.write(bytes(content, "utf8"))

            elif "/searchDrug" in self.path:
                self.send_info()
                if "&" in self.path:
                    drug_req= self.path.split("&")
                    active_ingredient = drug_req[0].split("=")[1]
                    limit = drug_req[1].split('=')[1]
                else:
                    active_ingredient = self.path.split("=")[1]
                    limit = 10

                search_url= "active_ingredient"
                mensaje = self.busca_info(limit,active_ingredient,search_url)
                self.wfile.write(bytes(mensaje, "utf8"))

            elif "/listDrugs" in self.path:
                self.send_info()
                limit = self.path.split("=")[1]
                mensaje = self.busca_info(limit)
                self.wfile.write(bytes(mensaje, "utf8"))

            elif "/searchCompany" in self.path:
                self.send_info()
                if "&" in self.path:
                    drug_req= self.path.split("&")
                    active_ingredient = drug_req[0].split("=")[1]
                    limit = drug_req[1].split('=')[1]
                else:
                    active_ingredient = self.path.split("=")[1]
                    limit = 10

                search_url = "openfda.manufacturer_name"
                mensaje = self.busca_info(limit,active_ingredient,search_url)
                self.wfile.write(bytes(mensaje, "utf8"))

            elif "/listCompanies" in self.path:
                self.send_info()
                limit = self.path.split("=")[1]
                mensaje = self.busca_empresas(limit)
                self.wfile.write(bytes(mensaje, "utf8"))

            elif "/listWarnings" in self.path:
                self.send_info()
                limit = self.path.split("=")[1]
                mensaje = self.busca_advertencias(limit)
                self.wfile.write(bytes(mensaje, "utf8"))

            elif "/secret" in self.path:
                self.send_error(401)
                self.send_header('keyword','value')

            elif "/redirect" in self.path:
                self.send_response(302)
                self.send_header('Location','http://www.localhost:8000')
                self.end_headers()

            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                mensaje = self.mensaje_error()
                self.wfile.write(bytes(mensaje, "utf8"))
            return
#-------------------------------------------------------

Handler = testHTTPRequestHandler

httpd = socketserver.TCPServer((IP, PORT), Handler)
print("serving at port", PORT)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
        pass

httpd.server_close()
print("")
print("Se ha interrumpido la conexión.")
