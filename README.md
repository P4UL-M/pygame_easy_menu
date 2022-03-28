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
To run the you need to start the ``menu_manager.run()`` function, this function will run until ``menu_manager.running`` is False. You need to put this function at the end of your code or in a function if you don't want your code to be stucked.

You can the stop the manager by calling ``menu_manager.stop()`` if you want to close the menu and launch back the game. You can also completly stop the program by calling ``menu_manager.destroy()``.

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

### Sprite
Each widget is a derivate from the sprite class, those fonctions are in most cases in other widget.

add a sprite : Sprite.add_sprite(self,sprite)
```python
@main_menu.add_sprite
def my_sprite():
    _sprite = Sprite(
        name="my_sprite",
        path="myimage.png",
        manager=menu_manager
    )

    """
    Put your config here
    """

    return _sprite
```

change postion : Sprite.set_positon(pos:Vector2)
```python
_sprite.set_position(Vector2(110,250)) # absolute position
_sprite.set_position(Vector2(0.5,0.33)) # position in percentage of the screen
```

change scale : Sprite.set_scale(pos:Vector2)
```python
_sprite.set_scale(Vector2(110,250)) # absolute scale
_sprite.set_scale(Vector2(0.5,0.33)) # scale in percentage of the previous surface size
```

add function on event : Sprite.Event(_event:pygame.Event)(function)
```python
@_sprite.Event(pygame.QUIT)
def debug_bye(event):
    """
    your code here
    """
```
this function will we executed each time the event pygame.QUIT is raise.

### Button

A Button is a derivate of the sprite class.

Button has the decorator on click : Button.on_click(self,function)
```python
@main_menu.add_sprite
def my_button():
    _button = Button(
        name="mybutton",
        path= "myimageofbutton.png",
        manager=menu_manager
    )

    """
    put the config of your button here
    """

    @_Button.on_click
    def debug(event):
        """
        your code here
        """
    
    return _button
```
this function will we executed each time the button is clicked.

### TextBox

A TextBox is a derivate of the sprite class.

```python
@_textbox.on_change
```

### InputBox

### Alert boox

## exemple code
```python
from pygame_easy_menu import *
from pygame_easy_menu.tools import BG,B_BG

import pygame

pygame.init()

menu_manager = Menu_Manager(name="mygame",size=Vector2(1000,800),background=BG)

main_menu = Menu(name="Main")

@main_menu.add_sprite
def play_button():
    _button = Button(
        name = "Play_Button",
        path = B_BG
    )

    _button.set_position(Vector2(0.5,0.33))

    _button.set_text("Play",padding=0.15)

    @_button.on_click
    def launch():
        print("my game is launch")

    return _button

@main_menu.add_sprite
def exit_button():
    _button = Button(
        name = "Exit_button",
        path = B_BG
    )

    _button.set_position(Vector2(0.5,0.66))

    _button.set_text("Exit",padding=0.15)

    @_button.on_click
    def launch():
        menu_manager.destroy()

    return _button

menu_manager.actual_menu = main_menu

if __name__ == "__main__":
    try:
        menu_manager.run()
    except KeyboardInterrupt:
        menu_manager.destroy()
```

# a faire

ajouter icon par défaut dans le module pour exemple code
finir read me
how to run the menu