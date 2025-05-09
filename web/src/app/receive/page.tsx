'use client';

import React, { useRef } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { useWallet } from '@/context/WalletContext';
import Button from '@/components/ui/Button';

export default function ReceivePage() {
  const { walletState } = useWallet();
  const addressRef = useRef<HTMLInputElement>(null);
  
  const copyAddressToClipboard = () => {
    if (addressRef.current && walletState.address) {
      addressRef.current.select();
      document.execCommand('copy');
      
      // Show a toast or notification (simplified here)
      alert('Address copied to clipboard');
    }
  };
  
  // QR code would be generated using a library like qrcode.react
  // Here we'll just display a placeholder
  
  return (
    <MainLayout>
      <div className="max-w-lg mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Receive SOL</h1>
        
        {!walletState.isConnected ? (
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-yellow-700">
                  Please connect your wallet to view your receive address
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-8">
            <div className="bg-white p-6 border border-gray-200 rounded-lg shadow-sm">
              <div className="flex justify-center mb-6">
                {/* This would be replaced with an actual QR code component */}
                <div className="w-48 h-48 bg-gray-200 flex items-center justify-center text-gray-500 text-sm">
                  QR Code Placeholder
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label htmlFor="wallet-address" className="block text-sm font-medium text-gray-700 mb-1">
                    Your Wallet Address
                  </label>
                  <div className="flex rounded-md shadow-sm">
                    <input
                      ref={addressRef}
                      type="text"
                      id="wallet-address"
                      className="flex-1 px-3 py-2 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-md focus:ring-blue-500 focus:border-blue-500 block w-full"
                      value={walletState.address || ''}
                      readOnly
                    />
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={copyAddressToClipboard}
                      className="ml-3"
                    >
                      Copy
                    </Button>
                  </div>
                </div>
                
                <div className="text-sm text-gray-500">
                  <p className="font-medium mb-1">How to receive SOL:</p>
                  <ol className="list-decimal pl-5 space-y-1">
                    <li>Share your wallet address with the sender</li>
                    <li>The sender will initiate a transaction to your address</li>
                    <li>Once confirmed, the SOL will appear in your wallet</li>
                  </ol>
                </div>
              </div>
            </div>
            
            <div className="bg-blue-50 p-4 rounded-md">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2h-1v-3a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-blue-800">Note About Quantum-Resistance</h3>
                  <p className="mt-1 text-sm text-blue-700">
                    Your Dirac wallet uses quantum-resistant cryptography to secure your funds. 
                    The address shown is compatible with the Solana blockchain while providing protection 
                    against future quantum computing threats.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
} 