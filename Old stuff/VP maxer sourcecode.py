#The VP maxer written by freshollie
#If any of the credits in this are wrong
#please inform me via a youtube inbox (toontowninjecting)

#I'm sorry that in the past I haven't given credit where credit is due
#but I didn't think it was that much of an issue.

import random #Random used in the enter battle functions to enter a random battle
from direct.interval.IntervalGlobal import * #Used for Sequences
from direct.distributed import DistributedObject #Used to hook the send update
from toontown.toonbase import ToontownBattleGlobals #Used to skip battle animations
from toontown.safezone import * #Used and imported by Peter's (Lifeless') 'toonup anywhere' to hook the generation function
from toontown.toon import * #Lots of these modules are used in hooks
from toontown.coghq import * #Lots of these modules are used in hooks
from toontown.distributed import ToontownClientRepository #Used to hook the 'dumpAllSSubShardObjects'
from toontown.battle import DistributedBattle #Lots of the functions in here are hooked
from toontown.battle import DistributedBattleFinal #Used as a hook
from toontown.suit.DistributedFactorySuit import DistributedFactorySuit #Used to work out if a render is a cog inside the factory
from toontown.suit.DistributedSuit import DistributedSuit #Used to work out if a render is a cog in sellbot hq
from toontown.suit import DistributedSellbotBoss #Lots of functions in here used as hooks
from toontown.building import DistributedDoor #Used and imported by Peter's (Lifeless') 'toonup anywhere' to hook the generation function
from toontown.building import DistributedBoardingParty #Used to skip the elevators

ToontownBattleGlobals.SkipMovie=1 #Used and found in the magic words to enable 'SMB' (Skip battle animations) This mainly skips the cog adjustments
DistributedToon.reconsiderCheesyEffect=lambda *x,**kwds:None #Sometimes while boarding an elevator this can cause problems
ToontownClientRepository.ToontownClientRepository.dumpAllSSubShardObjects=lambda self: None #This stops interests from being unloaded when you change
                                                                                            #an area meaning that toonup anywhere can be used in
                                                                                            #a bossbattle or any factory

faceOffHook = lambda self, ts, name, callback:self.d_faceOffDone(self)
DistributedBattleFactory.DistributedBattleFactory._DistributedLevelBattle__faceOff = faceOffHook #Used to hook the faceoff of factory battles
DistributedBattle.DistributedBattle._DistributedBattle__faceOff = faceOffHook #Used to hook the faceoff of a normal battle to make it instantly finish.


'''
Everything down to 'class restock'
was written by Peter (Lifeless) (http://www.youtube.com/user/TropiicalMango)
apart from the collision thing which I wrote
'''

oldTrolleyInit = DistributedTrolley.DistributedTrolley.__init__
oldPartyInit = DistributedPartyGate.DistributedPartyGate.__init__
oldDoorInit = DistributedDoor.DistributedDoor.__init__

#Collision hooks added due to your toon sometimes landing on top of one of the npc's
oldHandleEnterCollisionSphereParty=DistributedNPCPartyPerson.DistributedNPCPartyPerson.handleCollisionSphereEnter
DistributedNPCPartyPerson.DistributedNPCPartyPerson.handleCollisionSphereEnter=lambda *args: None
oldHandleEnterCollisionSphereFisherman=DistributedNPCFisherman.DistributedNPCFisherman.handleCollisionSphereEnter
DistributedNPCFisherman.DistributedNPCFisherman.handleEnterCollisionSphere=lambda *args: None
 
oldFisherAnnounceGenerate = DistributedNPCFisherman.DistributedNPCFisherman.announceGenerate
def newFishermanAnnounceGenerate(self):
    try:
        oldFisherAnnounceGenerate(self)
    except:
        return None
 
oldPartyPlannerAnnounceGenerate = DistributedNPCPartyPerson.DistributedNPCPartyPerson.announceGenerate
def newPartyPlannerAnnounceGenerate(self):
    try:
        oldPartyPlannerAnnounceGenerate(self)
    except:
        return None
 
def newInit(self, cr):
    for obj in dir(self):
        exec 'self.%s = lambda *x:None' % obj
    return None

