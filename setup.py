from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dirac-wallet",
    version="0.1.3",
    description="Quantum-resistant Solana wallet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Dirac Labs",
    author_email="Mukulkumar2027@gmail.com",
    url="https://github.com/mk0dz/dirac-wallet",
    packages=find_packages(),
    install_requires=[
        "solana>=0.25.0",
        "solders>=0.26.0",
        "click>=8.0.0",
        "pyyaml>=6.0",
        "pycryptodome>=3.17.0",
        "python-dotenv>=1.0.0",
        "base58>=2.1.0",
        "aiohttp>=3.8.0", 
        "asyncio>=3.4.3",
        "rich>=13.0.0",
        "cryptography>=41.0.0",
        "psutil>=5.9.0",
        "matplotlib>=3.5.0",
        "numpy>=1.20.0",
        "dirac-hashes",
    ],
    entry_points={
        "console_scripts": [
            "dirac-wallet=dirac_wallet.cli.commands:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Development Status :: 4 - Beta",
    ],
    keywords="solana, blockchain, cryptocurrency, quantum, wallet, post-quantum, cryptography",
    python_requires=">=3.8",
    include_package_data=True,
    project_urls={
        "Bug Reports": "https://github.com/mk0dz/dirac-wallet/issues",
        "Source": "https://github.com/mk0dz/dirac-wallet",
        "Documentation": "https://crypto.dirac.fun",
    },
)