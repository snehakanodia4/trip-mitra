import Link from "next/link";
import Navbar from "@/components/NavBar";
export default function Home() {
  return (
    <>
    <Navbar/>
    <main className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-blue-200 text-center p-6">
      <h1 className="text-6xl font-extrabold mb-6  bg-gradient-to-r from-purple-400 via-pink-500 to-yellow-400 bg-clip-text text-transparent">Travel Mitra </h1>
      <p className="text-lg font-semibold text-gray-800 mb-6 max-w-xl">
        AI-powered travel planner — get personalized itineraries, weather-aware
        suggestions, transport options, and hotels — all in one place.
      </p>
      <Link
        href="/chat"
        className="px-6 py-3 bg-blue-600 text-white rounded-xl shadow-md hover:bg-gradient-to-br from-purple-400 via-pink-500 to-yellow-400 transition"
      >
        Plan A Trip Now
      </Link>
    </main>
    </>
    
  );
}
