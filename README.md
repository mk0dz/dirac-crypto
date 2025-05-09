# Dirac Wallet - Quantum-Resistant Cryptocurrency Wallet

Dirac Wallet is a quantum-resistant cryptocurrency wallet designed to protect your digital assets against current and future quantum computing threats while maintaining compatibility with the Solana blockchain.

## Features

- **Quantum-Resistant Cryptography**: Built with Dilithium signatures that are resistant to quantum computer attacks
- **Solana Compatibility**: Works seamlessly with the Solana blockchain
- **Enhanced Security**: Robust encryption, secure key storage, and protection against various attacks
- **User-Friendly Interface**: Modern web-based UI for easy management of your crypto assets
- **Open-Source**: Transparent and community-auditable codebase

## Project Structure

The project is divided into three main components:

1. **Dirac Wallet Core**: Python-based implementation of the quantum-resistant wallet functionality
2. **Web Backend**: FastAPI server providing API endpoints for wallet operations
3. **Web Frontend**: Next.js web application with React components and Tailwind CSS

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

### Installation

#### Core Wallet & Backend

```bash
# Clone the repository
git clone https://github.com/yourusername/dirac-crypto.git
cd dirac-crypto

# Set up Python virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install backend dependencies
cd web-backend
pip install -r requirements.txt
```

#### Web Frontend

```bash
# Navigate to the web directory
cd ../web

# Install dependencies
npm install
```

### Running the Application

#### Backend Server

```bash
cd web-backend
python main.py
```

The API server will be available at http://localhost:8000.

#### Frontend Development Server

```bash
cd web
npm run dev
```

The web application will be available at http://localhost:3000.

## Usage

1. **Create a Wallet**: Generate a new quantum-resistant wallet with a secure password
2. **Send SOL**: Transfer SOL to other Solana addresses
3. **Receive SOL**: Get your wallet address to receive SOL from others
4. **View Balance**: Check your current SOL balance
5. **Security Information**: Learn about the quantum-resistant features protecting your assets

## Development Phases

### Phase 1: Core Wallet Implementation (Completed)
- ✅ Basic CLI wallet with create, balance, and info commands
- ✅ Implementation of Dilithium signatures
- ✅ Secure storage of wallet credentials

### Phase 2: Security & Testing (Completed)
- ✅ Enhanced security features (secure storage, high entropy, memory safety)
- ✅ Comprehensive security testing
- ✅ Performance benchmarking
- ✅ Penetration testing

### Phase 3: UI Development (Current)
- 🔄 Web-based user interface with Next.js
- 🔄 API backend for wallet operations
- 🔄 WebAssembly bridge for running wallet operations in the browser
- 🔄 Deployment to Vercel

## Security Considerations

The wallet implements several security measures:

- **Post-quantum cryptography**: Using Dilithium signatures to protect against quantum computer attacks
- **Secure storage**: PBKDF2 key derivation and Fernet encryption for protecting private keys
- **Key entropy validation**: Ensuring high-quality randomness in key generation
- **Password strength requirements**: Comprehensive password security checks
- **Memory safety**: Secure memory handling to prevent data leakage

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NIST for their post-quantum cryptography standardization
- The Solana community for their blockchain infrastructure
- The Python and JavaScript communities for their excellent libraries and tools 