export default function MessageBubble({ sender, text }) {
  return (
    <div
      className={`p-3 rounded-2xl max-w-[80%] break-words ${
        sender === "user"
          ? "bg-blue-600 text-white ml-auto"
          : "bg-gray-200 text-black mr-auto"
      }`}
    >
      {text}
    </div>
  );
}