class restock:
    '''
    Restock is a class used to restock
    laff and gags. Some of the functions
    in here were written by me and
    others were written by Cody (http://www.youtube.com/user/gamecrazzy441)
    and Peter (http://www.youtube.com/user/TropiicalMango).
    '''
    
    def __init__(self):
        '''
        All of theses ifs at the beginning here are used to work out the type
        of account this script is being used on
        '''
        
        if not base.localAvatar.getTrackAccess()[0]:
            self.noToonUp=True
            self.secondTrack=4
            self.desiredLevel2=5
        else:
            self.noToonUp=False
            self.secondTrack=0
            self.desiredLevel2=4
            
        if not base.localAvatar.getTrackAccess()[2]:
            self.firstTrack=4
            self.desiredLevel1=5
        else:
            self.firstTrack=2
            self.desiredLevel1=5
            
        if base.localAvatar.experience.getExpLevel(0)<4 and not self.noToonUp:
            base.localAvatar.setSystemMessage(0,'Running this will probably not work on your toon, make sure you have the required gag tracks and levels')
            
        elif base.localAvatar.experience.getExpLevel(2)<5 and base.localAvatar.getTrackAccess()[2]:
            base.localAvatar.setSystemMessage(0,'Running this will probably not work on your toon, make sure you have the required gag tracks and levels')
            
        elif base.localAvatar.experience.getExpLevel(4)<5:
            base.localAvatar.setSystemMessage(0,'Running this will probably not work on your toon, make sure you have the required gag tracks and levels')
            
        self.thirdTrack=4
        self.desiredLevel3=5
        self.createInventory()
        self.maxCarryGags = base.localAvatar.getMaxCarry() #Used in the restock gags function
        self.gagshop_zoneId = 4503 #Used in the restock gags function
        self.noToons=Sequence(Func(self.removeToons), Wait(1.5)) #Written by Peter to remove all toons that are no actually in your loaded zone
        self.noTrolley=False #This is no longer used
        self.unloaded=True #Used to determine if the interests have been unloaded
        self.wasInBattle=False #Used to determine if the toon has died in a battle and need to be put back into the battle
        DistributedNPCFisherman.DistributedNPCFisherman.announceGenerate = newFishermanAnnounceGenerate #Used in Peters Toonup anywhere
        DistributedNPCPartyPerson.DistributedNPCPartyPerson.announceGenerate = newPartyPlannerAnnounceGenerate #Used in Peters Toonup anywhere
        
        self.lookAroundHookSeq = Sequence(Func(self.lookAroundHookFunc), Wait(2.5))  #Used in Peters Toonup anywhere
        self.lookAroundHookSeq.loop() #Used in Peters Toonup anywhere
        ToonHead.ToonHead._ToonHead__lookAround = lambda *x:None #Used in Peters Toonup anywhere
    
    def createInventory(self):
        '''
        Created by me to create
        an inventory based on 
        the desired levels
        and disired gags.
        '''
        
        self.desiredInv=""
        if self.desiredLevel1==6:
            self.desiredLevel1=5
            
        if self.desiredLevel2==6:
            self.desiredLevel2=5
            
        for i in range(49):
            if i==((self.firstTrack*7)+self.desiredLevel1):
                if self.firstTrack==1:
                    self.desiredInv+="\x02"
                elif self.desiredLevel1>3:
                    self.desiredInv+="\x02"
                else:
                    self.desiredInv+="\x04"
            elif i==((self.secondTrack*7)+self.desiredLevel2):
                if self.secondTrack==1:
                    self.desiredInv+="\x02"
                elif self.desiredLevel2>3:
                    self.desiredInv+="\x02"
                else:
                    self.desiredInv+="\x04"
            elif i==((self.thirdTrack*7)+self.desiredLevel3):
                if self.thirdTrack==1:
                    self.desiredInv+="\x02"
                elif self.desiredLevel3>3:
                    self.desiredInv+="\x02"
                else:
                    self.desiredInv+="\x04"
            else:
                self.desiredInv+="\x00"
        
    def lookAroundHookFunc(self):
        '''
        Written by Peter which I guess (but haven't been told)
        is used to hook the toon's function once the toon has
        actually been loaded. In this case it is not actually
        needed but I left it in anyway.
        '''
        
        if hasattr(base, 'localAvatar'):
            base.localAvatar.findSomethingToLookAt = lambda *x:None
            self.oldFindSomethingToLookAt = base.localAvatar.findSomethingToLookAt
            self.lookAroundHookSeq.finish()
        self.oldLookAround = ToonHead.ToonHead._ToonHead__lookAround
        
    def collectLaff(self):
        '''
        Used to collect treasure
        from the loaded playgrounds
        '''
        
        for treasure in base.cr.doFindAll('Treasure'):
            treasure.d_requestGrab()
            
   def removeToons(self):
        '''
        This function is written by
        Peter and was again taken from
        his 'Toonup anywhere' script.
        It is use to unload most 
        renders (that are loaded when
        you add a playground as an
        interest) in order to reduce
        lagg on the client.
        '''
    
        for x in base.cr.doFindAll('Fisherman'):
            try:
                if x.zoneId != base.localAvatar.zoneId:
                    x.removeNode()
                    x.nametag.unmanage(base.marginManager)
            except:
                pass
 
        for x in base.cr.doFindAll('Party Planner'):
            try:
                if x.zoneId != base.localAvatar.zoneId:
                    x.removeNode()
                    x.nametag.unmanage(base.marginManager)
            except:
                pass
           
        for x in base.cr.doFindAll('render/donald'):
            try:
                if x.zoneId != base.localAvatar.zoneId:
                    x.removeNode()
                    x.nametag.unmanage(base.marginManager)
            except:
                pass
 
        for x in base.cr.doFindAll('render/minnie'):
            try:
                if x.zoneId != base.localAvatar.zoneId:
                    x.removeNode()
                    x.nametag.unmanage(base.marginManager)
            except:
                pass
 
        for x in base.cr.doFindAll('render/mickey'):
            try:
                if x.zoneId != base.localAvatar.zoneId:
                    x.removeNode()
                    x.nametag.unmanage(base.marginManager)
            except:
                pass
 
        for x in base.cr.doFindAll('render/pluto'):
            try:
                if x.zoneId != base.localAvatar.zoneId:
                    x.removeNode()
                    x.nametag.unmanage(base.marginManager)
            except:
                pass
 
        for x in base.cr.doFindAll('render/daisy'):
            try:
                if x.zoneId != base.localAvatar.zoneId:
                    x.removeNode()
                    x.nametag.unmanage(base.marginManager)
            except:
                pass
 
        for x in base.localAvatar.getNearbyPlayers(100000000000000, False):
            try:
                y = base.cr.doId2do.get(x)
                if y.zoneId != base.localAvatar.zoneId:
                    y.removeNode()
                    y.nametag.unmanage(base.marginManager)
            except:
                pass
 
        for x in base.cr.doFindAll('Butterfly'):
            x.butterflyNode.remove()
 
        for x in base.cr.doFindAll('Flower'):
            x.bigFlower.removeNode()
 
        for x in base.cr.doFindAll('Treasure'):
            x.setPosition(0, 0, 8**8)
 
        for x in base.cr.doFindAll('render/DistributedFishingTarget'):
            x.bubbles.removeNode()
            x.removeNode()
                
    def gainLaff(self):
        '''
        Gain Laff was written
        by me and is used to
        collect treasure from
        the loaded playgrounds
        if the playgrounds are
        loaded. It is also used
        to put the toon back in
        a battle if they have died
        '''
        
        if base.localAvatar.getHp()!=base.localAvatar.getMaxHp():
            if self.unloaded:
                vpMaxer.factoryAutoer.preTele()
                self.interest1=base.cr.addInterest(base.localAvatar.defaultShard, 9000, 5, None)
                self.interest2=base.cr.addInterest(base.localAvatar.defaultShard, 3000, 5, None)
                self.unloaded=False
            self.collectLaff()
        if self.wasInBattle:
            vpMaxer.factoryAutoer.enterBattle()
     
    def loadGagshop(self):       
        '''
        Load Gagshop Written by Peter
        and found in multihack
        it was very slightly modified
        but all credit for the function
        still goes to him.
        '''
        
        
        if not base.cr.doFind('Clerk'):
            self.contextId = base.cr.addInterest(base.localAvatar.defaultShard, self.gagshop_zoneId, 4, event=None)
        try:
            if not int(render.find('**/*gagShop_interior_english*').getZ()) == 8**8:
                render.find('**/*gagShop_interior_english*').setZ(8**8)
                for k in base.cr.doFindAll('Clerk'):
                    k.nametag.unmanage(base.marginManager)
        except:
            pass
            
    def buyGags(self):
        '''
        Buy gags found in Multihack
        but I have been informed
        that the function was Written
        by Cody and/or Peter 
        (Please inform me if I am wrong).
        It was very slightly modified
        due to it using up far more 
        jelly beans than it needed to
        but full credit still goes
        to them
        '''
    
        desiredInv=self.desiredInv
        try:
            maxCarryGags = base.localAvatar.getMaxCarry()     
            if base.cr.doFind('Clerk'):
                num_gags = 0
                for inventory_number in base.localAvatar.inventory.makeFromNetString(desiredInv):
                    for k in inventory_number[:-1]:
                        num_gags += k
                change = base.localAvatar.getMoney() - num_gags
                oldString = base.localAvatar.inventory.makeNetString()
                newString = desiredInv[:6] + oldString[6] + desiredInv[7:13] + oldString[13] + desiredInv[14:20] + oldString[20] + desiredInv[21:27] + oldString[27] + desiredInv[28:34] + oldString[34] + desiredInv[35:41] + oldString[41] + desiredInv[42:48] + oldString[48]
                
                for clerk in base.cr.doFindAll('Clerk'): #Add this statement to your restock to fix it.
                    clerk.setMovie=lambda *args,**kwds: None                   #
                    clerk.freeAvatar=lambda *args: None                        #
                    clerk.sendUpdate('avatarEnter')                            #
                    clerk.sendUpdate('setInventory', [newString, change, 1])   #
                    
                money = base.localAvatar.getMoney()
                maxMoney = base.localAvatar.getMaxMoney()
                base.cr.bankManager.d_transferMoney(money - maxMoney)
        except:
            pass
    
    def unloadGagshop(self):
        '''
        Written by Peter (I guess)
        and is used to loaded the
        gag shop interest which is
        defined in the load gagshop
        function
        '''
        
        if hasattr(self, 'contextId'):
            try:
                base.cr.removeInterest(self.contextId)
            except:
                pass
        
    def restock(self):
        '''
        This function was written by
        me and is used to load the
        gag shop quickly buy the gags
        and then unload it. It checks
        if it actually needs to buy
        the gags before doing this
        (Which is why there is a long if).
        '''
        
        try:
            if base.localAvatar.inventory.inventory[self.firstTrack][self.desiredLevel1]<2 or base.localAvatar.inventory.inventory[self.secondTrack][self.desiredLevel2]<2 or base.localAvatar.inventory.inventory[self.thirdTrack][self.desiredLevel3]<2:
                Sequence(Func(self.loadGagshop),Wait(1),Func(self.buyGags),Wait(0.5),Func(self.unloadGagshop)).start()
        
        except:
            pass
    
    def revertFunctions(self):
        '''
        Used in toonbot to unload the script
        It stops the noToons loop
        and removes the playground interests
        '''
        
        self.noToons.finish()
        try:
            base.cr.removeInterest(self.interest1)
            base.cr.removeInterest(self.interest2)
            self.unloaded=True
        except:
            pass
            
