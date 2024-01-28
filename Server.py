import socket
import threading
import datetime
import json
import time
import urllib.request
import random
import argparse

#//Declaracion de variables importantes//#
SweetHearts = []
usuarios_conectados = {}
usuarios_autorizados = {} #//Esta variable fue cambiada a diccionario para facilitar añadir claves//#
usuarios_muteados = []

print("🦊| BTFmkS")

argParser = argparse.ArgumentParser()
argParser.add_argument("-P", "--port", help="El puerto para iniciar el servidor (Opcional)")
argParser.add_argument("-H", "--host", help="IP del host del servidor (Opcional)")
argParser.add_argument("-A", "--admins", help="Lista de administradores, separada por comas, sin espacios (Opcional)")
args = argParser.parse_args()

#//Proceso de añadir administadores//#
if args.admins is not None:
    administradores = args.admins.split(",")
    for administrador in administradores:
        administrador = administrador.translate(str.maketrans("", "", " :[]")) #//Esta linea puede ser un poco compleja, crea una lista de traducciones, entonces en los primeros dos strings estan los valores que vamos a remplazar y en el tercero estan los valores por los que los va a remplazar//#
        if len(administrador) > 2:
            if not administrador == "":
                code = str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9))
                usuarios_autorizados[administrador] = code
                print(f"[+] {administrador} ahora inicia sesion como {administrador}:{code}")
        else:
            print(f'El usuario del administrador "{administrador}" es muy corto, asi que no fue añadido')

#//Puerto y IP//#
HOST = args.host or "0.0.0.0"
PORT = int(args.port) or 25583

print("Contact for Support at justbrewthefox#0")

#//Obtener direccion ip//#
def obtener_ip_publica():
    try:
        url = 'https://httpbin.org/ip'
        respuesta = urllib.request.urlopen(url) #//Se remplaza requests por urllib para que corra en python nativo//#
        datos = json.load(respuesta)
        return datos['origin']
    except Exception as e:
        print(f"Error al obtener la IP pública: {e}")
        return None


def Heartbeat(): #//Implemento sistema de heartbeat, para verificar la conexion de los clientes y evitar conexiones invalidas//#
    while True:
        usersnapshot = list(usuarios_conectados.keys())
        broadcast("Bark4MeHere") #//Esto se puede cambiar segun las nesecidades, pero tambien tiene que ser cambiado del lado del cliente//#
        time.sleep(10)
        for Heart in SweetHearts:
            if Heart in usersnapshot:
                usersnapshot.remove(Heart) #//Al recibir una palabra clave se añade la persona a la lista SweetHearts //#
        for user in usersnapshot:
            if user in usuarios_conectados: #//Si el usuario que no respondio al beat sigue conectado lo va a expulsar //#
                cliente_kick = usuarios_conectados[user]
                try:
                    cliente_kick.send("[!] Has sido expulsado del chat.".encode('utf-8'))
                    del usuarios_conectados[user]
                except:
                    try:
                        del usuarios_conectados[user]
                    except:
                        pass
                cliente_kick.close()
                time.sleep(0.05)
                broadcast(f"[-] {user} ha salido del chat.")
                print(f"[-] {user} ha salido del chat.")
        SweetHearts.clear() #//Se limpia SweetHearts para volver a ser utilizada //#
        time.sleep(0.5)
        broadcast_users()
        time.sleep(2)

def SlashSay(CurrentUser, Tellto, mensaje): #//Esta funcion se encarga de enviar mensajes privados a personas espeficas//#
    if Tellto in usuarios_conectados:
        if not CurrentUser in usuarios_muteados: #// Se ejecuta solo si el usuario no esta silenciado //#
            usuariodecir = usuarios_conectados[Tellto]
            usuariodecir.send(f"[{CurrentUser} - {Tellto}] ❯ {mensaje}".encode("utf-8"))
            if not CurrentUser == Tellto:
                usuarios_conectados[CurrentUser].send(f"[{CurrentUser} - {Tellto}] ❯ {mensaje}".encode("utf-8"))
        else:
            usuarios_conectados[CurrentUser].send("[!] Estas silenciado, no puedes hacer esto.".encode("utf-8"))
    else:
        usuarios_conectados[CurrentUser].send("[!] El usuario al que le intentaste enviar un el mensaje esta desconectado".encode("utf-8"))


