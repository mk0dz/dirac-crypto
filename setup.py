from setuptools import setup, find_packages

setup(
    name="dirac-wallet",
    version="0.1.0",
    description="Quantum-resistant Solana wallet",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "solana>=0.25.0",
        "click>=8.0.0",
        "pyyaml>=6.0",
        "pycryptodome>=3.17.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "dirac-wallet=dirac_wallet.cli.commands:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)