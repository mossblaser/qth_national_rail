from setuptools import setup, find_packages

with open("qth_national_rail/version.py", "r") as f:
    exec(f.read())

setup(
    name="qth_national_rail",
    version=__version__,
    packages=find_packages(),

    # Metadata for PyPi
    url="https://github.com/mossblaser/qth_national_rail",
    author="Jonathan Heathcote",
    description="Add UK rail network train times to Qth.",
    license="GPLv2",
    classifiers=[
        "Development Status :: 3 - Alpha",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",

        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="qth home-automation trains rail",

    # Requirements
    install_requires=["qth>=0.7.0", "zeep>=2.5.0"],

    # Scripts
    entry_points={
        "console_scripts": [
            "qth_national_rail = qth_national_rail:main",
        ],
    }
)
