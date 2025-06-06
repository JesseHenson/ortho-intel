from setuptools import setup, find_packages

setup(
    name="orthopedic-competitive-intelligence",
    version="1.0.0",
    description="AI-powered competitive intelligence for orthopedic device manufacturers",
    packages=find_packages(),
    install_requires=[
        "langgraph>=0.2.0",
        "langchain>=0.2.0", 
        "langchain-community>=0.2.0",
        "langchain-openai>=0.1.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "streamlit>=1.28.0",
        "pydantic>=2.4.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0"
    ],
    python_requires=">=3.9",
    author="Your Name",
    author_email="your.email@example.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "Programming Language :: Python :: 3.9",
    ],
)
