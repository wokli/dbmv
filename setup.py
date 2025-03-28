from setuptools import setup, find_packages

setup(
    name="dbmv",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "click",
        "boto3",
    ],
    entry_points={
        'console_scripts': [
            'dbmv=dbmv.cli:main',
        ],
    },
    author="Alex Nikolaev",
    author_email="wokli@users.noreply.github.com",
    description="A tool to copy PostgreSQL databases between servers and S3",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/wokli/dbmv",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 