"use client";

import { useState, useRef } from "react";

export default function ChatInput({ onSend }) {
  const [input, setInput] = useState("");
  const [recording, setRecording] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

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

  // 🎤 Start recording
  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });

        console.log("🎧 Audio recorded:", audioBlob);

        // Send audio to backend
        const formData = new FormData();
        formData.append("audio", audioBlob, "voice.webm");

        try {
          const res = await fetch("http://localhost:5000/voice", {
            method: "POST",
            body: formData,
          });

          const data = await res.json();

          if (data.text) {
            setInput(data.text); // ✅ Text from Savram API
          } else {
            alert("No text returned from voice API");
          }
        } catch (err) {
          console.error("Voice upload failed:", err);
        }
      };

      mediaRecorder.start();
      setRecording(true);
    } catch (err) {
      console.error("Mic access denied:", err);
      alert("Please allow microphone access");
    }
  }

  // 🛑 Stop recording
  function stopRecording() {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  }

  return (
    <div className="flex gap-2 items-center">
      <textarea
        rows={1}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={onKey}
        placeholder="Type or speak your message..."
        className="flex-1 border rounded-xl p-3 resize-none text-gray-800"
      />

      {/* 🎤 Record Button */}
      {!recording ? (
        <button
          onClick={startRecording}
          className="border rounded-xl px-3 py-2 bg-red-500 text-white hover:bg-red-600"
        >
          🎙️
        </button>
      ) : (
        <button
          onClick={stopRecording}
          className="border rounded-xl px-3 py-2 bg-gray-700 text-white animate-pulse"
        >
          ⏹️
        </button>
      )}

      <button
        onClick={handleSend}
        className="border rounded-xl px-4 py-2 text-gray-800 hover:bg-green-400"
      >
        Send
      </button>
    </div>
  );
}
