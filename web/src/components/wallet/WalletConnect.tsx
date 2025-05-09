'use client';

import React, { useState } from 'react';
import { useWallet } from '@/context/WalletContext';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';

interface WalletConnectProps {
  onClose?: () => void;
}

const WalletConnect: React.FC<WalletConnectProps> = ({ onClose }) => {
  const { connectWallet, createWallet, walletState } = useWallet();
  const [mode, setMode] = useState<'connect' | 'create'>('connect');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  
  const handleModeSwitch = () => {
    setMode(mode === 'connect' ? 'create' : 'connect');
    setError('');
  };
  
  const validatePassword = (): boolean => {
    if (mode === 'create' && password !== confirmPassword) {
      setError('Passwords do not match');
      return false;
    }
    
    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return false;
    }
    
    return true;
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!validatePassword()) {
      return;
    }
    
    try {
      let success = false;
      
      if (mode === 'connect') {
        success = await connectWallet(password);
        if (!success) {
          setError('Failed to connect wallet. Check your password and try again.');
        }
      } else {
        success = await createWallet(password);
        if (!success) {
          setError('Failed to create wallet. Please try again.');
        }
      }
      
      if (success && onClose) {
        onClose();
      }
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred');
    }
  };
  
  return (
    <div className="p-6 max-w-md mx-auto">
      <h2 className="text-2xl font-bold mb-6">
        {mode === 'connect' ? 'Connect to Wallet' : 'Create New Wallet'}
      </h2>
      
      <form onSubmit={handleSubmit}>
        <Input
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Enter your wallet password"
          fullWidth
          required
          autoFocus
        />
        
        {mode === 'create' && (
          <Input
            label="Confirm Password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirm your password"
            fullWidth
            required
          />
        )}
        
        {error && (
          <div className="mb-4 p-2 bg-red-50 text-red-700 rounded-md text-sm">
            {error}
          </div>
        )}
        
        <div className="mt-6 flex flex-col gap-4">
          <Button
            type="submit"
            fullWidth
            isLoading={walletState.isLoading}
            disabled={walletState.isLoading || !password || (mode === 'create' && !confirmPassword)}
          >
            {mode === 'connect' ? 'Connect' : 'Create Wallet'}
          </Button>
          
          <Button
            type="button"
            variant="outline"
            fullWidth
            onClick={handleModeSwitch}
            disabled={walletState.isLoading}
          >
            {mode === 'connect' ? 'Create a new wallet instead' : 'Connect to existing wallet instead'}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default WalletConnect; 