def SlashNick(CurrentUser, NewUser, socket, address): #//Esta funcion se encarga del sistema de nicks //#
    #//Bloque de validaciones //#
    if NewUser in usuarios_conectados:
        return f"[!] {NewUser} Es un usuario activo.".encode("utf-8")
    if NewUser in list(usuarios_autorizados.keys()): 
        return "[-] Escalar privilegios esta mal.".encode("utf-8")
    if CurrentUser in usuarios_muteados:
        return "[!] Te encuentras silenciado, no puedes hacer esto.".encode("utf-8")
    if len(NewUser) <= 2:
        return "[!] El usuario debe tener almenos 3 letras".encode("utf-8")
    if "[" in NewUser or "]" in NewUser or ":" in NewUser or " " in NewUser:
        return "[!] Hay caracteres invalidos en tu usuario".encode("utf-8")
    #/////////////////////////#

    broadcast(f"[!] {CurrentUser} ha cambiado de usuario, ahora se llama {NewUser}") #//Transmite el cambio de nombre //#
    del usuarios_conectados[CurrentUser]
    if CurrentUser in list(usuarios_autorizados.keys()): #//Si el usuario actual esta autorizado se elimina y el usuario nuevo pasa a autorizarse //#
        usuarios_autorizados[NewUser] = usuarios_autorizados[CurrentUser]
        del usuarios_autorizados[CurrentUser]
    time.sleep(0.1)
    client_thread = threading.Thread(target=handle_client, args=(socket, address, NewUser)) #//Se inicia un subhilo nuevo para el nombre nuevo //#
    client_thread.start()
    client_thread.join()
    print(f"[!] El usuario {CurrentUser} se cambio el nombre a {NewUser}")
    return "[OK]".encode('utf-8')

def SlashOP(operador, nuevoOperador): #//Esta funcion se encarga de añadir operadores //#
    if operador in list(usuarios_autorizados.keys()) and nuevoOperador in usuarios_conectados and not nuevoOperador in list(usuarios_autorizados.keys()):
        code = str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9)) #// Genera un codigo de 4 digitos como contraseña para el usuario //#
        usuarios_autorizados[nuevoOperador] = code #//Crea el administrador en el diccionario //#
        usuarios_conectados[nuevoOperador].send(f"[!] Te han dado permisos de operador, para tu proximo inicio de sesion nesecitaras el codigo {code} y tu usuario nuevo sera {nuevoOperador}:{code}".encode("utf-8")) 
        broadcast(f"[!] {operador} le dio permisos de operador a {nuevoOperador}.")
        return "".encode("utf-8")
    else:
        return "[!] No tienes permisos para brindar operador o el usuario es invalido".encode("utf-8")


def SlashDEOP(operador, Eliminado): #//Esta funcion se encarga de eliminar operadores //#
    if operador in list(usuarios_autorizados.keys()) and Eliminado in usuarios_conectados and Eliminado in list(usuarios_autorizados.keys()):
        del usuarios_autorizados[Eliminado] #//Elimina al operador antiguo de la lista //#
        broadcast(f"[!] {operador} le quito permisos de operador a {Eliminado}.")
        return "".encode("utf-8")
    else:
        return "[!] No tienes permisos para elimiar un operador o el usuario es invalido".encode("utf-8")


def kick_usuario(usuario_kick, usuario_que_kickea): #//Esta funcion se encarga de expulsar usuarios, simplemente borra el usuario y se cierra la conexion //#
    if usuario_kick in usuarios_conectados:
        cliente_kick = usuarios_conectados[usuario_kick]
        del usuarios_conectados[usuario_kick]
        cliente_kick.send("[!] Has sido expulsado del chat.".encode('utf-8'))
        cliente_kick.close()
        broadcast(f"[-] {usuario_kick} ha sido expulsado del chat por {usuario_que_kickea}.")
        broadcast_users()
    else:
        broadcast(f"[-] {usuario_que_kickea} intentó expulsar a {usuario_kick}, pero el usuario no existe o no tiene permiso.")

