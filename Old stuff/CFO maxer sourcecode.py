#The VP maxer written by freshollie
#If any of the credits in this are wrong
#please inform me via a youtube inbox (toontowninjecting)

#I'm sorry that in the past I haven't given credit where credit is due
#but I didn't think it was that much of an issue.

import random #Random used in the enter battle functions to enter a random battle
from direct.interval.IntervalGlobal import * #Used for Sequences
from direct.distributed import DistributedObject #Used to hook the send update
from toontown.distributed import ToontownClientRepository 
from toontown.battle import DistributedBattleFinal
from toontown.toonbase import ToontownBattleGlobals 
from toontown.toon import * #Lots of these modules are used in hooks
from toontown.battle import DistributedBattle 
from toontown.coghq import DistributedMintBattle #Used as a hook
from toontown.coghq import DistributedMint #Used as a hook
from toontown.coghq import DistributedCogHQDoor #Used as a hook
from toontown.coghq import CogDisguiseGlobals #Used to work out how many stocks you need
from toontown.suit.DistributedMintSuit import DistributedMintSuit #Used to work out if a render is an 
from toontown.suit.DistributedSuit import DistributedSuit 
from toontown.suit import DistributedCashbotBoss
from toontown.safezone import DLPlayground #Used and imported by Peter's (Lifeless') 'toonup anywhere' to hook the generation function
from toontown.safezone import DistributedPartyGate #Used and imported by Peter's (Lifeless') 'toonup anywhere' to hook the generation function
from toontown.safezone import DistributedTrolley #Used and imported by Peter's (Lifeless') 'toonup anywhere' to hook the generation function
from toontown.building import DistributedDoor #Used and imported by Peter's (Lifeless') 'toonup anywhere' to hook the generation function

ToontownBattleGlobals.SkipMovie=1 #Used and found in the magic words to enable 'SMB' (Skip battle animations) This mainly skips the cog adjustments
DistributedToon.reconsiderCheesyEffect=lambda *x,**kwds:None #Sometimes while boarding an elevator this can cause problems
ToontownClientRepository.ToontownClientRepository.dumpAllSSubShardObjects=lambda self: None #This stops interests from being unloaded when you change
                                                                                            #an area meaning that toonup anywhere can be used in
                                                                                            #a bossbattle or any factory

