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

To use menu in your pygame window you first need to initiate a menu manager, this class will be link to your pygame window and allow you to add menu, activate and desactivate it.

You can then add sprite to your menu and define their function trigger on pygame event.

### link your window or make one

create a new window : 
```python
from pygame_easy_menu import *
from pygame_easy_menu.tools import *
import pygame

pygame.init()

game = Menu_Manager(pygame=pygame, name="MySuperGame", size=Vector2(1000,800), background=BG)
```

link the library to an already existing window :
```python
from pygame_easy_menu import *
from pygame_easy_menu.tools import BG

"""
[...] your previous code
"""

game = Menu_Manager(window=win, background=BG) # win is your pygame window
```

### add menu

to add a menu you juste need to create it with the Menu class and it will automatically be added to your menu manager. To select the menu at screen of the menu manager, you need to store it in the ``actual_menu`` attribute. Every time a new menu is store in ``actual_menu`` the setup fonction of the menu will be executed.

```python
# to add a menu :
principal = Menu("principale",childs=["Play"])
# you can also select a specific background for a menu
second = Menu("second",background="myimage.png")
```

To edit the setup function of a menu you need to use the decorator set_setup add pass any function under it, the decorator will update the setup function automatically.
```python
@principal.set_setup
def setup():
    # you can name your function like you want
    # your stuff here
```

### add sprite

### sprite functions and parameters

## exemple code


# a faire

ajouter icon par défaut dans le module pour exemple code
finir read me