def handle_client(client_socket, addr, rename=None): #//Esta funcion se encarga de manejar los clientes //#
    if rename == None: #// Si no se esta intentando cambiar el nombre procede a simplemente añadir al cliente //#
        username = client_socket.recv(1024).decode('utf-8')
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[+] {addr[0]}:{addr[1]} ({username}) se ha conectado. | Hora: {current_time}")
        if not username in usuarios_conectados and not " " in username and not len(username) <= 2 and not "[" in username and not "]" in username: #//Validacion de caracteres antes de añadir el usuario //#
            if not username.split(":")[0] in list(usuarios_autorizados.keys()): #// Se verifica que no se este intentando suplantar una identidad //#
                if not ":" in username:
                    usuarios_conectados[username] = client_socket
                    IsClientEnabled = True
                    broadcast_users()
                else:
                    time.sleep(0.1)
                    client_socket.send('Error, Solo los administradores pueden usar ":" en sus nombres'.encode("utf-8"))
                    IsClientEnabled = False
                    client_socket.close()
            else: #// Si el usuario es un administrador //#
                if not username.endswith(str(":"+usuarios_autorizados[username.split(":")[0]])): #//Si la clave no es correcta va a tirar un error (Si, puedes odiarme por la forma en la que hice esto)//# 
                    time.sleep(0.1)
                    client_socket.send('Error, esta cuenta requiere autenticacion'.encode("utf-8"))
                    IsClientEnabled = False
                    client_socket.close()
                else:
                    username = username.split(":")[0]
                    usuarios_conectados[username] = client_socket
                    IsClientEnabled = True
                    broadcast_users()
        else: #// Tira error si el usuario no pasa las validaciones //#
            time.sleep(0.1)
            client_socket.send('Error, este usuario es invalido'.encode("utf-8"))
            print(f"{addr} Intento una conexion invalida")
            client_socket.close()
            IsClientEnabled = False
            return("Conexion invalida")
    else: #// Si el usuario se esta renombrando //#
        usuarios_conectados[rename] = client_socket
        IsClientEnabled = True
        broadcast_users()

    
    while IsClientEnabled: #// Mientras el cliente este activo //#
        try: #// Este es otro metodo de desconexion, en caso de que de error por falta de conexion el usuario se expulsara automaticamente //#
            try: 
                if not username in usuarios_conectados: #// Si el usuario se elimina va a apagar el hilo //#
                    IsClientEnabled = False
                    break
            except:
                IsClientEnabled = False #// Y si no se puede verificar tambien, util para manejar las desconexiones //#
                break
            
            mensaje = client_socket.recv(1024).decode('utf-8') #// Se reciben mensajes //#
            if not mensaje:
                break

            #// Esta es la logica de los comandos, esta compuesta principalmente de Elif's, porque en caso de que no se cumpla que el mensaje sea el comando /kick se pueda verificar que sean otros comandos y si no son se considere un mensaje y se pueda enviar atraves del socket //#
            if mensaje.startswith('/kick '):
                comando, usuario_kick = mensaje.split(' ', 1)
                if username in list(usuarios_autorizados.keys()):
                    kick_usuario(usuario_kick, username)
                else:
                    client_socket.send("[-] No tienes permiso para expulsar usuarios.".encode('utf-8'))
            elif mensaje.startswith("/nick "): #//Trigger del nick //#
                Nickname = mensaje.split(" ", 1)
                if len(Nickname)-1 == 1:
                    response = SlashNick(username, Nickname[1], client_socket, addr )
                    if "[OK]" in response.decode("utf-8"):
                        username = Nickname[1] #//Si el slash nick dice que todo esta perfecto se cambia el usuario del hilo //#
                    else:
                        client_socket.send(response) #//Si da error se envia el error al socket //#
                else: #//Si la persona no pone un nick //#
                    client_socket.send("[!] El nickeo requiere un parametro.".encode('utf-8'))

            elif mensaje.startswith("/op "):  #//Trigger del op //#
                nuevoop = mensaje.split(" ", 1)
                if len(nuevoop)-1 == 1:
                    client_socket.send(SlashOP(username, nuevoop[1]))
                else:
                    client_socket.send("[!] Nesecitas nombrar a alguien.".encode('utf-8'))
                
            elif mensaje.startswith("/deop "): #//Trigger del deop //#
                opeliminado = mensaje.split(" ", 1)
                if len(opeliminado)-1 == 1:
                    client_socket.send(SlashDEOP(username, opeliminado[1]))
                else:
                    client_socket.send("[!] Nesecitas nombrar a alguien.".encode('utf-8'))
                
            elif mensaje == 'Wooooooooooooof': #//Trigger del heartbeat //#
                if username not in SweetHearts:
                    SweetHearts.append(username)
                
            elif mensaje.startswith("/msg "): #//Trigger del msg //#
                MensajeParaOtraPersona = mensaje.split(" ", 2)
                if len(MensajeParaOtraPersona) == 3:
                    SlashSay(username, MensajeParaOtraPersona[1], MensajeParaOtraPersona[2])
            
            elif mensaje.startswith("/mute "): #//logica del mute //#
                infomute = mensaje.split(" ", 1)
                if len(infomute) == 2:
                    if not infomute[1] in usuarios_conectados: 
                        client_socket.send("[!] El usuario que intentaste mutear no existe en el servidor".encode("utf-8"))
                    else:
                        if not username in list(usuarios_autorizados.keys()): #//Si el usuario no esta autorizado //#
                            client_socket.send("[!] No estas autorizado para silenciar usuarios".encode("utf-8"))
                        else:
                            if not infomute[1] in usuarios_muteados:
                                usuarios_muteados.append(infomute[1])
                                broadcast(f"[!] {infomute[1]} fue silenciado por {username}")
                            else:
                                client_socket.send("[!] El usuario ya esta silenciado")
                else:
                    client_socket.send("[!] Para mutear a alguien se nesecita exactamente 1 parametro".encode("utf-8"))
            
            elif mensaje.startswith("/unmute "): #//logica del unmute //#
                infomute = mensaje.split(" ", 1)
                if len(infomute) == 2:
                    if not infomute[1] in usuarios_conectados:
                        client_socket.send("[!] El usuario que intentaste desmutear no existe en el servidor".encode("utf-8"))
                    else:
                        if not username in list(usuarios_autorizados.keys()): #//Si el usuario no esta autorizado //#
                            client_socket.send("[!] No estas autorizado para desilenciar usuarios".encode("utf-8"))
                        else:
                            if infomute[1] in usuarios_muteados:
                                usuarios_muteados.remove(infomute[1])
                                broadcast(f"[!] {infomute[1]} fue desilenciado por {username}")
                            else:
                                client_socket.send("[!] El usuario no esta silenciado".encode("utf-8"))
                else:
                    client_socket.send("[!] Para desmutear a alguien se nesecita exactamente 1 parametro".encode("utf-8"))

            elif mensaje.startswith("/password "): #//logica del cambio de contraseña //#
                password = mensaje.split(" ")
                if not len(password) > 2: #//Verfica que la contraseña sea solo una palabra //#
                    if not username in usuarios_autorizados:
                        client_socket.send("[!] Solo los administradores pueden usar contraseña".encode("utf-8"))
                    else:
                        del usuarios_autorizados[username] #// Se elimina el usuario autorizado para remplazar la contraseña //#
                        usuarios_autorizados[username] = password[1] #// Se re-autoriza el usuario con la nueva contraseña //#
                        client_socket.send(f"[+] Tu contraseña de administrador fue cambiada, porfavor para iniciar sesion utilize las credenciales {username}:{password[1]}".encode("utf-8"))
                else:
                    client_socket.send("[!] La contraseña debe tener exactamente una palabra".encode("utf-8"))

            else: #//En caso de que no se este enviando un comando //#
                if not username in usuarios_muteados: #//Si el usuario no esta silenciado se envia como mensaje //#
                    mensaje_con_usuario = f"{username} ❯ {mensaje}"
                    broadcast(mensaje_con_usuario)
                    print(f"{username} dijo: {mensaje}")
                else:
                    client_socket.send("[!] No puedes hablar, estas silenciado".encode("utf-8"))

            
        except Exception as e: #// En caso de que ocurra algun problema con un cliente lo va a desconectar //#
            print(e)
            print(f"[-] {addr[0]}:{addr[1]} ({username}) se ha desconectado.")
            if username in usuarios_conectados:
                del usuarios_conectados[username]
                broadcast_users()
                client_socket.close()
                time.sleep(0.1)
                mensaje_desconexion = f"[-] {username} se ha desconectado. Hay {len(usuarios_conectados)} usuarios online."
                broadcast(mensaje_desconexion)

