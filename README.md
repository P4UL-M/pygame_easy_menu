# Pygame easy menu :

## Project description

### table of content

### disclaimer
This package is free of uses, modifications for any project.

### why ?
If you want to implement menus in your pygame app in python without recoding every classic widgets, this is for you. Pygame_easy_menu allow you to link your windows to a menu_manager that you can toggle or not. It will then allow you to add widget to every menu with pre-code functions.

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

menu_manager = Menu_Manager(name="MySuperGame", size=Vector2(1000,800), background=BG)
```

link the library to an already existing window :
```python
from pygame_easy_menu import *
from pygame_easy_menu.tools import BG # a free background image for your tests

"""
[...] your previous code
"""

menu_manager = Menu_Manager(window=win, background=BG) # win is your pygame window
```

### add menu

to add a menu you juste need to create it with the Menu class and it will automatically be added to your menu manager. To select the menu at screen of the menu manager, you need to store it in the ``actual_menu`` attribute. Every time a new menu is store in ``actual_menu`` the setup fonction of the menu will be executed.

```python
# to add a menu :
principal = Menu("principale")
# you can also select a specific background for a menu
second = Menu("second",background="myimage.png")

menu_manager.actual_menu = principal #this will change the actual menu of your game, if your menu manager is running this attribute can't be empty.
```

To edit the setup function of a menu you need to use the decorator set_setup add pass any function under it, the decorator will update the setup function automatically.
```python
@principal.set_setup
def setup():
    # you can name your function like you want
    # your stuff here
```

### add sprite
To add a sprite to a menu you need to declare a function where you return a sprite based class and put it under the ``add_sprite`` decorator of you menu. If you want to create your own sprite class you need to pass the ``sprite`` class in its inherance.

```python
@principal.add_sprite
def back_button():
    _button = Button(
        name="mybutton",
        path= "myimageofbutton.png"  
    )

    """
    put the config of your button here
    """

    return _button
```

there currently are the following widget : AlertBox,InputBox,Button,textZone,sprite

### run the menu_manager
To run the you need to start the ``menu_manager.run()`` function, this function will run until ``menu_manager.running`` is False. You need to put this function at the end of your code or in a function if you don't want your code to be stop.

## menu functions and parameters

### child and parents

Every menu can be link with other menu by parent/child system. This way you can retreive a menu either with your global variable or by menu's functions.
One menu can have multiple children but only one parent. When you define your Menu you can also pass name of children or future children, or the name of its parent. Warning if you say that a menu is the children of a parent menu, the name wont be automatically add to the list of the other instance (for now).

Add a child :
```python
principal = Menu("principal",childs=["second"])
```

Add a parent :
```python
second = Menu("second",parent="principal",childs="third")
```
// childs parameter can be either a list or a string.


You can then when the menu_manager is running get one child of your menu or its parent.

Get a child : Menu.get_child(self,child_name)
```python
mychilds = second.get_child("third")
```

Get all children (return a generator) : Menu.get_childs(self)
```python
# return a generator you can itter in
for child in second.get_childs():
    """
    your code here
    """

# to transform to a list
mychild = [child for child in second.get_childs()]
```

Get the parent : Menu.get_parent(self)
```python
mychilds = second.get_parent()
```

### sprites

Once you add a sprite to a Menu you can then access it with either the list of sprite or with the ``get_sprite`` function.

Get a sprite : Menu.get_sprite(self,name)
```python
_button = second.get_sprite("mybutton")

# you can also itter in the list directly
for _button in second.sprites:
    """
    your code here
    """
```

## sprite functions and parameters

## exemple code


# a faire

ajouter icon par défaut dans le module pour exemple code
finir read me
how to run the menu