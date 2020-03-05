from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
  name = "nmcog",
  packages = [
      "nmcog",
      "nmcog.spinnaker",
      "nmcog.spinnaker.discriminate",
      "nmcog.spinnaker.associate",
      "nmcog.spinnaker.specialfunctions.neal",
      ],
  version = "0.0.1",
  license="BSD Clause-3",
  description = "Module (Library) for simulation cognitive models in Neuromorphic hardwares",
  long_description = long_description,
  long_description_content_type = "text/markdown",
  author = "Lungsi Ngwua",
  author_email = "lungsi.ngwua@cnrs.fr",
  url = "https://github.com/myHBPwork/NMCog",
  download_url = "https://github.com/NMCog/archive/v0.0.1.tar.gz",
  keywords = ["NEUROMORPHIC", "COGNITIVE", "SPIKING", "NEURAL NETWORK", "SPINNAKER", "BRAINSCALES"],
  install_requires=[
          "numpy",
          "quantities",
          "spynnaker8",
      ],
  classifiers=[
    "Development Status :: 3 - Alpha",      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    "Intended Audience :: Developers",      # Define that your audience are developers
    "Topic :: Software Development :: Build Tools",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
  ],
  python_requires = ">=3.5",
)
