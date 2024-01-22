from nicegui import ui, Client, app
import socket
import time
import json
import threading
from typing import Optional
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
import argparse

unrestricted_page_routes = {'/'}
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not app.storage.user.get('Usuario'):
            if request.url.path in Client.page_routes.values() and request.url.path not in unrestricted_page_routes:
                app.storage.user['referrer_path'] = request.url.path  
                return RedirectResponse('/') #// A donde hiba el usuario que estaba en una parte que no debia//#
        return await call_next(request)

app.add_middleware(AuthMiddleware)

argParser = argparse.ArgumentParser()
argParser.add_argument("-P", "--port", help="El puerto del servidor chatgroup (Opcional)")
argParser.add_argument("-H", "--host", help="IP del host de chatgroup (Opcional)")
args = argParser.parse_args()

usuariosgroup = ["Espere..."] #//Se declara una lista global para los usuarios//#
lock = threading.Lock()

@ui.page("/") #// Define que la pagina de inicio de sesion va a quedar en "/" //#
def Login() -> Optional[RedirectResponse]:
    def MakeChecks(usuario): #// Por culpa de zerordia esto esta aqui so hotfix en 5 minutos btw//#
        if len(usuario) < 3:
            ui.notify("El usuario es muy corto")
            return("Muy corto")
        app.storage.user.update({'Usuario':usuario})
        ui.open(app.storage.user.get('referrer_path', '/'))

    #//Tarjetas de inicio de sesion //#
    with ui.card().classes("absolute-center items-center").style('height: auto; font-size: 22px;'): #//El with es para indicar que un elemento esta dentro de otro //#
        ui.label('ChatGroup')
        if app.storage.user.get('Error'):
            time.sleep(0.2)
            with ui.dialog() as dialog:
                with ui.card():
                    ui.label('Ocurrio un problema :(').style("font-size: 25px")
                    ui.label(app.storage.user.get('Error')).style("font-size: 20px; color:#DC143C")
                    ui.button('Cerrar', on_click=lambda:(dialog.close(), app.storage.user.pop('Error'))).style('width:100%')
            dialog.open()
        usuario = ui.input('Como te llamas?',validation={'El nombre es muy corto': lambda value: len(value) > 2})
        ui.button('Iniciar sesion', on_click=lambda:(MakeChecks(usuario.value)))
    
    if app.storage.user.get('Usuario'):
        return RedirectResponse('/Chat/')




@ui.page("/Chat/") #// Define que la pagina del chat va a quedar en "/Chat/" //#
def chat() -> Optional[RedirectResponse]:

