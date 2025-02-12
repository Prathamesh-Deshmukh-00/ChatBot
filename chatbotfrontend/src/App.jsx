import { useEffect } from "react";
import "./App.css";

function App() {
  useEffect(() => {
    const socket = new WebSocket("ws://127.0.0.1:8000/ws");

    socket.onopen = () => {
      console.log("Connected to chatbot");
      socket.send("What is the price of a laptop?");
    };

    socket.onmessage = (event) => {
      console.log("Bot:", event.data);
    };

    socket.onerror = (error) => {
      console.error("WebSocket Error:", error);
    };

    socket.onclose = () => {
      console.log("WebSocket Disconnected");
    };

    return () => socket.close(); // Cleanup on unmount
  }, []); // Runs only once

  return <h1>Hello</h1>;
}

export default App;
