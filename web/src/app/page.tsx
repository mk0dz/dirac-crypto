'use client'
import Image from 'next/image'
import React from 'react';

export default function Home() {
  
  return (
    <div className="flex min-h-screen relative">
      {/* Left content */}
      <div className="flex flex-col justify-center sm:p-20 w-2/3 bg-black text-white">
        <div className="">
          <h1 className="text-7xl font-normal mb-4">
            a collaborative
            <br />
            <span className="text-teal-400 font-bold">project</span> of <span className="text-teal-400">satoshi</span>
            <br />
            nakamoto & paul
            <br />
            <span className="text-teal-400 font-bold">dirac</span>
          </h1>
          
          <div className="flex gap-4 mt-12">
            <a
              href="/docs"
              className="border border-teal-400 py-2 px-6 inline-block hover:bg-teal-400/10 transition-colors"
            >
              Documentation
            </a>
            <a
              href="https://hashes.dirac.fun/"
              className="border border-teal-400 py-2 px-6 inline-block hover:bg-teal-400/10 transition-colors"
            >
              hashes
            </a>
          </div>
        </div>
      </div>
      
      {/* Right image - positioned at the right edge */}
      <div className="relative w-full md:w-1/3 h-64 md:h-auto">
      
        <Image 
          src="/dirac.png"
          alt="Paul Dirac"
          layout="fill"
          objectFit="cover"
        />
        <p style={{fontFamily: 'Chivo Mono'}} className='absolute bottom-0 left-2 text-xs sm:text-sm md:text-md font-thin text-white bg-black bg-opacity-30 px-2 py-1 rounded'>Copyright © 2025, <a href="https://github.com/mk0dz" className='underline'>mk0dz</a></p>
      </div>

    </div>
  )
}


