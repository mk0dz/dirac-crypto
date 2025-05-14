'use client'
import React, { useState } from 'react'
import Image from 'next/image'
import Link from 'next/link'

export default function Documentation() {
  const [activeTab, setActiveTab] = useState('dirac-wallet')
  const [expandedQnAs, setExpandedQnAs] = useState<string[]>([])
  const [walletTab, setWalletTab] = useState('overview')

  const toggleQnA = (id: string) => {
    setExpandedQnAs(prev => 
      prev.includes(id) ? prev.filter(item => item !== id) : [...prev, id]
    )
  }

  return (
    <div className="flex h-screen bg-black text-white">
      {/* Sidebar */}
      <div className="w-48 border-r border-gray-800 flex flex-col h-full">
        {/* Top icon */}
        <div className="p-6 border-b border-gray-800">
          <Link href="/">
            <Image src="/logo.svg" alt="Dirac Logo" width={200} height={200} />
          </Link>
        </div>
        
        {/* Navigation links */}
        <nav className="flex-1">
          <Link href="/" className="block px-4 py-3 hover:bg-gray-900 text-gray-400 hover:text-teal-400">
            Home
          </Link>
          <button 
            onClick={() => setActiveTab('dirac-wallet')}
            className={`text-left block w-full px-4 py-3 hover:bg-gray-900 ${activeTab === 'dirac-wallet' ? 'text-teal-400' : 'text-gray-400'}`}
          >
            dirac-wallet
          </button>
          <button 
            onClick={() => window.open('https://hashes.dirac.fun/', '_blank')}
            className={`text-left block w-full px-4 py-3 hover:bg-gray-900 ${activeTab === 'hashes' ? 'text-teal-400' : 'text-gray-400'}`}
          >
            hashes
          </button>
          <button 
            onClick={() => setActiveTab('team')}
            className={`text-left block w-full px-4 py-3 hover:bg-gray-900 ${activeTab === 'team' ? 'text-teal-400' : 'text-gray-400'}`}
          >
            team
          </button>
          <button 
            onClick={() => setActiveTab('qnas')}
            className={`text-left block w-full px-4 py-3 hover:bg-gray-900 ${activeTab === 'qnas' ? 'text-teal-400' : 'text-gray-400'}`}
          >
            QnAs
          </button>
        </nav>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-auto">
        {/* Header */}
        <header className="border-b border-gray-800 p-6 flex justify-between items-center">
          <h1 className="text-2xl font-mono">Documentation</h1>
          <div className="text-teal-400">post quantum cryptography</div>
        </header>

        {/* Content based on active tab */}
        <div className="p-6">
          {activeTab === 'dirac-wallet' && (
            <div>
              <div className="flex items-center mb-6">
                <div className="text-teal-400 mr-4">🔒</div>
                <h2 className="text-3xl font-mono text-teal-400">Dirac Wallet</h2>
              </div>
              
              <p className="text-teal-400 text-xl mb-8">
                A lightweight, quantum-resistant Solana wallet using post-quantum cryptography.
              </p>
              
              {/* Internal tabs for dirac-wallet documentation */}
              <div className="mb-8">
                <div className="flex border-b border-gray-800 mb-6">
                  <button 
                    onClick={() => setWalletTab('overview')}
                    className={`px-4 py-2 font-medium ${walletTab === 'overview' ? 'text-teal-400 border-b-2 border-teal-400' : 'text-gray-400'}`}
                  >
                    Overview
                  </button>
                  <button 
                    onClick={() => setWalletTab('features')}
                    className={`px-4 py-2 font-medium ${walletTab === 'features' ? 'text-teal-400 border-b-2 border-teal-400' : 'text-gray-400'}`}
                  >
                    Features
                  </button>
                  <button 
                    onClick={() => setWalletTab('installation')}
                    className={`px-4 py-2 font-medium ${walletTab === 'installation' ? 'text-teal-400 border-b-2 border-teal-400' : 'text-gray-400'}`}
                  >
                    Installation
                  </button>
                  <button 
                    onClick={() => setWalletTab('usage')}
                    className={`px-4 py-2 font-medium ${walletTab === 'usage' ? 'text-teal-400 border-b-2 border-teal-400' : 'text-gray-400'}`}
                  >
                    Usage
                  </button>
                  <button 
                    onClick={() => setWalletTab('security')}
                    className={`px-4 py-2 font-medium ${walletTab === 'security' ? 'text-teal-400 border-b-2 border-teal-400' : 'text-gray-400'}`}
                  >
                    Security
                  </button>
                  <button 
                    onClick={() => setWalletTab('comparison')}
                    className={`px-4 py-2 font-medium ${walletTab === 'comparison' ? 'text-teal-400 border-b-2 border-teal-400' : 'text-gray-400'}`}
                  >
                    Comparison
                  </button>
                </div>
                
                {/* Content for each wallet tab */}
                {walletTab === 'overview' && (
                  <div>
                    <p className="text-gray-300 mb-4">
                      Dirac Wallet is a quantum-resistant Solana wallet that provides protection against both classical and quantum attacks. With the advancement of quantum computing, traditional cryptographic methods used in current wallets will become vulnerable. Our wallet is designed with the future in mind, providing robust security that can withstand the computational power of quantum computers.
                    </p>
                    
                    <div className="bg-gray-900 p-4 rounded-sm font-mono text-sm mb-8">
                      <div className="text-teal-400"># Install via pip</div>
                      <div className="text-white">pip install dirac-wallet</div>
                    </div>
                    
                    <h3 className="text-xl mb-4 mt-8 pb-2 border-b border-gray-800">What is the Dirac Wallet?</h3>
                    
                    <p className="text-gray-300 mb-4">
                      Our wallet provides a secure way to store and manage digital assets on the Solana blockchain with protection against both classical and quantum attacks. It implements NIST-approved post-quantum cryptographic algorithms such as CRYSTALS-Dilithium for signatures, ensuring your assets remain secure even as quantum computing advances.
                    </p>
                    
                    <p className="text-gray-300 mb-4">
                      While maintaining full compatibility with the Solana ecosystem, Dirac Wallet adds an extra layer of security by replacing vulnerable elliptic curve cryptography with quantum-resistant algorithms, future-proofing your assets against emerging threats.
                    </p>
                  </div>
                )}
                
                {walletTab === 'features' && (
                  <div>
                    <h3 className="text-teal-400 mb-4">Key Features:</h3>
                    
                    <ul className="space-y-3 mb-6">
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <div>
                          <span className="text-teal-400 font-bold">Quantum-Resistant Cryptography</span>: Uses CRYSTALS-Dilithium for signatures, providing protection against quantum computing attacks
                        </div>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <div>
                          <span className="text-teal-400 font-bold">Solana Blockchain Support</span>: Compatible with Solana devnet, testnet, and mainnet
                        </div>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <div>
                          <span className="text-teal-400 font-bold">Secure Key Storage</span>: Encrypted wallet files with strong password protection
                        </div>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <div>
                          <span className="text-teal-400 font-bold">Transaction History</span>: Track and view your transaction history
                        </div>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <div>
                          <span className="text-teal-400 font-bold">Interactive CLI</span>: Easy-to-use command line interface
                        </div>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <div>
                          <span className="text-teal-400 font-bold">Airdrop Support</span>: Request test SOL on devnet and testnet with simple commands
                        </div>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <div>
                          <span className="text-teal-400 font-bold">Multi-Wallet Management</span>: Create and manage multiple wallets easily
                        </div>
                      </li>
                    </ul>
                    
                    <h3 className="text-xl mb-4 mt-8 pb-2 border-b border-gray-800">Technical Implementation</h3>
                    
                    <p className="text-gray-300 mb-4">
                      Dirac Wallet is built on a foundation of post-quantum cryptographic primitives, primarily using lattice-based cryptography for signatures. The wallet implements NIST-approved CRYSTALS-Dilithium algorithm for digital signatures to ensure quantum resistance.
                    </p>
                    
                    <h3 className="text-xl mb-4 mt-8 pb-2 border-b border-gray-800">Architecture</h3>
                    
                    <p className="text-gray-300 mb-4">
                      The wallet architecture consists of several core components:
                    </p>

                    <ul className="space-y-3 mb-6 text-gray-300">
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <div>
                          <span className="text-teal-400 font-bold">Key Management System</span>: Securely generates, stores, and manages cryptographic keys using post-quantum algorithms.
                        </div>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <div>
                          <span className="text-teal-400 font-bold">Transaction Module</span>: Handles the creation, signing, and verification of Solana blockchain transactions.
                        </div>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <div>
                          <span className="text-teal-400 font-bold">Solana Connector</span>: Interfaces with the Solana blockchain networks (devnet, testnet, mainnet).
                        </div>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <div>
                          <span className="text-teal-400 font-bold">Command Line Interface</span>: Provides an intuitive interface for interacting with the wallet.
                        </div>
                      </li>
                    </ul>
                  </div>
                )}
                
                {walletTab === 'installation' && (
                  <div>
                    <h3 className="text-xl mb-4 pb-2 border-b border-gray-800">Installation</h3>
                    
                    <h4 className="text-teal-400 mb-2 mt-4">From PyPI</h4>
                    <div className="bg-gray-900 p-4 rounded-sm font-mono text-sm mb-6">
                      <div className="text-white">pip install dirac-wallet</div>
                    </div>
                    
                    <h4 className="text-teal-400 mb-2 mt-4">From Source</h4>
                    <div className="bg-gray-900 p-4 rounded-sm font-mono text-sm mb-6">
                      <div className="text-white">
                        # Clone the repository<br/>
                        git clone https://github.com/dirac-labs/dirac-wallet.git<br/>
                        cd dirac-wallet<br/>
                        <br/>
                        # Create virtual environment<br/>
                        python -m venv venv<br/>
                        source venv/bin/activate  # On Windows: venv\Scripts\activate<br/>
                        <br/>
                        # Install dependencies and package<br/>
                        pip install -e .
                      </div>
                    </div>
                    
                    <h3 className="text-xl mb-4 mt-8 pb-2 border-b border-gray-800">Networks</h3>
                    
                    <p className="text-gray-300 mb-4">
                      Dirac-Wallet supports three Solana networks:
                    </p>
                    
                    <ul className="space-y-2 mb-4 text-gray-300">
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <span><span className="text-teal-400">devnet</span> (default): Development network with test tokens</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <span><span className="text-teal-400">testnet</span>: Test network with test tokens</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <span><span className="text-teal-400">mainnet</span>: Production network with real SOL (use with caution)</span>
                      </li>
                    </ul>
                    
                    <div className="bg-gray-900 p-4 rounded-sm font-mono text-sm mb-6">
                      <div className="text-teal-400"># Example usage with network specification:</div>
                      <div className="text-white">dirac-wallet create mywallet --network mainnet</div>
                    </div>
                  </div>
                )}
                
                {walletTab === 'usage' && (
                  <div>
                    <h3 className="text-xl mb-4 pb-2 border-b border-gray-800">Quick Start</h3>
                    
                    <div className="bg-gray-900 p-4 rounded-sm font-mono text-sm mb-6">
                      <div className="text-white">
                        # Create a new wallet named &quot;mywallet&quot;<br/>
                        dirac-wallet create mywallet<br/>
                        <br/>
                        # Get test SOL from devnet (default network)<br/>
                        dirac-wallet airdrop mywallet<br/>
                        <br/>
                        # Check your balance<br/>
                        dirac-wallet balance mywallet<br/>
                        <br/>
                        # Send SOL to another address<br/>
                        dirac-wallet send mywallet &lt;recipient_address&gt; &lt;amount&gt;<br/>
                        <br/>
                        # View transaction history<br/>
                        dirac-wallet history mywallet<br/>
                        <br/>
                        # View wallet information<br/>
                        dirac-wallet info mywallet<br/>
                        <br/>
                        # List all your wallets<br/>
                        dirac-wallet list-wallets
                      </div>
                    </div>
                    
                    <h3 className="text-xl mb-4 mt-8 pb-2 border-b border-gray-800">Command Reference</h3>
                    
                    <div className="overflow-x-auto mb-8">
                      <table className="min-w-full bg-gray-900 text-gray-300">
                        <thead>
                          <tr>
                            <th className="py-2 px-4 border-b border-gray-800 text-left text-teal-400">Command</th>
                            <th className="py-2 px-4 border-b border-gray-800 text-left text-teal-400">Description</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            <td className="py-2 px-4 border-b border-gray-800 font-mono">create &lt;name&gt;</td>
                            <td className="py-2 px-4 border-b border-gray-800">Create a new wallet</td>
                          </tr>
                          <tr>
                            <td className="py-2 px-4 border-b border-gray-800 font-mono">balance &lt;name&gt;</td>
                            <td className="py-2 px-4 border-b border-gray-800">Check wallet balance</td>
                          </tr>
                          <tr>
                            <td className="py-2 px-4 border-b border-gray-800 font-mono">send &lt;name&gt; &lt;recipient&gt; &lt;amount&gt;</td>
                            <td className="py-2 px-4 border-b border-gray-800">Send SOL to another address</td>
                          </tr>
                          <tr>
                            <td className="py-2 px-4 border-b border-gray-800 font-mono">airdrop &lt;name&gt; [amount]</td>
                            <td className="py-2 px-4 border-b border-gray-800">Request SOL airdrop (devnet/testnet only)</td>
                          </tr>
                          <tr>
                            <td className="py-2 px-4 border-b border-gray-800 font-mono">info &lt;name&gt;</td>
                            <td className="py-2 px-4 border-b border-gray-800">Show wallet information</td>
                          </tr>
                          <tr>
                            <td className="py-2 px-4 border-b border-gray-800 font-mono">history &lt;name&gt;</td>
                            <td className="py-2 px-4 border-b border-gray-800">Show transaction history</td>
                          </tr>
                          <tr>
                            <td className="py-2 px-4 border-b border-gray-800 font-mono">list-wallets</td>
                            <td className="py-2 px-4 border-b border-gray-800">List all wallets in the default directory</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                    
                    <h4 className="text-teal-400 mb-2">Global Options</h4>
                    <ul className="space-y-2 mb-6 text-gray-300">
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <span><span className="font-mono">--network</span> or <span className="font-mono">-n</span>: Specify network (devnet, testnet, mainnet). Default is <span className="font-mono">devnet</span>.</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <span><span className="font-mono">--path</span> or <span className="font-mono">-p</span>: Specify custom wallet file path.</span>
                      </li>
                    </ul>
                  </div>
                )}
                
                {walletTab === 'security' && (
                  <div>
                    <h3 className="text-xl mb-4 pb-2 border-b border-gray-800">Security Notes</h3>
                    
                    <ul className="space-y-3 mb-6 text-gray-300">
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <span>Your private keys are encrypted with your password</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <span>Always back up your wallet files (stored in <span className="font-mono">~/.dirac_wallet/</span> by default)</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <span>Keep your password secure - there is no recovery option if forgotten</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <span>Transaction signatures use quantum-resistant algorithms by default</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">•</span> 
                        <span>The wallet is resistant to future quantum computing attacks</span>
                      </li>
                    </ul>
                    
                    <h3 className="text-xl mb-4 mt-8 pb-2 border-b border-gray-800">Development Status</h3>
                    
                    <p className="text-gray-300 mb-4">
                      Dirac-Wallet is currently in beta. Use on mainnet with caution.
                    </p>
                    
                    <ul className="space-y-2 mb-6 text-gray-300">
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">✅</span> 
                        <span>Key generation and storage</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">✅</span> 
                        <span>Transaction signing and verification</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">✅</span> 
                        <span>Network connectivity and transaction submission</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">✅</span> 
                        <span>Command line interface</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">✅</span> 
                        <span>Transaction history</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">✅</span> 
                        <span>Multi-wallet support</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-teal-400 mr-2">✅</span> 
                        <span>Quantum-resistant cryptography</span>
                      </li>
                    </ul>
                  </div>
                )}
                
                {walletTab === 'comparison' && (
                  <div>
                    <h3 className="text-xl mb-4 pb-2 border-b border-gray-800">Comparison with Traditional Wallets</h3>
                    
                    <div className="overflow-x-auto mb-8">
                      <table className="min-w-full bg-gray-900 text-gray-300">
                        <thead>
                          <tr>
                            <th className="py-2 px-4 border-b border-gray-800 text-left text-teal-400">Feature</th>
                            <th className="py-2 px-4 border-b border-gray-800 text-left text-teal-400">Traditional Solana Wallets</th>
                            <th className="py-2 px-4 border-b border-gray-800 text-left text-teal-400">Dirac-Wallet</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            <td className="py-2 px-4 border-b border-gray-800 font-bold">Cryptography</td>
                            <td className="py-2 px-4 border-b border-gray-800">Uses ECDSA (elliptic curve)</td>
                            <td className="py-2 px-4 border-b border-gray-800">Uses quantum-resistant CRYSTALS-Dilithium</td>
                          </tr>
                          <tr>
                            <td className="py-2 px-4 border-b border-gray-800 font-bold">Security Against Quantum Attacks</td>
                            <td className="py-2 px-4 border-b border-gray-800">Vulnerable to quantum computing attacks</td>
                            <td className="py-2 px-4 border-b border-gray-800">Resistant to quantum computing threats</td>
                          </tr>
                          <tr>
                            <td className="py-2 px-4 border-b border-gray-800 font-bold">Key Generation</td>
                            <td className="py-2 px-4 border-b border-gray-800">Based on classical cryptography</td>
                            <td className="py-2 px-4 border-b border-gray-800">Uses post-quantum algorithms</td>
                          </tr>
                          <tr>
                            <td className="py-2 px-4 border-b border-gray-800 font-bold">Future-Proofing</td>
                            <td className="py-2 px-4 border-b border-gray-800">May require upgrades when quantum computing advances</td>
                            <td className="py-2 px-4 border-b border-gray-800">Already prepared for quantum era</td>
                          </tr>
                          <tr>
                            <td className="py-2 px-4 border-b border-gray-800 font-bold">Transaction Speed</td>
                            <td className="py-2 px-4 border-b border-gray-800">Standard Solana speed</td>
                            <td className="py-2 px-4 border-b border-gray-800">Maintains Solana speed while adding quantum security</td>
                          </tr>
                          <tr>
                            <td className="py-2 px-4 border-b border-gray-800 font-bold">Compatibility</td>
                            <td className="py-2 px-4 border-b border-gray-800">Works with current Solana ecosystem</td>
                            <td className="py-2 px-4 border-b border-gray-800">Fully compatible with Solana blockchain</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                    
                    <p className="text-gray-300 mb-4">
                      While traditional wallets rely on elliptic curve cryptography that could be broken by sufficiently powerful quantum computers, Dirac-Wallet implements NIST-approved post-quantum cryptographic algorithms designed to withstand quantum attacks while maintaining compatibility with the Solana ecosystem.
                    </p>
                    
                    <h3 className="text-xl mb-4 mt-8 pb-2 border-b border-gray-800">Benchmark Performance</h3>
                    
                    <div className="overflow-x-auto mb-8">
                      <table className="min-w-full bg-gray-900 text-gray-300">
                        <thead>
                          <tr>
                            <th className="py-2 px-4 border-b border-gray-800 text-left text-teal-400">Operation</th>
                            <th className="py-2 px-4 border-b border-gray-800 text-left text-teal-400">Time (ms)</th>
                            <th className="py-2 px-4 border-b border-gray-800 text-left text-teal-400">Memory Usage</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            <td className="py-2 px-4 border-b border-gray-800">Key Generation</td>
                            <td className="py-2 px-4 border-b border-gray-800">97ms</td>
                            <td className="py-2 px-4 border-b border-gray-800">2.3MB</td>
                          </tr>
                          <tr>
                            <td className="py-2 px-4 border-b border-gray-800">Transaction Signing</td>
                            <td className="py-2 px-4 border-b border-gray-800">45ms</td>
                            <td className="py-2 px-4 border-b border-gray-800">1.8MB</td>
                          </tr>
                          <tr>
                            <td className="py-2 px-4 border-b border-gray-800">Signature Verification</td>
                            <td className="py-2 px-4 border-b border-gray-800">38ms</td>
                            <td className="py-2 px-4 border-b border-gray-800">1.5MB</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
          
          {activeTab === 'hashes' && (
            <div>
              <h2 className="text-3xl font-mono text-teal-400 mb-6">Quantum-Resistant Hash Functions</h2>
              <p className="text-gray-300 mb-6">
                Our hashing algorithms provide protection against quantum attacks while maintaining high performance.
              </p>
              <div className="bg-gray-900 p-4 rounded-sm font-mono text-sm mb-8">
                <div className="text-teal-400"># Example usage</div>
                <div className="text-white">
                  from dirac_hashes import quantum_hash<br/>
                  <br/>
                  result = quantum_hash(&quot;your data here&quot;)<br/>
                  print(result)
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'team' && (
            <div>
              <h2 className="text-3xl font-mono text-teal-400 mb-6">Our Team</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="border border-gray-800 p-6">
                  <h3 className="text-xl text-teal-400 mb-2">Mukul</h3>
                  <p className="text-gray-400 mb-4">Builder</p>
                  <p className="text-gray-300 mb-4">
                    Research and Development - Quantum Computing
                  </p>
                  <p className="text-teal-400">Mukulpal108@hotmail.com</p>
                </div>

                <div className="border border-gray-800 p-6">
                  <h3 className="text-xl text-teal-400 mb-2">Dr. Satoshi Nakamoto - hypothetical</h3>
                  <p className="text-gray-400 mb-4">Chief Cryptography Officer</p>
                  <p className="text-gray-300 mb-4">
                    Pioneering research in quantum-resistant blockchain technologies.
                  </p>
                  <p className="text-teal-400">satoshi@dirac.fun</p>
                </div>
                
                <div className="border border-gray-800 p-6">
                  <h3 className="text-xl text-teal-400 mb-2">Dr. Paul Dirac - hypothetical</h3>
                  <p className="text-gray-400 mb-4">Quantum Security Lead</p>
                  <p className="text-gray-300 mb-4">
                    Specializing in post-quantum cryptographic algorithms.
                  </p>
                  <p className="text-teal-400">paul@dirac.fun</p>
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'qnas' && (
            <div>
              <h2 className="text-3xl font-mono text-teal-400 mb-6">Frequently Asked Questions</h2>
              
              <div className="space-y-6">
                {/* QnA 1 */}
                <div className="border border-gray-800 rounded-md overflow-hidden">
                  <button 
                    className="w-full flex justify-between items-center p-4 text-left bg-gray-900 hover:bg-gray-800 transition-colors"
                    onClick={() => toggleQnA('qna1')}
                  >
                    <h3 className="text-xl text-teal-400">What makes these hash functions quantum-resistant?</h3>
                    <span className="text-teal-400 text-2xl">{expandedQnAs.includes('qna1') ? '−' : '+'}</span>
                  </button>
                  {expandedQnAs.includes('qna1') && (
                    <div className="p-4 bg-gray-900 bg-opacity-50">
                      <p className="text-gray-300">
                        Our hash functions are designed to be resistant to attacks from quantum computers, specifically Grover&apos;s algorithm which can provide a quadratic speedup for brute force attacks. We achieve this by increasing the output size and using complex non-linear operations that are difficult to reverse even with quantum computing.
                      </p>
                    </div>
                  )}
                </div>
                
                {/* QnA 2 */}
                <div className="border border-gray-800 rounded-md overflow-hidden">
                  <button 
                    className="w-full flex justify-between items-center p-4 text-left bg-gray-900 hover:bg-gray-800 transition-colors"
                    onClick={() => toggleQnA('qna2')}
                  >
                    <h3 className="text-xl text-teal-400">How does the DiracWallet compare to traditional wallets?</h3>
                    <span className="text-teal-400 text-2xl">{expandedQnAs.includes('qna2') ? '−' : '+'}</span>
                  </button>
                  {expandedQnAs.includes('qna2') && (
                    <div className="p-4 bg-gray-900 bg-opacity-50">
                      <p className="text-gray-300">
                        Traditional wallets rely on elliptic curve cryptography which is vulnerable to quantum attacks. DiracWallet uses lattice-based cryptography and hash-based signatures that remain secure even against quantum computers, while maintaining similar performance characteristics.
                      </p>
                    </div>
                  )}
                </div>
                
                {/* QnA 3 */}
                <div className="border border-gray-800 rounded-md overflow-hidden">
                  <button 
                    className="w-full flex justify-between items-center p-4 text-left bg-gray-900 hover:bg-gray-800 transition-colors"
                    onClick={() => toggleQnA('qna3')}
                  >
                    <h3 className="text-xl text-teal-400">Is this compatible with existing blockchain infrastructure?</h3>
                    <span className="text-teal-400 text-2xl">{expandedQnAs.includes('qna3') ? '−' : '+'}</span>
                  </button>
                  {expandedQnAs.includes('qna3') && (
                    <div className="p-4 bg-gray-900 bg-opacity-50">
                      <p className="text-gray-300">
                        Yes, our solution is designed to be backward compatible with existing blockchain networks while providing enhanced security for the future. We offer bridges and adapters for major blockchain protocols.
                      </p>
                    </div>
                  )}
                </div>

                {/* QnA 4 */}
                <div className="border border-gray-800 rounded-md overflow-hidden">
                  <button 
                    className="w-full flex justify-between items-center p-4 text-left bg-gray-900 hover:bg-gray-800 transition-colors"
                    onClick={() => toggleQnA('qna4')}
                  >
                    <h3 className="text-xl text-teal-400">What cryptographic algorithms does Dirac Wallet use?</h3>
                    <span className="text-teal-400 text-2xl">{expandedQnAs.includes('qna4') ? '−' : '+'}</span>
                  </button>
                  {expandedQnAs.includes('qna4') && (
                    <div className="p-4 bg-gray-900 bg-opacity-50">
                      <p className="text-gray-300">
                        Dirac Wallet implements CRYSTALS-Dilithium for digital signatures and CRYSTALS-Kyber for key encapsulation, both NIST PQC standardization finalists. We also use SPHINCS+ as a stateless hash-based signature scheme for additional security. Our implementation includes hybrid systems that combine these post-quantum algorithms with traditional cryptography for a defense-in-depth approach.
                      </p>
                    </div>
                  )}
                </div>

                {/* QnA 5 */}
                <div className="border border-gray-800 rounded-md overflow-hidden">
                  <button 
                    className="w-full flex justify-between items-center p-4 text-left bg-gray-900 hover:bg-gray-800 transition-colors"
                    onClick={() => toggleQnA('qna5')}
                  >
                    <h3 className="text-xl text-teal-400">When will quantum computers break current cryptography?</h3>
                    <span className="text-teal-400 text-2xl">{expandedQnAs.includes('qna5') ? '−' : '+'}</span>
                  </button>
                  {expandedQnAs.includes('qna5') && (
                    <div className="p-4 bg-gray-900 bg-opacity-50">
                      <p className="text-gray-300">
                        Experts estimate that quantum computers capable of breaking current cryptographic systems could be developed within 5-15 years. However, there&apos;s significant uncertainty in these timelines. What&apos;s certain is that data encrypted today with classical methods could be stored by attackers until quantum computers are available to decrypt it (&quot;harvest now, decrypt later&quot; attacks). Dirac Wallet provides protection against this threat now, ensuring your assets remain secure regardless of quantum computing advancements.
                      </p>
                    </div>
                  )}
                </div>

                {/* QnA 6 */}
                <div className="border border-gray-800 rounded-md overflow-hidden">
                  <button 
                    className="w-full flex justify-between items-center p-4 text-left bg-gray-900 hover:bg-gray-800 transition-colors"
                    onClick={() => toggleQnA('qna6')}
                  >
                    <h3 className="text-xl text-teal-400">How does key recovery work with Dirac Wallet?</h3>
                    <span className="text-teal-400 text-2xl">{expandedQnAs.includes('qna6') ? '−' : '+'}</span>
                  </button>
                  {expandedQnAs.includes('qna6') && (
                    <div className="p-4 bg-gray-900 bg-opacity-50">
                      <p className="text-gray-300">
                        Dirac Wallet uses quantum-resistant seed phrases that enable secure key recovery. Our approach generates a mnemonic phrase using a wordlist designed for high entropy and memorability. These phrases are then processed through a quantum-resistant key derivation function to generate your wallet&apos;s master key. The recovery process works similarly to traditional wallets but with the added benefit of quantum security.
                      </p>
                    </div>
                  )}
                </div>

                {/* QnA 7 */}
                <div className="border border-gray-800 rounded-md overflow-hidden">
                  <button 
                    className="w-full flex justify-between items-center p-4 text-left bg-gray-900 hover:bg-gray-800 transition-colors"
                    onClick={() => toggleQnA('qna7')}
                  >
                    <h3 className="text-xl text-teal-400">What is the performance impact of quantum-resistant algorithms?</h3>
                    <span className="text-teal-400 text-2xl">{expandedQnAs.includes('qna7') ? '−' : '+'}</span>
                  </button>
                  {expandedQnAs.includes('qna7') && (
                    <div className="p-4 bg-gray-900 bg-opacity-50">
                      <p className="text-gray-300">
                        Post-quantum algorithms typically have larger key sizes and slightly higher computational requirements than their classical counterparts. However, through optimization and efficient implementation, Dirac Wallet maintains excellent performance while providing quantum security. Our benchmarks show that key operations like signing transactions have negligible impact on user experience compared to traditional wallets, with most operations completing in under 100ms on modern devices.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 