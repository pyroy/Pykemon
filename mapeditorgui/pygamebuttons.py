import pygame
version = "v1.5"

def void():
    return True

class Simplebutton():
    def __init__(self,width,height,color,text,font):
        self.width,self.height,self.color,self.text = width,height,color,text
        self.pos = (0,0)
        self.textcolor = (0,0,0)
        self.border = False
        self.bordercolor = (255,255,255)
        self.borderwidth = 5
        self.func = void
        self.font = font
    def link(self,func):
        self.func = func
    def draw(self,surf):
        if self.border:
            self.size = (self.pos[0]+self.borderwidth/4,self.pos[1]+self.borderwidth/4,self.width-self.borderwidth/2,self.height-self.borderwidth/2)
            pygame.draw.rect(surf, self.color, self.size)
            pygame.draw.rect(surf, self.bordercolor, self.size, self.borderwidth)
        else:
            pygame.draw.rect(surf, self.color, (self.pos[0],self.pos[1],self.width,self.height))
        self.txt = self.font.render(self.text, False, self.textcolor, self.color)
        surf.blit(self.txt, (self.pos[0]+self.width/2-self.txt.get_width()/2,self.pos[1]+self.height/2-self.txt.get_height()/2))
    def push(self,event):
        if self.pos[0] <= event.pos[0] <= self.pos[0]+self.width:
            if self.pos[1] <= event.pos[1] <= self.pos[1]+self.height:
                if event.button == 1:
                    self.func()

if __name__ == "__main__":
    print("pygamebuttons.Simplebutton(width,height,color,text) => Button object")
    print("has attributes:")
    print("\t- pos > (x,y)")
    print("\t- color > color of button in (r,g,b)")
    print("\t- textcolor > color of the text displayed in the button in (r,g,b)")
    print("\t- border > boolean, if enabled draws a border around the button,")
    print("\t  but the size doesn't change.")
    print("\t- bordercolor > color of the border in (r,g,b)")
    print("\t- borderwidth > int, width of the border")
    print("has functions:")
    print("\t- push(event) > must be called if event.type is a pygame.MOUSEBUTTONDOWN")
    print("\t  checks if button is pressed")
    print("\t- draw(Surface) > draws the button on Surface")
    print("\t- link(function) > specifies the function to be executed")
    print("\t  when the button is pressed")