class OtherFunctions:
    '''
    Other functions written by
    me is used to hold functions
    that are used by both of the
    Autoers
    '''
    
    #Defining functions used will be used in the hooks
    oldGardensInit=DGPlayground.DGPlayground.__init__ #Used to show that you have teleported to Daisys Gardens playground (Could have died)
    oldSellbotInit=SellbotHQExterior.SellbotHQExterior.__init__ #Used to show that you have teleported to a sellbot hq
    oldSendUpdate=DistributedObject.DistributedObject.sendUpdate #Used to skip some of the movies when you request attack
    oldEnterHealth=HealthForceAcknowledge.HealthForceAcknowledge.enter #Used to show that you weren't at full health when you tried to teleport out of the playground
    oldSetAnim=LocalToon.LocalToon.setAnimState #Used to make the player invisible when the set animstate function is called
    oldPostInvite=DistributedBoardingParty.DistributedBoardingParty.postInvite #Used to accept your own invite as soon as it is received

    def __init__(self):
        self.shouldContinue=False #Used to let the hooks know if the script is actually running or not
        self.bossCount=0
        self.shouldEnd=False 
        self.canSetParentAgain=True
        self.onlyFactory=False #Used to say that the user only wants to do the Factory (If they want to complete tasks)
        self.numberToSuit={0:'Cold Caller',1:'Telemarketer',2:'Name Dropper',3:'Glad Hander',
                           4:'Mover & Shaker',5:'Two-Face',6:'The Mingler',7:'Mr. Hollywood'} #Used by the gui

        DGPlayground.DGPlayground.__init__=lambda *args:self.newGardensInit(*args) 
        oldSellbotInit=SellbotHQExterior.SellbotHQExterior.__init__=lambda *args: self.newSellbotInit(*args)#Used to hook the function. Syntax I have used can be found in lots of other
                                                                                                            #scripts where people have hooked functions
        HealthForceAcknowledge.HealthForceAcknowledge.enter=lambda newSelf,hplevel: self.newEnterHealth(newSelf,hplevel)
        LocalToon.LocalToon.setAnimState=lambda *args,**kwds:self.newSetAnimState(*args,**kwds)
        DistributedBoardingParty.DistributedBoardingParty.postInvite=lambda newSelf,leaderId,inviterId: self.newPostInvite(newSelf,leaderId,inviterId)
        

    def attack(self):
        '''
        Syntax used can be found in the original gag trainer
        but has been very much modified to suit the purpose of
        the Factory Autoer
        '''
        
        try:
            for battle in base.cr.doFindAll('battle'):
                if vpMaxer.restock.noToonUp and not vpMaxer.restock.noLure:
                    if vpMaxer.restock.firstTrack==2 and base.localAvatar.getHp()>(base.localAvatar.getMaxHp()*0.75):
                        battle.sendUpdate('requestAttack', [vpMaxer.restock.firstTrack, vpMaxer.restock.desiredLevel1, battle.suits[0].doId])
                    if base.localAvatar.getHp()>(base.localAvatar.getMaxHp()*0.75):
                        battle.sendUpdate('requestAttack', [vpMaxer.restock.thirdTrack, vpMaxer.restock.desiredLevel3, battle.suits[0].doId])
                        
                elif vpMaxer.restock.noLure:
                    if vpMaxer.restock.secondTrack==0 and base.localAvatar.getHp()<(base.localAvatar.getMaxHp()*0.75):
                        battle.sendUpdate('requestAttack', [vpMaxer.restock.secondTrack, vpMaxer.restock.desiredLevel2, base.localAvatar.doId])
                    if base.localAvatar.getHp()>(base.localAvatar.getMaxHp()*0.75):
                        battle.sendUpdate('requestAttack', [vpMaxer.restock.thirdTrack, vpMaxer.restock.desiredLevel3, battle.suits[0].doId])
                        
                else:
                    if base.localAvatar.inventory.inventory[vpMaxer.restock.firstTrack][vpMaxer.restock.desiredLevel1]>0:
                        battle.sendUpdate('requestAttack', [vpMaxer.restock.firstTrack, vpMaxer.restock.desiredLevel1, battle.suits[0].doId])
                    else:
                        break
                        
                    if base.localAvatar.getHp()<(base.localAvatar.getMaxHp()*0.25):
                    
                        if base.localAvatar.inventory.inventory[vpMaxer.restock.secondTrack][vpMaxer.restock.desiredLevel2]>0:
                            battle.sendUpdate('requestAttack', [vpMaxer.restock.secondTrack, vpMaxer.restock.desiredLevel2, base.localAvatar.doId])
                        else:
                            break
                            
                        if base.localAvatar.inventory.inventory[vpMaxer.restock.thirdTrack][vpMaxer.restock.desiredLevel3]>0:
                            battle.sendUpdate('requestAttack', [vpMaxer.restock.thirdTrack, vpMaxer.restock.desiredLevel3, battle.suits[0].doId])
                        else:
                            break
                            
                    else:
                        if base.localAvatar.inventory.inventory[vpMaxer.restock.thirdTrack][vpMaxer.restock.desiredLevel3]>0:
                            battle.sendUpdate('requestAttack', [vpMaxer.restock.thirdTrack, vpMaxer.restock.desiredLevel3, battle.suits[0].doId])
                        else:
                            break
        except:
            pass
        
    def sendUpdateHook(self, newself, fieldName, args=[], sendToId=None):
        '''
        Used to call more functions to skips battle animations when
        the request attack Distributed Class is called
        '''
        
        if fieldName=="requestAttack":
            self.oldSendUpdate(newself,"requestAttack", args, sendToId)
            self.oldSendUpdate(newself,"movieDone",[])
            newself.d_rewardDone(base.localAvatar.doId)
        else:
            self.oldSendUpdate(newself,fieldName, args, sendToId)
        
    def newGardensInit(self,*args):
        '''
        Used to show that the toon has been teleported
        to Daisys gardens
        '''
        
        self.oldGardensInit(*args)
        if self.shouldContinue:
            vpMaxer.factoryAutoer.gainLaffSeq.finish()
            vpMaxer.factoryAutoer.attackSeq.finish()
            self.checkMerits()
     
    def newSetAnimState(self,*args,**kwds):
        '''
        Used to make the player invisible when an animation
        is called, it makes sure that another animation
        hasn't been called in the last 2 seconds so as
        not to overload the server with requests
        '''
        
        self.oldSetAnim(*args,**kwds)
        if self.canSetParentAgain:
            base.localAvatar.d_setParent(1)
            self.canSetParentAgain=False
            Sequence(Wait(2),Func(self.doUnsetCanSetParentAgain)).start()
    
    def doUnsetCanSetParentAgain(self):
        '''
        Used to allow the script to set
        parent 1 again.
        '''
        
        self.canSetParentAgain=True
    
    def newEnterHealth(self,newSelf,hplevel):
        '''
        Used to show that the Maxer has tried to teleport
        out of the playground without having any laff
        so it can now retry
        '''
        
        try:
            self.oldEnterHealth(newSelf,hplevel)
            newSelf.handleOk(base.localAvatar.getHp())
            newSelf.exit()
            if self.shouldContinue:
                Sequence(Wait(2),Func(self.checkMerits)).start()
        except:
            pass
            
    def newSellbotInit(self,*args):
        '''
        Used to show that the toon has teleported
        to sellbot hq
        '''
        
        self.oldSellbotInit(*args)
        if self.shouldContinue:
            self.walk()
            Sequence(Wait(1),Func(self.checkMerits)).start()
    
    def newPostInvite(self,newSelf,leaderId,inviterId):
        '''
        Used to accept the boarding group invitation from yourself
        when it is asked.
        '''
    
        if leaderId==base.localAvatar.doId:
            newSelf.sendUpdate('requestAcceptInvite',[inviterId,leaderId])
        else:
            self.oldPostInvite(newSelf,leaderId,inviterId)
        
    def checkMerits(self):
        '''
        Written by me it is a function to determine
        what the maxer needs to do with the toon next
        it works everything out depeding of the toons
        merits needed and the settings they have chosen.
        '''
        
        if self.onlyFactory:
            base.localAvatar.cogMerits[3]=-4000
        if self.shouldEnd:
            self.shouldContinue=False
        if self.haveJb():
            if self.shouldContinue:
                if self.getMeritsLeft()==0 and not self.onlyFactory:
                    if base.cr.doFind('DistributedSellbotHQDoor') and base.localAvatar.getZoneId()>=11000 and base.localAvatar.getZoneId()<11100:
                        vpMaxer.vpAutoer.start()
                    else:
                        vpMaxer.restock.restock()
                        vpMaxer.restock.collectLaff()
                        self.walk()
                        vpMaxer.autoerGui.display.newLine('Teleporting to Sellbot hq')
                        Sequence(Wait(2),Func(self.teleBack)).start()
                else:
                    if base.cr.doFind('DistributedSellbotHQDoor') and base.localAvatar.getZoneId()>=11000 and base.localAvatar.getZoneId()<11100:
                        vpMaxer.factoryAutoer.goFactory()
                    else:
                        vpMaxer.restock.restock()
                        vpMaxer.restock.collectLaff()
                        self.walk()
                        vpMaxer.autoerGui.display.newLine('Teleporting to Sellbot hq')
                        Sequence(Wait(2),Func(self.teleBack)).start()
            else:
                vpMaxer.restock.noToons.finish()
                try:
                    base.cr.removeInterest(vpMaxer.restock.interest1)
                    base.cr.removeInterest(vpMaxer.restock.interest2)
                    vpMaxer.restock.unloaded=True
                except:
                    pass
                base.localAvatar.setSystemMessage(1,"Thanks for using freshollie's VP maxer")
                vpMaxer.autoerGui.display.newLine("Stopped")
                vpMaxer.factoryAutoer.attackSeq.finish()
        else:
            base.localAvatar.setSystemMessage(0,'You have run out of jelly beans, please use the fishing code to gain some')
            vpMaxer.autoerGui.display.newLine('You have run out of jelly beans, please use the fishing code to gain some')
    
    def getMeritsLeft(self):
        '''
        Uses the CogDisguiseGlobals to work out how many
        stock options te toon needs to gain before it can
        do the vp.
        '''
        
        return CogDisguiseGlobals.getTotalMerits(base.localAvatar,3)-base.localAvatar.cogMerits[3]

    def walk(self):
        '''
        Walk is a function built into magic words
        which I used instead of sendOpenTalk('~walk').
        '''
        
        try:
            base.cr.playGame.getPlace().fsm.forceTransition('walk')
        except:
            pass
       
    def teleBack(self,zone=11000):
        '''
        TeleBack used to teleport to a playground or cog
        hq if no zone is given it teleports to sellbot
        hq.
        '''
        
        try:
            self.walk()
            base.cr.playGame.getPlace().handleBookCloseTeleport(zone, zone)
        except:
            pass
            
    def onlyDoFactory(self):
        '''
        Written so that the user can choose if they want to do the Factory only.
        '''
        
        self.onlyFactory=True
        base.localAvatar.setSystemMessage(0,'The VP Maxer will do only factory runs')
        
    def doBoth(self):
        self.onlyFactory=False
        base.localAvatar.setSystemMessage(0,'The VP Maxer will do both factories and VPs')
        
    def haveJb(self):
        '''
        Checks if the user has more than 100
        jelly beans so they don't run out during
        a Factory.
        '''
        
        if base.localAvatar.cogLevels[0]==49:
            return True
        elif base.localAvatar.getTotalMoney()<100:
            return False
        else:
            return True
        
    def setStop(self):
        self.shouldEnd=True
        base.localAvatar.setSystemMessage(1,"The Autoer will stop at the end of this run")
        vpMaxer.autoerGui.stopTimer()
    
    def start(self):
        DistributedObject.DistributedObject.sendUpdate=lambda newself, fieldName, args=[], sendToId=None: self.sendUpdateHook(newself, fieldName, args, sendToId)
        self.shouldEnd=False
        self.shouldContinue=True
        self.bossCount=0
        vpMaxer.autoerGui.startTimer()
        emptyShardList=[]
        for shard in base.cr.activeDistrictMap:
            if base.cr.activeDistrictMap[shard].avatarCount<30:
                emptyShardList.append(shard)
        if emptyShardList==[]:
            emptyShardList=[650000000, 754000000, 608000000, 756000000, 658000000, 712000000, 360000000, 410000000, 620000000, 454000000, 726000000, 362000000, 688000000, 316000000]
        if base.localAvatar.defaultShard not in emptyShardList:
            vpMaxer.autoerGui.display.newLine('TPing to an empty district')
            base.cr.playGame.getPlace().requestTeleport(11000,11000,random.choice(emptyShardList),base.localAvatar.doId)
        elif base.localAvatar.getZoneId()>=11000 and base.localAvatar.getZoneId()<11100:
            self.checkMerits()
        else:
            base.cr.playGame.getPlace().requestTeleport(11000,11000,None,None)
        vpMaxer.restock.noToons.loop()
        
    def revertFunctions(self):
        '''
        Revert to the original functions so other scripts can be loaded.
        '''
        
        LocalToon.LocalToon.setAnimState=self.oldSetAnim
        DGPlayground.DGPlayground.__init__=self.oldGardensInit
        SellbotHQExterior.SellbotHQExterior.__init__=self.oldSellbotInit
        DistributedObject.DistributedObject.sendUpdate=self.oldSendUpdate
        HealthForceAcknowledge.HealthForceAcknowledge.enter=self.oldEnterHealth
        DistributedBoardingParty.DistributedBoardingParty.postInvite=self.oldPostInvite

