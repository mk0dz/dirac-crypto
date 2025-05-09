'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import MainLayout from '@/components/layout/MainLayout';
import { useWallet } from '@/context/WalletContext';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';

// Define the form schema
const sendFormSchema = z.object({
  recipient: z.string().min(32, 'Please enter a valid Solana address'),
  amount: z.string().refine(
    (val) => !isNaN(parseFloat(val)) && parseFloat(val) > 0,
    {
      message: 'Amount must be a positive number',
    }
  ),
  memo: z.string().optional(),
});

type SendFormValues = z.infer<typeof sendFormSchema>;

export default function SendPage() {
  const { walletState, signTransaction } = useWallet();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [transactionHash, setTransactionHash] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  
  const { register, handleSubmit, formState: { errors } } = useForm<SendFormValues>({
    resolver: zodResolver(sendFormSchema),
    defaultValues: {
      recipient: '',
      amount: '',
      memo: '',
    },
  });
  
  const onSubmit = async (data: SendFormValues) => {
    if (!walletState.isConnected || !walletState.address) {
      setError('Wallet not connected');
      return;
    }
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      // For a real implementation, we would:
      // 1. Create a transaction
      // 2. Sign it with the wallet
      // 3. Submit it to the blockchain
      const mockTransaction = {
        sender: walletState.address,
        recipient: data.recipient,
        amount: parseFloat(data.amount),
        memo: data.memo || '',
        timestamp: new Date().toISOString(),
      };
      
      const signature = await signTransaction(mockTransaction);
      
      if (signature) {
        setTransactionHash(signature);
        
        // In a real implementation, we would submit the transaction to the network
        // For now, just simulate a successful transaction
        setTimeout(() => {
          setIsSubmitting(false);
        }, 1000);
      } else {
        throw new Error('Failed to sign transaction');
      }
    } catch (err: any) {
      console.error('Error sending transaction:', err);
      setError(err.message || 'Failed to send transaction');
      setIsSubmitting(false);
    }
  };
  
  return (
    <MainLayout>
      <div className="max-w-lg mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Send SOL</h1>
        
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
                  Please connect your wallet to send SOL
                </p>
              </div>
            </div>
          </div>
        ) : transactionHash ? (
          <div className="bg-green-50 border-l-4 border-green-400 p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-green-700">
                  Transaction sent successfully!
                </p>
                <p className="text-sm text-green-700 mt-1">
                  <span className="font-medium">Transaction hash:</span> {transactionHash}
                </p>
              </div>
            </div>
          </div>
        ) : null}
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <Input
            label="Recipient Address"
            placeholder="Enter recipient Solana address"
            {...register('recipient')}
            error={errors.recipient?.message}
            fullWidth
            disabled={!walletState.isConnected || isSubmitting || !!transactionHash}
          />
          
          <Input
            label="Amount (SOL)"
            placeholder="0.00"
            type="number"
            step="0.000001"
            min="0.000001"
            {...register('amount')}
            error={errors.amount?.message}
            fullWidth
            disabled={!walletState.isConnected || isSubmitting || !!transactionHash}
          />
          
          <Input
            label="Memo (Optional)"
            placeholder="Add a note"
            {...register('memo')}
            error={errors.memo?.message}
            fullWidth
            disabled={!walletState.isConnected || isSubmitting || !!transactionHash}
          />
          
          {error && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}
          
          <div className="flex space-x-4">
            <Button
              type="submit"
              disabled={!walletState.isConnected || isSubmitting || !!transactionHash}
              isLoading={isSubmitting}
              fullWidth
            >
              Send
            </Button>
            
            {transactionHash && (
              <Button
                type="button"
                variant="secondary"
                onClick={() => {
                  setTransactionHash(null);
                  setError(null);
                }}
                fullWidth
              >
                Send Another
              </Button>
            )}
          </div>
        </form>
        
        {walletState.isConnected && (
          <div className="mt-8 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-sm font-medium text-gray-500">Transaction Fee</h3>
            <p className="mt-1 text-sm text-gray-700">0.000005 SOL</p>
            
            <div className="mt-4 flex items-center justify-between">
              <span className="text-sm font-medium text-gray-500">Available Balance:</span>
              <span className="text-sm font-medium text-gray-900">
                {walletState.balance !== null ? `${walletState.balance.toFixed(6)} SOL` : '--'}
              </span>
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
} 