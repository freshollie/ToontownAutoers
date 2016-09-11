class Scroller:
    def __init__(self,itemList):
        self.list=itemList
        self.listPos=0
        self.shownItem=self.list[self.listPos]
        

    def scrollUp(self):
        if self.listPos-1<0:
            return
        else:
            self.listPos-=1
            self.shownScript=self.list[self.listPos]
            self.updateShownItem()

    def scrollDown(self):
        if self.listPos+1>len(self.list):
            return
        else:
            self.listPos+=1
            self.shownScript=self.list[self.listPos]
            self.updateShownItem()

    def updateShownItem(self)
        print self.shownScript
