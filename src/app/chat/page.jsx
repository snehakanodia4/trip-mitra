import ChatWindow from "../../components/ChatWindow";
import Navbar from "@/components/NavBar";
export default function ChatPage() {
  return (
    <div className="">
      <Navbar className="align-top"/>
      <main className="flex items-center justify-center min-h-screen bg-gray-100 pt-20">
       
      <div className="w-full max-w-3xl">
        
        <h1 className="text-3xl font-extrabold text-center mb-4 text-blue-950">Hi! My name is Trip-Mitra 🤖</h1>
        <ChatWindow />
      </div>
    </main>
    </div>
    
  );
}
