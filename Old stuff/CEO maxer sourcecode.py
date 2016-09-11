#The CEO maxer written by freshollie
#If any of the credits in this are wrong
#please inform me via a youtube inbox

#I'm sorry that in the past I haven't given credit where credit is due
#but I didn't think it was that much of an issue.

import random #Random used in the enter battle functions to enter a random battle
from direct.interval.IntervalGlobal import * #Used for Sequences
from direct.distributed import DistributedObject #Used to hook the send update
from toontown.distributed import ToontownClientRepository #Used to hook the 'dumpAllSSubShardObjects'
from toontown.battle import DistributedBattleFinal #Used as a hook
from toontown.toonbase import ToontownBattleGlobals #Used to skip battle movies
from toontown.toon import * #Lots of these modules are used in hooks
from toontown.battle import DistributedBattle #Lots of the functions in here are hooked
from toontown.coghq import DistributedCountryClubBattle #Some functions in here are hooked
from toontown.coghq import DistributedCountryClub #Used to hook the __init__ function
from toontown.coghq import DistributedGolfGreenGame #Used to hook the enter function
from toontown.coghq import DistributedCogHQDoor #Used to hook the __init__ function
from toontown.coghq import CogDisguiseGlobals #Used to work out how many stocks you need
from toontown.suit.DistributedMintSuit import DistributedMintSuit #Used to work out if a render is a cog inside the countryclub
from toontown.suit.DistributedSuit import DistributedSuit #Used to work out if a render is a cog in cashbot hq
from toontown.suit import DistributedBossbotBoss #Lots of functions in here used as hooks
from toontown.safezone import DDPlayground #Used to hook the __init__ function to work out if you have died
from toontown.safezone import DistributedPartyGate #Used and imported by Peter's (Lifeless') 'toonup anywhere' to hook the generation function
from toontown.safezone import DistributedTrolley #Used and imported by Peter's (Lifeless') 'toonup anywhere' to hook the generation function
from toontown.building import DistributedDoor #Used and imported by Peter's (Lifeless') 'toonup anywhere' to hook the generation function

ToontownBattleGlobals.SkipMovie=1 #Used and found in the magic words to enable 'SMB' (Skip battle animations) This mainly skips the cog adjustments
DistributedToon.reconsiderCheesyEffect=lambda *x,**kwds:None #Sometimes while boarding an elevator this can cause problems
ToontownClientRepository.ToontownClientRepository.dumpAllSSubShardObjects=lambda self: None #This stops interests from being unloaded when you change
                                                                                            #an area meaning that toonup anywhere can be used in
                                                                                            #a bossbattle or any factory

