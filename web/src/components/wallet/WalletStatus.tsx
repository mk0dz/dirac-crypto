import React from 'react';
import { useWallet } from '@/context/WalletContext';
import Button from '@/components/ui/Button';

interface WalletStatusProps {
  onConnectClick?: () => void;
}

const WalletStatus: React.FC<WalletStatusProps> = ({ onConnectClick }) => {
  const { walletState, disconnectWallet, refreshBalance } = useWallet();
  const { isConnected, address, balance, isLoading, network } = walletState;
  
  const formatAddress = (addr: string | null): string => {
    if (!addr) return '';
    return `${addr.substring(0, 4)}...${addr.substring(addr.length - 4)}`;
  };
  
  const handleRefresh = () => {
    refreshBalance();
  };
  
  if (!isConnected) {
    return (
      <div className="flex items-center">
        <Button
          onClick={onConnectClick}
          size="sm"
          isLoading={isLoading}
        >
          Connect Wallet
        </Button>
      </div>
    );
  }
  
  return (
    <div className="flex items-center space-x-4">
      <div className="hidden md:block bg-blue-50 py-1 px-3 rounded-full text-sm text-blue-700">
        {network}
      </div>
      
      <div className="px-3 py-1 rounded-md bg-gray-100">
        <div className="flex items-center">
          <span className="text-sm font-medium">
            {formatAddress(address)}
          </span>
        </div>
      </div>
      
      <div className="px-3 py-1 rounded-md bg-green-50 text-green-700">
        <div className="flex items-center">
          <span className="text-sm font-medium">
            {balance !== null ? `${balance.toFixed(4)} SOL` : '--'}
          </span>
          <button 
            onClick={handleRefresh}
            className="ml-2 text-gray-400 hover:text-gray-600 focus:outline-none"
            title="Refresh balance"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>
      
      <Button
        variant="outline"
        size="sm"
        onClick={disconnectWallet}
      >
        Disconnect
      </Button>
    </div>
  );
};

export default WalletStatus; 