class VpAutoer:
    '''
    Ceo Autoer written by me with some functions written by others.
    '''
    #Used as hooks to find out where your toon is during the bossbattle
    oldBossEnterElevator=DistributedSellbotBoss.DistributedSellbotBoss.enterElevator
    oldEnterBattleThree=DistributedSellbotBoss.DistributedSellbotBoss.enterBattleThree
    oldEnterPrepareBattleTwo=DistributedSellbotBoss.DistributedSellbotBoss.enterPrepareBattleTwo
    oldEnterPrepareBattleThree=DistributedSellbotBoss.DistributedSellbotBoss.enterPrepareBattleThree
    oldEnterEpilogue=DistributedSellbotBoss.DistributedSellbotBoss.enterEpilogue
    oldEnterRollToBattleTwo=DistributedSellbotBoss.DistributedSellbotBoss.enterRollToBattleTwo
    oldEnterWaitForInput=DistributedBattleFinal.DistributedBattleFinal.enterWaitForInput
    oldBossEnterIntro=DistributedSellbotBoss.DistributedSellbotBoss.enterIntroduction
    oldAvatarExit=DistributedCogHQDoor.DistributedCogHQDoor.avatarExit
    
    def __init__(self):
        self.filter=False
        self.cardsWanted=['Flippy','Barnacle Bessie','Lil Oldman','Professor Pete','Stinky Ned','Daffy Don','Moe Zart','Sid Sonata','Franz Neckvein']
        
        DistributedSellbotBoss.DistributedSellbotBoss.enterElevator=lambda newSelf: self.newBossEnterElevator(newSelf)
        DistributedSellbotBoss.DistributedSellbotBoss.enterIntroduction=lambda newSelf,*args: self.newBossEnterIntro(newSelf,*args)
        DistributedSellbotBoss.DistributedSellbotBoss.enterRollToBattleTwo=lambda newSelf: self.newEnterRollToBattleTwo(newSelf)
        DistributedSellbotBoss.DistributedSellbotBoss.enterBattleThree=lambda newSelf: self.newEnterBattleThree(newSelf)
        DistributedBattleFinal.DistributedBattleFinal.enterWaitForInput=lambda *args: self.newEnterWaitForInput(*args)
        DistributedCogHQDoor.DistributedCogHQDoor.avatarExit=lambda newSelf,id: self.newAvatarExit(newSelf,id)
        DistributedSellbotBoss.DistributedSellbotBoss.enterPrepareBattleThree=lambda newSelf: self.newEnterPrepareBattleThree(newSelf)
        DistributedSellbotBoss.DistributedSellbotBoss.enterPrepareBattleTwo=lambda newSelf: self.newEnterPrepareBattleTwo(newSelf)
        DistributedSellbotBoss.DistributedSellbotBoss.enterEpilogue=lambda newSelf: self.newEnterEpilogue(newSelf)
        
    def newBossEnterElevator(self,newSelf):
        '''
        The same idea as the introduction hook function.
        '''
        
        self.oldBossEnterElevator(newSelf)
        if vpMaxer.otherFunctions.shouldContinue:
            vpMaxer.autoerGui.display.newLine('Skipping Elevator')
            newSelf._DistributedBossCog__doneElevator()
            
    def newBossEnterIntro(self,newSelf,*args):
        '''
        When the function to enter the boss introduction
        the maxer automatically exits the introduction
        effectively skipping it.
        '''
        
        self.oldBossEnterIntro(newSelf,*args)
        if vpMaxer.otherFunctions.shouldContinue:
            if self.cardFilter():
                newSelf.exitIntroduction()
                vpMaxer.autoerGui.display.newLine('Skipping VP introduction')
            else:
                vpMaxer.autoerGui.display.newLine('Card not in wanted cards')
                vpMaxer.autoerGui.display.newLine('Restarting the VP')
                Sequence(Wait(2),Func(vpMaxer.otherFunctions.teleBack)).start()
    
    def newEnterEpilogue(self,newSelf):
        '''
        When the boss enter epilogue function is called
        the bosscount gets 1 added to it and the toon gets
        teleported back.
        '''
        
        self.oldEnterEpilogue(newSelf)
        if vpMaxer.otherFunctions.shouldContinue:
            vpMaxer.otherFunctions.bossCount+=1
            vpMaxer.otherFunctions.teleBack()
            vpMaxer.autoerGui.display.newLine('Finished VP')
    
    def newEnterRollToBattleTwo(self,newSelf):
        '''
        The same idea as the introduction hook function.
        '''
        self.oldEnterRollToBattleTwo(newSelf)
        if vpMaxer.otherFunctions.shouldContinue:
            newSelf.exitRollToBattleTwo()
            vpMaxer.autoerGui.display.newLine('Skipping cutscene')
    
    def newEnterPrepareBattleTwo(self,newSelf):
        '''
        The same idea as the introduction hook function.
        '''
        
        self.oldEnterPrepareBattleTwo(newSelf)
        if vpMaxer.otherFunctions.shouldContinue:
            newSelf._DistributedSellbotBoss__onToBattleTwo(33)
            vpMaxer.autoerGui.display.newLine('Skipping dialogue 1')
    
    def newEnterPrepareBattleThree(self,newSelf):
        '''
        The same idea as the introduction hook function.
        '''
        
        self.oldEnterPrepareBattleThree(newSelf)
        if vpMaxer.otherFunctions.shouldContinue:
            newSelf._DistributedSellbotBoss__onToBattleThree(33)
            vpMaxer.autoerGui.display.newLine('Skipping dialogue 2')
    
    def newEnterBattleThree(self,newSelf):
        '''
        The same idea as the introduction hook function.
        '''
        
        self.oldEnterBattleThree(newSelf)
        if vpMaxer.otherFunctions.shouldContinue:
            self.endBattle()
            vpMaxer.autoerGui.display.newLine('Completing pie round')
    
    def newEnterWaitForInput(self,*args):
        '''
        When the cogs are ready to be attacked the exploit is ready to be used
        which is what this hook is for.
        '''
        
        self.oldEnterWaitForInput(*args)
        if vpMaxer.otherFunctions.shouldContinue:
            self.exploit()
            vpMaxer.autoerGui.display.newLine('Skipping Battle')
        
    def newAvatarExit(self,newSelf,id):
        '''
        As soon as the toon exits the door it invites its self to a boarding
        group and then requests to leave via the elevator just like pressing
        the 'Go' button for a boarding group
        '''
        
        self.oldAvatarExit(newSelf,id)
        if base.cr.doFind('Elevator') and id==base.localAvatar.doId and vpMaxer.otherFunctions.shouldContinue:
            vpMaxer.otherFunctions.walk()
            vpMaxer.autoerGui.display.newLine('Heading to VP')
            base.cr.doFind('Boarding').sendUpdate('requestInvite',[base.localAvatar.doId])
            base.cr.doFind('Boarding').sendUpdate('requestGoToSecondTime',[base.cr.doFind('Elevator').doId])

    def destroyBattle(self):
        '''
        The battle exploit first founded by Pascal (http://www.youtube.com/user/leftylemonzilla)
        and has been used here to skip the cog battles in the ceo.
        '''
        
        base.cr.doFind('SafeZone').sendUpdate('enterSafeZone')
    
    def filterOn(self):
        self.filter=True
        base.localAvatar.setSystemMessage(0,'The VP Maxer will filter bad cards')
    
    def filterOff(self):
        self.filter=False
        base.localAvatar.setSystemMessage(0,'The VP Maxer will not filter bad cards')

    def exploit(self):
        Sequence(Func(self.destroyBattle), Wait(.5), Func(vpMaxer.otherFunctions.walk)).start()
        
    def endBattle(self):
        '''
        This was not created by me but
        I don't actually know where it
        came from. It's something that
        is not hard to take from the 
        dc files though.
        '''
        
        if base.cr.doFind('V. P'):
            base.cr.doFind('V. P').sendUpdate('hitBossInsides')
            base.cr.doFind('V. P').sendUpdate('hitBoss', [100])
            base.cr.doFind('V. P').sendUpdate('finalPieSplat')
            
    def start(self):
        base.localAvatar.collisionsOff()
        vpMaxer.autoerGui.display.newLine('Starting Vice President')
        vpMaxer.autoerGui.display.newLine('Entering Lobby')
        base.cr.doFind('DistributedSellbotHQDoor').sendUpdate('requestEnter')
    
    def cardFilter(self):
        '''
        Card filter idea taken from many other VP autoers
        '''
        
        if base.cr.doFind('V. P').cagedToon.getName() in self.cardsWanted or not self.filter:
            return True
        else:
            return False
    
    def revertFunctions(self):
        '''
        Revert to the original functions so other scripts can be loaded.
        '''
        
        DistributedSellbotBoss.DistributedSellbotBoss.enterElevator=self.oldBossEnterElevator
        DistributedSellbotBoss.DistributedSellbotBoss.enterBattleThree=self.oldEnterBattleThree
        DistributedSellbotBoss.DistributedSellbotBoss.enterPrepareBattleTwo=self.oldEnterPrepareBattleTwo
        DistributedSellbotBoss.DistributedSellbotBoss.enterPrepareBattleThree=self.oldEnterPrepareBattleThree
        DistributedSellbotBoss.DistributedSellbotBoss.enterEpilogue=self.oldEnterEpilogue
        DistributedSellbotBoss.DistributedSellbotBoss.enterRollToBattleTwo=self.oldEnterRollToBattleTwo
        DistributedBattleFinal.DistributedBattleFinal.enterWaitForInput=self.oldEnterWaitForInput
        DistributedSellbotBoss.DistributedSellbotBoss.enterIntroduction=self.oldBossEnterIntro
        DistributedCogHQDoor.DistributedCogHQDoor.avatarExit=self.oldAvatarExit
            