faceOffHook = lambda self, ts, name, callback:self.d_faceOffDone(self)
DistributedCountryClubBattle.DistributedCountryClubBattle._DistributedLevelBattle__faceOff = faceOffHook #Used to hook the faceoff of country club (doesn't work properly)
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
        self.firstTrack=2
        self.secondTrack=0
        self.thirdTrack=4
        self.fourthTrack=3
        self.desiredLevel1=5
        self.desiredLevel2=4
        self.desiredLevel3=5
        self.desiredLevel4=5
        self.desiredInv='\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        #^ A premade inventory to buy Level 5 Toonup level 6 lure and level 6 throw
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
                ceoMaxer.countryClubAutoer.preTele()
                self.interest1=base.cr.addInterest(base.localAvatar.defaultShard, 9000, 5, None)
                self.interest2=base.cr.addInterest(base.localAvatar.defaultShard, 3000, 5, None)
                self.unloaded=False
            self.collectLaff()
        if self.wasInBattle:
            ceoMaxer.countryClubAutoer.enterBattle()
     
    def loadGagshop(self):       
        '''
        Load Gagshop Written by Peter
        and found in his building autoer.
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
    oldDockInit=DDPlayground.DDPlayground.__init__  #Used to show that you have teleported to Donalds Dock playground (Could have died)
    oldHqDoorInit=DistributedCogHQDoor.DistributedCogHQDoor.__init__ #Used to show that you have teleported to a cog hq (Bossbot or cashbot)
    oldEnterReward=DistributedBattle.DistributedBattle.enterReward #Used to show that you have finish a battle
    oldDenyBattle=DistributedSuit.denyBattle #Used to show that the cog has denied you a battle
    oldSendUpdate=DistributedObject.DistributedObject.sendUpdate #Used to skip some of the movies when you request attack
    oldEnterHealth=HealthForceAcknowledge.HealthForceAcknowledge.enter #Used to show that you weren't at full health when you tried to teleport out of the playground
    
    def __init__(self):
        self.shouldContinue=False #Used to let the hooks know if the script is actually running or not
        self.bossCount=0
        self.limit10=True #Used to limit the Ceo boss count to only 10 before it stops (To stop bans)
        self.onlyClub=False #Used to say that the user only wants to do the country clubs (If they want to completed tasks)
        self.isHealing=False #Used to define that the user is trying to heal so 
        self.numberToSuit={0:'Flunky',1:'Pencil Pusher',2:'Yesman',3:'Micromanager',
                           4:'Downsizer',5:'Head Hunter',6:'Corporate Raider',7:'The Big Cheese'} #Used by the gui
        DDPlayground.DDPlayground.__init__=lambda *args:self.newDockInit(*args)
        DistributedCogHQDoor.DistributedCogHQDoor.__init__=lambda *args: self.newHqDoorInit(*args) #Used to hook the function. Syntax I have used can be found in lots of other
                                                                                                   #scripts where people have hooked functions
        DistributedBattle.DistributedBattle.enterReward=lambda newSelf,*args: self.newEnterReward(newSelf,*args)
        DistributedSuit.denyBattle=lambda *args: self.newDenyBattle(*args)
        HealthForceAcknowledge.HealthForceAcknowledge.enter=lambda newSelf,hplevel: self.newEnterHealth(newSelf,hplevel)

    def attack(self):
        '''
        Syntax used can be found in the original gag trainer
        but has been very much modified to suit the purpose of
        the Country Club Autoer
        '''
        try:
            for battle in base.cr.doFindAll('battle'):
                if base.localAvatar.inventory.inventory[ceoMaxer.restock.firstTrack][ceoMaxer.restock.desiredLevel1]>0:
                    battle.sendUpdate('requestAttack', [ceoMaxer.restock.firstTrack, ceoMaxer.restock.desiredLevel1, battle.suits[0].doId])
                else:
                    break
                    
                if base.localAvatar.getHp()<(base.localAvatar.getMaxHp()*0.75) or self.isHealing:
                
                    if base.localAvatar.inventory.inventory[ceoMaxer.restock.secondTrack][ceoMaxer.restock.desiredLevel2]>0:
                        battle.sendUpdate('requestAttack', [ceoMaxer.restock.secondTrack, ceoMaxer.restock.desiredLevel2, base.localAvatar.doId])
                    else:
                        break
                        
                    if base.localAvatar.inventory.inventory[ceoMaxer.restock.thirdTrack][ceoMaxer.restock.desiredLevel3]>0:
                        battle.sendUpdate('requestAttack', [ceoMaxer.restock.thirdTrack, ceoMaxer.restock.desiredLevel3, battle.suits[0].doId])
                    else:
                        break
                        
                else:
                    if base.localAvatar.inventory.inventory[ceoMaxer.restock.thirdTrack][ceoMaxer.restock.desiredLevel3]>0:
                        battle.sendUpdate('requestAttack', [ceoMaxer.restock.thirdTrack, ceoMaxer.restock.desiredLevel3, battle.suits[0].doId])
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
        
    def newDockInit(self,*args):
        '''
        Used to show that the toon has been teleported
        to donalds dock
        '''
        self.oldDockInit(*args)
        if self.shouldContinue: 
            ceoMaxer.countryClubAutoer.gainLaffSeq.finish()
            ceoMaxer.countryClubAutoer.attackSeq.finish()
            self.checkStocks()
    
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
                Sequence(Wait(2),Func(self.checkStocks)).start()
        except:
            pass
     
    def checkWhatToDo(self):
        '''
        Used because both cashbot hq and bossbot hq
        have a coghq door so the autoer needs to
        check where it is because it can find out
        which is it suppose to be doing
        '''
        
        self.walk()
        if base.cr.doFind('CogKart') or base.localAvatar.getZoneId()!=12000:
            self.checkStocks()
        else:
            ceoMaxer.countryClubAutoer.attackSeq.loop()
            self.enterRandomBattle()
         
    def newHqDoorInit(self,*args):
        '''
        Used to show that the toon has teleported
        to either bossbot hq or cashbot hq
        '''
        
        self.oldHqDoorInit(*args)
        if self.shouldContinue and base.localAvatar.getZoneId()!=10100:
            Sequence(Wait(3),Func(self.checkWhatToDo)).start()
    
    def newEnterReward(self,newSelf,*args):
        '''
        Used when the Maxer needs to gain back laff 
        to do the country clubs so when it kills
        a cog it has to check if it is the right hp
        level or if it needs to do another cog
        '''
        
        self.oldEnterReward(newSelf,*args)
        if base.localAvatar.doId not in newSelf.toons:
            return
        if ceoMaxer.otherFunctions.shouldContinue:
            if base.localAvatar.getHp()>105:
                self.isHealing=False
                ceoMaxer.countryClubAutoer.attackSeq.finish()
                Sequence(Wait(1),Func(self.teleBack)).start()
            else:
                Sequence(Wait(1),Func(self.enterRandomBattle)).start()
     
    def newDenyBattle(self,*args):
        '''
        Used to go to the next cog if the cog denys the battle
        '''
    
        self.oldDenyBattle(*args)
        if self.shouldContinue and self.isHealing:
            self.enterRandomBattle()
        
    def checkStocks(self):
        '''
        Written by me it is a function to determine
        what the maxer needs to do with the toon next
        it works everything out depeding of the toons
        stocks needed and the settings they have chosen.
        '''
        
        if self.onlyClub:
            base.localAvatar.cogMerits[0]=-4000
        if self.limit10 and self.bossCount>9:
            self.shouldContinue=False
        if self.shouldEnd:
            self.shouldContinue=False
        if self.haveJb():
            if self.shouldContinue:
                if self.getStocksLeft()==0 and not self.onlyClub:
                    if base.cr.doFind('DistributedCogHQDoor') and base.localAvatar.getZoneId()>=10000 and base.localAvatar.getZoneId()<10100:
                        ceoMaxer.ceoAutoer.start()
                    else:
                        ceoMaxer.restock.restock()
                        ceoMaxer.restock.collectLaff()
                        self.walk()
                        ceoMaxer.autoerGui.display.newLine('Teleporting to bossbot hq')
                        Sequence(Wait(2),Func(self.teleBack)).start()
                else:
                    if base.cr.doFind('DistributedCogHQDoor') and base.localAvatar.getZoneId()>=10000 and base.localAvatar.getZoneId()<10100:
                        if base.localAvatar.getHp()>105:
                            ceoMaxer.countryClubAutoer.start()
                        else:
                            ceoMaxer.autoerGui.display.newLine('Gaining laff back')
                            Sequence(Wait(2),Func(self.teleBack,12000)).start()
                    else:
                        ceoMaxer.restock.restock()
                        ceoMaxer.restock.collectLaff()
                        self.walk()
                        if base.localAvatar.getHp()>105:
                            ceoMaxer.autoerGui.display.newLine('Teleporting to bossbot hq')
                            Sequence(Wait(2),Func(self.teleBack)).start()
                        else:
                            self.isHealing=True
                            ceoMaxer.autoerGui.display.newLine('Gaining laff back')
                            Sequence(Wait(2),Func(self.teleBack,12000)).start()
            else:
                ceoMaxer.restock.noToons.finish()
                try:
                    base.cr.removeInterest(ceoMaxer.restock.interest1)
                    base.cr.removeInterest(ceoMaxer.restock.interest2)
                    ceoMaxer.restock.unloaded=True
                except:
                    pass
                base.localAvatar.setSystemMessage(0,"Thanks for using freshollie's ceo maxer")
                ceoMaxer.autoerGui.display.newLine('Stopped')
        else:
            base.localAvatar.setSystemMessage(0,'You have run out of jelly beans, please use the fishing code to gain some')
            ceoMaxer.autoerGui.display.newLine('Stopped')
    
    def getStocksLeft(self):
        '''
        Uses the CogDisguiseGlobals to work out how many
        stock options te toon needs to gain before it can
        do the ceo.
        '''
        
        return CogDisguiseGlobals.getTotalMerits(base.localAvatar,0)-base.localAvatar.cogMerits[0]

    def walk(self):
        '''
        Walk is a function built into magic words
        which I used instead of sendOpenTalk('~walk').
        '''
        
        try:
            base.cr.playGame.getPlace().fsm.forceTransition('walk')
        except:
            pass
       
    def teleBack(self,zone=10000):
        '''
        TeleBack used to teleport to a playground or cog
        hq if no zone is given it teleports to bossbot
        hq.
        '''
        
        try:
            self.walk()
            base.cr.playGame.getPlace().handleBookCloseTeleport(zone, zone)
        except:
            pass
                
    def onlyDoClub(self):
        '''
        Written so that the user can choose if they want to do the Country Club only.
        '''
        
        self.onlyClub=True
        base.localAvatar.setSystemMessage(0,'CEO maxer set to only do the Country Club')
    
    def doBoth(self):
        self.onlyClub=False
        base.localAvatar.setSystemMessage(0,'CEO maxer set to do both the Country Club and the CEO')
        
    def haveJb(self):
        '''
        Checks if the user has more than 100
        jelly beans so they don't run out during
        a Country Club.
        '''
        
        if base.localAvatar.cogLevels[0]==49:
            return True
        elif base.localAvatar.getTotalMoney()<100:
            return False
        else:
            return True
           
    def enterRandomBattle(self):
        '''
        Written by Cody originally to find a cog to battle.
        '''
        
        if base.cr.doFindAll('battle')==[]:
            battles = []
            cogList = base.cr.doFindAll("render")
            for x in cogList:
                if isinstance(x, DistributedSuit):
                    if x.activeState == 6:
                        battles.append(x)
            if battles != []:
                self.walk()
                battle = random.choice(battles)
                pos, hpr = battle.getPos(), battle.getHpr()
                base.localAvatar.setPosHpr(pos, hpr)
                battle.d_requestBattle(pos, hpr)
            else:
                pass
        
    def limiterOn(self):
        self.limit10=True
        base.localAvatar.setSystemMessage(0,'CEO maxer set to be limited to only 10 CEOs')
    
    def limiterOff(self):
        self.limit10=False
        base.localAvatar.setSystemMessage(0,'CEO maxer set to unlimited number of CEOs')
        
    def setStop(self):
        self.shouldEnd=True
        base.localAvatar.setSystemMessage(1,"The Autoer will stop at the end of this run")
        ceoMaxer.autoerGui.stopTimer()
    
    def start(self):
        DistributedObject.DistributedObject.sendUpdate=lambda newself, fieldName, args=[], sendToId=None: self.sendUpdateHook(newself, fieldName, args, sendToId)
        self.bossCount=0
        self.shouldContinue=True
        self.shouldEnd=False
        ceoMaxer.autoerGui.startTimer()
        emptyShardList=[]
        for shard in base.cr.activeDistrictMap:
            if base.cr.activeDistrictMap[shard].avatarCount<30:
                emptyShardList.append(shard)
        if emptyShardList==[]:
            emptyShardList=[650000000, 754000000, 608000000, 756000000, 658000000, 712000000, 360000000, 410000000, 620000000, 454000000, 726000000, 362000000, 688000000, 316000000]
        if base.localAvatar.defaultShard not in emptyShardList:
            ceoMaxer.autoerGui.display.newLine('TPing to an empty district')
            base.cr.playGame.getPlace().requestTeleport(10000,10000,random.choice(emptyShardList),base.localAvatar.doId)
        else:
            self.checkStocks()
        ceoMaxer.restock.noToons.loop()
    
    def revertFunctions(self):
        '''
        Revert to the original functions so other scripts can be loaded.
        '''
        DDPlayground.DDPlayground.__init__=self.oldDockInit
        DistributedCogHQDoor.DistributedCogHQDoor.__init__=self.oldHqDoorInit
        DistributedBattle.DistributedBattle.enterReward=self.oldEnterReward
        DistributedSuit.denyBattle=self.oldDenyBattle
        DistributedObject.DistributedObject.sendUpdate=self.oldSendUpdate
        HealthForceAcknowledge.HealthForceAcknowledge.enter=self.oldEnterHealth

class CeoAutoer:
    '''
    Ceo Autoer written by me with some functions written by others.
    '''
    
    #Used as hooks to find out where your toon is during the bossbattle
    oldBossEnterElevator=DistributedBossbotBoss.DistributedBossbotBoss.enterElevator
    oldEnterBattleTwo=DistributedBossbotBoss.DistributedBossbotBoss.enterBattleTwo
    oldEnterBattleFour=DistributedBossbotBoss.DistributedBossbotBoss.enterBattleFour
    oldEnterPrepareBattleTwo=DistributedBossbotBoss.DistributedBossbotBoss.enterPrepareBattleTwo
    oldEnterPrepareBattleThree=DistributedBossbotBoss.DistributedBossbotBoss.enterPrepareBattleThree
    oldEnterPrepareBattleFour=DistributedBossbotBoss.DistributedBossbotBoss.enterPrepareBattleFour
    oldEnterEpilogue=DistributedBossbotBoss.DistributedBossbotBoss.enterEpilogue
    oldEnterWaitForInput=DistributedBattleFinal.DistributedBattleFinal.enterWaitForInput
    oldBossEnterIntro=DistributedBossbotBoss.DistributedBossbotBoss.enterIntroduction
    oldAvatarExit=DistributedCogHQDoor.DistributedCogHQDoor.avatarExit
    
    def __init__(self):
        DistributedCogHQDoor.DistributedCogHQDoor.avatarExit=lambda newSelf,id: self.newAvatarExit(newSelf,id)
        DistributedBossbotBoss.DistributedBossbotBoss.enterElevator=lambda newSelf: self.newBossEnterElevator(newSelf)
        DistributedBossbotBoss.DistributedBossbotBoss.enterIntroduction=lambda newSelf,*args: self.newBossEnterIntro(newSelf,*args)
        DistributedBossbotBoss.DistributedBossbotBoss.enterBattleFour=lambda newSelf: self.newEnterBattleFour(newSelf)
        DistributedBossbotBoss.DistributedBossbotBoss.enterBattleTwo=lambda newSelf: self.newEnterBattleTwo(newSelf)
        DistributedBattleFinal.DistributedBattleFinal.enterWaitForInput=lambda *args: self.newEnterWaitForInput(*args)
        DistributedBossbotBoss.DistributedBossbotBoss.enterPrepareBattleThree=lambda newSelf: self.newEnterPrepareBattleThree(newSelf)
        DistributedBossbotBoss.DistributedBossbotBoss.enterPrepareBattleTwo=lambda newSelf: self.newEnterPrepareBattleTwo(newSelf)
        DistributedBossbotBoss.DistributedBossbotBoss.enterPrepareBattleFour=lambda newSelf: self.newEnterPrepareBattleFour(newSelf)
        DistributedBossbotBoss.DistributedBossbotBoss.enterEpilogue=lambda newSelf: self.newEnterEpilogue(newSelf)
    
    def newAvatarExit(self,newSelf,id):
        '''
        Gives the maxer the information that the toon has exited a cog hq door so the maxer
        can do what it needs to do which in this case is board the elevator.
        '''
        
        self.oldAvatarExit(newSelf,id)
        if base.cr.doFind('Elevator') and id==base.localAvatar.doId and ceoMaxer.otherFunctions.shouldContinue:
            ceoMaxer.otherFunctions.walk()
            ceoMaxer.autoerGui.display.newLine('Boarded CEO Elevator')
            base.cr.doFind('Elevator').sendUpdate('requestBoard')
    
    def newBossEnterIntro(self,newSelf,*args):
        '''
        When the function to enter the boss introduction
        the maxer automatically exits the introduction
        effectively skipping it.
        '''
        
        self.oldBossEnterIntro(newSelf,*args)
        if ceoMaxer.otherFunctions.shouldContinue:
            newSelf.exitIntroduction()
            ceoMaxer.autoerGui.display.newLine('Skipping CEO introduction')
    
    def newEnterPrepareBattleTwo(self,newSelf):
        '''
        The same idea as the introduction hook function.
        '''
        
        self.oldEnterPrepareBattleTwo(newSelf)
        if ceoMaxer.otherFunctions.shouldContinue:
            newSelf.exitPrepareBattleTwo()
            ceoMaxer.autoerGui.display.newLine('Skipping cutscene')
    
    def newEnterEpilogue(self,newSelf):
        '''
        When the boss enter epilogue function is called
        the bosscount gets 1 added to it and the toon gets
        teleported back.
        '''
        
        self.oldEnterEpilogue(newSelf)
        if ceoMaxer.otherFunctions.shouldContinue:
            ceoMaxer.otherFunctions.bossCount+=1
            ceoMaxer.otherFunctions.teleBack()
            ceoMaxer.autoerGui.display.newLine('Finished CEO')
    
    def newEnterPrepareBattleThree(self,newSelf):
        '''
        The same idea as the introduction hook function.
        '''
        
        self.oldEnterPrepareBattleThree(newSelf)
        newSelf.exitPrepareBattleThree()
        ceoMaxer.autoerGui.display.newLine('Skipping cutscene')
    
    def newEnterPrepareBattleFour(self,newSelf):
        '''
        The same idea as the introduction hook function.
        '''
        
        self.oldEnterPrepareBattleFour(newSelf)
        newSelf.exitPrepareBattleFour()
        ceoMaxer.autoerGui.display.newLine('Skipping cutscene')
    
    def destroyBattle(self):
        '''
        The battle exploit first founded by Pascal (http://www.youtube.com/user/leftylemonzilla)
        and has been used here to skip the cog battles in the ceo.
        '''
        
        base.cr.doFind('SafeZone').sendUpdate('enterSafeZone')
    
    def exploit(self):
        Sequence(Func(self.destroyBattle), Wait(.5), Func(ceoMaxer.otherFunctions.walk)).start()
    
    def newEnterWaitForInput(self,*args):
        '''
        When the cogs are ready to be attacked the exploit is ready to be used
        which is what this hook is for.
        '''
        
        self.oldEnterWaitForInput(*args)
        if ceoMaxer.otherFunctions.shouldContinue:
            self.exploit()
            ceoMaxer.autoerGui.display.newLine('Skipping Battle')
    
    def newBossEnterElevator(self,newSelf):
        '''
        The same idea as the introduction hook function.
        '''
        
        self.oldBossEnterElevator(newSelf)
        if ceoMaxer.otherFunctions.shouldContinue:
            ceoMaxer.autoerGui.display.newLine('Skipping Elevator')
            newSelf._DistributedBossCog__doneElevator()
    
    def newEnterBattleTwo(self,newSelf):
        '''
        This function is used to tell the user that it has to wait for the
        300 second timer.
        '''
        
        self.oldEnterBattleTwo(newSelf)
        ceoMaxer.autoerGui.display.newLine('Waiting for timer')
        
    def newEnterBattleFour(self,newSelf):
        '''
        This function is used to end the battle
        when it enters the last battle.
        '''
        
        self.oldEnterBattleFour(newSelf)
        self.endBattle(newSelf)
        
    def start(self):
        base.cr.doFind('DistributedCogHQDoor').sendUpdate('requestEnter')
        ceoMaxer.autoerGui.display.newLine('Starting the CEO')
        ceoMaxer.autoerGui.display.newLine('Entering Lobby')
        
    def endBattle(self,newSelf):
        '''
        This was not created by me but
        I don't actually know where it
        came from.
        '''
        
        newSelf.sendUpdate('hitBoss', [250])
        ceoMaxer.autoerGui.display.newLine('Killing CEO')
        newSelf.exitBattleFour()
        
    def revertFunctions(self):
        '''
        Revert to the original functions so other scripts can be loaded.
        '''
        
        DistributedBossbotBoss.DistributedBossbotBoss.enterElevator=self.oldBossEnterElevator
        DistributedBossbotBoss.DistributedBossbotBoss.enterBattleTwo=self.oldEnterBattleTwo
        DistributedBossbotBoss.DistributedBossbotBoss.enterBattleFour=self.oldEnterBattleFour
        DistributedBossbotBoss.DistributedBossbotBoss.enterPrepareBattleTwo=self.oldEnterPrepareBattleTwo
        DistributedBossbotBoss.DistributedBossbotBoss.enterPrepareBattleThree=self.oldEnterPrepareBattleThree
        DistributedBossbotBoss.DistributedBossbotBoss.enterPrepareBattleFour=self.oldEnterPrepareBattleFour
        DistributedBossbotBoss.DistributedBossbotBoss.enterEpilogue=self.oldEnterEpilogue
        DistributedBattleFinal.DistributedBattleFinal.enterWaitForInput=self.oldEnterWaitForInput
        DistributedBossbotBoss.DistributedBossbotBoss.enterIntroduction=self.oldBossEnterIntro
        DistributedCogHQDoor.DistributedCogHQDoor.avatarExit=self.oldAvatarExit
        
class CountryClubAutoer:
    oldCountryClubInit=DistributedCountryClub.DistributedCountryClub.__init__
    oldEnterReward=DistributedCountryClubBattle.DistributedCountryClubBattle.enterReward
    oldGolfGameToonEnter=DistributedGolfGreenGame.DistributedGolfGreenGame._DistributedGolfGreenGame__handleToonEnter
    oldEnterCountryClubReward=DistributedCountryClubBattle.DistributedCountryClubBattle.enterCountryClubReward
    
    def __init__(self,ceoMaxer): 
        self.attackSeq=Sequence(Func(ceoMaxer.restock.restock),Wait(1.0),Func(ceoMaxer.otherFunctions.attack),Wait(1.0))
        self.gainLaffSeq=Sequence(Func(ceoMaxer.restock.gainLaff),Wait(3.0))
        self.battleNum=1
        DistributedCountryClub.DistributedCountryClub.__init__=lambda *args:self.newCountryClubInit(*args)
        DistributedCountryClubBattle.DistributedCountryClubBattle.enterReward=lambda *args:self.newEnterReward(*args)
        DistributedGolfGreenGame.DistributedGolfGreenGame._DistributedGolfGreenGame__handleToonEnter=lambda *args:self.newGolfGameToonEnter(*args)
        base.cr.doFind('SafeZone').d_enterSafeZone=lambda *args: self.newSafeZone(*args)
        base.localAvatar.died=lambda *args: self.newSafeZone(*args)
        LocalToon.LocalToon.died=lambda *args: self.newSafeZone(*args)
        DistributedCountryClubBattle.DistributedCountryClubBattle.d_toonDied=lambda *args: self.newSafeZone(*args)
        DistributedCountryClubBattle.DistributedCountryClubBattle.enterCountryClubReward=lambda *args:self.newEnterCountryClubReward(*args)
    
    def setFrontThree(self):
        '''
        Sets the autoer to do the Front Three
        '''
        
        self.floorNumToKartRoomNum={0:17,1:17,2:18} #Tells the autoer the kart room number for the floor number
        self.battles=[1,3,5] #Tells the autoer the first battle num of each floor
        self.greenRoom=9 #Tells the autoer the green room number
        self.countryClubName='The Front Three' #Tells tge autoer the name of the Country Club

    def setMiddleSix(self):
        '''
        Sets the autoer to do the Middle Six
        '''
    
        self.greenRoom=29 
        self.battles=[1,3,5,7,9,11]
        self.floorNumToKartRoomNum={0:17,1:17,2:17,3:17,4:17,5:18}
        self.countryClubName='The Middle Six'
    
    def setBackNine(self):
        '''
        Sets the autoer to do the Back Nine
        '''
        
        self.greenRoom=39
        self.battles=[1,3,5,7,9,11,13,15,17]
        self.floorNumToKartRoomNum={0:17,1:17,2:17,3:17,4:17,5:17,6:17,7:17,8:18}
        self.countryClubName='The Back Nine'
        
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
        base.localAvatar.findSomethingToLookAt = ceoMaxer.restock.oldFindSomethingToLookAt
        ToonHead.ToonHead._ToonHead__lookAround = ceoMaxer.restock.oldLookAround

    def enterBattle(self):
        '''
        Enter battle is the same as enterRandomBattle in
        OtherFunctions and was written by Cody but
        slightly modified to work with the countryClubAutoer.
        '''
        
        if base.localAvatar.getHp()>0:
            ceoMaxer.restock.wasInBattle=False
            battles = []
            cogList = base.cr.doFindAll("render")
            for x in cogList:
                if isinstance(x, DistributedMintSuit):
                    if x.activeState == 6:
                        if self.battleNum in self.battles:
                            if x.doId not in base.cr.doFind('DistributedCountryClubRoom '+str(self.floorNumToKartRoomNum[base.cr.doFind('DistributedCountryClub.DistributedCountryClub').floorNum])).suitIds:
                                battles.append(x)
                        else:
                            if x.doId in base.cr.doFind('DistributedCountryClubRoom '+str(self.floorNumToKartRoomNum[base.cr.doFind('DistributedCountryClub.DistributedCountryClub').floorNum])).suitIds:
                                battles.append(x)
                            
            if battles != []:
                battle=battles[0]
                pos, hpr = battle.getPos(), battle.getHpr()
                base.localAvatar.setPosHpr(pos, hpr)
                battle.d_requestBattle(pos, hpr)
                ceoMaxer.autoerGui.display.newLine('Entering Battle '+str(self.battleNum))
                return True
            else:
                return False
        else:
            return True
    
    def doMoles(self):
        '''
        Do Moles is a function that is found in
        multihack but was modified to work with
        people who live outside of the US (Like me).
        '''
        
        moleSeq=Sequence()
        ceoMaxer.autoerGui.display.newLine('Entering Floor '+str(base.cr.doFind('DistributedCountryClub.DistributedCountryClub').floorNum+1))
        ceoMaxer.autoerGui.display.newLine('Completing Mole Field')
        for moleField in base.cr.doFindAll('MoleField'):
            for i in range(moleField.numMoles):
                moleSeq.append(Func(moleField.sendUpdate,'whackedMole', [0, i]))
                moleSeq.append(Wait(0.05))
        moleSeq.append(Wait(0.5))
        moleSeq.append(Func(self.enterBattle))
        moleSeq.start()
            
    def doGolf(self):
        '''
        Do Golf also found in multihack
        but didn't need to be modified.
        '''
        
        gameSeq=Sequence()
        ceoMaxer.autoerGui.display.newLine('Completing Golf')
        for greenGame in base.cr.doFindAll('GolfGreenGame'):
            for i in range(greenGame.boardsLeft):
                gameSeq.append(Func(greenGame.sendUpdate,'requestBoard', [1]))
        gameSeq.append(Wait(1))
        gameSeq.append(Func(self.endFloor))
        gameSeq.start()
        
    def enterCountryClub(self):
        '''
        Enter Country Club is a funtion which puts
        you into the write kart depeding on which
        country club needs to be done.
        '''
        
        ceoMaxer.otherFunctions.walk()
        for kart in base.cr.doFindAll('DistributedCogKart'):
            if kart.getDestName()==self.countryClubName:
                kart.handleEnterSphere(base.localAvatar.doId)
    
    def boardKart(self):
        '''
        Board kart is a function used to board the kart
        at the end of a CountryClub floor.
        '''
        
        ceoMaxer.otherFunctions.walk()
        for kart in base.cr.doFindAll('DistributedClubElevator'):
            kart.handleEnterSphere(base.localAvatar.doId)
            ceoMaxer.autoerGui.display.newLine('Boarding Kart')
            return
        ceoMaxer.autoerGui.display.newLine('Finishing Country Club')
        ceoMaxer.otherFunctions.teleBack()
        self.generateAgain()
        self.attackSeq.finish()
        self.gainLaffSeq.finish()
    
    def warpToRoom(self,room):
        if base.cr.doFind('DistributedCountryClub.DistributedCountryClub'):
            base.cr.doFind('DistributedCountryClub.DistributedCountryClub').warpToRoom(room)
                
    def newCountryClubInit(self,*args):
        '''
        Used to tell the maxer that the toon has entered the
        CountryClub so it can start.
        '''
        
        self.oldCountryClubInit(*args)
        self.attackSeq.loop()
        self.gainLaffSeq.loop()
        Sequence(Wait(1),Func(self.doMoles)).starfft()
    
    def newGolfGameToonEnter(self,*args):
        '''
        Used to tell the maxer that the toon has entered the
        Golf Game so it can finish the game
        '''
        
        self.oldGolfGameToonEnter(*args)
        if ceoMaxer.otherFunctions.shouldContinue:
            Sequence(Wait(1),Func(self.doGolf)).start()
    
    def newEnterReward(self,*args):
        '''
        Used to tell the maxer that the toon has finsihed
        the battle so toon can go to the next battle.
        '''
        
        self.oldEnterReward(*args)
        if ceoMaxer.otherFunctions.shouldContinue:
            ceoMaxer.autoerGui.display.newLine('Finished Battle '+str(self.battleNum))
            base.cr.doFind('battle').d_rewardDone(base.localAvatar.doId)
            self.battleNum+=1
            ceoMaxer.otherFunctions.walk()
            if not self.enterBattle():
                self.warpToRoom(self.greenRoom)
                ceoMaxer.otherFunctions.walk()
    
    def newSafeZone(self,*args):
        '''
        Used to hook functions they are called the
        walk function is called to stop the toon from
        teleporting away and the wasInBattle bool set
        to true so the gain laff function will go back
        into the battle when it has full laff.
        '''
        
        ceoMaxer.otherFunctions.walk()
        ceoMaxer.restock.wasInBattle=True
        ceoMaxer.autoerGui.display.newLine('Died, recovering')

    def newEnterCountryClubReward(self,*args):
        '''
        Used to tell the maxer that the toon has finsihed
        the CountryClub so it can teleport out
        '''
        
        self.oldEnterCountryClubReward(*args)
        if ceoMaxer.otherFunctions.shouldContinue:
            ceoMaxer.otherFunctions.walk()
            ceoMaxer.autoerGui.display.newLine('Finished Battle '+str(self.battleNum))
            if not self.enterBattle():
                self.warpToRoom(self.greenRoom)
                Sequence(Wait(0.5),Func(ceoMaxer.otherFunctions.walk)).start()

    def endFloor(self):
        ceoMaxer.otherFunctions.walk()
        self.warpToRoom(self.floorNumToKartRoomNum[base.cr.doFind('DistributedCountryClub.DistributedCountryClub').floorNum])
        Sequence(Wait(0.5),Func(self.boardKart)).start()
    
    def start(self):
        self.battleNum=1
        if ceoMaxer.otherFunctions.getStocksLeft()>953:
            ceoMaxer.autoerGui.display.newLine('Entering The Back Nine')
            self.setBackNine()
        elif ceoMaxer.otherFunctions.getStocksLeft()>386:
            ceoMaxer.autoerGui.display.newLine('Entering The Middle Six')
            self.setMiddleSix()
        else:
            ceoMaxer.autoerGui.display.newLine('Entering The Front Three')
            self.setFrontThree()
        Sequence(Wait(1),Func(self.enterCountryClub)).start()
    
    def revertFunctions(self):
        DistributedCountryClub.DistributedCountryClub.__init__=self.oldCountryClubInit
        DistributedCountryClubBattle.DistributedCountryClubBattle.enterReward=self.oldEnterReward
        DistributedGolfGreenGame.DistributedGolfGreenGame._DistributedGolfGreenGame__handleToonEnter=self.oldGolfGameToonEnter
        DistributedCountryClubBattle.DistributedCountryClubBattle.enterCountryClubReward=self.oldEnterCountryClubReward
        base.cr.doFind('SafeZone').d_enterSafeZone=lambda *args: None
        base.localAvatar.died=lambda *args: None
        LocalToon.LocalToon.died=lambda *args: None
        DistributedCountryClubBattle.DistributedCountryClubBattle.d_toonDied=lambda *args: None
        self.generateAgain()

class CEOMaxer:
    def __init__(self):
        self.restock=restock()
        self.otherFunctions=OtherFunctions()
        self.ceoAutoer=CeoAutoer()
        self.countryClubAutoer=CountryClubAutoer(self)
        self.autoerGui=AutoerGui('CEO Maxer',['Run Time',"Number of ceo's","Ceo's/Hour",'Suit','Stocks needed'],\
                                ['self.hours+":"+self.minutes+":"+self.seconds','str(ceoMaxer.otherFunctions.bossCount)','str(self.workOutNumberAnHour(ceoMaxer.otherFunctions.bossCount))'\
                                ,'str(ceoMaxer.otherFunctions.numberToSuit[base.localAvatar.cogTypes[0]])+" Lvl "+str(base.localAvatar.cogLevels[0]+1)','str(ceoMaxer.otherFunctions.getStocksLeft())'],\
                                'CEO MXR','boss')
        
    def revert(self):
        self.restock.revertFunctions()
        self.countryClubAutoer.revertFunctions()
        self.ceoAutoer.revertFunctions()
        self.otherFunctions.revertFunctions()
        self.autoerGui.destroy()
        DistributedNPCFisherman.DistributedNPCFisherman.handleCollisionSphereEnter=oldHandleEnterCollisionSphereFisherman
        DistributedNPCPartyPerson.DistributedNPCPartyPerson.handleCollisionSphereEnter=oldHandleEnterCollisionSphereParty
global ceoMaxer
ceoMaxer=CEOMaxer()