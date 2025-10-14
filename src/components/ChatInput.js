"use client";

import { useState } from "react";

export default function ChatInput({ onSend }) {
  const [input, setInput] = useState("");

  function handleSend() {
    if (!input.trim()) return;
    onSend(input.trim());
    setInput("");
  }

  function onKey(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="flex gap-2">
      <textarea
        rows={1}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={onKey}
        placeholder="Type your message..."
        className="flex-1 border rounded-xl p-3 resize-none text-gray-800"
      />
      <button
        onClick={handleSend}
        className="border rounded-xl px-4 py-2 text-gray-800 hover:bg-green-400 "
      >
        Send
      </button>
    </div>
  );
}