class FactoryAutoer:
    oldFactoryInit=FactoryExterior.FactoryExterior.__init__
    oldDistributedFactoryInit=DistributedFactory.DistributedFactory.__init__
    oldEnterReward=DistributedBattleFactory.DistributedBattleFactory.enterReward
    oldEnterFactoryReward=DistributedBattleFactory.DistributedBattleFactory.enterFactoryReward
    
    def __init__(self,vpMaxer):
        self.roomNum=0
        self.zones=[4,7,8,13,22,24,34,32] #Factory zones
        self.roomValues=[28,36,32,56,32,40,80,56] #Factory merits given per room
        self.gainLaffSeq=Sequence(Func(vpMaxer.restock.gainLaff),Wait(3.0))
        self.attackSeq=Sequence(Func(vpMaxer.restock.restock),Wait(1.0),Func(vpMaxer.otherFunctions.attack),Wait(1.0))
        
        FactoryExterior.FactoryExterior.__init__=lambda *args: self.newFactoryInit(*args)
        DistributedFactory.DistributedFactory.__init__=lambda *args: self.newDistributedFactoryInit(*args)
        DistributedBattleFactory.DistributedBattleFactory.enterReward=lambda newSelf,*args:self.newEnterReward(newSelf,*args)
        base.cr.doFind('SafeZone').d_enterSafeZone=lambda *args: self.newSafeZone(*args)
        base.localAvatar.died=lambda *args: self.newSafeZone(*args)
        DistributedBattleFactory.DistributedBattleFactory.d_toonDied=lambda *args: self.newSafeZone(*args)
        DistributedBattleFactory.DistributedBattleFactory.enterFactoryReward=lambda newSelf,*args:self.newEnterFactoryReward(newSelf,*args)
                
    def enterBattle(self):
        '''
        Enter battle is the same as enterRandomBattle in
        OtherFunctions and was written by Cody but
        slightly modified to work with the Factory Autoer.
        '''
    
        if base.localAvatar.getHp()>0:
            if base.cr.doFindAll('battle')==[]:
                battles = []
                cogList = base.cr.doFindAll("render")
                for x in cogList:
                    if isinstance(x, DistributedFactorySuit) or isinstance(x, DistributedSuit):
                        if x.activeState == 6:
                            battles.append(x)
                try:
                    if battles != []:
                        battle=battles[0]
                        pos, hpr = battle.getPos(), battle.getHpr()
                        vpMaxer.otherFunctions.walk()
                        vpMaxer.restock.wasInBattle=False
                        base.localAvatar.setPosHpr(pos, hpr)
                        battle.d_requestBattle(pos, hpr)
                        return True
                    else:
                        self.warpToZone(self.roomsNeeded[self.roomNum])
                        return False
                except:
                    return False
            else:
                return False
        else:
            return False
    
    def newEnterReward(self,newSelf,*args):
        '''
        Enter battle is the same as enterRandomBattle in
        OtherFunctions and was written by Cody but
        slightly modified to work with the Factory Autoer.
        '''
        
        self.oldEnterReward(newSelf,*args)
        if vpMaxer.otherFunctions.shouldContinue:
            newSelf.d_rewardDone(base.localAvatar.doId)
            vpMaxer.otherFunctions.walk()
            vpMaxer.autoerGui.display.newLine('Finished Factory Battle '+str(self.roomNum))
            if self.roomNum>=len(self.roomsNeeded):
                self.attackSeq.finish()
                self.gainLaffSeq.finish()
                self.generateAgain()
                vpMaxer.autoerGui.display.newLine('Error in completing factory')
                vpMaxer.autoerGui.display.newLine('No merits Recieved')
                Sequence(Wait(1),Func(vpMaxer.otherFunctions.walk),Func(vpMaxer.otherFunctions.teleBack)).start()
            else:
                Sequence(Wait(5),Func(self.enterBattle)).start()
    
    def newEnterFactoryReward(self,newSelf,*args):
        self.oldEnterFactoryReward(newSelf,*args)
        if vpMaxer.otherFunctions.shouldContinue:
            self.attackSeq.finish()
            self.gainLaffSeq.finish()
            self.generateAgain()
            vpMaxer.autoerGui.display.newLine('Completed Factory')
            Sequence(Wait(1),Func(vpMaxer.otherFunctions.walk),Func(vpMaxer.otherFunctions.teleBack)).start()
                
    def newFactoryInit(self,*args):
        '''
        Used to tell the maxer that the toon
        has entered the Factory Lobby.
        '''
        
        self.oldFactoryInit(*args)
        if vpMaxer.otherFunctions.shouldContinue:
            vpMaxer.restock.restock()
            Sequence(Wait(2),Func(self.enterElevator)).start()
        
    def newDistributedFactoryInit(self,*args):
        '''
        Used to tell the maxer that the
        toon has entered the Factory
        '''
        
        self.oldDistributedFactoryInit(*args)
        if vpMaxer.otherFunctions.shouldContinue:
            vpMaxer.otherFunctions.walk()
            self.attackSeq.loop()
            self.gainLaffSeq.loop()
            self.roomNum=0
            self.workOutRoomsNeeded()
            vpMaxer.autoerGui.display.newLine('Entering Factory')
            Sequence(Wait(2),Func(self.warpToZone,self.roomsNeeded[self.roomNum])).start()
    
    def workOutRoomsNeeded(self):
        '''
        Used to work out the number of battle
        the Autoer needs to do in order to
        get the correct amount of merits
        for the user
        '''
        
        self.roomsNeeded=[]
        meritsNeeded=vpMaxer.otherFunctions.getMeritsLeft()
        meritsNeeded-=self.roomValues[-1]
        for i in range(7):
            if meritsNeeded>0:
                self.roomsNeeded.append(self.zones[i])
                meritsNeeded-=self.roomValues[i]
            else:
                break
        self.roomsNeeded.append(self.zones[-1])
            
    def warpToZone(self,zone):
        for factory in base.cr.doFindAll('Factory'):
            if hasattr(factory, 'warpToZone'):
                factory.warpToZone(zone)
                vpMaxer.autoerGui.display.newLine('Warping to Room '+str(self.roomNum+1))
                self.roomNum+=1
        Sequence(Wait(1),Func(self.enterBattle)).start()
    
    def newSafeZone(self,*args):
        '''
        Used to hook functions they are called the
        walk function is called to stop the toon from
        teleporting away and the wasInBattle bool set
        to true so the gain laff function will go back
        into the battle when it has full laff.
        '''
        
        vpMaxer.otherFunctions.walk()
        vpMaxer.restock.wasInBattle=True
        vpMaxer.autoerGui.display.newLine('Died, recovering')
        
    def preTele(self):
        '''
        The lines in pretele are written by
        Peter to stop the game from generating
        those objects and stopping the toons
        head from moving.
        '''
        
        DistributedTrolley.DistributedTrolley.__init__ = newInit
        DistributedPartyGate.DistributedPartyGate.__init__ = newInit
        DistributedDoor.DistributedDoor.__init__ = newInit
        base.localAvatar.stopLookAroundNow()
            
    def generateAgain(self):
        '''
        Generate again fixes the functions back
        to what they were before importing the script
        '''
        
        DistributedTrolley.DistributedTrolley.__init__ = oldTrolleyInit
        DistributedPartyGate.DistributedPartyGate.__init__ = oldPartyInit
        DistributedDoor.DistributedDoor.__init__ = oldDoorInit
        base.localAvatar.findSomethingToLookAt = vpMaxer.restock.oldFindSomethingToLookAt
        ToonHead.ToonHead._ToonHead__lookAround = vpMaxer.restock.oldLookAround
             
    def goFactory(self):
        '''
        Sets the position to the Factory tunnel
        '''
        
        vpMaxer.otherFunctions.walk()
        vpMaxer.autoerGui.display.newLine('Heading to the factory')
        base.localAvatar.setPos(167.151, -157.024, -0.64781)
        
    def enterElevator(self):
        '''
        Invites its self to a boarding group and then requests to
        leave via the front entrance elevator
        '''
    
        for elevator in base.cr.doFindAll("Elevator"):
            if elevator.getDestName()=='Front Entrance':
                vpMaxer.otherFunctions.walk()
                base.localAvatar.collisionsOff()
                vpMaxer.autoerGui.display.newLine('Teleporting to Factory')
                base.cr.doFind('Boarding').sendUpdate('requestInvite',[base.localAvatar.doId])
                base.cr.doFind('Boarding').sendUpdate('requestGoToSecondTime',[elevator.doId])
                return
                
    def revertFunctions(self):
        DistributedFactoryElevatorExt.DistributedFactoryElevatorExt.__init__=self.oldFactoryElevatorInit
        DistributedFactory.DistributedFactory.__init__=self.oldDistributedFactoryInit
        DistributedBattleFactory.DistributedBattleFactory.enterReward=self.oldEnterReward
        DistributedBattleFactory.DistributedBattleFactory.enterFactoryReward=self.oldEnterFactoryReward
        base.cr.doFind('SafeZone').d_enterSafeZone=lambda *args: None
        base.localAvatar.died=lambda *args: None
        DistributedBattleFactory.DistributedBattleFactory.d_toonDied=lambda *args: None
        self.generateAgain()
        
