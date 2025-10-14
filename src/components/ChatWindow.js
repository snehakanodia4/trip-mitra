"use client";

import { useState, useRef, useEffect } from "react";
import ChatInput from "./ChatInput";
import MessageBubble from "./MessageBubble";
import { sendMessageToBackend } from "../lib/api";

export default function ChatWindow() {
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "I am your chatbot, I can help you plan your next trip.",
    },
    {
      sender: "bot",
      text: "Ask me anything.",
    },
  ]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSend(userMsg) {
    setMessages((prev) => [...prev, { sender: "user", text: userMsg }]);
    setLoading(true);

    try {
      const res = await sendMessageToBackend(userMsg);
      const replyText = res.reply || "Sorry, I couldn't get a reply.";
      setMessages((prev) => [...prev, { sender: "bot", text: replyText }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Error: Could not reach backend." },
      ]);
    } finally {
      setLoading(false);
    }
  }
  return (
    <div className="flex flex-col h-[75vh] border rounded-xl  bg-gradient-to-tl from-pink-400 via-orange-400 to-yellow-300 shadow-md">
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((m, i) => (
          <MessageBubble key={i} sender={m.sender} text={m.text} />
        ))}
        {loading && <MessageBubble sender="bot" text={"...fetching "} />}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t">
        <ChatInput onSend={handleSend} />
      </div>
    </div>
  );
}
