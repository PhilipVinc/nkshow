from setuptools import setup, find_packages

BASE_DEPENDENCIES = ["numpy~=1.18", "netket", "rich", "textual", "pyfiglet", "watchdog"]

DEV_DEPENDENCIES = [
    "pytest>=6",
]

setup(
    name="nkreader",
    author="Filippo Vicentini",
    url="http://github.com/PhilipVinc/numba4jax",
    author_email="filippovicentini@gmail.com",
    license="MIT",
    description="Usa numba in jax-compiled kernels.",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
    ],
    packages=find_packages(),
    install_requires=BASE_DEPENDENCIES,
    python_requires=">=3.7",
    extras_require={"dev": DEV_DEPENDENCIES},
    entry_points={
        "console_scripts": [
            "nkshow = nkshow:run",
        ],
    },
)
