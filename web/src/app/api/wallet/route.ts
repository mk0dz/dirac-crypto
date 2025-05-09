import { NextRequest, NextResponse } from 'next/server';

// Backend API URL
const API_URL = process.env.BACKEND_API_URL || 'http://localhost:8000';

/**
 * Generic handler for proxying requests to the backend API
 */
async function proxyToBackend(req: NextRequest, endpoint: string) {
  try {
    const url = `${API_URL}/api/wallet/${endpoint}`;
    
    // Clone the request with the new URL
    const backendReq = new Request(url, {
      method: req.method,
      headers: req.headers,
      body: req.method !== 'GET' && req.method !== 'HEAD' ? await req.text() : undefined,
    });
    
    // Forward the request to the backend
    const response = await fetch(backendReq);
    const data = await response.json();
    
    // Return the response from the backend
    return NextResponse.json(data, { status: response.status });
  } catch (error: any) {
    console.error(`Error proxying to ${endpoint}:`, error);
    return NextResponse.json(
      { error: 'Failed to communicate with backend API' },
      { status: 500 }
    );
  }
}

/**
 * GET handler for balance endpoint
 */
export async function GET(req: NextRequest) {
  const { pathname } = new URL(req.url);
  
  // Extract the endpoint from the pathname
  const path = pathname.replace('/api/wallet/', '');
  
  if (path.startsWith('balance/')) {
    const address = path.replace('balance/', '');
    return proxyToBackend(req, `balance/${address}`);
  } else if (path.startsWith('tokens/')) {
    const address = path.replace('tokens/', '');
    return proxyToBackend(req, `tokens/${address}`);
  } else if (path === 'state') {
    return proxyToBackend(req, 'state');
  } else {
    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  }
}

/**
 * POST handler for wallet operations
 */
export async function POST(req: NextRequest) {
  const { pathname } = new URL(req.url);
  
  // Extract the endpoint from the pathname
  const path = pathname.replace('/api/wallet/', '');
  
  if (path === 'create' || path === 'unlock' || path === 'sign') {
    return proxyToBackend(req, path);
  } else {
    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  }
} 