import { NextRequest, NextResponse } from 'next/server';

// Backend API URL
const API_URL = process.env.BACKEND_API_URL || 'http://localhost:8000';

/**
 * Generic handler for proxying requests to the backend API
 */
async function proxyToBackend(req: NextRequest, endpoint: string) {
  try {
    const url = `${API_URL}/api/network/${endpoint}`;
    
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
 * GET handler for network endpoints
 */
export async function GET(req: NextRequest) {
  const { pathname } = new URL(req.url);
  
  // Extract the endpoint from the pathname
  const path = pathname.replace('/api/network/', '');
  
  if (path === 'status') {
    return proxyToBackend(req, 'status');
  } else if (path === 'blockhash') {
    return proxyToBackend(req, 'blockhash');
  } else if (path.startsWith('info/')) {
    const network = path.replace('info/', '');
    return proxyToBackend(req, `info/${network}`);
  } else {
    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  }
} 