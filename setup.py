from setuptools import setup, find_packages

setup(
    name="dirac-wallet",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "solana>=0.29.2",
        "solders>=0.18.1",
        "typer>=0.9.0",
        "rich>=13.4.2",
        "matplotlib>=3.7.1",
        "pandas>=2.0.2",
        "base58>=2.1.0",
    ],
    entry_points={
        "console_scripts": [
            "dirac-wallet=dirac.__main__:main",
        ],
    },
    author="Dirac Crypto Team",
    author_email="info@diracsystems.io",
    description="Quantum-resistant cryptocurrency wallet for Solana",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/diracsystems/dirac-crypto",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
) 