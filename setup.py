import setuptools

version = "1.2.2"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fastapi_lazy",
    version=version,
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
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "fastapi",
        "databases",
        "motor",
        "pyjwt",
        "aioredis==2.0.0",
        "email-validator",
    ],
)
