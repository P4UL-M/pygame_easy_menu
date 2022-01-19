import pygame as py             # PYGAME
from pygame.locals import *     # PYGAME constant & functions

from sys import exit            # exit script
import textwrap3                 # wrap text automatically

import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')

_window = None
FONT = None

class Vector2:
    """
    class Vecteur 2 dimension pour un stockage des position et range plus facile qu'avec un array tuple
    """
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f'({self.x},{self.y})'

    def __call__(self) -> tuple:
        """return a tuple of the vector"""
        return (self.x,self.y)
        
class Menu_Manager(object):
    """
    class principale de pygame qui gère la fenetre
    """
    def __init__(self,window=None,name=None,size:Vector2=None,background=None,icon=None) -> None:
        """
        initialisation de pygame et de la fenêtre et des variables globales
        """
        py.init()

        if not window and not size:
            raise Exception("You must pass either your window either the size of your new window")

        self.screen:py.Surface = window or py.display.set_mode(size(),0,32)

        if name:
            py.display.set_caption(name)
        if icon:
            py.display.set_icon(icon)

        self.actual_menu:Menu = None
        self.menus:list[Menu] = []
        self.running = False
        # ******** le background devrait etre gérer indivituellement pour les menu en option pour overidecelui là
        if background: 
            try:
                self.background = py.image.load(background).convert() # tuile pour le background
                self.background = py.transform.scale(self.background, (size.x, size.y))
            except FileNotFoundError:
                logging.error("File not found : the background of your menu was not found")
                raise FileNotFoundError
        else:
            self.background = py.Surface(size())
        
        global _window
        _window = self
    
    def __setattr__(self, __name: str, __value):
        super().__setattr__(__name,__value)
        if __name == "actual_menu" and type(__value)==Menu:
            __value.setup()

    def set_font(self,path):
        global FONT
        FONT = path

    def run(self):
        """
        fonction principale du jeu qui gère la fenetre
        """
        self.running = True
        while self.running:
            if self.actual_menu:
                if self.actual_menu.background == None:
                    self.screen.blit(self.background,(0,0))
                else:
                    self.screen.blit(self.actual_menu.background,(0,0))
                self.actual_menu.Update()
            py.display.update()

    def stop(self):
        """
        stop the current thread de la classe
        """
        self.running = False

    def destroy(self):
        """
        Use to stop the local thread
        """
        exit()

