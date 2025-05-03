from setuptools import setup, find_packages

setup(
    name="dirac-wallet",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "solana>=0.30.2",
        "solders>=0.18.0",
        "borsh==0.0.1",
        "pynacl>=1.5.0",
        "typer>=0.9.0",
        "rich>=13.4.2",
        "matplotlib>=3.5.0",
        "numpy>=1.20.0",
    ],
    entry_points={
        "console_scripts": [
            "dirac-wallet=src.cli.wallet_cli:app",
            "dirac-benchmark=src.cli.benchmark_cli:app",
        ],
    },
    python_requires=">=3.7",
    author="Dirac Crypto",
    author_email="info@diraccrypto.com",
    description="Quantum-resistant Solana wallet",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/diraccrypto/dirac-solana-wallet",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
) 