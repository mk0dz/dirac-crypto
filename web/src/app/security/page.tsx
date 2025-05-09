'use client';

import React from 'react';
import MainLayout from '@/components/layout/MainLayout';

export default function SecurityPage() {
  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-gray-900 sm:text-4xl">
            Quantum-Resistant Security
          </h1>
          <p className="mt-4 text-xl text-gray-500">
            How Dirac Wallet protects your assets from current and future threats
          </p>
        </div>
        
        <div className="prose prose-lg mx-auto">
          <h2>The Quantum Computing Threat</h2>
          <p>
            Quantum computers leverage quantum mechanical phenomena to solve certain types of problems 
            exponentially faster than classical computers. While still in early development, quantum 
            computers pose a significant threat to many cryptographic systems used in today's blockchains.
          </p>
          <p>
            Specifically, Shor's algorithm running on a sufficiently powerful quantum computer could 
            break elliptic curve cryptography (ECC) and RSA, the foundations of security for most 
            cryptocurrencies including Bitcoin and Ethereum.
          </p>
          
          <h2>Dilithium: Post-Quantum Cryptography</h2>
          <p>
            Dirac Wallet implements Dilithium, a lattice-based digital signature algorithm selected by NIST 
            (National Institute of Standards and Technology) as a standard for post-quantum cryptography.
          </p>
          <p>
            Dilithium is designed to be secure against both classical and quantum computing attacks, 
            while maintaining reasonable key and signature sizes with good performance characteristics.
          </p>
          
          <div className="bg-gray-50 p-6 rounded-lg my-8">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Key Security Features</h3>
            <ul className="space-y-4">
              <li>
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-6 w-6 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h4 className="text-base font-medium text-gray-900">Quantum-resistant signatures</h4>
                    <p className="mt-1 text-sm text-gray-500">Transactions signed with Dilithium are secure against attacks by quantum computers.</p>
                  </div>
                </div>
              </li>
              <li>
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-6 w-6 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h4 className="text-base font-medium text-gray-900">Encrypted key storage</h4>
                    <p className="mt-1 text-sm text-gray-500">Private keys are protected with advanced encryption and secure password-based key derivation.</p>
                  </div>
                </div>
              </li>
              <li>
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-6 w-6 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h4 className="text-base font-medium text-gray-900">Memory safety</h4>
                    <p className="mt-1 text-sm text-gray-500">Sensitive data is properly cleared from memory when no longer needed.</p>
                  </div>
                </div>
              </li>
              <li>
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-6 w-6 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h4 className="text-base font-medium text-gray-900">Blockchain compatibility</h4>
                    <p className="mt-1 text-sm text-gray-500">Maintains compatibility with existing blockchains while adding quantum resistance.</p>
                  </div>
                </div>
              </li>
            </ul>
          </div>
          
          <h2>How Dirac Wallet Works with Solana</h2>
          <p>
            Dirac Wallet integrates with Solana by creating a special address derivation path that maps 
            quantum-resistant Dilithium public keys to Solana-compatible addresses. This allows the wallet 
            to maintain compatibility with the Solana blockchain while adding a layer of quantum security.
          </p>
          <p>
            When you create a transaction:
          </p>
          <ol>
            <li>The transaction is prepared according to Solana's transaction format</li>
            <li>Instead of using elliptic curve signatures, Dirac signs the transaction using the Dilithium algorithm</li>
            <li>The resulting signature is converted to a format compatible with Solana</li>
            <li>The transaction can be verified by the Solana network</li>
          </ol>
          
          <h2>Security Audits and Testing</h2>
          <p>
            The Dirac Wallet codebase undergoes regular security audits and testing, including:
          </p>
          <ul>
            <li>Penetration testing to ensure resistance to various attack vectors</li>
            <li>Security validation for entropy and randomness quality</li>
            <li>Stress testing and performance benchmarking</li>
            <li>Code reviews by security experts</li>
          </ul>
          
          <div className="bg-blue-50 p-5 rounded-lg mt-6 mb-8">
            <h3 className="text-lg font-medium text-blue-800 mb-2">Future-Proof Your Assets</h3>
            <p className="text-blue-700">
              By using Dirac Wallet, you're taking a proactive step to protect your cryptocurrency 
              assets from future quantum computing threats. While quantum computers capable of breaking 
              traditional cryptography may still be years away, preparing now ensures your assets remain 
              secure in the long term.
            </p>
          </div>
        </div>
      </div>
    </MainLayout>
  );
} 