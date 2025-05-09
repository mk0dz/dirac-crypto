'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { loadWalletModule, getWalletBridge, isWalletModuleLoaded } from '@/lib/pyodide';

// Define wallet state interface
interface WalletState {
  address: string | null;
  isConnected: boolean;
  isLoading: boolean;
  balance: number | null;
  network: string;
  publicKey: string | null;
  isPyodideLoaded: boolean;
}

// Define wallet context interface with state and methods
interface WalletContextType {
  walletState: WalletState;
  connectWallet: (password: string) => Promise<boolean>;
  createWallet: (password: string) => Promise<boolean>;
  disconnectWallet: () => void;
  signTransaction: (transaction: any) => Promise<string | null>;
  refreshBalance: () => Promise<void>;
}

// Create the wallet context with default values
const WalletContext = createContext<WalletContextType>({
  walletState: {
    address: null,
    isConnected: false,
    isLoading: false,
    balance: null,
    network: 'testnet',
    publicKey: null,
    isPyodideLoaded: false,
  },
  connectWallet: async () => false,
  createWallet: async () => false,
  disconnectWallet: () => {},
  signTransaction: async () => null,
  refreshBalance: async () => {},
});

// Define props for the wallet provider component
interface WalletProviderProps {
  children: ReactNode;
}

// Create the wallet provider component
export const WalletProvider: React.FC<WalletProviderProps> = ({ children }) => {
  // Initialize wallet state
  const [walletState, setWalletState] = useState<WalletState>({
    address: null,
    isConnected: false,
    isLoading: true,
    balance: null,
    network: 'testnet',
    publicKey: null,
    isPyodideLoaded: false,
  });

  // Load Pyodide and wallet module on mount
  useEffect(() => {
    const initWalletModule = async () => {
      try {
        setWalletState(prev => ({ ...prev, isLoading: true }));
        await loadWalletModule();
        
        // Check if there's a stored wallet state
        const storedState = localStorage.getItem('walletState');
        if (storedState) {
          const parsedState = JSON.parse(storedState);
          if (parsedState.isConnected) {
            // If there was a connected wallet, we'll need to reconnect
            // For now, just update the UI state
            setWalletState(prev => ({
              ...prev,
              address: parsedState.address,
              isConnected: false, // We'll need to reconnect
              isLoading: false,
              network: parsedState.network || 'testnet',
              isPyodideLoaded: true,
            }));
          } else {
            setWalletState(prev => ({
              ...prev,
              isLoading: false,
              isPyodideLoaded: true,
            }));
          }
        } else {
          setWalletState(prev => ({
            ...prev,
            isLoading: false,
            isPyodideLoaded: true,
          }));
        }
      } catch (error) {
        console.error('Failed to initialize wallet module:', error);
        setWalletState(prev => ({
          ...prev,
          isLoading: false,
          isPyodideLoaded: false,
        }));
      }
    };

    initWalletModule();
  }, []);

  // Save wallet state to localStorage when it changes
  useEffect(() => {
    if (walletState.address || walletState.isConnected) {
      localStorage.setItem('walletState', JSON.stringify({
        address: walletState.address,
        isConnected: walletState.isConnected,
        network: walletState.network,
      }));
    }
  }, [walletState.address, walletState.isConnected, walletState.network]);

  // Connect to an existing wallet
  const connectWallet = async (password: string): Promise<boolean> => {
    setWalletState(prev => ({ ...prev, isLoading: true }));
    
    try {
      if (!isWalletModuleLoaded()) {
        await loadWalletModule();
      }

      const bridge = getWalletBridge();
      const result = bridge.unlock_wallet(password);
      
      if (result.success) {
        const info = result.info;
        setWalletState({
          address: info.address,
          isConnected: true,
          isLoading: false,
          balance: null,
          network: 'testnet',
          publicKey: null,
          isPyodideLoaded: true,
        });
        
        // Fetch the balance
        await refreshBalance();
        
        return true;
      } else {
        setWalletState(prev => ({ ...prev, isLoading: false }));
        throw new Error(result.error || 'Failed to unlock wallet');
      }
    } catch (error) {
      console.error('Failed to connect wallet:', error);
      setWalletState(prev => ({ ...prev, isLoading: false }));
      return false;
    }
  };

  // Create a new wallet
  const createWallet = async (password: string): Promise<boolean> => {
    setWalletState(prev => ({ ...prev, isLoading: true }));
    
    try {
      if (!isWalletModuleLoaded()) {
        await loadWalletModule();
      }

      const bridge = getWalletBridge();
      const result = bridge.create_wallet(password);
      
      setWalletState({
        address: result.address,
        isConnected: true,
        isLoading: false,
        balance: 0,
        network: 'testnet',
        publicKey: null,
        isPyodideLoaded: true,
      });
      
      return true;
    } catch (error) {
      console.error('Failed to create wallet:', error);
      setWalletState(prev => ({ ...prev, isLoading: false }));
      return false;
    }
  };

  // Disconnect the wallet
  const disconnectWallet = () => {
    // Clear local storage
    localStorage.removeItem('walletState');
    
    setWalletState({
      address: null,
      isConnected: false,
      isLoading: false,
      balance: null,
      network: 'testnet',
      publicKey: null,
      isPyodideLoaded: walletState.isPyodideLoaded,
    });
  };

  // Sign a transaction
  const signTransaction = async (transaction: any): Promise<string | null> => {
    try {
      if (!walletState.isConnected) {
        throw new Error('Wallet not connected');
      }

      if (!isWalletModuleLoaded()) {
        await loadWalletModule();
      }

      const bridge = getWalletBridge();
      const result = bridge.sign_transaction(transaction, 'password'); // In a real app, we'd need to get the password
      
      if (result.success) {
        return result.signature;
      } else {
        throw new Error(result.error || 'Failed to sign transaction');
      }
    } catch (error) {
      console.error('Failed to sign transaction:', error);
      return null;
    }
  };

  // Refresh the wallet balance
  const refreshBalance = async (): Promise<void> => {
    if (!walletState.address) return;
    
    try {
      const response = await fetch(`/api/wallet/balance/${walletState.address}`);
      
      if (!response.ok) {
        // If the API isn't available, use mock data
        setWalletState(prev => ({
          ...prev,
          balance: 1.5, // Mock balance
        }));
        return;
      }
      
      const data = await response.json();
      
      setWalletState(prev => ({
        ...prev,
        balance: data.balance,
      }));
    } catch (error) {
      console.error('Failed to refresh balance:', error);
      // If the API isn't available, use mock data
      setWalletState(prev => ({
        ...prev,
        balance: 1.5, // Mock balance
      }));
    }
  };

  // Create the context value
  const contextValue: WalletContextType = {
    walletState,
    connectWallet,
    createWallet,
    disconnectWallet,
    signTransaction,
    refreshBalance,
  };

  return (
    <WalletContext.Provider value={contextValue}>
      {children}
    </WalletContext.Provider>
  );
};

// Create a hook for using the wallet context
export const useWallet = () => useContext(WalletContext);

export default WalletContext; 