class VPMaxer:
    def __init__(self):
        self.restock=restock()
        self.otherFunctions=OtherFunctions()
        self.vpAutoer=VpAutoer()
        self.factoryAutoer=FactoryAutoer(self)
        self.autoerGui=AutoerGui('VP Maxer',['Run Time',"Number of VP's","VP's/Hour",'Suit','Merits needed'],\
                                ['self.hours+":"+self.minutes+":"+self.seconds','str(vpMaxer.otherFunctions.bossCount)',\
                                'str(self.workOutNumberAnHour(vpMaxer.otherFunctions.bossCount))',\
                                'str(vpMaxer.otherFunctions.numberToSuit[base.localAvatar.cogTypes[3]])+" lvl "+str(base.localAvatar.cogLevels[3]+1)','str(vpMaxer.otherFunctions.getMeritsLeft())'],\
                                'VP MXR','sell')
        
    def revert(self):
        self.restock.revertFunctions()
        self.factoryAutoer.revertFunctions()
        self.vpAutoer.revertFunctions()
        self.otherFunctions.revertFunctions()
        self.autoerGui.destroy()
        DistributedNPCFisherman.DistributedNPCFisherman.handleCollisionSphereEnter=oldHandleEnterCollisionSphereFisherman
        DistributedNPCPartyPerson.DistributedNPCPartyPerson.handleCollisionSphereEnter=oldHandleEnterCollisionSphereParty
        DistributedNPCFisherman.DistributedNPCFisherman.announceGenerate=oldFisherAnnounceGenerate
        DistributedNPCPartyPerson.DistributedNPCPartyPerson.announceGenerate=oldPartyPlannerAnnounceGenerate

global vpMaxer
vpMaxer=VPMaxer()