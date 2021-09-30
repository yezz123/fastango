import setuptools

ver = "1.0.0"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fastapi-lazy",
    version=ver,
    author="Yezz123",
    author_email="yasserth19@gmail.com",
    description="Utilities that you use in various projects made in FastAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yezz123/fastapi-lazy",
    include_package_data=True,
    project_urls={"Bug Tracker": "https://github.com/yezz123/fastapi-lazy/issues",},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Unlicense",
        "Operating System :: OS Independent",
    ],
    install_requires=["fastapi", "databases", "motor", "pyjwt", "aioredis==2.0.0"],
    package_dir={"": "fastapi-lazy"},
    packages=setuptools.find_packages(where="fastapi-lazy"),
    python_requires=">=3.7",
)
