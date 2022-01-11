import setuptools 
  
with open("README.md", "r") as fh: 
    long_description = fh.read()
  
setuptools.setup( 
    name="pygame_easy_menu", 

    version="0.0.1", 
  
    
    author="Paul Mairesse",
    author_email="paul.mairesse@free.fr", 

    long_description=long_description, 
    long_description_content_type="text/markdown",
    
    packages=setuptools.find_packages(),
  
    license="MIT", 

    classifiers=[ 
        "Programming Language :: Python :: 3", 
        "License :: OSI Approved :: MIT License", 
        "Operating System :: OS Independent", 
    ], 
) 