#//las variables son arreglos porque es muy dificil la comunicacion entre un hilo y nicegui//#

    listamensajes = []
    def updateLista(List):
        listamensajes.append(List)
    
    listalocal = []
    isactivo = []
    
    def killerthread(): #// Este hilo se encarga de detectar inactividad//#
        index = 0
        while not True in listalocal: #// Mientras no exista verdadero en lista local va a iterar//#
            time.sleep(1)
            index += 1
            if "LogOut" in listalocal:
                listalocal.clear()
                listalocal.append(True)
            if index >= 100: #// Si llega a 100 segundos y el usuario no tiene actividad se va a expulsar del chat, si no el contador se reinica//#
                if True in isactivo:
                    isactivo.clear()
                    index = 0
                else:
                    with lock: #// Si el usuario se expulsa se envia un mensaje y entra True a lista local, lo que significa que el hilo principal debe detenerse //#
                        listamensajes.append(['[!] Se te ha expulsado del servidor por inactividad, para reconectarte reinicia la pagina en unos segundos.', 'Ayuda'])
                        listalocal.append(True)
                    mensajes.refresh() #// Refresca el elemento que se encarga de manejar los mensajes //#
        

    def idk(client):
        threading.Thread(target=killerthread).start()
        while not True in listalocal: #// mientras no esta verdadero en la lista local que se utiliza para la comunicacion entre sockets y nicegui //#
            mensaje = client.recv(1064).decode("utf-8") #// Se reciben mensajes desde el socket del servidor //#
            if mensaje.startswith("USUARIOS:") or mensaje == "Bark4MeHere": 
                if mensaje.startswith("USUARIOS:"): #//Si el mensaje comienza con usuarios se va a guardar en la lista global de usuarios //#
                    with lock:
                        mensaje= mensaje.split(':')[1]
                        usuariosgroup.clear()
                        lista = json.loads(mensaje)
                        for i in range(len(lista)):
                            usuariosgroup.append(lista[i])
                        elementos.refresh()
                if mensaje == "Bark4MeHere": #// Esto responde a los heartbeats, el contenido del beat es Bark4MeHere y se tiene que responder con Wooooooooooooof //#
                    client.send('Wooooooooooooof'.encode("utf-8"))
            else: #// Y si no entra en las dos opciones se guarda como un mensaje en la lista de mensajes//#
                with lock:
                    if "❯" in mensaje: #// Si el mensaje tiene ❯ se asume que es un de un usuario, si no es automatizado del servidor y se refrescan las listas de mensajes//#
                        updateLista([mensaje.split("❯")[1], mensaje.split("❯")[0]])
                        mensajes.refresh()
                    else:
                        updateLista([mensaje, "Ayuda"])
                        mensajes.refresh()
        client.close() #// En el momento en el que se entra true en listalocal se cierra el socket y se lanza un error para finalizar el hilo //#
        raise Exception ('Finalizo Correctamente')
    
    with ui.row().classes('absolute-center items-center').style('width:100%; height:100%'):
    # Primera tarjeta para el área de desplazamiento (pequeña)
        with ui.card().style('width:20%; height:90%; position:absolute; left:3%'):
                with ui.scroll_area().style('height:95%;'):
                    ui.label("Nombre")
                    ui.separator()
                    @ui.refreshable
                    def elementos():
                        div = ui.element('div')
                        with div:
                            for usuario in usuariosgroup: #// Por cada usuario se crea un label dentro del div //#
                                ui.label(usuario)

                    elementos()

                    #// Este bloque se encarga de iniciar la conexion por socket al servidor//#
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client.connect((args.host or '0.0.0.0', args.port or 25583))
                    client.send(app.storage.user.get('Usuario').encode())
                    FirstClientMsg = client.recv(1064).decode("utf-8")
                    if not "Error, " in FirstClientMsg:
                        iniciosocket = threading.Thread(target=idk, args=(client,))
                        iniciosocket.daemon = True
                        iniciosocket.start()
                    else:
                        app.storage.user.clear()
                        app.storage.user['Error'] = FirstClientMsg
                        return RedirectResponse('/')
                    #// ----------------------------------------------------------------------//#

                ui.button("Salir", on_click=lambda:(app.storage.user.clear(),listalocal.append("LogOut"), ui.open('/'))).style('width:100%') #//Al darle click al boton se elimina la informacion del usuario, se da la orden al hilo de cerrar y se abre la pagina raiz(Login) //#

    # Segunda tarjeta para el chat (grande)
        with ui.card().style('width:70%; height:90%; position:absolute; left:25%'):
            @ui.refreshable
            def mensajes():
                with ui.scroll_area().style('width:100%; height:90%;') as area:
                    with ui.element('div'): #// Estas lineas se encargan de manejar los mensajes, cuando llega un mensaje va a bajar lo mas posible y va a iterar sobre los mensajes agregando un elemento de mensaje de chat //#
                        for mensaje in listamensajes: 
                            ui.chat_message(listamensajes[mensaje][0], name=listamensajes[mensaje][1])
                    area.scroll_to(percent=1)
                
            mensajes()
            mensaje = ui.input('Tu mensaje', on_change=lambda:(isactivo.append(True))).style('width:100%') #// Cuando se escribe se resetean los 100 segundos de inactividad //#
            ui.button('Enviar', on_click=lambda:(client.send(mensaje.value.encode("utf-8")), mensaje.set_value(""))).style('width:100%')  #//Al darle click se envia el mensaje a traves del socket  //#


def startweb():
    ui.run(dark=True, storage_secret='TextoSecretoxD', on_air=True, title='Arx ChatGroup')
startweb()


################################################################################################################################################################################
################################################################################################################################################################################
##                                                                                                                                                                            ##
## Gracias a zerordia#0 por dejarme su codigo de ChatGroup, es un proyecto bastante interesante, intuitivo y facil de modificar para ajustarlo a mis necesidades especificas. ##
## El proyecto original tiene 166 lineas, este casi que triplica eso, pero tecnicamente un poco mas pequeño que el original de zerordia, este proyecto me ayudo a             ##
## Aprender bastante de conexiones por socket e hilos. Muchas Gracias por brindarme acceso a este proyecto.                                                                   ##
##                                                                                                                                                                            ##
################################################################################################################################################################################
################################################################################################################################################################################

#                 _______                                    
#                |       \                                   
#                | $$$$$$$\  ______    ______   __   __   __ 
# ______  ______ | $$__/ $$ /      \  /      \ |  \ |  \ |  \
#|      \|      \| $$    $$|  $$$$$$\|  $$$$$$\| $$ | $$ | $$
# \$$$$$$ \$$$$$$| $$$$$$$\| $$   \$$| $$    $$| $$ | $$ | $$
#                | $$__/ $$| $$      | $$$$$$$$| $$_/ $$_/ $$
#                | $$    $$| $$       \$$     \ \$$   $$   $$
#                 \$$$$$$$  \$$        \$$$$$$$  \$$$$$\$$$$  (tpn_q150#0)
