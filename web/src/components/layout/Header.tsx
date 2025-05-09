'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import WalletStatus from '@/components/wallet/WalletStatus';
import WalletConnect from '@/components/wallet/WalletConnect';

const Header: React.FC = () => {
  const [showConnectModal, setShowConnectModal] = useState(false);
  
  const handleConnectClick = () => {
    setShowConnectModal(true);
  };
  
  const handleCloseModal = () => {
    setShowConnectModal(false);
  };
  
  return (
    <header className="sticky top-0 z-10 bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center">
              <span className="text-2xl font-bold text-blue-600">
                Dirac
              </span>
              <span className="ml-2 text-xs bg-blue-100 text-blue-800 py-0.5 px-2 rounded-full">
                Quantum-Resistant
              </span>
            </Link>
            
            <nav className="hidden md:ml-8 md:flex md:space-x-4">
              <Link href="/" className="px-3 py-2 rounded-md text-sm font-medium text-gray-900 hover:bg-gray-50">
                Dashboard
              </Link>
              <Link href="/send" className="px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900">
                Send
              </Link>
              <Link href="/receive" className="px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900">
                Receive
              </Link>
              <Link href="/security" className="px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900">
                Security
              </Link>
            </nav>
          </div>
          
          <div className="flex items-center">
            <WalletStatus onConnectClick={handleConnectClick} />
          </div>
        </div>
      </div>
      
      {showConnectModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="flex justify-end p-2">
              <button
                onClick={handleCloseModal}
                className="text-gray-400 hover:text-gray-600 focus:outline-none"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <WalletConnect onClose={handleCloseModal} />
          </div>
        </div>
      )}
    </header>
  );
};

export default Header; 