class sprite:
    def __init__(self,name,path,isactive,layer):
        self.name = name
        self.file = path
        self.position = Vector2(0,0)
        self.rect = None
        self.layer = layer
        self.isactive = isactive
        
        self.handles = []
        try:
            self.surface:py.Surface = py.image.load(self.file).convert_alpha()
        except FileNotFoundError:
            logging.error(f"File not found : your image for your sprite {self.name} was not found")
            raise FileNotFoundError

        self.scale = Vector2(self.surface.get_width(),self.surface.get_height())
    
    def set_position(self,pos:Vector2,TopLeft=False,parent=None):
        """
        attribue les valeur du vecteur à la position de l'image, si les valeur sont en float alors elle sont considérer comme un multiplicateur
        """
        if TopLeft:
            x,y = pos.x,pos.y
            if type(pos.x)==float:
                if parent:
                    x = int(parent.surface.get_width()*pos.x) + parent.position.x
                else:
                    x = int(_window.screen.get_width()*pos.x)
            if type(pos.y)==float:
                if parent:
                    y = int(parent.surface.get_height()*pos.y) + parent.position.y
                else:
                    y = int(_window.screen.get_height()*pos.y)
        else:
            x = int(pos.x - self.surface.get_width()/2)
            y = int(pos.y - self.surface.get_height()/2)
            if type(pos.x)==float:
                if parent:
                    x = int(parent.surface.get_width()*pos.x - self.surface.get_width()/2) + parent.position.x
                else:
                    x = int(_window.screen.get_width()*pos.x - self.surface.get_width()/2)
            if type(pos.y)==float:
                if parent:
                    y = int(parent.surface.get_height()*pos.y - self.surface.get_height()/2) + parent.position.y
                else:
                    y = int(_window.screen.get_height()*pos.y - self.surface.get_height()/2)
        self.position:Vector2 = Vector2(x,y)
        self.set_rect(Vector2(x,y))
    
    def set_scale(self,sca:Vector2):
        """
        attribue les valeur du vecteur à la taille de l'image, si les valeur sont en float alors elle sont considérer comme un multiplicateur
        """
        x,y = sca.x,sca.y
        if type(sca.x)==float:
            x = int(self.surface.get_width()*sca.x)
        if type(sca.y)==float:
            y = int(self.surface.get_height()*sca.y)
        self.scale = Vector2(x,y)
        self.actualize_scale()

    def actualize_scale(self):
        offset = Vector2(
            x= int(self.position.x - (self.scale.x - self.surface.get_width())/2),
            y= int(self.position.y - (self.scale.y - self.surface.get_height())/2)
        )
        self.set_position(offset,TopLeft=True)
        self.surface = py.transform.scale(self.surface,(self.scale.x,self.scale.y))

    def set_rect(self,coord:Vector2):
        self.rect = self.surface.get_rect(topleft=(coord.x,coord.y))
    
    def Event(self,event):
        """
        Ce décorateur crée une fonction qui ajoute celle ci à la liste des fonctions.
        La fonction passé en décoration n'est executé que si l'évènement est appellé.
        Si l'event passé est nulle alors la fonction est attribué à la fonction Update executé
        juste avant l'affichage
        """
        def decorator(func):
            if event !=None:
                def wrap(_event:py.event.Event,*args, **kwargs):
                    if _event.type == event:
                        return func(_event,*args, **kwargs)
                self.handles.append(wrap)
            else:
                def wrap(*args, **kwargs):
                    if self.isactive:
                        return func(*args,**kwargs)
                setattr(self,"Update",wrap)
            return True
        return decorator

    def draw(self,ecran):
        if self.isactive:
            ecran.blit(self.surface,(self.position.x,self.position.y))

    def Handle(self,*arg,**kargs):
        if self.isactive:
            for func in self.handles:
                func(*arg,**kargs)

    def Update(*args,**kargs): ...

class textZone(sprite):
    """class pour ajouter automatiquement du text"""
    def __init__(self, name, isactive=True,text_color='white', layer=0):
        self.name = name
        self.position = Vector2(0,0)
        self.scale = Vector2(50,50)
        self.rect = None
        self.isactive = isactive
        self.layer = layer
        self.handles = []

        self.surface = py.Surface((self.scale.x,self.scale.y),flags=py.SRCALPHA)

        self.text_color = text_color
        self.FONT_PATH = FONT
        self.FONT = py.font.Font(FONT,36)
        self.text = None
        self.align_center = False

    def set_text(self,text,wrap_lenght=None,align_center=False):
        self.text = text
        self.align_center = align_center

        if wrap_lenght:
            text = ""
            for line in self.text.split("\n"):
                text += "\n" if text else ""
                text += textwrap3.fill(line,wrap_lenght)
            self.text = text
        
        self.render()

    def render(self):
        self.scale = self.get_text_size(self.text)
        self.surface = py.Surface(self.scale(),flags=py.SRCALPHA)

        # calcul positions
        x = 0
        y = 0
        # Blit the text
        for line in self.text.split("\n"):
            txt_surface = self.FONT.render(line, True,self.text_color)
            if self.align_center:
                x = self.surface.get_width()//2 - txt_surface.get_width()//2
            self.surface.blit(txt_surface,(x,y))
            
            y += txt_surface.get_height()

        self.surface = self.surface.convert_alpha()
        self.actualize_scale()
        return self.surface

    def get_text_size(self,text:str=None):
        if text==None:
            text=self.text
        max_text = text.split("\n")[0]
        for line in text.split("\n")[1:]:
            if self.FONT.size(max_text)[0]<self.FONT.size(line)[0]:
                max_text = line
        
        x = self.FONT.size(max_text)[0]
        y = 0

        for line in text.split("\n"):
            y += self.FONT.size(line)[1]

        return Vector2(x,y)

    def set_font(self,name=None,size=36):
        self.FONT = py.font.Font(name,size)
        self.FONT_PATH = name

    def size_to_scale(self,scale:Vector2):
        """size the police size to an max area"""
        _size = self.get_text_size()()
        text_size = 1
        offset = 32

        while offset>=1:
            self.FONT = py.font.Font(self.FONT_PATH,int(text_size + offset))
            _size = self.get_text_size()()
            if _size[0] > scale.x or _size[1] > scale.y:
                offset /= 2
            else:
                text_size += offset

