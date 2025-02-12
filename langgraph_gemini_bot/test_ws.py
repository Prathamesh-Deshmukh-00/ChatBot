import asyncio
import websockets

async def test_websocket():
    uri = "ws://127.0.0.1:8000/ws"
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello, chatbot!")  # Send message
        response = await websocket.recv()  # Receive response
        print("🤖 Chatbot response:", response)

# Run WebSocket test
asyncio.run(test_websocket())