def broadcast(mensaje): #//Esta funcion se encarga de retransmitir los mensajes a todos los usuarios //#
    for cliente_socket in usuarios_conectados.values(): #//Lo que significa que itera por todas las conexiones y envia la informacion //#
        try:
            cliente_socket.send(mensaje.encode('utf-8'))
        except:
            continue

def enviar_mensaje_consola(): #//Logica de la consola //#
    while True:
        mensaje = input("[Consola del Servidor] > ")
        mensaje_servidor = f"[Servidor] ❯ {mensaje}"
        if not mensaje.startswith("/op "): #//Verifica que el comando op no este especificamente en el mensaje //#
            broadcast(mensaje_servidor)
            print(f"[Servidor] dijo: {mensaje}")
        else: #// Y si esta se asigna como un nuevo operador //#
            operador = mensaje.split(" ", 1)
            if not len(operador) == 2:
                print("[!] Asignar un operador requiere 1 parametro")
            else:
                if not operador[1] in usuarios_conectados or operador[1] in list(usuarios_autorizados.keys()):
                    print("[!] El usuario no esta conectado o ya esta autorizado")
                else:
                    code = str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9))
                    usuarios_autorizados[operador[1]] = code
                    usuarios_conectados[operador[1]].send(f"[!] Te han dado permisos de operador, para tu proximo inicio de sesion nesecitaras el codigo {code} y tu usuario nuevo sera {operador[1]}:{code}".encode("utf-8"))
                    print(f"[!] {operador[1]} ahora es un operador")
                    broadcast(f"[!] {operador[1]} ahora es un operador")


