from fastapi import FastAPI,WebSocket,WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import collections

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Real Time log viewer</title>
    </head>
    <body>
        <h1>Real Time log viewer</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/logs");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""



class Connection():
    def __init__(self,websocket:WebSocket):
        self.websocket=websocket
        self.is_alive = True
    async def send_data(self,txt:str):
       await self.websocket.send_text(txt)




file_path="log_file.txt"
last_line=0
async def read_file():
    last_position=0
    try:
        with open(file_path, "r") as file:
            line=file.readlines()
            last_position=len(line)
            del line
            file.seek(last_position)
            while True:
                update_in_file= file.readline()
                if update_in_file:
                    #we can send to web client from here
                    for client in Connections:
                        if client.is_alive:
                            await client.send_data(update_in_file)
                        else:
                            Connections.remove(client)
                    last_position= file.tell()
                await asyncio.sleep(0.01)
    except FileNotFoundError:
        print("file is not present")
        await asyncio.sleep(10)



@app.get("/")
def main_route():
    return HTMLResponse(html)


Connections=[]

@app.websocket("/logs")
async def connect_to_scocket(websocket:WebSocket):
    await websocket.accept()
    client=Connection(websocket)
    try:
       with open(file_path, "r") as file:
         last_line=collections.deque(file,10)
         for line in last_line:
            await client.send_data(line)
       Connections.append(client)
    except FileNotFoundError:
        print("file is not present")
    try: 
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        client.is_alive=False



@app.on_event('startup')
def read_the_file_data():
    asyncio.create_task(read_file())
