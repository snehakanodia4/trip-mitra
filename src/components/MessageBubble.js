import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/* Cleans messy markdown coming from backend */
function cleanMarkdown(text) {
  if (!text) return "";

  let cleaned = text
    .replace(/```markdown/g, "")
    .replace(/```/g, "")
    .replace(/^\*\s+/gm, "- ")   // Fix "* item" -> "- item"
    .trim();

  return cleaned;
}

export default function MessageBubble({ sender, text }) {
  const formattedText = cleanMarkdown(text);

  return (
    <div
      className={`p-3 rounded-2xl max-w-[80%] break-words ${
        sender === "user"
          ? "bg-blue-600 text-white ml-auto"
          : "bg-gray-200 text-black mr-auto"
      }`}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => (
            <h1 className="text-xl font-bold mt-3 mb-2">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-lg font-semibold mt-3 mb-2">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-md font-semibold mt-2 mb-1">{children}</h3>
          ),
          ul: ({ children }) => (
            <ul className="list-disc pl-5 space-y-1">{children}</ul>
          ),
          strong: ({ children }) => (
            <strong className="text-pink-600">{children}</strong>
          ),

          /* ✅ TURN PHOTO LINKS INTO ACTUAL IMAGES */
          a: ({ href }) => {
            if (!href) return null;

            return (
              <img
                src={href}
                alt="Hotel"
                className="rounded-xl mt-3 max-w-full shadow-md"
                loading="lazy"
              />
            );
          },
        }}
      >
        {formattedText}
      </ReactMarkdown>
    </div>
  );
}