def broadcast_users(): #// Esta funcion se encarga de transmitir los usuarios //#
    usuarios = list(usuarios_conectados.keys()) #//Guarda los nombres de los valores del diccionario //#
    usuarios_data = json.dumps(usuarios) #// Los convierte a JSON //#
    usuarios_broadcast = f'USUARIOS:{usuarios_data}' #// Los envia con la keyword USUARIOS: //#
    broadcast(usuarios_broadcast)

def main(): #// Se encarga de manejar el servidor por socket //#
    server.listen(5)
    try: #// Obtiene la ip local si es posible //#
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        print(f"[*] Servidor de chat escuchando en {ip_local}:{PORT}")
        s.close()
    except:
        print("[!] No se pudo obtener la ip local")

    ip_publica = obtener_ip_publica()
    
    if ip_publica:
        print(f"La dirección IP pública del servidor es: {ip_publica}")
    else:
        print("No se pudo obtener la dirección IP pública.")
    
    #// Inicia los hilos necesarios para el correcto funcionamiento de la consola y el sistema de desconexion//#
    heartbeat_thread = threading.Thread(target=Heartbeat) 
    heartbeat_thread.start()
    consola_thread = threading.Thread(target=enviar_mensaje_consola)
    consola_thread.daemon = True
    consola_thread.start()

    while True:
        #//Acepta clientes por siempre, todos en un hilo distinto //#
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()
if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    main()

################################################################################################################################################################################
################################################################################################################################################################################
##                                                                                                                                                                            ##
## Gracias a zerordia#0 por dejarme su codigo de ChatGroup, es un proyecto bastante interesante, intuitivo y facil de modificar para ajustarlo a mis necesidades especificas. ##
## El proyecto original tiene 111 lineas, este casi que triplica eso, pero tecnicamente es un 150% - 160% mas grande que el original de zerordia, este proyecto me ayudo a    ##
## Aprender bastante de conexiones por socket, hilos y aprendi el metodo translate de un string y maketrans de str. Muchas Gracias por brindarme acceso a este proyecto.      ##
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
#                 \$$$$$$$  \$$        \$$$$$$$  \$$$$$\$$$$  (justbrewthefox#0)
