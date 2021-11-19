import setuptools

__version__ = "1.2.5"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fastapi_lazy",
    version=__version__,
    author="Yasser Tahiri",
    author_email="yasserth19@gmail.com",
    description="Utilities that you use in various projects made in FastAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yezz123/fastapi-lazy",
    packages=setuptools.find_packages(
        exclude=["tests", "tests.*", "*.tests", "*.tests.*"],
    ),
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Framework :: FastAPI",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP :: Session",
    ],
    python_requires=">=3.7",
    install_requires=[
        "fastapi",
        "databases",
        "motor",
        "pyjwt",
        "aioredis==2.0.0",
        "email-validator",
        "passlib",
    ],
)