class Button(sprite):
    """
    classe de bouton simple avec méthode rapide pour Event et On_Click
    """
    def __init__(self,name,path,isactive=True,layer=0):
        super().__init__(name,path,isactive,layer)

    def on_click(self,func):
        """
        nouvelle fonction qui n'executera que la fonction en cas de click du boutton
        la nouvelle fonction est ajouté dans la liste des function à executé
        """
        def wrap(_event:py.event.Event,*args,**kargs):   
            if _event.type == py.MOUSEBUTTONUP:
                if self.rect.collidepoint(py.mouse.get_pos()):
                    if self.check_layer():
                        return func(*args,**kargs)
        self.handles.append(wrap)
    
    def check_layer(self):
        for _sprite in _window.actual_menu.sprites:
            if _sprite.isactive:
                if _sprite.rect.collidepoint(py.mouse.get_pos()) and _sprite.layer > self.layer:
                    return False
        else:
            return True

    def set_text(self,text,color="white",padding=0.05):

        self.surface = py.transform.scale(py.image.load(self.file).convert_alpha(),(self.scale.x,self.scale.y))
        
        _text = textZone(
            name=f"textZone_{self.name}",
            text_color=color
        ) 

        _text.set_text(text,align_center=True)  

        _size = Vector2(self.surface.get_width()*(1 - padding*2),self.surface.get_height()*(1 - padding*2)) if type(padding)==float else Vector2(self.surface.get_width() - padding,self.surface.get_height() - padding)
        
        _text.size_to_scale(_size)

        _render = _text.render()

        _pos = (
            self.surface.get_width()//2 - _render.get_width()//2,
            self.surface.get_height()//2 - _render.get_height()//2
            )
         
        self.surface.blit(_render,_pos)

