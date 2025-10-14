// Frontend -> Backend helper.
// Replace the URL if your backend runs on a different host or port.
const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function sendMessageToBackend(message) {
  const res = await fetch(`${BACKEND_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  if (!res.ok) {
    throw new Error("Backend request failed");
  }
  const data = await res.json();
  return data; // { reply: "..." }
}
