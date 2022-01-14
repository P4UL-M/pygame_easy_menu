# Pygame easy menu :

## Project description

### table of content

### disclaimer

### why ?

### installation

command :
```
python -m pip install pygame_easy_menu
```

## How to use ?

### link your window or make one

create a new window : 
```python
from pygame_easy_menu import *
import pygame

pygame.init()

game = Menu_Manager(pygame=pygame, name="MySuperGame", size=Vector2(1000,800), background="my_image.png")
```

link the library to an already existing window :
```python
from pygame_easy_menu import *

"""
[...] your previous code
"""

game = Menu_Manager(window=win, background="my_image.png") # win is your pygame window
```

### add menu

### add sprite

### exemple code


# a faire

ajouter image/icon par défaut dans le module pour exemple code
finir read me
replace print by logging