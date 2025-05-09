'use client';

import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { useWallet } from '@/context/WalletContext';
import Link from 'next/link';
import Button from '@/components/ui/Button';

export default function Home() {
  const { walletState } = useWallet();
  const { isConnected, address, balance } = walletState;
  
  return (
    <MainLayout>
      <div className="px-4 py-8 sm:px-0">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl sm:tracking-tight lg:text-6xl">
            Dirac Wallet
          </h1>
          <p className="mt-5 max-w-xl mx-auto text-xl text-gray-500">
            A quantum-resistant cryptocurrency wallet built to protect your assets today and tomorrow
          </p>
        </div>
        
        {isConnected ? (
          <div className="mt-10">
            <div className="bg-white overflow-hidden shadow rounded-lg divide-y divide-gray-200">
              <div className="px-4 py-5 sm:p-6">
                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">Wallet Overview</h3>
                    <div className="mt-5">
                      <dl className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                        <div className="bg-gray-50 px-4 py-5 sm:p-6 rounded-lg">
                          <dt className="text-sm font-medium text-gray-500 truncate">Address</dt>
                          <dd className="mt-1 text-sm text-gray-900 truncate">{address}</dd>
                        </div>
                        <div className="bg-gray-50 px-4 py-5 sm:p-6 rounded-lg">
                          <dt className="text-sm font-medium text-gray-500 truncate">Balance</dt>
                          <dd className="mt-1 text-2xl font-semibold text-gray-900">{balance !== null ? `${balance.toFixed(4)} SOL` : '--'}</dd>
                        </div>
                      </dl>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
                    <div className="mt-5 space-y-4">
                      <Link href="/send" className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                        Send
                      </Link>
                      <Link href="/receive" className="w-full inline-flex justify-center items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                        Receive
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="mt-10 flex flex-col items-center">
            <div className="bg-white overflow-hidden shadow rounded-lg w-full max-w-md">
              <div className="px-4 py-5 sm:p-6 text-center">
                <h3 className="text-lg font-medium text-gray-900">Get Started</h3>
                <p className="mt-2 text-sm text-gray-500">
                  Connect to your existing wallet or create a new one to get started.
                </p>
                <div className="mt-5">
                  <Link href="/wallet/create" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                    Get Started
                  </Link>
                </div>
              </div>
            </div>
            
            <div className="mt-10 px-4 py-5 sm:p-6 text-center max-w-2xl">
              <h2 className="text-2xl font-bold text-gray-900">Quantum-Resistant Security</h2>
              <p className="mt-3 text-lg text-gray-500">
                Dirac Wallet uses post-quantum cryptography to protect your assets against quantum computing threats while maintaining compatibility with existing blockchain networks.
              </p>
              
              <div className="mt-8 grid grid-cols-1 gap-8 md:grid-cols-3">
                <div className="bg-white p-6 rounded-lg shadow-sm">
                  <h3 className="text-lg font-medium text-gray-900">Post-Quantum Algorithms</h3>
                  <p className="mt-2 text-sm text-gray-500">
                    Built with Dilithium signatures, resistant to quantum computer attacks.
                  </p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm">
                  <h3 className="text-lg font-medium text-gray-900">Enhanced Security</h3>
                  <p className="mt-2 text-sm text-gray-500">
                    Robust encryption, secure key storage, and protection against various attacks.
                  </p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm">
                  <h3 className="text-lg font-medium text-gray-900">Solana Compatible</h3>
                  <p className="mt-2 text-sm text-gray-500">
                    Works seamlessly with the Solana blockchain while providing extra security.
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