faceOffHook = lambda self, ts, name, callback:self.d_faceOffDone(self)
DistributedMintBattle.DistributedMintBattle._DistributedLevelBattle__faceOff = faceOffHook #Used to hook the faceoff of mint battles
DistributedBattle.DistributedBattle._DistributedBattle__faceOff = faceOffHook #Used to hook the face off of a normal battle


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
                cfoMaxer.mintAutoer.preTele()
                self.interest1=base.cr.addInterest(base.localAvatar.defaultShard, 9000, 5, None)
                self.interest2=base.cr.addInterest(base.localAvatar.defaultShard, 3000, 5, None)
                self.unloaded=False
            self.collectLaff()
        if self.wasInBattle:
            cfoMaxer.mintAutoer.enterBattle()
     
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
    oldDreamlandInit=DLPlayground.DLPlayground.__init__ #Use to show that the toon has been teleported to donalds dreamland
    oldHqDoorInit=DistributedCogHQDoor.DistributedCogHQDoor.__init__ #Used to show that the player has teleported to a cog hq
    oldEnterReward=DistributedBattle.DistributedBattle.enterReward #Used to show that the player has finished a battle
    oldDenyBattle=DistributedSuit.denyBattle #Used to show that the cog has denied the battle
    oldSendUpdate=DistributedObject.DistributedObject.sendUpdate #Used to skip some of the movies when you request attack
    oldEnterHealth=HealthForceAcknowledge.HealthForceAcknowledge.enter #Used to show that you weren't at full health when you tried to teleport out of the playground
    oldSetAnim=LocalToon.LocalToon.setAnimState #Used to make the player invisible when the set animstate function is called
    oldPostInvite=DistributedBoardingParty.DistributedBoardingParty.postInvite #Used to accept your own invite as soon as it is received
    
    def __init__(self):
        self.shouldContinue=False #Used to let the hooks know if the script is actually running or not
        self.bossCount=0
        self.onlyMint=False #Used to say that the user only wants to do the Mint (If they want to complete tasks)
        self.isHealing=False
        self.attackCogId=0
        self.canSetParentAgain=True
        self.numberToSuit={0:'Short Change',1:'Penny Pusher',2:'Tightwad',3:'Bean Counter',
                           4:'Number Cruncher',5:'Money Bags',6:'Loan Shark',7:'Robber Baron'} #Used by the gui
        DLPlayground.DLPlayground.__init__=lambda *args:self.newDreamlandInit(*args)#Used to hook the function. Syntax I have used can be found in lots of other
                                                                                    #scripts where people have hooked functions
        DistributedCogHQDoor.DistributedCogHQDoor.__init__=lambda *args: self.newHqDoorInit(*args)
        DistributedBattle.DistributedBattle.enterReward=lambda newSelf,*args: self.newEnterReward(newSelf,*args)
        DistributedSuit.denyBattle=lambda *args: self.newDenyBattle(*args)
        HealthForceAcknowledge.HealthForceAcknowledge.enter=lambda newSelf,hplevel: self.newEnterHealth(newSelf,hplevel)
        LocalToon.LocalToon.setAnimState=lambda *args,**kwds:self.newSetAnimState(*args,**kwds)
        DistributedBoardingParty.DistributedBoardingParty.postInvite=lambda newSelf,leaderId,inviterId: self.newPostInvite(newSelf,leaderId,inviterId)

    def attack(self):
        '''
        Syntax used can be found in the original gag trainer
        but has been very much modified to suit the purpose of
        the Mint Autoer
        '''
        
                try:
            for battle in base.cr.doFindAll('battle'):
                if cfoMaxer.mintAutoer.finalDone:
                    if len(battle.suits)>1:
                        for suit in battle.suits: 
                            if suit.getActualLevel()!=12:
                                attackSuit=suit
                    else:
                        attackSuit=battle.suits[0]
                else:
                    attackSuit=battle.suits[0]
                    
                if base.localAvatar.inventory.inventory[cfoMaxer.restock.firstTrack][cfoMaxer.restock.desiredLevel1]>0:
                    battle.sendUpdate('requestAttack', [cfoMaxer.restock.firstTrack, cfoMaxer.restock.desiredLevel1, attackSuit.doId])
                else:
                    break
                    
                if base.localAvatar.getHp()<(base.localAvatar.getMaxHp()*0.75) or self.isHealing:
                
                    if base.localAvatar.inventory.inventory[cfoMaxer.restock.secondTrack][cfoMaxer.restock.desiredLevel2]>0:
                        battle.sendUpdate('requestAttack', [cfoMaxer.restock.secondTrack, cfoMaxer.restock.desiredLevel2, base.localAvatar.doId])
                    else:
                        break
                        
                    if base.localAvatar.inventory.inventory[cfoMaxer.restock.thirdTrack][cfoMaxer.restock.desiredLevel3]>0:
                        battle.sendUpdate('requestAttack', [cfoMaxer.restock.thirdTrack, cfoMaxer.restock.desiredLevel3, attackSuit.doId])
                    else:
                        break
                        
                else:
                    if base.localAvatar.inventory.inventory[cfoMaxer.restock.thirdTrack][cfoMaxer.restock.desiredLevel3]>0:
                        battle.sendUpdate('requestAttack', [cfoMaxer.restock.thirdTrack, cfoMaxer.restock.desiredLevel3, attackSuit.doId])
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
        
    def newDreamlandInit(self,*args):
        '''
        Used to show that the toon has been teleported
        to Donalds Dreamland
        '''
        
        self.oldDreamlandInit(*args)
        if self.shouldContinue:
            cfoMaxer.mintAutoer.gainLaffSeq.finish()
            cfoMaxer.mintAutoer.attackSeq.finish()
            cfoMaxer.restock.wasInBattle=False
            self.checkCogbucks()
    
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
    
    def newPostInvite(self,newSelf,leaderId,inviterId):
        '''
        Used to accept the boarding group invitation from yourself
        when it is asked.
        '''
    
        if leaderId==base.localAvatar.doId:
            newSelf.sendUpdate('requestAcceptInvite',[inviterId,leaderId])
        else:
            self.oldPostInvite(newSelf,leaderId,inviterId)
    
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
            cfoMaxer.autoerGui.display.newLine('TPing failed, trying again')
            if self.shouldContinue:
                Sequence(Wait(3),Func(self.checkCogbucks)).start()
        except:
            pass
            
    def newHqDoorInit(self,*args):
        '''
        Used to show that the toon has teleported
        to a cog hq. This functions checks if they
        have been teleported to Cashbot HQ
        '''
        
        self.oldHqDoorInit(*args)
        if self.shouldContinue and base.localAvatar.getZoneId()==12000:
            base.localAvatar.collisionsOff()
            Sequence(Wait(2),Func(self.checkCogbucks)).start()
    
    def newEnterReward(self,newSelf,*args):
        '''
        Used when the Maxer needs to gain back laff 
        to do the Mint so when it kills
        a cog it has to check if it is the right hp
        level or if it needs to do another cog
        '''
        
        self.oldEnterReward(newSelf,*args)
        if self.shouldContinue and self.isHealing:
            if base.localAvatar.getHp()>70:
                cfoMaxer.mintAutoer.attackSeq.finish()
                self.isHealing=False
                self.checkCogbucks()
            else:
                Sequence(Wait(1),Func(self.enterRandomBattle)).start()
     
    def newDenyBattle(self,*args):
        '''
        Used to go to the next cog if the cog denys the battle
        '''    
    
        self.oldDenyBattle(*args)
        if self.shouldContinue and self.isHealing and args[0].doId==self.attackCogId:
            self.enterRandomBattle()
        
    def checkCogbucks(self):
        '''
        Written by me it is a function to determine
        what the maxer needs to do with the toon next
        it works everything out depeding of the toons
        merits needed and the settings they have chosen.
        '''
        
        if self.onlyMint:
            base.localAvatar.cogMerits[2]=-4000
        if self.shouldEnd:
            self.shouldContinue=False
        if self.haveJb():
            if self.shouldContinue:
                if self.getCogbucksLeft()==0 and not self.onlyMint:
                    if base.cr.doFind('DistributedCogHQDoor') and base.localAvatar.getZoneId()>=12000 and base.localAvatar.getZoneId()<12100:
                        cfoMaxer.cfoAutoer.start()
                    else:
                        cfoMaxer.restock.restock()
                        cfoMaxer.restock.collectLaff()
                        self.walk()
                        cfoMaxer.autoerGui.display.newLine('Teleporting to cashbot hq')
                        Sequence(Wait(2),Func(self.teleBack)).start()
                else:
                    if base.cr.doFind('DistributedCogHQDoor') and base.localAvatar.getZoneId()>=12000 and base.localAvatar.getZoneId()<12100:
                        cfoMaxer.mintAutoer.start()
                    else:
                        cfoMaxer.restock.restock()
                        cfoMaxer.restock.collectLaff()
                        self.walk()
                        cfoMaxer.autoerGui.display.newLine('Teleporting to cashbot hq')
                        Sequence(Wait(2),Func(self.teleBack)).start()
            else:
                cfoMaxer.restock.noToons.finish()
                try:
                    base.cr.removeInterest(cfoMaxer.restock.interest1)
                    base.cr.removeInterest(cfoMaxer.restock.interest2)
                    cfoMaxer.restock.unloaded=True
                except:
                    pass
                base.localAvatar.setSystemMessage(0,"Thanks for using freshollie's cfo maxer")
                cfoMaxer.autoerGui.display.newLine('Stopped')
                toonBot.scriptOn=False
        else:
            base.localAvatar.setSystemMessage(0,'You have run out of jelly beans, please use the fishing code to gain some')
            toonBot.scriptOn=False
    
    def getCogbucksLeft(self):
        '''
        Uses the CogDisguiseGlobals to work out how many
        stock options te toon needs to gain before it can
        do the ceo.
        '''
        
        return CogDisguiseGlobals.getTotalMerits(base.localAvatar,2)-base.localAvatar.cogMerits[2]

    def walk(self):
        '''
        Walk is a function built into magic words
        which I used instead of sendOpenTalk('~walk').
        '''
        
        try:
            base.cr.playGame.getPlace().fsm.forceTransition('walk')
        except:
            pass
       
    def teleBack(self,zone=12000):
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
                
    def onlyDoMint(self):
        '''
        Written so that the user can choose if they want to do the Country Club only.
        '''
        
        self.onlyMint=True
        base.localAvatar.setSystemMessage(0,'CFO maxer set to only do the Mint')
    
    def doBoth(self):
        self.onlyMint=False
        base.localAvatar.setSystemMessage(0,'CFO maxer set to do both the Mint and the CFO')
        
    def haveJb(self):
        '''
        Checks if the user has more than 100
        jelly beans so they don't run out during
        a Mint
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
            base.localAvatar.collisionsOn()
            base.localAvatar.setPosHpr(pos, hpr)
            battle.d_requestBattle(pos, hpr)
            self.attackCogId=battle.doId
        else:
            pass
        
    def setStop(self):
        self.shouldEnd=True
        base.localAvatar.setSystemMessage(1,"The Autoer will stop at the end of this run")
        cfoMaxer.autoerGui.stopTimer()
    
    def start(self):
        DistributedObject.DistributedObject.sendUpdate=lambda newself, fieldName, args=[], sendToId=None: self.sendUpdateHook(newself, fieldName, args, sendToId)
        self.bossCount=0
        self.shouldContinue=True
        self.shouldEnd=False
        cfoMaxer.autoerGui.startTimer()
        emptyShardList=[]
        for shard in base.cr.activeDistrictMap:
            if base.cr.activeDistrictMap[shard].avatarCount<30:
                emptyShardList.append(shard)
        if emptyShardList==[]:
            emptyShardList=[650000000, 754000000, 608000000, 756000000, 658000000, 712000000, 360000000, 410000000, 620000000, 454000000, 726000000, 362000000, 688000000, 316000000]
        if base.localAvatar.defaultShard not in emptyShardList:
            cfoMaxer.autoerGui.display.newLine('TPing to an empty district')
            base.cr.playGame.getPlace().requestTeleport(12000,12000,random.choice(emptyShardList),None)
        else:
            self.checkCogbucks()
        cfoMaxer.restock.noToons.loop()
    
    def revertFunctions(self):
        '''
        Revert to the original functions so other scripts can be loaded.
        '''
        
        LocalToon.LocalToon.setAnimState=self.oldSetAnim
        DLPlayground.DLPlayground.__init__=self.oldDreamlandInit
        DistributedCogHQDoor.DistributedCogHQDoor.__init__=self.oldHqDoorInit
        DistributedBattle.DistributedBattle.enterReward=self.oldEnterReward
        DistributedSuit.denyBattle=self.oldDenyBattle
        DistributedObject.DistributedObject.sendUpdate=self.oldSendUpdate
        HealthForceAcknowledge.HealthForceAcknowledge.enter=self.oldEnterHealth
        DistributedBoardingParty.DistributedBoardingParty.postInvite=self.oldPostInvite

class CfoAutoer:
    '''
    Cfo Autoer written by me with some functions written by others.
    '''
    
    #Used as hooks to find out where your toon is during the bossbattle
    oldBossEnterElevator=DistributedCashbotBoss.DistributedCashbotBoss.enterElevator
    oldEnterBattleThree=DistributedCashbotBoss.DistributedCashbotBoss.enterBattleThree
    oldEnterPrepareBattleThree=DistributedCashbotBoss.DistributedCashbotBoss.enterPrepareBattleThree
    oldEnterEpilogue=DistributedCashbotBoss.DistributedCashbotBoss.enterEpilogue
    oldEnterWaitForInput=DistributedBattleFinal.DistributedBattleFinal.enterWaitForInput
    oldBossEnterIntro=DistributedCashbotBoss.DistributedCashbotBoss.enterIntroduction
    oldAvatarExit=DistributedCogHQDoor.DistributedCogHQDoor.avatarExit
    
    def __init__(self):
        DistributedCogHQDoor.DistributedCogHQDoor.avatarExit=lambda newSelf,id: self.newAvatarExit(newSelf,id)
        DistributedCashbotBoss.DistributedCashbotBoss.enterElevator=lambda newSelf: self.newBossEnterElevator(newSelf)
        DistributedCashbotBoss.DistributedCashbotBoss.enterIntroduction=lambda newSelf,*args: self.newBossEnterIntro(newSelf,*args)
        DistributedCashbotBoss.DistributedCashbotBoss.enterBattleThree=lambda newSelf: self.newEnterBattleThree(newSelf)
        DistributedBattleFinal.DistributedBattleFinal.enterWaitForInput=lambda *args: self.newEnterWaitForInput(*args)
        DistributedCashbotBoss.DistributedCashbotBoss.enterPrepareBattleThree=lambda newSelf: self.newEnterPrepareBattleThree(newSelf)
        DistributedCashbotBoss.DistributedCashbotBoss.enterEpilogue=lambda newSelf: self.newEnterEpilogue(newSelf)
        DistributedCashbotBoss.DistributedCashbotBoss.newState=DistributedCashbotBoss.DistributedCashbotBoss.setState
    
    def newAvatarExit(self,newSelf,id):
        '''
        Gives the maxer the information that the toon has exited a cog hq door so the maxer
        can do what it needs to do which in this case is board the elevator.
        '''
        
        self.oldAvatarExit(newSelf,id)
        if base.cr.doFind('Elevator') and id==base.localAvatar.doId and cfoMaxer.otherFunctions.shouldContinue:
            cfoMaxer.otherFunctions.walk()
            cfoMaxer.autoerGui.display.newLine('Heading to the CFO')
            base.cr.doFind('Boarding').sendUpdate('requestLeave',[base.localAvatar.doId])
            base.cr.doFind('Boarding').sendUpdate('requestInvite',[base.localAvatar.doId])
            base.cr.doFind('Boarding').sendUpdate('requestGoToSecondTime',[base.cr.doFind('Elevator').doId])
    
    def newBossEnterIntro(self,newSelf,*args):
        '''
        When the function to enter the boss introduction
        the maxer automatically exits the introduction
        effectively skipping it.
        '''
        
        self.oldBossEnterIntro(newSelf,*args)
        if cfoMaxer.otherFunctions.shouldContinue:
            newSelf.exitIntroduction()
            cfoMaxer.autoerGui.display.newLine('Skipping CFO introduction')
  
    def newEnterEpilogue(self,newSelf):
        '''
        When the boss enter epilogue function is called
        the bosscount gets 1 added to it and the script
        skips through the chat text to gain the unite
        '''
        
        self.oldEnterEpilogue(newSelf)
        if cfoMaxer.otherFunctions.shouldContinue:
            for i in range(5):
                newSelf._DistributedCashbotBoss__epilogueChatNext(i,1)
            cfoMaxer.otherFunctions.teleBack()
            cfoMaxer.otherFunctions.bossCount+=1
            cfoMaxer.autoerGui.display.newLine('Finished CFO')
    
    def newEnterPrepareBattleThree(self,newSelf):
        '''
        The same idea as the introduction hook function.
        '''
        
        self.oldEnterPrepareBattleThree(newSelf)
        newSelf.exitPrepareBattleThree()
        cfoMaxer.autoerGui.display.newLine('Skipping cutscene')
    
    def destroyBattle(self):
        '''
        The battle exploit first founded by Pascal (http://www.youtube.com/user/leftylemonzilla)
        and has been used here to skip the cog battles in the ceo.
        '''
        
        base.cr.doFind('SafeZone').sendUpdate('enterSafeZone')
    
    def exploit(self):
        Sequence(Func(self.destroyBattle), Wait(.5), Func(cfoMaxer.otherFunctions.walk)).start()
    
    def newEnterWaitForInput(self,*args):
        '''
        When the cogs are ready to be attacked the exploit is ready to be used
        which is what this hook is for.
        '''
        
        self.oldEnterWaitForInput(*args)
        if cfoMaxer.otherFunctions.shouldContinue:
            self.exploit()
            cfoMaxer.autoerGui.display.newLine('Skipping Battle')
    
    def newBossEnterElevator(self,newSelf):
        '''
        The same idea as the introduction hook function.
        '''
        
        self.oldBossEnterElevator(newSelf)
        if cfoMaxer.otherFunctions.shouldContinue:
            cfoMaxer.autoerGui.display.newLine('Skipping Elevator')
            newSelf._DistributedBossCog__doneElevator()
    
    def newEnterBattleThree(self,newSelf):
        '''
        This function is used to end the battle
        when it enters the last battle.
        '''
        
        self.oldEnterBattleThree(newSelf)
        self.endBattle(newSelf)
        
    def start(self):
        base.cr.doFind('DistributedCogHQDoor').sendUpdate('requestEnter')
        cfoMaxer.autoerGui.display.newLine('Starting the CFO')
        cfoMaxer.autoerGui.display.newLine('Entering Lobby')
        
    def endBattle(self,newSelf):
        '''
        This was not created by me but
        I don't actually know where it
        came from.
        '''
        
        newSelf.cranes[0].sendUpdate('requestControl', [])
        for goon in base.cr.doFindAll('goon'):
            goon.sendUpdate('requestGrab', [])
            goon.sendUpdate('clearSmoothing', [0])
            goon.sendUpdate('hitBoss', [20.0])
        Sequence(Wait(1),Func(newSelf.exitBattleFour)).start()
        
    def revertFunctions(self):
        '''
        Revert to the original functions so other scripts can be loaded.
        '''
        
        DistributedCashbotBoss.DistributedCashbotBoss.enterElevator=self.oldBossEnterElevator
        DistributedCashbotBoss.DistributedCashbotBoss.enterBattleThree=self.oldEnterBattleThree
        DistributedCashbotBoss.DistributedCashbotBoss.enterPrepareBattleThree=self.oldEnterPrepareBattleThree
        DistributedCashbotBoss.DistributedCashbotBoss.enterEpilogue=self.oldEnterEpilogue
        DistributedBattleFinal.DistributedBattleFinal.enterWaitForInput=self.oldEnterWaitForInput
        DistributedCashbotBoss.DistributedCashbotBoss.enterIntroduction=self.oldBossEnterIntro
        DistributedCogHQDoor.DistributedCogHQDoor.avatarExit=self.oldAvatarExit
        
class MintAutoer:
    oldMintAnnounceGenerate=DistributedMint.DistributedMint.announceGenerate
    oldEnterReward=DistributedMintBattle.DistributedMintBattle.enterReward
    oldEnterMintReward=DistributedMintBattle.DistributedMintBattle.enterMintReward
    
    def __init__(self,cfoMaxer):
        self.floorNumToLastRoomNum=[17,23,21,19,17,23,21,19,17,23,21,19,17,24,21,19,17,24,21,19]
        self.attackSeq=Sequence(Func(cfoMaxer.restock.restock),Wait(1.0),Func(cfoMaxer.otherFunctions.attack),Wait(1.0))
        self.gainLaffSeq=Sequence(Func(cfoMaxer.restock.gainLaff),Wait(3.0))
        DistributedMint.DistributedMint.announceGenerate=lambda *args:self.newMintAnnounceGenerate(*args)
        DistributedMintBattle.DistributedMintBattle.enterReward=lambda *args:self.newEnterReward(*args)
        DistributedMintBattle.DistributedMintBattle.d_toonDied=lambda *args: self.newSafeZone(*args)
        DistributedMintBattle.DistributedMintBattle.enterMintReward=lambda *args:self.newEnterMintReward(*args)
        
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
        base.localAvatar.findSomethingToLookAt = cfoMaxer.restock.oldFindSomethingToLookAt
        ToonHead.ToonHead._ToonHead__lookAround = cfoMaxer.restock.oldLookAround

    def enterBattle(self):
        '''
        Enter battle is the same as enterRandomBattle in
        OtherFunctions and was written by Cody but
        slightly modified to work with the Mint Autoer.
        '''
        
        if base.localAvatar.getHp()>0:
            battles = []
            cogList = base.cr.doFindAll("render")
            for x in cogList:
                if isinstance(x, DistributedMintSuit):
                    if x.activeState == 6:
                        if x.doId not in base.cr.doFind('DistributedMintRoom '+str(self.floorNumToLastRoomNum[base.cr.doFind('DistributedMint.DistributedMint').floorNum])).suitIds and not self.finalDone:
                            battles.append(x)
                        elif self.finalDone and x.doId in base.cr.doFind('DistributedMintRoom '+str(self.floorNumToLastRoomNum[base.cr.doFind('DistributedMint.DistributedMint').floorNum])).suitIds:
                            battles.append(x)
                            
            if battles != []:
                battle=battles[0]
                pos, hpr = battle.getPos(), battle.getHpr()
                base.localAvatar.collisionsOn()
                base.localAvatar.setPosHpr(pos, hpr)
                battle.d_requestBattle(pos, hpr)
                cfoMaxer.restock.wasInBattle=False
                cfoMaxer.autoerGui.display.newLine('Entering Battle '+str(self.battleNum))
                return True
            else:
                return False
        else:
            return True
            
    def boardElevator(self):
        '''
        Used to enter the mint, it invites itself
        to a boarding group and then teleports to
        the Mint
        '''
        
        if base.localAvatar.getHp()>70:
            for elevator in base.cr.doFindAll("Elevator"):
                if "Bullion" in elevator.getDestName():
                    cfoMaxer.autoerGui.display.newLine('Entering the Bullion Mint')
                    base.cr.doFind('Boarding').sendUpdate('requestLeave',[base.localAvatar.doId])
                    base.cr.doFind('Boarding').sendUpdate('requestInvite',[base.localAvatar.doId])
                    base.cr.doFind('Boarding').sendUpdate('requestGoToSecondTime',[elevator.doId])
                    break
        else:
            self.attackSeq.loop()
            cfoMaxer.otherFunctions.isHealing=True
            cfoMaxer.autoerGui.display.newLine('Healing')
            cfoMaxer.otherFunctions.enterRandomBattle()
    
    def warpToRoom(self,room):
        if base.cr.doFind('DistributedMint.DistributedMint'):
            base.cr.doFind('DistributedMint.DistributedMint').warpToRoom(room)
                
    def newMintAnnounceGenerate(self,*args):
        '''
        Used to tell the maxer that the toon has entered the
        Mint so it can start.
        '''
        
        self.oldMintAnnounceGenerate(*args)
        self.attackSeq.loop()
        self.gainLaffSeq.loop()
        Sequence(Wait(4),Func(self.workOutRoomsNeeded),Func(self.enterBattle)).start()
    
    def workOutRoomsNeeded(self):
        battles = []
        cogList = base.cr.doFindAll("render")
        for x in cogList:
            if isinstance(x, DistributedMintSuit):
                if x.activeState == 6:
                    battles.append(x)
        self.battlesNeeded=0
        numBattles=(len(battles)/4)-1
        cogbucksNeeded=cfoMaxer.otherFunctions.getCogbucksLeft()
        cogbucksNeeded-=68
        for i in range(numBattles):
            if cogbucksNeeded>0:
                self.battlesNeeded+=1
                cogbucksNeeded-=68
            else:
                break
    
    def newEnterReward(self,*args):
        '''
        Used to tell the maxer that the toon has finsihed
        the battle so toon can go to the next battle.
        '''
        
        self.oldEnterReward(*args)
        if cfoMaxer.otherFunctions.shouldContinue:
            cfoMaxer.autoerGui.display.newLine('Finished Battle '+str(self.battleNum))
            base.cr.doFind('battle').d_rewardDone(base.localAvatar.doId)
            self.battleNum+=1
            cfoMaxer.otherFunctions.walk()
            if self.battleNum>self.battlesNeeded and not self.finalDone:
                cfoMaxer.autoerGui.display.newLine('Warping to final room')
                self.warpToRoom(self.floorNumToLastRoomNum[base.cr.doFind('DistributedMint.DistributedMint').floorNum])
                self.finalDone=True
                Sequence(Wait(0.5),Func(self.enterBattle)).start()
            elif self.enterBattle():
                pass
            else:
                cfoMaxer.otherFunctions.walk()
                cfoMaxer.autoerGui.display.newLine('Error no cogbucks recieved')
                self.generateAgain()
                self.attackSeq.finish()
                self.gainLaffSeq.finish()
                Sequence(Wait(1),Func(cfoMaxer.otherFunctions.teleBack)).start()
    
    def newSafeZone(self,*args):
        '''
        Used to hook functions they are called the
        walk function is called to stop the toon from
        teleporting away and the wasInBattle bool set
        to true so the gain laff function will go back
        into the battle when it has full laff.
        '''
        
        Sequence(Wait(1),Func(cfoMaxer.otherFunctions.walk)).start()
        base.localAvatar.collisionsOff()
        cfoMaxer.restock.wasInBattle=True
        cfoMaxer.autoerGui.display.newLine('Died, recovering')

    def newEnterMintReward(self,*args):
        '''
        Used to tell the maxer that the toon has finsihed
        the Mint so it can teleport out
        '''
        
        self.oldEnterMintReward(*args)
        if cfoMaxer.otherFunctions.shouldContinue:
            cfoMaxer.otherFunctions.walk()
            cfoMaxer.autoerGui.display.newLine('Finished Final Battle')
            self.generateAgain()
            self.attackSeq.finish()
            self.gainLaffSeq.finish()
            Sequence(Wait(1),Func(cfoMaxer.otherFunctions.teleBack)).start()
    
    def start(self):
        self.battleNum=1
        self.finalDone=False
        Sequence(Wait(1),Func(self.boardElevator)).start()
    
    def revertFunctions(self):
        DistributedMint.DistributedMint.announceGenerate=self.oldMintAnnounceGenerate
        DistributedMintBattle.DistributedMintBattle.enterReward=self.oldEnterReward
        DistributedMintBattle.DistributedMintBattle.enterCountryClubReward=self.oldEnterMintReward
        DistributedMintBattle.DistributedMintBattle.d_toonDied=lambda *args: None
        self.attackSeq.finish()
        self.gainLaffSeq.finish()
        self.generateAgain()

class CFOmaxer:

    def __init__(self):
        self.restock=restock()
        self.otherFunctions=OtherFunctions()
        self.cfoAutoer=CfoAutoer()
        self.mintAutoer=MintAutoer(self)
        self.autoerGui=AutoerGui('CFO Maxer',['Run Time',"Number of cfo's","Cfo's/Hour",'Suit','Cogbucks needed'],\
                                ['self.hours+":"+self.minutes+":"+self.seconds','str(cfoMaxer.otherFunctions.bossCount)','str(self.workOutNumberAnHour(cfoMaxer.otherFunctions.bossCount))'\
                                ,'str(cfoMaxer.otherFunctions.numberToSuit[base.localAvatar.cogTypes[2]])+" Lvl "+str(base.localAvatar.cogLevels[2]+1)','str(cfoMaxer.otherFunctions.getCogbucksLeft())'],\
                                'CFO MXR','cash')
        
    def revert(self):
        self.restock.revertFunctions()
        self.mintAutoer.revertFunctions()
        self.cfoAutoer.revertFunctions()
        self.otherFunctions.revertFunctions()
        self.autoerGui.destroy()
        DistributedNPCFisherman.DistributedNPCFisherman.handleCollisionSphereEnter=oldHandleEnterCollisionSphereFisherman
        DistributedNPCPartyPerson.DistributedNPCPartyPerson.handleCollisionSphereEnter=oldHandleEnterCollisionSphereParty
        DistributedNPCFisherman.DistributedNPCFisherman.announceGenerate=oldFisherAnnounceGenerate
        DistributedNPCPartyPerson.DistributedNPCPartyPerson.announceGenerate=oldPartyPlannerAnnounceGenerate

global cfoMaxer
cfoMaxer=CFOmaxer()