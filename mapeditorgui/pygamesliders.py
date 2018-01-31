import pygame
version = "v1.5"

def arb():
    pass

class Simpleslider():
    def __init__(self,width,height,vmin,vmax,color1,color2):
        self.width,self.height,self.vmin,self.vmax,self.color1,self.color2 = width,height,vmin,vmax,color1,color2
        self.currentVal = 0
        self.pos = (0,0)
        self.sliding = 0
        self.onUpdate = arb
    def draw(self,surf):
        if self.sliding and not pygame.mouse.get_pressed()[0]:
            self.sliding = 0
        elif self.sliding:
            self.value = self.vmax*(pygame.mouse.get_pos()[0]-self.pos[0])/self.width
            self.oldVal = self.currentVal
            self.currentVal = min(max(self.vmin, self.value ),self.vmax)
            if self.oldVal != self.currentVal:
                self.onUpdate()
        pygame.draw.rect(surf, self.color1, (self.pos[0],self.pos[1],self.width,self.height))
        self.x = self.width*(self.currentVal-self.vmin)/(self.vmax-self.vmin)
        pygame.draw.rect(surf, self.color2, (self.pos[0]+self.x-5,self.pos[1]-5,10,10+self.height))
    def push(self,event):
        if self.pos[0] <= event.pos[0] <= self.pos[0]+self.width:
            if self.pos[1]-5 <= event.pos[1] <= self.pos[1]+self.height+5:
                if event.button == 1:
                    self.sliding = 1
    def link(self,func):
        self.onUpdate = func

if __name__ == "__main__":
    print("pygamesliders.Simpleslider(width,height,vmin,vmax,color1,color2) => Slider object")
    print("has attributes:")
    print("\t- pos > (x,y)")
    print("\t- vmin & vmax > minimum and maximum values of the slider")
    print("\t- color1 > color of slider bar in (r,g,b)")
    print("\t- color2 > color of slider handle in (r,g,b)")
    print("\t- currentValue > int")
    print("has functions:")
    print("\t- push(event) > must be called if event.type is a pygame.MOUSEBUTTONDOWN")
    print("\t  checks if slider is held")
    print("\t- draw(Surface) > draws the slider on Surface")