class InputBox(sprite):
    """
    class de InputBox autonome, permet de rentrer du texte facilement
    """
    def __init__(self,name,path,paceHolder='Enter text...',color='black',text_color='grey',alter_text_color="white",max_char=16,isactive=True,layer=0):

        super().__init__(name,path,isactive,layer)

        self.color = Color(color)
        self.text = ''
        self.paceHolder = paceHolder
        self.max_char = max_char
        self.text_color = Color(text_color)
        self.text_color_inactive = Color(text_color)
        self.text_color_active = Color(alter_text_color)

        self.text_size = self.get_text_size()

        self.FONT = py.font.Font(FONT,self.text_size)
        self.txt_surface = self.FONT.render(self.paceHolder, True, self.text_color)
        self.active = False

    def get_text_size(self):
        i = self.surface.get_height()
        temp = py.font.Font(None,i)
        size_temp = temp.size("A"*max(self.max_char,len(self.paceHolder)))
        while int(self.surface.get_height()*0.80)<size_temp[1] or int(self.surface.get_width()*0.9)<size_temp[0]:
            i -=1
            temp = py.font.Font(None,i)
            size_temp = temp.size("A"*max(self.max_char,len(self.paceHolder)))
        return(i)

    def on_enter(self,func):
        """
        Ce décorateur crée une fonction qui ajoute celle ci à la liste des fonctions.
        La fonction passé en décoration n'est executé que si la touche Enter est pressé.
        """
        def wrap(_event,*args, **kwargs):
            if _event.type==KEYDOWN:
                if self.isactive and self.active and _event.key == K_RETURN:
                    return func(*args,**kwargs)
        setattr(self,"Enter_func",wrap)
        return True

    def Handle(self, event:py.event.Event):
        if event.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos): # If the user clicked on the input_box rect.
                # Toggle the active variable.
                self.active = not self.active
                self.text_color = self.text_color_active if self.active else self.text_color_inactive
            else:
                self.active = False
                self.text_color = self.text_color_inactive
        if self.active:
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    self.text = self.text[:-1]
            if event.type == TEXTINPUT:
                    if len(self.text)<self.max_char:
                        self.text += event.text
        self.Enter_func(event)

    def draw(self,ecran):
        render = self.surface.copy()
        
        self.txt_surface = self.FONT.render(self.text or self.paceHolder, True, self.text_color)

        # calcul positions
        x = int(render.get_width()*0.05)
        y = int(render.get_height()//2 - self.txt_surface.get_height()//2)
        # Blit the text.
        render.blit(self.txt_surface,(x,y))
        if py.time.get_ticks() % 1000 > 500 and self.active:
            cursor = Rect(self.txt_surface.get_rect(topleft=(x,y-5)).topright, (3, self.txt_surface.get_rect().height))
            py.draw.rect(render, self.text_color, cursor)
        if self.isactive:
            ecran.blit(render,(self.position.x,self.position.y))

    def Enter_func(self,_event): ...

class AlertBox(sprite):
    """
    class de alertbox autonome, permet de rentrer d'afficher une erreur facilement
    """
    def __init__(self,name,path,color='black',text_color='grey',padding=0.05,isactive=True,layer=0):
        super().__init__(name,path,isactive,layer)

        self.color = Color(color)
        self.text = ''
        self.text_color = Color(text_color)
        self.padding = padding

        self.FONT = py.font.Font(FONT,36)

        self.childs:list[Button] = list()
  
    def set_scale(self,sca:Vector2):
        """
        attribue les valeur du vecteur à la taille de l'image, si les valeur sont en float alors elle sont considérer comme un multiplicateur
        """
        x,y = sca.x,sca.y
        if type(sca.x)==float:
            x = int(self.surface.get_width()*sca.x)
        if type(sca.y)==float:
            y = int(self.surface.get_height()*sca.y)
        self.scale = Vector2(x,y)

        self.actualize_child_position()
        self.actualize_scale()

    def actualize_child_position(self):
        #calcul pourcentage d'augmentation
        offset = Vector2(
            x= self.scale.x / self.surface.get_width(),
            y= self.scale.y / self.surface.get_height()
        )
        for _button in self.childs:
            #calcul position pourcentage du centre du parent
            pos = Vector2(
                ((_button.position.x + _button.scale.x/2) - self.position.x - self.surface.get_width()/2)/self.surface.get_width(),
                ((_button.position.y + _button.scale.y/2) - self.position.y - self.surface.get_height()/2)/self.surface.get_height()
            )
            #calcul nouvelle position par rapport au coin haut gauche du parent
            pos.x = pos.x*offset.x + 0.5; pos.y = pos.y*offset.y+0.5
            _button.set_position(pos,parent=self)

    def set_rect(self, coord: Vector2):
        super().set_rect(coord)
        for _button in self.childs:
            self.rect = self.rect.union(_button.rect)

    def on_enter(self,func):
        """
        Ce décorateur crée une fonction qui ajoute celle ci à la liste des fonctions.
        La fonction passé en décoration n'est executé que si la touche Enter est pressé.
        """
        def wrap(_event,*args, **kwargs):
            if _event.type==KEYDOWN:
                if self.isactive and _event.key == K_RETURN:
                    return func(*args,**kwargs)
        setattr(self,"Enter_func",wrap)
        return True

    def add_button(self,func):
        _button = func()

        if type(_button) == Button:
            self.childs.append(_button)
            self.set_rect(self.position)
        else:
            logging.warning("Add button function only take button type, your sprite wasn't added to your alertbox")

    def set_text(self,text,wrap_lenght=None,align_center=False):
        self.text = text

        _text = textZone(
            name=f'text_{self.name}',
            text_color=self.text_color
        )
        
        _text.set_text(text,wrap_lenght,align_center)

        _size = Vector2(self.surface.get_width()*(1 - self.padding*2),self.surface.get_height()*(1 - self.padding*2)) if type(self.padding)==float else Vector2(self.surface.get_width() - self.padding,self.surface.get_height() - self.padding)
        
        _text.size_to_scale(_size)

        _render = _text.render()

        _pos = (
            self.surface.get_width()//2 - _render.get_width()//2,
            self.surface.get_height()//2 - _render.get_height()//2
            )
        
        self.surface.blit(_render,_pos)

    def Event(self, event): ...

    def Handle(self, event:py.event.Event):
        self.Enter_func(event)
        for _button in self.childs:
            _button.Handle(event)

    def draw(self, ecran):
        super().draw(ecran)
        for _button in self.childs:
            _button.draw(ecran)

    def Update(self,*args, **kargs):
        for _button in self.childs:
            _button.Update(*args,**kargs)

    def Enter_func(self,_event): ...

class Menu:
    """
    classe principale du Menu
    """
    def __init__(self,name,parent=None,childs=None,background=None):
        self.name:str = name
        self.parent:str = parent
        self.childs:list[str] = [childs] if type(childs)==str else childs
        self.sprites:list[sprite] = []
        _window.menus.append(self)
        if _window == None:
            raise RuntimeError("Vous devez d'abors initialiser la fenêtre")
        if background!=None:
            try:
                self.background = py.image.load(background).convert() # tuile pour le background
                self.background = py.transform.scale(self.background, (_window.screen.get_width(), _window.screen.get_height()))
            except FileNotFoundError:
                logging.error(f"File not found : Youf background for your menu {self.name} was not found")
                raise FileNotFoundError
        else:
            self.background = None

    def add_sprite(self,func):
        """
        decorateur qui ajoute automatiquement le retour de la fonction à la liste
        """
        _sprite = func()
        if _sprite.__class__.__base__ == sprite:
            self.sprites.append(_sprite)
        else:
            raise TypeError("You must return a sprite based class to add, type returned was :",type(_sprite))

    def Update(self):
        """
        fonction update des bouton du menu avec en premier les event, ensuite les function effectué chaque frame et finalement l'affichage
        """
        for _event in py.event.get():
            if py.QUIT==_event.type:
                _window.destroy()
            for sprite in self.sprites:
                sprite.Handle(_event)
        for sprite in self.sprites:
            sprite.Update()
        self.Draw(_window.screen)
        
    def Draw(self,ecran:py.Surface):
        """
        fonction pour ajouter chaque bouton à l'écran
        """
        surface = py.Surface((ecran.get_width(),ecran.get_height())).convert_alpha()
        for sprite in self.sprites:
            sprite.draw(surface)
        ecran.blit(surface,(0,0))
    
    def get_childs(self):
        """
        fonction pour récupérer les menus enfants
        """
        for _menu in _window.menus:
            if _menu.name in self.childs:
                yield _menu

    def get_child(self,child_name):
        """
        fonction pour récupérer un menu enfants nomé
        """
        for _menu in _window.menus:
            if _menu.name in self.childs and _menu.name == child_name:
                return _menu
        else:
            raise Exception("Menu not found")

    def get_parent(self):
        """
        fonction pour récupérer le menu parent
        """
        for _menu in _window.menus:
            if _menu.name == self.parent:
                return _menu

    def get_sprite(self,name):
        for sprite in self.sprites:
            if sprite.name == name:
                return sprite

    def set_setup(self,func):
        """
        this function add a setup function execute when the menu is change
        """
        setattr(self,"setup",func)

    def setup(self): ...
