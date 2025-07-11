from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="claude-multiagent-framework",
    version="1.0.0",
    author="Claude MultiAgent Team",
    description="Мультиагентный фреймворк для AI-проектов",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/USERNAME/Claude-MultiAgent-Framework",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "click>=8.0.0",
        "rich>=10.0.0",
        "pydantic>=1.8.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "aiofiles>=0.7.0",
        "python-dotenv>=0.19.0",
        "sqlalchemy>=1.4.0",
        "alembic>=1.7.0",
        "scikit-learn>=1.0.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0"
    ],
    entry_points={
        "console_scripts": [
            "claude-framework=claude_framework_cli:main",
        ],
    },
)
