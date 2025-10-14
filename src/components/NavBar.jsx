"use client";

import Link from "next/link";
import { useState } from "react";

export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <nav className="bg-blue-600 text-white px-4 py-4 shadow-md fixed w-full z-50">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        {/* Logo */}
        <Link href="/" className=" font-extrabold font-stretch-150% text-5xl  bg-gradient-to-tl from-purple-400 via-pink-400 to-yellow-300 bg-clip-text text-transparent">
           M
        </Link>

        {/* Desktop Menu */}
        <div className="hidden md:flex space-x-6">
          <Link href="/" className="hover:text-gray-200">
            Home
          </Link>
          <Link href="/" className="hover:text-gray-200">
            You
          </Link>
        </div>

        {/* Mobile Menu Button */}
        <div className="md:hidden">
          <button
            onClick={() => setOpen(!open)}
            className="focus:outline-none"
          >
            {open ? (
              <span className="text-2xl">&#10005;</span> // X icon
            ) : (
              <span className="text-2xl">&#9776;</span> // Hamburger icon
            )}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {open && (
        <div className="md:hidden mt-2 flex flex-col space-y-2 bg-blue-500 p-4 rounded-lg">
          <Link href="/" className="hover:text-gray-200" onClick={() => setOpen(false)}>
            Home
          </Link>
          <Link href="/" className="hover:text-gray-200" onClick={() => setOpen(false)}>
            You
          </Link>
        </div>
      )}
    </nav>
  );
}
