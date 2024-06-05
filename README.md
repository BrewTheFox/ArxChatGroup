# Arx Chatgroup 💬

## ¿Qué es?
- 🔄 Reescritura open source del protocolo [ChatGroup](https://github.com/alejodd/ChatGroup) de [alejodd](https://github.com/alejodd)
- 🐍 Sistema de chat simple escrito en Python
- 🔐 Servicio de chat semiprivado
- 🌐 Chat por socket

## ¿Qué tiene de nuevo? 🆕
<details>
  <summary>Comandos 🤖</summary>

  - <code>/kick (Administrador)</code>: Expulsa a un usuario de la sala. Uso: `/kick "usuario"`
  - <code>/nick (Usuario)</code>: Cambia tu usuario. Uso: `/nick "NuevoUsuario"`
  - <code>/op (Administrador)</code>: Agrega permisos de operador a un usuario. Uso: `/op "Usuario"`
  - <code>/deop (Administrador)</code>: Remueve permisos de operador a un usuario. Uso: `/deop "Usuario"`
  - <code>/msg (Usuario)</code>: Envía un mensaje privado a un usuario en la sala. Uso: `/msg "Usuario" "Mensaje"`
  - <code>/mute (Administrador)</code>: Silencia un usuario de forma global. Uso: `/mute "Usuario"`
  - <code>/unmute (Administrador)</code>: Le quita el silencio a un usuario de forma global. Uso: `/unmute "Usuario"`
  - <code>/password (Administrador)</code>: Cambia la contraseña de tu perfil administrador. Uso: `/password "Contraseña"`
</details>
<details>
  <summary>HeartBeat 💓</summary>
  
  - Se encarga de expulsar al usuario cuando su cliente es inválido o cuando se desconecta.
</details>

<details>
  <summary>Argumentos 🛠️</summary>
  <details>
    <summary>Servidor 🔧</summary>
  
  - <code>-P</code>: Establece el puerto de la sala. Uso: `python Server.py -P xxxxx`
  - <code>-A</code>: Lista de administradores, separada por comas, sin espacios. Uso: `python Server.py -A Admin1,Admin2,Admin3...`
  - <code>-H</code>: IP del host del servidor. Uso: `python Server.py -H 0.0.0.0`
   </details>
     <details>
    <summary>Servidor Web 🌐</summary>
  
  - <code>-P</code>: Establece el puerto de la sala a la que se va a conectar. Uso: `python webserver.py -P xxxxx`
  - <code>-H</code>: Establece la IP del host del servidor de la sala a la que se va a conectar. Uso: `python Server.py -H 0.0.0.0`
   </details>
</details>

## Cómo instalar 🚀
<details>
  <summary>Servidor 🔧</summary>

  - No requiere repositorios adicionales.
  - Ejecutar: `python Server.py`
</details>

<details>
  <summary>Servidor Web 🌐</summary>

  - Requiere Uvicorn, NiceGUI y AIOHTTP
  - Ejecutar: `pip install -r requirements.txt`
  - Ejecutar: `python webserver.py`
</details>

## Galeria 📷
<details>
  <summary>Mostrar ✅</summary>
  
  ![AdminChatGroup](https://github.com/BrewTheFox/ArxChatGroup/blob/main/img/240121_11h06m05s_screenshot.png)
  ![LoginChatGroup](https://github.com/BrewTheFox/ArxChatGroup/blob/main/img/240121_11h27m10s_screenshot.png)
  ![InterfazChatGroup](https://github.com/BrewTheFox/ArxChatGroup/blob/main/img/240121_11h27m24s_screenshot.png)
  ![ErrorChatGroup](https://github.com/BrewTheFox/ArxChatGroup/blob/main/img/240121_11h27m42s_screenshot.png)
</details>

¡Disfruta de Arx Chatgroup y únete a la conversación! 🎉.
