from direct.interval.IntervalGlobal import *
from direct.gui.DirectLabel import DirectLabel
from toontown.toon import DistributedNPCToon
from toontown.safezone import Playground
from toontown.battle import SuitBattleGlobals
from toontown.building import DistributedBuilding
from toontown.battle import DistributedBattleBldg
from toontown.suit import SuitDNA
from toontown.quest import Quests
from toontown.quest import QuestBookPoster
from toontown.toon import ToonHead
from toontown.building import DistributedDoor
from toontown.safezone import DistributedPartyGate
from toontown.safezone import DistributedTrolley
from toontown.toon import DistributedNPCFisherman
from toontown.toon import DistributedNPCPartyPerson
from toontown.shtiker import PurchaseManager
from toontown.minigame import DistributedMinigame
from toontown.estate import Estate
from toontown.estate import House

HQZONES=[10000,11000,12000,13000]
        
class TaskAutoer:
    oldTeleportInPlayground=Playground.Playground.exitTeleportIn
    #oldBattleBldg=DistributedBattleBldg.DistributedBattleBldg.__init__
    #oldBuildingGenerate=DistributedBuilding.DistributedBuilding.generate
    #oldEnterToon=DistributedBuilding.DistributedBuilding.enterToon
    oldAnnounceGenerate1=DistributedMinigame.DistributedMinigame.announceGenerate
    oldAnnounceGenerate2=PurchaseManager.PurchaseManager.announceGenerate
    oldEstateTeleportIn=Estate.Estate.exitTeleportIn
    oldHouseDoorIn=House.House.exitDoorIn
    
    def __init__(self):
        DistributedMinigame.DistributedMinigame.announceGenerate=lambda newSelf: self.newAnnounceGenerate1(newSelf)
        PurchaseManager.PurchaseManager.announceGenerate=lambda newSelf: self.newAnnounceGenerate2(newSelf)
        Playground.Playground.exitTeleportIn=lambda newSelf,*args,**kwds: self.newTeleportInPlayground(newSelf,*args,**kwds)
        Estate.Estate.exitTeleportIn=lambda newSelf,*args,**kwds: self.newEstateTeleportIn(newSelf,*args,**kwds)
        House.House.exitDoorIn=lambda newSelf,*args,**kwds: self.newHouseDoorIn(newSelf,*args,**kwds)
        #DistributedBuilding.DistributedBuilding.generate=lambda newSelf,*args: self.newBuildingGenerate(newSelf,*args)
        #DistributedBuilding.DistributedBuilding.enterToon=lambda newSelf,*args: self.newEnterToon(newSelf,*args)
        base.localAvatar.setWantBattles(False)
        self.shardIds=[]
        self.isMember=True
        self.jellybeansNeeded=500
        self.questGui=QuestBookPoster.QuestBookPoster(pos=(0.95,1,0.5))
        self.questGui.mouseEnterPoster(0)
        self.questGui.mouseExitPoster=self.questGui.mouseEnterPoster
        self.oldNPCmovie=None
        self.updateQuestGuiLoop=Sequence(Func(self.updateQuestGui),Wait(0.5))
        self.updateQuestGuiLoop.loop()
        for shard in base.cr.activeDistrictMap:
            if base.cr.activeDistrictMap[shard].avatarCount<50:
                self.shardIds.append(shard)
        self.wantedTracks=[1,3]
        self.status=None
        self.buildingLevelToZoneDict={1:1000,2:5000,3:4000,4:3000,5:9000}
        DirectLabel(parent=aspect2d,relief=None,text='\x01shadow\x01Freshollies Toontask Autoer\x02',text_scale=0.17, pos=(0, 0, 0.87), text_fg=(1, 1, 1, 1))
        DirectLabel(parent=aspect2d,relief=None,text='\x01shadow\x01Freshollies Toontask Autoer\x02',text_scale=0.17, pos=(0, 0, 0.87), text_fg=(0, 0, 0, 0))
        
    def newAnnounceGenerate1(self,newSelf):
        self.oldAnnounceGenerate1(newSelf)
        messenger.send('minigameAbort')

    def newAnnounceGenerate2(self,newSelf):
        self.oldAnnounceGenerate2(newSelf)
        Sequence(Wait(10),Func(self.skipTrolley)).start()
    
    def skipTrolley(self):
        for i in range(5):
            messenger.send('doneChatPage')
        Sequence(Wait(4),Func(messenger.send,'purchaseBackToToontown')).start()
    
    def newNPCmovie(self, mode, npcId, avId, quests, timestamp):
        self.oldNPCmovie(mode, npcId, avId, quests, timestamp)
        if avId==base.localAvatar.doId:
            for quest in quests:
                if not Quests.isQuestJustForFun(quest,Quests.getFinalRewardId(quest)):
                    self.officer.sendChooseQuest(quest)
                    self.officer.sendUpdate('setMovieDone')
                    self.officer.setMovie=self.oldNPCmovie
                    base.cr.playGame.getPlace().fsm.forceTransition('walk')
                    return
    
    def newBuildingGenerate(self,newSelf,*args):
        try:
            oldBuildingGenerate(newSelf,*args)
        except:
            pass
    
    def newEnterToon(self,newSelf,*args):
        try:
            oldEnterToon(newSelf,*args)
        except:
            pass
    
    def newTeleportInPlayground(self,newSelf,*args,**kwds):
        self.oldTeleportInPlayground(newSelf,*args,**kwds)
        if buildingAutoer.shouldContinue:
            buildingAutoer.checkStop()
             
            if buildingAutoer.shouldContinue and not self.isQuestComplete():
                buildingAutoer.killElevators.append(buildingAutoer.lastElevator)
                Sequence(Wait(2),Func(buildingAutoer.teleportBackToStreet)).start()
            else:
                Sequence(Wait(2),Func(self.checkWhatToDo)).start()
        elif gagTrainer.shouldContinue:
            Sequence(Wait(2),Func(gagTrainer.teleportBackToStreet)).start()
        else:
            Sequence(Wait(2),Func(self.checkWhatToDo)).start()
    
    def newEstateTeleportIn(self,newSelf,*args,**kwds):
        self.oldEstateTeleportIn(newSelf,*args,**kwds)
        for door in base.cr.doFindAll('Door'):  
            if 'esHouse_1' in str(door.getBuilding()):
                door.sendUpdate('requestEnter')
           
    def newHouseDoorIn(self,newSelf,*args,**kwds):
        self.oldHouseDoorIn(newSelf,*args,**kwds)
        base.cr.doFind('phone').sendUpdate('avatarEnter')
        base.cr.doFind('phone').sendUpdate('avatarExit')
        Sequence(Wait(2),Func(self.checkWhatToDo)).start()
            
    def checkWhatToDo(self):
        if base.localAvatar.getTotalMoney()>self.jellybeansNeeded:
            self.jellybeansNeeded=500
    
        if base.localAvatar.defaultShard not in self.shardIds:
            base.cr.playGame.getPlace().requestTeleport(2000,2000,random.choice(self.shardIds),None)
            
        elif self.status=='Fishing':
            if not self.isQuestComplete():
                self.fishOnce()
            else:
                for dock in base.cr.doFindAll('DistributedFishingSpot'):
                    dock.sendUpdate('requestExit')
                self.status=None
                self.doTask()
                
        elif self.jellybeansNeeded==12000:
            self.fishOnce()
                
        elif base.localAvatar.getTotalMoney()<self.jellybeansNeeded:
            self.jellybeansNeeded=12000
            base.cr.playGame.getPlace().requestTeleport(2000,2000,None,None)
        
        elif base.localAvatar.quests:
            self.doTask()
        else:
            self.collectNewTask()
    
    def updateQuestGui(self):
        if base.localAvatar.quests:
            self.questGui.update(base.localAvatar.quests[0])
        else:
            self.questGui.clear()
        
    def getCurrentQuest(self):
        return Quests.getQuest(base.localAvatar.quests[0][0])
    
    def getBestZoneForCogLevel(self,level):
        if self.isMember:
            if level<3:
                return 2000
            elif level<4:
                return 1000
            elif level<5:
                return 5000
            elif level<6:
                return 4000
            elif level<7:
                return 3000
            elif level<8:
                return 9000
            elif level<9:
                return 12000
            else:
                return 13000
        else:
            return 2000
    
    def getBestZoneForBuildingLevel(self,level):
        return self.buildingLevelToZoneDict.get(level)
    
    def getSuitName(self,suitType):
        try:
            return SuitBattleGlobals.SuitAttributes[suitType].get('name')
        except:
            return suitType
    
    def getCogLevelFromCog(self,suitType):
        try:
            return SuitBattleGlobals.SuitAttributes[suitType].get('level')+1
        except:
            return 1
            
    
    def getSuitDepartment(self,suitType):
        return SuitDNA.getSuitDept(suitType)
    
    def getCorrectChoice(self,choices):
        if 0 in choices:
            return 0
        elif 2 in choices:
            return 2
        elif self.wantedTracks[0] in choices:
            return self.wantedTracks[0]
        else:
            return self.wantedTracks[1]
                    
    def newTask(self):
        for officer in base.cr.doFindAll('HQ Officer'):
            if officer.allowedToTalk():
                if officer.setMovie!=self.oldNPCmovie:
                    self.oldNPCmovie=officer.setMovie
                self.officer=officer
                officer.setMovie=self.newNPCmovie
                officer.sendUpdate('avatarEnter')
                break
        
    def collectNewTask(self):
        interest=base.cr.addInterest(base.localAvatar.defaultShard, 2742, 5, None)
        Sequence(Wait(1),Func(self.newTask),Wait(2),Func(base.cr.removeInterest,interest),Func(self.checkWhatToDo)).start()
    
    def nextShard(self):
        base.cr.playGame.getPlace().fsm.forceTransition('walk')
        base.cr.playGame.getPlace().requestTeleport(2000,2000,self.shardIds[0],None)
        self.shardIds.append(self.shardIds[0])
        del self.shardIds[0]
    
    def catchFish(self):
        try:
            fish = base.cr.doFindAll("FishingTarget")[0]
            for fp in base.cr.doFindAll("FishingPond"):
                fp.d_hitTarget(fish)
        except:
            pass
    
    def fishOnce(self):
        entered=False
        for spot in reversed(base.cr.doFindAll('DistributedFishingSpot')):
            if spot.allowedToEnter():
                entered=True
                spot.sendUpdate('requestEnter')
                usedSpot=spot
                break
        if entered:
            catchFishSeq=Sequence()
            catchFishSeq.append(Wait(1))
            for i in range(23):
                catchFishSeq.append(Func(self.catchFish))
                catchFishSeq.append(Wait(0.05))
            catchFishSeq.append(Wait(1))
            catchFishSeq.append(Func(self.sellFish))
            catchFishSeq.append(Wait(0.5))
            catchFishSeq.append(Func(self.checkWhatToDo))
            catchFishSeq.start()
        else:
            Sequence(Wait(2),Func(self.fishOnce)).start()
            
    def sellFish(self):
        base.cr.doFind('Fisherman').sendUpdate('avatarEnter')
        base.cr.doFind('Fisherman').sendUpdate('completeSale',[1])
        
    def speakToNpc(self,name):
        if base.cr.doFind(name):
            for npc in base.cr.doFindAllInstances(DistributedNPCToon.DistributedNPCToon):
                if npc.getName()==name:
                    if npc.allowedToTalk():
                        npc.sendUpdate('avatarEnter')
                        npc.sendUpdate('setMovieDone')
                        base.cr.removeInterest(self.interest)
                        Sequence(Wait(1),Func(self.checkWhatToDo)).start()
                        found=True
                        foundNPC=True
                        break
                    else:
                        found=False
                        foundNPC=True
                else:
                    foundNPC=False
            if not foundNPC:
                Sequence(Func(base.cr.removeInterest,self.interest),Wait(0.5),Func(self.nextShard)).start()
            elif not found:
                Sequence(Wait(5),Func(self.speakToNpc,name)).start()
        else:
            Sequence(Func(base.cr.removeInterest,self.interest),Wait(0.5),Func(self.nextShard)).start()
    
    def chooseTrack(self,name):
        if base.cr.doFind(name):
            for npc in base.cr.doFindAllInstances(DistributedNPCToon.DistributedNPCToon):
                if npc.getName()==name:
                    if npc.allowedToTalk():
                        npc.sendUpdate('avatarEnter')
                        try:
                            npc.sendChooseTrack(self.getCorrectChoice(self.getCurrentQuest().getChoices()))
                            npc.sendUpdate('setMovieDone')
                        except:
                            pass
                        base.cr.removeInterest(self.interest)
                        Sequence(Wait(0.5),Func(self.checkWhatToDo)).start()
                        found=True
                        foundNPC=True
                        break
                    else:
                        found=False
                        foundNPC=True
                else:
                    foundNPC=False
            if not foundNPC:
                Sequence(Func(base.cr.removeInterest,self.interest),Wait(0.5),Func(self.nextShard)).start()
            elif not found:
                Sequence(Wait(5),Func(self.chooseTrack)).start()
        else:
            Sequence(Func(base.cr.removeInterest,self.interest),Wait(0.5),Func(self.nextShard)).start()
        
    def doTrolleyTask(self):
        if base.localAvatar.getZoneId()==2000:
            if base.cr.doFind('Trolley').allowedToEnter():
                base.cr.playGame.getPlace().fsm.forceTransition('walk')
                base.localAvatar.setPos(-133.548, -71.1069, 0.525)
            else:
                Sequence(Wait(2),Func(self.doTrolleyTask)).start()
        else:
            base.cr.playGame.getPlace().requestTeleport(2000,2000,None,None)

        
    def doNPCTask(self,isTrackTask=False):
        try:
            questList=base.localAvatar.quests
            zoneId=Quests.NPCToons.getNPCZone(questList[0][2])
            listedDict=list(Quests.NPCToons.NPCToonDict)
            try:
                npcName=Quests.getNpcInfo(questList[0][2])[0]
            except:
                npcName='HQ Officer'
            if listedDict.count(questList[0][2])==1:
                if zoneId==-1:
                    zoneId=2742
                self.interest=base.cr.addInterest(base.localAvatar.defaultShard, zoneId, 5, None)
                if not isTrackTask:
                    Sequence(Wait(2),Func(self.speakToNpc,npcName)).start()
                else:
                    Sequence(Wait(2),Func(self.chooseTrack,npcName)).start()
        except:
            self.checkWhatToDo()
    
    def doTask(self):
        '''
        Ignore these terrible If's
        '''
        quest=Quests.getQuest(base.localAvatar.quests[0][0])
       
        if self.isQuestComplete() or quest.getType()==Quests.VisitQuest:
            self.doNPCTask()
        
        elif quest.getType()==Quests.DeliverItemQuest:
            self.doNPCTask()
        
        elif quest.getType() in (Quests.CogQuest,Quests.CogLevelQuest,Quests.CogTrackQuest):
            buildingAutoer.clearSettings()
            gagTrainer.clearSettings()
            if quest.getLocation()==11500:
                vpMaxer.otherFunctions.onlyDoFactory()
                vpMaxer.otherFunctions.start()
            elif quest.getType()==Quests.CogTrackQuest:
                if quest.getLocation()==1:
                    if quest.getCogType()=='c' or base.localAvatar.getMaxHp()<30:
                        location=2000
                    elif quest.getCogType()=='s':
                        location=11200
                    elif quest.getCogType()=='m':
                        location=12000
                    else:
                        location=13000
                    gagTrainer.setLocation(location)
                else:
                    gagTrainer.setLocation(quest.getLocation())
                gagTrainer.setCogType(quest.getCogType())
                gagTrainer.start()

            elif quest.getType()==Quests.CogLevelQuest:
                if not base.localAvatar.getTrackAccess()[2] or quest.getLocation() in HQZONES or quest.getCogLevel()<11:
                    if quest.getLocation()==1:
                        gagTrainer.setLocation(self.getBestZoneForCogLevel(quest.getCogLevel()+1))
                    else:
                        if quest.getLocation() in range(12500,12701,1000):
                            cfoMaxer.otherFunctions.onlyLast=False
                            cfoMaxer.otherFunctions.onlyDoMint()
                            cfoMaxer.mintAutoer.setType(quest.getLocation())
                            cfoMaxer.otherFunctions.start()
                        elif quest.getLocation()==11500:
                            vpMaxer.otherFunctions.onlyLast=False
                            vpMaxer.otherFunctions.onlyDoFactory()
                            vpMaxer.otherFunctions.start()
                        else:
                            gagTrainer.setLocation(quest.getLocation())
                        
                    if quest.getCogType()==1:
                        gagTrainer.setCogLevel(quest.getCogLevel())
                    else:
                        gagTrainer.setCogName(self.getSuitName(quest.getCogType()))
                    gagTrainer.start()
                else:
                    if quest.getCogType()==1:
                        buildingAutoer.setBuildingType('')
                        buildingAutoer.setNumFloors(4)
                    else:
                        buildingAutoer.setBuildingType(self.getSuitDepartment(self.getCogType()))
                        buildingAutoer.setNumFloors(4)
                        
                    if quest.getLocation()!=1:
                        buildingAutoer.setLocation(quest.getLocation())
                    else:
                        if base.localAvatar.getMaxHp()>70:
                            buildingAutoer.setLocation(self.getBestZoneForBuildingLevel(5))
                        else:
                            buildingAutoer.setLocation(self.getBestZoneForBuildingLevel(4))
                    buildingAutoer.start()
            else:
                if not base.localAvatar.getTrackAccess()[2] or quest.getLocation() in HQZONES or self.getCogLevelFromCog(quest.getCogType())+4<11:
                
                    if quest.getLocation()==1:
                        if base.localAvatar.getMaxHp()>30 and quest.getCogType()==1:
                            gagTrainer.setLocation(11200)
                        else:
                            gagTrainer.setLocation(self.getBestZoneForCogLevel(self.getCogLevelFromCog(quest.getCogType())+1))
                    else:
                        gagTrainer.setLocation(quest.getLocation())
                            
                    if quest.getCogType()==1:
                        gagTrainer.setCogName(None)
                    else:
                        gagTrainer.setCogName(self.getSuitName(quest.getCogType()))
                    gagTrainer.start()
                else:
                    if quest.getCogType()==1:
                        buildingAutoer.setBuildingType('')
                        buildingAutoer.setNumFloors(4)
                    else:
                        buildingAutoer.setBuildingType(self.getSuitDepartment(quest.getCogType()))
                        buildingAutoer.setNumFloors(4)
                        
                    if quest.getLocation()!=1:
                        buildingAutoer.setLocation(quest.getLocation())
                    else:
                        if base.localAvatar.getMaxHp()>70:
                            buildingAutoer.setLocation(self.getBestZoneForBuildingLevel(5))
                        else:
                            buildingAutoer.setLocation(self.getBestZoneForBuildingLevel(4))
                    buildingAutoer.start()
            
        elif quest.getType()==Quests.BuildingQuest:
            buildingAutoer.clearSettings()
            if quest.getLocation()==1:
                buildingAutoer.setLocation(self.getBestZoneForBuildingLevel(quest.getNumFloors()))
            else:
                buildingAutoer.setLocation(quest.getLocation())
            buildingAutoer.setNumFloors(quest.getNumFloors())
            if quest.getBuildingTrack()==1:
                buildingAutoer.setBuildingType('')
            else:
                buildingAutoer.setBuildingType(quest.getBuildingTrack())
            
            buildingAutoer.start()
        
        elif quest.getType()==Quests.RecoverItemQuest:
            if quest.getHolder()==4:
                if quest.getLocation()==1:
                    if base.localAvatar.getZoneId()!=2000:
                        base.cr.playGame.getPlace().requestTeleport(2000,2000,None,None)
                        self.status='Fishing'
                    else:
                        self.status='Fishing'
                        self.checkWhatToDo()
                    
                else:
                    if base.localAvatar.getZoneId()!=quest.getLocation():
                        base.cr.playGame.getPlace().requestTeleport(quest.getLocation(),quest.getLocation(),None,None)
                        self.status='Fishing'
                    else:
                        self.status='Fishing'
                        self.checkWhatToDo()
            else:
                buildingAutoer.clearSettings()
                gagTrainer.clearSettings()
                if not self.isSuitOnlyBldg(quest.getHolder()) or quest.getHolderType()=='track':
                    if quest.getLocation()==1:
                        if type(quest.getHolder())==int:
                            gagTrainer.setLocation(self.getBestZoneForCogLevel(quest.getHolder()+1))
                        elif quest.getHolderType()=='track':
                            gagTrainer.setLocation(2000)
                        else:
                            gagTrainer.setLocation(self.getBestZoneForCogLevel(self.getCogLevelFromCog(quest.getHolder())+1))
                    else:
                        gagTrainer.setLocation(quest.getLocation())
                     
                    if type(quest.getHolder())==int:
                        gagTrainer.setCogLevel(quest.getHolder())
                    elif quest.getHolderType()=='track':
                        gagTrainer.setCogType(quest.getHolder())
                    else:
                        gagTrainer.setCogName(self.getSuitName(quest.getHolder()))
                    gagTrainer.start()
                    
                elif quest.getLocation()==12000:
                    cfoMaxer.otherFunctions.onlyLast=True
                    cfoMaxer.otherFunctions.onlyDoMint()
                    cfoMaxer.mintAutoer.setType(12500)
                    cfoMaxer.otherFunctions.start()
                    
                elif quest.getLocation()==11000:
                    vpMaxer.otherFunctions.onlyLast=True
                    vpMaxer.otherFunctions.onlyDoFactory()
                    vpMaxer.otherFunctions.start()    
                
                else:
                    if quest.getLocation()==1:
                        buildingAutoer.setLocation(self.getBestZoneForBuildingLevel(4))
                    else:
                        buildingAutoer.setLocation(quest.getLocation())
                    if quest.getHolder()==1:
                        buildingAutoer.setBuildingType('')
                    else:
                        buildingAutoer.setBuildingType(self.getSuitDepartment(quest.getHolder()))
                    buildingAutoer.start()
        
        elif quest.getType()==Quests.DeliverGagQuest:
            Sequence(Func(gagTrainer.restock.restockGags,quest.getGagType()),Wait(2),Func(self.doNPCTask)).start()
                    
        elif quest.getType()==Quests.SkelecogLevelQuest:
            if quest.getLocation()==11000:
                vpMaxer.otherFunctions.onlyLast=False
                vpMaxer.otherFunctions.onlyDoFactory()
                vpMaxer.otherFunctions.start()
            elif quest.getLocation()==12000:
                cfoMaxer.otherFunctions.onlyLast=False
                cfoMaxer.mintAutoer.setType(12500)
                cfoMaxer.otherFunctions.onlyDoMint()
                cfoMaxer.otherFunctions.start()
            elif quest.getLocation()==13000:
                cjMaxer.otherFunctions.onlyDoDa()
                cjMaxer.otherFunctions.start()
            elif quest.getLocation()==1:
                if quest.getCogLevel()<9:
                    vpMaxer.otherFunctions.onlyLast=False
                    vpMaxer.otherFunctions.onlyDoFactory()
                    vpMaxer.otherFunctions.start()
                else:
                    cfoMaxer.otherFunctions.onlyLast=False
                    cfoMaxer.mintAutoer.setType(12500)
                    cfoMaxer.otherFunctions.onlyDoMint()
                    cfoMaxer.otherFunctions.start()
                    
        elif quest.getType() in (Quests.FactoryQuest,Quests.ForemanQuest):
            vpMaxer.otherFunctions.onlyLast=True
            vpMaxer.otherFunctions.onlyDoFactory()
            vpMaxer.otherFunctions.start()
        
        elif quest.getType()==Quests.SupervisorQuest:
            cfoMaxer.otherFunctions.onlyLast=True
            cfoMaxer.otherFunctions.onlyDoMint()
            cfoMaxer.mintAutoer.setType(quest.getLocation())
            cfoMaxer.otherFunctions.start()
       
        elif quest.getType()==Quests.SkeleReviveQuest:
            ceoMaxer.otherFunctions.start()
            
        elif quest.getType()==Quests.TrackChoiceQuest:
            self.doNPCTask(isTrackTask=True)
        
        elif quest.getType()==Quests.TrolleyQuest:
            self.doTrolleyTask()
        
        elif quest.getType()==Quests.PhoneQuest:
            base.localAvatar._LocalToon__handleClarabelleButton()
        
        else:
            base.localAvatar.setSystemMessage(0,'Unknown task')
            
                
    def isQuestComplete(self):
        base.localAvatar.book.pages[4].updatePage()
        if base.localAvatar.book.pages[4].questFrames[0].headline['text']=='COMPLETE':
            return True
        else:
            return False
    
    def isSuitOnlyBldg(self,suitType):
        try:
            if SuitBattleGlobals.SuitAttributes[suitType]['level']+1>6:
                return True
            else:
                return False
        except KeyError:
            return False 

taskAutoer=TaskAutoer()

from toontown.town import Street
from toontown.toon import HealthForceAcknowledge
from toontown.safezone import *
from toontown.toonbase import ToontownBattleGlobals
from toontown.battle import DistributedBattleBldg
from toontown.building import SuitInterior
from toontown.building import DistributedBuilding
from toontown.building import DistributedElevatorExt
from toontown.building import DistributedSuitInterior
from direct.interval.IntervalGlobal import *

ToontownBattleGlobals.SkipMovie=1

faceOffHook = lambda self, ts, name, callback:self._DistributedBattleBldg__handleFaceOffDone()
DistributedBattleBldg.DistributedBattleBldg._DistributedBattleBldg__faceOff = faceOffHook

class BuildingAutoer:
    oldTeleportInStreet=Street.Street.exitTeleportIn
    
    oldExitBecomingToon=DistributedBuilding.DistributedBuilding.exitBecomingToon
    oldEnterHealth=HealthForceAcknowledge.HealthForceAcknowledge.enter
    oldEnterElevator=DistributedSuitInterior.DistributedSuitInterior.enterElevator
    oldEnterFloorReward=DistributedBattleBldg.DistributedBattleBldg.enterReward
    oldEnterBuildingReward=DistributedBattleBldg.DistributedBattleBldg.enterBuildingReward
    
    def __init__(self):
        Street.Street.exitTeleportIn=lambda newSelf,*args,**kwds: self.newTeleportInStreet(newSelf,*args,**kwds)
        
        DistributedBuilding.DistributedBuilding.exitBecomingToon=lambda newSelf: self.newExitBecomingToon(newSelf)
        DistributedSuitInterior.DistributedSuitInterior.enterElevator=lambda newSelf,*args: self.newEnterElevator(newSelf,*args)
        DistributedBattleBldg.DistributedBattleBldg.enterReward=lambda newSelf,*args: self.newEnterFloorReward(newSelf,*args)
        DistributedBattleBldg.DistributedBattleBldg.enterBuildingReward=lambda newSelf,*args: self.newEnterBuildingReward(newSelf,*args)
        HealthForceAcknowledge.HealthForceAcknowledge.enter=lambda newSelf,hplevel: self.newEnterHealth(newSelf,hplevel)
        self.attackSeq=Sequence(Func(self.attack),Wait(1),Func(self.restock),Wait(1))
        self.invisibleSeq=Sequence(Func(base.localAvatar.d_setParent,1),Wait(1))
        self.shouldChangeDistrict=True
        self.shouldChangeStreet=True
        self.shouldChangeHood=False
        self.shouldContinue=False
        self.shouldStop=False
        self.findDistrictIds()
        self.buildingLevel=1
        self.buildingType=''
        self.foundElevator=False
        self.bldgCount=0
        self.hoods=['1','3','4','5','9']
        self.lastElevators=None
        self.killElevators=[]
        self.gagshop_zoneId = 4503
        self.firstTrack=0
        self.secondTrack=4
        self.thirdTrack=2

        self.desiredLevel1=4
        self.desiredLevel2=5
        self.desiredLevel3=5
            
        
    
    def newEnterHealth(self,newSelf,hplevel):
        try:
            self.oldEnterHealth(newSelf,hplevel)
            newSelf.handleOk(base.localAvatar.getHp())
            newSelf.exit()
            if self.shouldContinue:
                Sequence(Wait(2),Func(self.teleportBackToStreet)).start()
        except:
            pass
    
    def createInventory(self):
        desiredInv=""
        for i in range(7*7):
            if i==((self.firstTrack*7)+self.desiredLevel1):
                if self.firstTrack==1:
                    desiredInv+="\x02"
                elif self.desiredLevel1>3:
                    desiredInv+="\x02"
                else:
                    desiredInv+="\x04"
            elif i==((self.secondTrack*7)+self.desiredLevel2):
                if self.secondTrack==1:
                    desiredInv+="\x02"
                elif self.desiredLevel2>3:
                    desiredInv+="\x02"
                else:
                    desiredInv+="\x04"
            elif i==((self.thirdTrack*7)+self.desiredLevel3) and base.localAvatar.getTrackAccess()[self.thirdTrack]:
                if self.thirdTrack==1:
                    desiredInv+="\x02"
                elif self.desiredLevel3>3:
                    desiredInv+="\x02"
                else:
                    desiredInv+="\x04"
            else:
                desiredInv+="\x00"
        self.desiredInv=desiredInv
    
    def clearSettings(self):
        self.buildingType=''
        self.numFloors=1
        
    def teleportBackToStreet(self):
        self.foundElevator=False
        self.walk()
        for treasure in base.cr.doFindAll('Treasure'):
            treasure.sendUpdate('requestGrab')
        base.cr.playGame.getPlace().requestTeleport(round(self.startId,-3),self.startId,None,base.localAvatar.doId)
    
    def findBuilding(self):
        self.checkStop()
        
        if self.shouldContinue:
            for elevator in base.cr.doFindAllInstances(DistributedElevatorExt.DistributedElevatorExt):
                if 'sbfo' not in str(elevator.getElevatorModel()) and 'waitEmpty' in str(elevator.fsm) and elevator.bldg.numFloors>=self.numFloors and self.buildingType in str(elevator.getElevatorModel()) and elevator.doId not in self.killElevators:
                    self.walk()
                    elevator.sendUpdate('requestBoard')
                    self.lastElevator=elevator.doId
                    self.foundElevator=True
                    return
            self.nextZone()
        
    def newTeleportInStreet(self,newSelf,*args,**kwds):
        self.oldTeleportInStreet(newSelf,*args,**kwds)
        self.checkStop()
            
        if self.shouldContinue:
            Sequence(Wait(2),Func(self.findBuilding)).start()
    
    def newExitBecomingToon(self,newSelf):
        self.oldExitBecomingToon(newSelf)
        self.checkStop()
            
        if self.shouldContinue and not self.foundElevator:
            if not taskAutoer.isQuestComplete():
                Sequence(Wait(1),Func(self.findBuilding)).start()
            else:
                self.stop()
                taskAutoer.checkWhatToDo()
            
    def newEnterFloorReward(self,newSelf,*args):
        self.oldEnterFloorReward(newSelf,*args)
        if self.shouldContinue:
            Sequence(Wait(7),Func(self.boardElevator)).start()
    
    def boardElevator(self):
        if self.shouldContinue and base.cr.doFind('Elevator'):
            base.cr.doFind('Elevator').sendUpdate('requestBoard')
            Sequence(Wait(2),Func(base.cr.doFind('Elevator').sendUpdate,'requestExit'),Wait(0.5),Func(base.cr.doFind('Elevator').sendUpdate,'requestBoard')).start()
    
    def newEnterBuildingReward(self,newSelf,*args):
        self.oldEnterBuildingReward(newSelf,*args)
        if self.shouldContinue:
            newSelf.d_rewardDone(base.localAvatar.doId)
            self.foundElevator=False
            self.bldgCount+=1
    
    def newEnterElevator(self,newSelf,*args):
        self.oldEnterElevator(newSelf,*args)
        if self.shouldContinue:
            newSelf.sendUpdate('elevatorDone', [])
            for x in base.cr.doFindAll('DistributedCogdoInterior'):
                x.sendUpdate('elevatorDone', [])
            
    def checkStop(self):
        if self.shouldStop:
            self.shouldContinue=False
            self.shouldStop=False
            self.attackSeq.finish()
            self.invisibleSeq.finish()
    
    def findDistrictIds(self):
        self.shardIds=[]
        for shard in base.cr.activeDistrictMap:
            if base.cr.activeDistrictMap[shard].avatarCount<50:
                self.shardIds.append(shard)
    
    def nextZone(self):
        try:
            base.cr.playGame.getPlace().enterZone(base.localAvatar.getZoneId()+1)
            Sequence(Wait(0.5),Func(self.findBuilding)).start()
        except KeyError:
            if self.shouldChangeStreet:
                self.newStreet()
            else:
                base.cr.playGame.getPlace().enterZone(self.startId)
                Sequence(Wait(0.5),Func(self.findBuilding)).start()
    
    def checkWhatToDo(self):
        if hasattr(base.cr.playGame.getPlace(),'enterZone') and round(base.localAvatar.getZoneId(),-3)==round(self.startId,-3):
            self.findBuilding()
        else:
            if self.startId!=0:
                self.teleportBackToStreet()
            else:
                base.localAvatar.setSystemMessage(0,'The building auto needs to be started on a street')
            
    def newDistrict(self):
        base.cr.playGame.getPlace().requestTeleport(round(base.localAvatar.getZoneId(),-3),self.startId,self.shardIds[0],base.localAvatar.doId)
        self.shardIds.append(self.shardIds[0])
        del self.shardIds[0]
    
    def newStreet(self):
        todo='street'
        if self.startId<9000:
            if int(str(self.startId)[1:])>300:
                if self.shouldChangeDistrict:
                    self.startId-=200
                    todo='district'
                elif self.shouldChangeHood:
                    todo='hood'
                else:
                    self.startId-=200
            else:
                self.startId+=100
        elif int(str(self.startId)[1:])>200:
            if self.shouldChangeDistrict:
                self.startId-=100
                todo='district'
                
            elif self.shouldChangeHood:
                todo='hood'
            else:
                self.startId-=100
        else:
            self.startId+=100
        
        if todo=='district':
            self.newDistrict()
        elif todo=='hood':
            Sequence(Wait(3),Func(self.newHood)).start()
        else:
            self.teleportBackToStreet()
    
    def newHood(self):
        self.startId=int(self.hoods[0]+'102')
        self.hoods.append(self.hoods[0])
        del self.hoods[0]
        self.teleportBackToStreet()
    
    def setLocation(self,zoneId):
        self.startId=int(str(zoneId)[0]+'102')
    
    def setNumFloors(self,numFloors):
        self.numFloors=numFloors
    
    def setBuildingType(self,type):
        if type=='l':
            type='legal'
        elif type=='s':
            type='sales'
        elif type=='m':
            type='money'
        elif type=='c':
            type='corp'
        self.buildingType=type
        
    def workOutStreetId(self):
        zoneId=base.localAvatar.getZoneId()
        self.startId=int(str(zoneId)[:2]+'01')
    
    def loadGagshop(self):         
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
                for clerk in base.cr.doFindAll('Clerk'):
                    clerk.setMovie=lambda *args,**kwds: None
                    clerk.freeAvatar=lambda *args: None
                    clerk.sendUpdate('avatarEnter')
                for clerk in base.cr.doFindAll('Clerk'):
                    clerk.sendUpdate('setInventory', [newString, change, 1])
                    
                money = base.localAvatar.getMoney()
                maxMoney = base.localAvatar.getMaxMoney()
                try:
                    base.cr.bankManager.d_transferMoney(money - maxMoney)
                except AttributeError:
                    pass
        except:
            pass
    
    def unloadGagshop(self):
        if hasattr(self, 'contextId'):
            try:
                base.cr.removeInterest(self.contextId)
            except:
                pass
        
    def restock(self):
        self.desiredLevel1=base.localAvatar.experience.getExpLevel(self.firstTrack)
        if self.desiredLevel1 in [1,3,5]:
            self.desiredLevel1-=1
        self.desiredLevel2=base.localAvatar.experience.getExpLevel(self.secondTrack)
        self.desiredLevel3=base.localAvatar.experience.getExpLevel(self.thirdTrack)
        if self.desiredLevel1>5:
            self.desiredLevel1=4
        if self.desiredLevel2>5:
            self.desiredLevel2=5
        if self.desiredLevel3>5:
            self.desiredLevel3=5
        self.createInventory()
        if base.localAvatar.inventory.inventory[self.firstTrack][self.desiredLevel1]<2 or base.localAvatar.inventory.inventory[self.secondTrack][self.desiredLevel2]<2 or (base.localAvatar.inventory.inventory[self.thirdTrack][self.desiredLevel3]<2 and base.localAvatar.getTrackAccess()[self.thirdTrack]):
            Sequence(Func(self.loadGagshop),Wait(1),Func(self.buyGags),Wait(0.5),Func(self.unloadGagshop)).start()
        
    def attack(self):
        try:
            for battle in base.cr.doFindAll('battle'):
                if base.localAvatar.getTrackAccess()[2]:
                    if base.localAvatar.inventory.inventory[2][self.desiredLevel3]>0:
                        battle.sendUpdate('requestAttack', [2, self.desiredLevel3, battle.suits[0].doId])
                        battle.sendUpdate('movieDone')
                    else:
                        break
                    
                if base.localAvatar.getHp()<(base.localAvatar.getMaxHp()*0.9):
                
                    if base.localAvatar.inventory.inventory[0][self.desiredLevel1]>0:
                        battle.sendUpdate('requestAttack', [0, self.desiredLevel1, base.localAvatar.doId])
                        battle.sendUpdate('movieDone')
                    else:
                        break
                        
                    if base.localAvatar.inventory.inventory[4][self.desiredLevel2]>0:
                        battle.sendUpdate('requestAttack', [4, self.desiredLevel2, battle.suits[0].doId])
                        battle.sendUpdate('movieDone')
                    else:
                        break
                        
                else:
                    if base.localAvatar.inventory.inventory[4][self.desiredLevel2]>0:
                        battle.sendUpdate('requestAttack', [4, self.desiredLevel2, battle.suits[0].doId])
                        battle.sendUpdate('movieDone')
                    else:
                        break
        except:
            pass
    
    def walk(self):
        try:
            base.cr.playGame.getPlace().fsm.forceTransition('walk')
        except:
            pass
        
    def getBuildingType(self):
        if self.buildingType=='legal':
            return 'Lawbot'
        elif self.buildingType=='sales':
            return 'Sellbot'
        elif self.buildingType=='money':
            return 'Cashbot'
        elif self.buildingType=='corp':
            return 'Bossbot'
        else:
            return 'All'
         
    def getBuildingLevel(self):
        return self.buildingLevel
            
    def start(self):
        self.shouldContinue=True
        self.shouldStop=False
        self.createInventory()
        self.attackSeq.loop()
        self.invisibleSeq.loop()
        self.checkWhatToDo()
    
    def stop(self):
        self.shouldContinue=False
        self.shouldStop=False
        self.attackSeq.finish()
        self.invisibleSeq.finish()
        
    def revert(self):
        Street.Street.exitTeleportIn=self.oldTeleportInStreet
        DistributedBuilding.DistributedBuilding.exitBecomingToon=self.oldExitBecomingToon
        HealthForceAcknowledge.HealthForceAcknowledge.enter=self.oldEnterHealth
        DistributedSuitInterior.DistributedSuitInterior.enterElevator=self.oldEnterElevator
        DistributedBattleBldg.DistributedBattleBldg.enterReward=self.oldEnterFloorReward
        DistributedBattleBldg.DistributedBattleBldg.enterBuildingReward=self.oldEnterBuildingReward
        ToontownBattleGlobals.SkipMovie=0
        self.attackSeq.finish()
        
buildingAutoer=BuildingAutoer()

import random
import __main__
from toontown.battle import BattlePlace
from toontown.safezone import *
from toontown.toonbase import ToontownBattleGlobals
from toontown.safezone import Playground
from toontown.suit import DistributedSuit
from toontown.suit import SuitDNA
from toontown.toon import HealthForceAcknowledge
from toontown.battle import DistributedBattle
from toontown.distributed import ToontownClientRepository
from toontown.effects import DistributedFireworkShow
for attribute in dir(DistributedFireworkShow.DistributedFireworkShow):
    exec('DistributedFireworkShow.DistributedFireworkShow.'+attribute+'=lambda *args,**kwds: None')

ToontownBattleGlobals.SkipMovie=1
oldDumpShards=ToontownClientRepository.ToontownClientRepository.dumpAllSubShardObjects
def newDumpShards(self):
    try:
        oldDumpShards(self)
    except:
        pass
ToontownClientRepository.ToontownClientRepository.dumpAllSubShardObjects=newDumpShards
    
suitToDamage={1:4,2:6,3:9,4:13,5:15,6:19,7:22,8:25,9:27,10:29,11:30,12:40}

faceOffHook = lambda self, ts, name, callback:self.d_faceOffDone(self)
DistributedBattle.DistributedBattle._DistributedBattle__faceOff = faceOffHook

oldHandleEnterCollisionSphereParty=DistributedNPCPartyPerson.DistributedNPCPartyPerson.handleCollisionSphereEnter
DistributedNPCPartyPerson.DistributedNPCPartyPerson.handleCollisionSphereEnter=lambda *args: None
oldHandleEnterCollisionSphereFisherman=DistributedNPCFisherman.DistributedNPCFisherman.handleCollisionSphereEnter
DistributedNPCFisherman.DistributedNPCFisherman.handleEnterCollisionSphere=lambda *args: None

hooks='''
try:
    _announceGenerate1
except:
    _announceGenerate1 = DistributedDoor.DistributedDoor.announceGenerate
def announceGenerate(self):
    try:
        _announceGenerate1(self)
    except:
        return None
DistributedDoor.DistributedDoor.announceGenerate = announceGenerate
try:
    _announceGenerate2
except:
    _announceGenerate2 = DistributedPartyGate.DistributedPartyGate.announceGenerate
def announceGenerate(self):
    try:
        _announceGenerate2(self)
    except:
        return None
DistributedPartyGate.DistributedPartyGate.announceGenerate = announceGenerate
try:
    old__init__
except:
    old__init__ = DistributedTrolley.DistributedTrolley.__init__
def new__init__(self, cr):
    for obj in dir(self):
        exec 'self.%s = lambda *x:None' % obj
    return None
DistributedTrolley.DistributedTrolley.__init__ = new__init__
try:
    old__init__2
except:
    old__init__2 = DistributedPartyGate.DistributedPartyGate.__init__
def new__init__2(self, cr):
    for obj in dir(self):
        exec 'self.%s = lambda *x:None' % obj
    return None
DistributedPartyGate.DistributedPartyGate.__init__ = new__init__2
try:
    old__init__3
except:
    old__init__3 = DistributedDoor.DistributedDoor.__init__
def new__init__3(self, cr):
    for obj in dir(self):
        exec 'self.%s = lambda *x:None' % obj
    return None
DistributedDoor.DistributedDoor.__init__ = new__init__3
try:
    old__init__4
except:
    old__init__4 = DistributedPicnicBasket.DistributedPicnicBasket.__init__
def new__init__4(self, cr):
    for obj in dir(self):
        exec 'self.%s = lambda *x:None' % obj
    return None
DistributedPicnicBasket.DistributedPicnicBasket.__init__ = new__init__4
base.localAvatar.stopLookAroundNow()
base.localAvatar.findSomethingToLookAt = lambda *x:None
ToonHead.ToonHead._ToonHead__lookAround = lambda *x:None
'''


class Inventory:

    def __init__(self):
        self.firstTrack=4
        self.secondTrack=5
        self.useOwnLevels=False
        self.firstTrackLevel=0
        self.secondTrackLevel=0
        self.noTrolley=False
        self.inBattle=False
        
    def getInv(self,command):
        if command=="get1":
            try:
                return self.firstTrack
            except:
                return 4
        elif command=="get2":
            try:
                return self.secondTrack
            except:
                return 5
        elif command=="getLevel1":
            try:
                return self.firstTrackLevel
            except:
                return 0
        elif command=="getLevel2":
            try:
                return self.secondTrackLevel
            except:
                return 0
        elif command=="useOwnLevels":
            try:
                return self.useOwnLevels
            except:
                return False
                
    def setThrow1(self):
        self.firstTrack=4
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use throw as first gag',5)
    def setThrow2(self):
        self.secondTrack=4
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use throw as second gag',5)
        
    def setSquirt1(self):
        self.firstTrack=5
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use squirt as first gag',5)
        
    def setSquirt2(self):
        self.secondTrack=5
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use squirt as second gag',5)
        
    def setLure1(self):
        self.firstTrack=2
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use lure as first gag',5)
        
    def setLure2(self):
        self.secondTrack=2
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use lure as second gag',5)
        
    def setTrap1(self):
        self.firstTrack=1
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use trap as first gag',5)
        
    def setTrap2(self):
        self.secondTrack=1
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use trap as second gag',5)
        
    def setSound1(self):
        self.firstTrack=3
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use sound as first gag',5)
        
    def setSound2(self):
        self.secondTrack=3
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use sound as second gag',5)
        
    def setDrop1(self):
        self.firstTrack=6
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use drop as first gag',5)
        
    def setDrop2(self):
        self.secondTrack=6
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use drop as second gag',5)
        
    def setToonUp1(self):
        self.secondTrack=0
        
    def setToonUp2(self):
        self.secondTrack=0
        
    def track1Set1(self):
        self.firstTrackLevel=0
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use level 1 on first track',4)
        
    def track2Set1(self):
        self.secondTrackLevel=0
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use level 1 on second track',4)
        
    def track1Set2(self):
        self.firstTrackLevel=1
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use level 2 on first track',4)
        
    def track2Set2(self):
        self.secondTrackLevel=1
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use level 2 on second track',4)
        
    def track1Set3(self):
        self.firstTrackLevel=2
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use level 3 on first track',4)
        
    def track2Set3(self):
        self.secondTrackLevel=2
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use level 3 on second track',4)
        
    def track1Set4(self):
        self.firstTrackLevel=3
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use level 4 on first track',4)
        
    def track2Set4(self):
        self.secondTrackLevel=3
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use level 4 on second track',4)
        
    def track1Set5(self):
        self.firstTrackLevel=4
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use level 5 on first track',4)
        
    def track2Set5(self):
        self.secondTrackLevel=4
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use level 5 on second track',4)
        
    def track1Set6(self):
        self.firstTrackLevel=5
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use level 6 on first track',4)
        
    def track2Set6(self):
        self.secondTrackLevel=5
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use level 6 on second track',4)
        
    def useLevelsTrue(self):
        self.useOwnLevels=True
        levelsTrueFalse.setText("Using custom levels")
        base.localAvatar.setSystemMessage(0,'Gag trainer set to use levels')
        
    def useLevelsFalse(self):
        self.useOwnLevels=False
        levelsTrueFalse.setText("Not Using custom levels")
        base.localAvatar.setSystemMessage(0,'Gag trainer set to not use levels')
        
    def setNoTrolley(self,value):
        self.noTrolley=value
        
    def getNoTrolley(self):
        return self.noTrolley
    
class Restock:

    def __init__(self):
        self.inventory=Inventory()
        self.tryNum=1
        self.maxCarryGags = base.localAvatar.getMaxCarry()
        self.numToZone={1:2000,2:3000,3:9000,4:4000,5:6000,6:5000}
        self.gagshop_zoneId = 4503
        self.noToons=Sequence(Func(self.removeToons), Wait(3))
        base.localAvatar.stopLookAroundNow()
        
        self.lookAroundHookSeq = Sequence(Func(self.lookAroundHookFunc), Wait(2.5))
        self.lookAroundHookSeq.loop()
        ToonHead.ToonHead._ToonHead__lookAround = lambda *x:None
        
    def lookAroundHookFunc(self):
        if hasattr(base, 'localAvatar'):
            base.localAvatar.findSomethingToLookAt = lambda *x:None
            self.oldFindSomethingToLookAt = base.localAvatar.findSomethingToLookAt
            self.lookAroundHookSeq.finish()
        self.oldLookAround = ToonHead.ToonHead._ToonHead__lookAround
        
    def collectLaff(self):
        for treasure in base.cr.doFindAll('Treasure'):
            treasure.d_requestGrab()
    
    def removeToons(self):
    
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

    def loadGagshop(self):         
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
                for clerk in base.cr.doFindAll('Clerk'):
                    clerk.setMovie=lambda *args: None
                    clerk.freeAvatar=lambda *args: None
                    clerk.sendUpdate('avatarEnter')
                    clerk.sendUpdate('setInventory', [newString, change, 1])
                    
                money = base.localAvatar.getMoney()
                maxMoney = base.localAvatar.getMaxMoney()
                try:
                    base.cr.bankManager.d_transferMoney(money - maxMoney)
                except AttributeError:
                    pass
        except:
            pass
    
    def unloadGagshop(self):
        base.cr.removeInterest(self.contextId)
        
    def restockGags(self,specificGag=[]):
        if not specificGag:
            self.gagShopRetZone = 4503
            self.firstTrack=self.inventory.getInv("get1")
            self.secondTrack=self.inventory.getInv("get2")
            
            firstTrackLevel=self.inventory.getInv("getLevel1")
            secondTrackLevel=self.inventory.getInv("getLevel2")
            useOwnLevel=self.inventory.getInv("useOwnLevels")
            
            desiredLevel1=self.executeGags("return1")
            desiredLevel2=self.executeGags("return2")
            
            if desiredLevel1==6:
                desiredLevel1=5
                
            if desiredLevel2==6:
                desiredLevel2=5
        else:
            self.firstTrack=specificGag[0]
            desiredLevel1=specificGag[1]
            self.secondTrack=5
            desiredLevel2=0
            
        self.desiredInv=""
            
        for i in range(7*7):
            if i==((self.firstTrack*7)+desiredLevel1):
                if desiredLevel1>3:
                    if self.firstTrack==1:
                        self.desiredInv+="\x02"
                    else:
                        self.desiredInv+="\x03"
                        
                elif self.firstTrack==1:
                    self.desiredInv+="\x03"
                    
                else:
                    self.desiredInv+="\x04"
                    
            elif i==((self.secondTrack*7)+desiredLevel2):
                if desiredLevel2>3:
                    if self.secondTrack==1:
                        self.desiredInv+="\x02"
                    else:
                        self.desiredInv+="\x03"
                        
                elif self.secondTrack==1:
                    self.desiredInv+="\x03"
                    
                else:
                    self.desiredInv+="\x04"

            else:
                self.desiredInv+="\x00"
    
        if base.localAvatar.inventory.inventory[self.firstTrack][self.executeGags("return1")]<2 or base.localAvatar.inventory.inventory[self.secondTrack][self.executeGags("return2")]<2 or specificGag:
            Sequence(Func(self.loadGagshop),Wait(1),Func(self.buyGags),Wait(0.5),Func(self.unloadGagshop)).start()
        
    def gainLaff(self):
        if self.tryNum>5:
            self.tryNum=0
        self.tryNum+=1
        
        zone=self.numToZone[self.tryNum]
        if base.localAvatar.getHp()!=base.localAvatar.getMaxHp():
            self.toonUp=base.cr.addInterest(base.localAvatar.defaultShard, zone, 5, None)
            Sequence(Wait(1.0),Func(self.collectLaff),Func(base.cr.removeInterest, self.toonUp)).start()
    
    def gag(self,battle,track,level,toAttack):
        battle.sendUpdate('requestAttack', [track, level, toAttack])
        battle.sendUpdate('movieDone')
        
    def executeGags(self,command):
        badGags=[1,3,5]
        firstTrackLevel=self.inventory.getInv("getLevel1")
        secondTrackLevel=self.inventory.getInv("getLevel2")
        useOwnLevel=self.inventory.getInv("useOwnLevels")
        firstTrack=self.inventory.getInv("get1")
        secondTrack=self.inventory.getInv("get2")
        
        if useOwnLevel:
            desiredLevel1=firstTrackLevel
            desiredLevel2=secondTrackLevel
        else:
            desiredLevel1=base.localAvatar.experience.getExpLevel(firstTrack)
            desiredLevel2=base.localAvatar.experience.getExpLevel(secondTrack)
            
        if desiredLevel1==6:
            desiredLevel1=5
            
        if desiredLevel2==6:
            desiredLevel2=5
        
        if firstTrack==0 and desiredLevel1 in badGags:
            desiredLevel1-=1
            
        if secondTrack==0 and desiredLevel2 in badGags:
            desiredLevel2-=1
            
        if command=="return1":
            return desiredLevel1
        elif command=="return2":
            return desiredLevel2

        for battle in base.cr.doFindAll('battle'):
            if base.localAvatar in battle.toons:
                try:
                    if firstTrack==0:
                        toAttack1=base.localAvatar.doId
                    else:
                        toAttack1=battle.suits[0].doId
                        
                    if secondTrack==0:
                        toAttack2=base.localAvatar.doId
                    else:
                        toAttack2=battle.suits[0].doId
                        
                    if base.localAvatar.inventory.inventory[firstTrack][desiredLevel1]>0:
                        self.gag(battle,firstTrack,desiredLevel1,toAttack1)
                        
                    if base.localAvatar.inventory.inventory[secondTrack][desiredLevel2]>0:
                        self.gag(battle,secondTrack,desiredLevel2,toAttack2)
                                        
                except:
                    pass
        

class GagTrainer:
    oldBattlePlaceTeleportIn=BattlePlace.BattlePlace.exitTeleportIn
    oldEnterReward=DistributedBattle.DistributedBattle.enterReward
    oldEnterFaceOff=DistributedBattle.DistributedBattle.enterFaceOff
    oldDenyBattle=DistributedSuit.DistributedSuit.denyBattle
    oldEnterHealth=HealthForceAcknowledge.HealthForceAcknowledge.enter
    
    def __init__(self):
        self.restock=Restock()
        self.clearSettings()
        self.shouldContinue=False
        self.shouldChangeHood=False
        self.shouldChangeDistrict=True
        self.shouldChangeStreet=True
        self.checkCogWalked=None
        self.shardIds=[]
        for shard in base.cr.activeDistrictMap:
            if base.cr.activeDistrictMap[shard].avatarCount<50:
                self.shardIds.append(shard)
        self.lastCogId=0
        self.buyGags=Sequence(Func(self.restock.restockGags),Wait(3.0))
        self.gainLaff=Sequence(Func(self.restock.gainLaff),Wait(3.0))
        self.battleLoop=Sequence(Wait(1.5),Func(self.restock.executeGags,None))
        self.invisibleSeq=Sequence(Func(base.localAvatar.d_setParent,1),Wait(1))
        DistributedBattle.DistributedBattle.enterReward=lambda newSelf,*args: self.newEnterReward(newSelf,*args)
        DistributedSuit.DistributedSuit.denyBattle=lambda newSelf,*args: self.newDenyBattle(newSelf,*args)
        DistributedBattle.DistributedBattle.enterFaceOff=lambda newSelf,*args: self.newEnterFaceOff(newSelf,*args)
        HealthForceAcknowledge.HealthForceAcknowledge.enter=lambda newSelf,hplevel: self.newEnterHealth(newSelf,hplevel)
        BattlePlace.BattlePlace.exitTeleportIn=lambda newSelf,*args: self.newBattlePlaceTeleportIn(newSelf,*args)
        
    def newEnterHealth(self,newSelf,hplevel):
        try:
            self.oldEnterHealth(newSelf,hplevel)
            newSelf.handleOk(base.localAvatar.getHp())
            newSelf.exit()
            if self.shouldContinue:
                Sequence(Wait(3),Func(self.teleportBackToStreet)).start()
        except:
            pass
    
    def newEnterFaceOff(self,newSelf,*args):
        self.oldEnterFaceOff(newSelf,*args)
        if self.checkCogWalked:
            self.checkCogWalked.pause()
    
    def newDenyBattle(self,newSelf,*args):
        self.oldDenyBattle(newSelf,*args)
        if self.lastCogId==newSelf.doId and self.shouldContinue:
            if self.checkCogWalked:
                self.checkCogWalked.pause()
            Sequence(Wait(1),Func(self.enterRandomBattle)).start()
    
    def newEnterReward(self,newSelf,*args):
        self.oldEnterReward(newSelf,*args)
        if base.localAvatar in newSelf.toons and self.shouldContinue:
            newSelf.d_rewardDone(base.localAvatar.doId)
            
            if not taskAutoer.isQuestComplete():
                Sequence(Wait(3),Func(self.enterRandomBattle)).start()
            else:
                self.stop()
                base.localAvatar.collisionsOff()
                Sequence(Wait(3),Func(taskAutoer.checkWhatToDo)).start()
    
    def newBattlePlaceTeleportIn(self,newSelf,*args):
        self.oldBattlePlaceTeleportIn(newSelf,*args)
        if self.shouldContinue:
            self.startLoops()
            Sequence(Wait(2),Func(self.enterRandomBattle)).start()
    
    def clearSettings(self):
        self.hasSettings=False
        self.cogName=None
        self.cogType=None
        self.cogLevel=None
    
    def setCogName(self,name):
        self.hasSettings=True
        self.cogName=name
    
    def setCogType(self,type):
        self.hasSettings=True
        if type=='l':
            type='Lawbot'
        elif type=='s':
            type='Sellbot'
        elif type=='m':
            type='Cashbot'
        elif type=='c':
            type='Bossbot'
        self.cogType=type
    
    def setCogLevel(self,level):
        self.hasSettings=True
        self.cogLevel=level
       
    def newDistrict(self):
        base.cr.playGame.getPlace().requestTeleport(round(base.localAvatar.getZoneId(),-3),self.streetId,self.shardIds[0],base.localAvatar.doId)
        self.shardIds.append(self.shardIds[0])
        del self.shardIds[0]
        
    def newStreet(self):
        todo='street'
        if self.streetId<9000:
            if int(str(self.streetId)[1:])>300:
                if self.shouldChangeDistrict:
                    self.streetId-=200
                    todo='district'
                elif self.shouldChangeHood:
                    todo='hood'
                else:
                    self.streetId-=200
            else:
                self.streetId+=100
        elif int(str(self.streetId)[1:])>200:
            if self.shouldChangeDistrict:
                self.streetId-=100
                todo='district'
                
            elif self.shouldChangeHood:
                todo='hood'
            else:
                self.streetId-=100
        else:
            self.streetId+=100
        
        if todo=='district':
            Sequence(Wait(2),Func(self.newDistrict)).start()
        elif todo=='hood':
            self.newHood()
        else:
            self.teleportBackToStreet()  
        
    def nextZone(self):
        try:
            base.cr.playGame.getPlace().enterZone(base.localAvatar.getZoneId()+1)
            Sequence(Wait(0.5),Func(self.enterRandomBattle)).start()
        except KeyError:
            if self.shouldChangeStreet:
                self.newStreet()
            else:
                base.cr.playGame.getPlace().enterZone(self.streetId)
                Sequence(Wait(0.5),Func(self.enterRandomBattle)).start()
                
    def enterRandomBattle(self):
        if self.checkCogWalked:
            self.checkCogWalked.pause()
        firstTrack=self.restock.inventory.getInv("get1")
        secondTrack=self.restock.inventory.getInv("get2")
        battles = []
        battles2 = []
        for x in base.cr.doFindAllInstances(DistributedSuit.DistributedSuit):
            if x.activeState == 6:
                if x.getCurrentAnim() in ['walk','landing']:
                    if self.hasSettings and x.getActualLevel()>=self.cogLevel and (x.getName()==self.cogName or x.getStyleDept()==self.cogType or (not self.cogType and not self.cogName)):
                        battles.append(x)
                        battles2.append(True)
                    elif not self.hasSettings and x.getActualLevel()>self.restock.executeGags("return2") and x.getActualLevel()>self.restock.executeGags("return2"):
                        if base.localAvatar.getMaxHp()>suitToDamage[x.getActualLevel()] or self.restock.executeGags("return1")>3 or self.restock.executeGags("return2")>3:
                            battles.append(x)
                            battles2.append(True)
                        elif self.getPlace()>=11200 and self.getPlace()<=11300 and self.restock.executeGags("return1")>2 and self.restock.executeGags("return2")>2:
                            battles.append(x)
                            battles2.append(True)
                        else:
                            battles2.append(False)
                    else:
                        battles2.append(False)
        if not taskAutoer.isQuestComplete():
            try:
                if battles and base.localAvatar.getHp()>0:
                    battle = random.choice(battles)
                    pos, hpr = battle.getPos(), battle.getHpr()
                    base.localAvatar.collisionsOn()
                    base.localAvatar.setPosHpr(pos, hpr)
                    battle.d_requestBattle(pos,hpr)
                    self.checkCogWalked=Sequence(Wait(20),Func(self.enterRandomBattle))
                    self.checkCogWalked.start()
                    self.lastCogId=battle.doId
                else:
                    if hasattr(base.cr.playGame.getPlace(),'enterZone') and base.localAvatar.getZoneId() not in range(HQZONES[0],HQZONES[-1]+1000):
                        self.nextZone()
                    else:
                        self.newDistrict()
            except:
                pass
        else:
            self.stop()
            base.localAvatar.collisionsOff()
            Sequence(Wait(2),Func(taskAutoer.checkWhatToDo)).start()
    
    def setLocation(self,zoneId):
        if zoneId in range(10000,13999):
            self.streetId=zoneId
        elif round(zoneId,-3)!=zoneId:
            self.streetId=zoneId+2
        else:
            self.streetId=zoneId+102
    
    def teleportBackToStreet(self):
        self.walk()
        self.restock.collectLaff()
        base.cr.playGame.getPlace().requestTeleport(round(self.streetId,-3),self.streetId,None,base.localAvatar.doId)
    
    def startLoops(self):
        self.buyGags.loop()
        self.gainLaff.loop()
        self.battleLoop.loop()
        self.invisibleSeq.loop()
    
    def stopLoops(self):
        self.buyGags.finish()
        self.gainLaff.finish()
        self.battleLoop.finish()
        self.invisibleSeq.finish()
    
    def start(self):
        if base.localAvatar.getTrackAccess()[0]:
            self.restock.inventory.setToonUp2()
        self.shouldContinue=True
        exec hooks in __main__.__dict__
        if base.localAvatar.getZoneId() not in range(self.streetId,self.streetId+90):
            self.teleportBackToStreet()
        else:
            self.startLoops()
            self.enterRandomBattle()
    
    def stop(self):
        DistributedDoor.DistributedDoor.announceGenerate=_announceGenerate1
        DistributedPartyGate.DistributedPartyGate.announceGenerate=_announceGenerate2
        DistributedTrolley.DistributedTrolley.__init__=old__init__
        DistributedPartyGate.DistributedPartyGate.__init__=old__init__2
        DistributedDoor.DistributedDoor.__init__=old__init__3
        DistributedPicnicBasket.DistributedPicnicBasket.__init__=old__init__4
        self.shouldContinue=False
        self.stopLoops()
    
    def walk(self):
        base.cr.playGame.getPlace().fsm.forceTransition('walk')
        
gagTrainer=GagTrainer()

import random
from direct.interval.IntervalGlobal import *
from direct.distributed import DistributedObject
from toontown.toonbase import ToontownBattleGlobals
from toontown.toon import *
from toontown.coghq import *
from toontown.distributed import ToontownClientRepository
from toontown.battle import DistributedBattle
from toontown.battle import DistributedBattleFinal
from toontown.suit.DistributedFactorySuit import DistributedFactorySuit
from toontown.suit import DistributedSuit
from toontown.suit import DistributedSellbotBoss
from toontown.building import DistributedDoor
from toontown.building import DistributedBoardingParty

ToontownBattleGlobals.SkipMovie=1
ToontownClientRepository.ToontownClientRepository.forbidCheesyEffects=lambda *x,**kwds: None

faceOffHook = lambda self, ts, name, callback:self.d_faceOffDone(self)
DistributedBattleFactory.DistributedBattleFactory._DistributedLevelBattle__faceOff = faceOffHook
DistributedBattle.DistributedBattle._DistributedBattle__faceOff = faceOffHook

oldHandleEnterCollisionSphereParty=DistributedNPCPartyPerson.DistributedNPCPartyPerson.handleCollisionSphereEnter
DistributedNPCPartyPerson.DistributedNPCPartyPerson.handleCollisionSphereEnter=lambda *args: None
oldHandleEnterCollisionSphereFisherman=DistributedNPCFisherman.DistributedNPCFisherman.handleCollisionSphereEnter
DistributedNPCFisherman.DistributedNPCFisherman.handleEnterCollisionSphere=lambda *args: None

class restock:

    def __init__(self):
        if not base.localAvatar.getTrackAccess()[0] or base.localAvatar.experience.getExpLevel(0)<4:
            self.noToonUp=True
            self.secondTrack=4
            self.desiredLevel2=5
        else:
            self.noToonUp=False
            self.secondTrack=0
            self.desiredLevel2=4
            
        if not base.localAvatar.getTrackAccess()[2] or base.localAvatar.experience.getExpLevel(2)<5:
            self.noLure=True
            self.firstTrack=4
            self.desiredLevel1=5
        else:
            self.noLure=False
            self.firstTrack=2
            self.desiredLevel1=5
            
        if base.localAvatar.experience.getExpLevel(4)<5:
            base.localAvatar.setSystemMessage(0,'You do not have the required throw level to run this.')
            
        self.thirdTrack=4
        self.desiredLevel3=5
        self.createInventory()
        self.maxCarryGags = base.localAvatar.getMaxCarry()
        self.gagshop_zoneId = 4503
        self.noToons=Sequence(Func(self.removeToons), Wait(1.5))
        self.noTrolley=False
        self.unloaded=True
        self.wasInBattle=False
        
        self.lookAroundHookSeq = Sequence(Func(self.lookAroundHookFunc), Wait(2.5))
        self.lookAroundHookSeq.loop()
        ToonHead.ToonHead._ToonHead__lookAround = lambda *x:None
    
    def createInventory(self):
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
        if hasattr(base, 'localAvatar'):
            base.localAvatar.findSomethingToLookAt = lambda *x:None
            self.oldFindSomethingToLookAt = base.localAvatar.findSomethingToLookAt
            self.lookAroundHookSeq.finish()
        self.oldLookAround = ToonHead.ToonHead._ToonHead__lookAround
        
    def collectLaff(self):
        for treasure in base.cr.doFindAll('Treasure'):
            treasure.d_requestGrab()
            
    def removeToons(self):
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
                for clerk in base.cr.doFindAll('Clerk'):
                    clerk.setMovie=lambda *args,**kwds: None
                    clerk.freeAvatar=lambda *args: None
                    clerk.sendUpdate('avatarEnter')
                    clerk.sendUpdate('setInventory', [newString, change, 1])
                    
                money = base.localAvatar.getMoney()
                maxMoney = base.localAvatar.getMaxMoney()
                base.cr.bankManager.d_transferMoney(money - maxMoney)
        except:
            pass
    
    def unloadGagshop(self):
        if hasattr(self, 'contextId'):
            try:
                base.cr.removeInterest(self.contextId)
            except:
                pass
        
    def restock(self):
        try:
            if base.localAvatar.inventory.inventory[self.firstTrack][self.desiredLevel1]<2 or base.localAvatar.inventory.inventory[self.secondTrack][self.desiredLevel2]<2 or base.localAvatar.inventory.inventory[self.thirdTrack][self.desiredLevel3]<2:
                Sequence(Func(self.loadGagshop),Wait(1),Func(self.buyGags),Wait(0.5),Func(self.unloadGagshop)).start()
        
        except:
            pass
    
    def revertFunctions(self):
        self.noToons.finish()
        try:
            base.cr.removeInterest(self.interest1)
            base.cr.removeInterest(self.interest2)
            self.unloaded=True
        except:
            pass
            
class OtherFunctions:

    oldGardensInit=DGPlayground.DGPlayground.__init__
    oldSellbotInit=SellbotHQExterior.SellbotHQExterior.__init__
    oldSendUpdate=DistributedObject.DistributedObject.sendUpdate
    oldEnterHealth=HealthForceAcknowledge.HealthForceAcknowledge.enter
    oldSetAnim=LocalToon.LocalToon.setAnimState
    oldPostInvite=DistributedBoardingParty.DistributedBoardingParty.postInvite


    def __init__(self):
        self.shouldContinue=False
        self.bossCount=0
        self.shouldEnd=False
        self.onlyLast=True
        self.onlyFactory=False
        self.canSetParentAgain=True
        self.isMember=True
        self.numberToSuit={0:'Cold Caller',1:'Telemarketer',2:'Name Dropper',3:'Glad Hander',
                           4:'Mover & Shaker',5:'Two-Face',6:'The Mingler',7:'Mr. Hollywood'}

        DGPlayground.DGPlayground.__init__=lambda *args:self.newGardensInit(*args)
        SellbotHQExterior.SellbotHQExterior.__init__=lambda *args: self.newSellbotInit(*args)
        HealthForceAcknowledge.HealthForceAcknowledge.enter=lambda newSelf,hplevel: self.newEnterHealth(newSelf,hplevel)
        LocalToon.LocalToon.setAnimState=lambda *args,**kwds:self.newSetAnimState(*args,**kwds)
        DistributedBoardingParty.DistributedBoardingParty.postInvite=lambda newSelf,leaderId,inviterId: self.newPostInvite(newSelf,leaderId,inviterId)

    def attack(self):
        try:
            for battle in base.cr.doFindAll('battle'):
                if vpMaxer.factoryAutoer.roomNum==len(vpMaxer.factoryAutoer.roomsNeeded):
                    if len(battle.suits)>1:
                        for suit in battle.suits: 
                            if suit.getName()!='Skelecog':
                                attackSuit=suit
                    else:
                        attackSuit=battle.suits[0]
                else:
                    attackSuit=battle.suits[0]
                    
                if vpMaxer.restock.noToonUp and not vpMaxer.restock.noLure:
                    if vpMaxer.restock.firstTrack==2 and base.localAvatar.getHp()>(base.localAvatar.getMaxHp()*0.75):
                        battle.sendUpdate('requestAttack', [vpMaxer.restock.firstTrack, vpMaxer.restock.desiredLevel1, attackSuit.doId])
                    if base.localAvatar.getHp()>(base.localAvatar.getMaxHp()*0.75):
                        battle.sendUpdate('requestAttack', [vpMaxer.restock.thirdTrack, vpMaxer.restock.desiredLevel3, attackSuit.doId])
                        
                elif vpMaxer.restock.noLure:
                    if vpMaxer.restock.secondTrack==0 and base.localAvatar.getHp()<(base.localAvatar.getMaxHp()*0.75):
                        battle.sendUpdate('requestAttack', [vpMaxer.restock.secondTrack, vpMaxer.restock.desiredLevel2, base.localAvatar.doId])
                    if base.localAvatar.getHp()>(base.localAvatar.getMaxHp()*0.75):
                        battle.sendUpdate('requestAttack', [vpMaxer.restock.thirdTrack, vpMaxer.restock.desiredLevel3, attackSuit.doId])
                        
                else:
                    if base.localAvatar.inventory.inventory[vpMaxer.restock.firstTrack][vpMaxer.restock.desiredLevel1]>0:
                        battle.sendUpdate('requestAttack', [vpMaxer.restock.firstTrack, vpMaxer.restock.desiredLevel1, attackSuit.doId])
                    else:
                        break
                        
                    if base.localAvatar.getHp()<(base.localAvatar.getMaxHp()*0.5):
                    
                        if base.localAvatar.inventory.inventory[vpMaxer.restock.secondTrack][vpMaxer.restock.desiredLevel2]>0:
                            battle.sendUpdate('requestAttack', [vpMaxer.restock.secondTrack, vpMaxer.restock.desiredLevel2, base.localAvatar.doId])
                        else:
                            break
                            
                        if base.localAvatar.inventory.inventory[vpMaxer.restock.thirdTrack][vpMaxer.restock.desiredLevel3]>0:
                            battle.sendUpdate('requestAttack', [vpMaxer.restock.thirdTrack, vpMaxer.restock.desiredLevel3, attackSuit.doId])
                        else:
                            break
                            
                    else:
                        if base.localAvatar.inventory.inventory[vpMaxer.restock.thirdTrack][vpMaxer.restock.desiredLevel3]>0:
                            battle.sendUpdate('requestAttack', [vpMaxer.restock.thirdTrack, vpMaxer.restock.desiredLevel3, attackSuit.doId])
                        else:
                            break
        except:
            pass
        
    def sendUpdateHook(self, newself, fieldName, args=[], sendToId=None):
        if fieldName=="requestAttack":
            self.oldSendUpdate(newself,"requestAttack", args, sendToId)
            self.oldSendUpdate(newself,"movieDone",[])
            newself.d_rewardDone(base.localAvatar.doId)
        else:
            self.oldSendUpdate(newself,fieldName, args, sendToId)
        
    def newGardensInit(self,*args):
        self.oldGardensInit(*args)
        if self.shouldContinue:
            vpMaxer.factoryAutoer.gainLaffSeq.finish()
            vpMaxer.factoryAutoer.attackSeq.finish()
            vpMaxer.restock.wasInBattle=False
            self.checkMerits()
    
    def newSetAnimState(self,*args,**kwds):
        self.oldSetAnim(*args,**kwds)
        if self.canSetParentAgain and self.shouldContinue:
            base.localAvatar.d_setParent(1)
            self.canSetParentAgain=False
            Sequence(Wait(2),Func(self.doUnsetCanSetParentAgain)).start()
    
    def doUnsetCanSetParentAgain(self):
        self.canSetParentAgain=True
    
    def newEnterHealth(self,newSelf,hplevel):
        try:
            self.oldEnterHealth(newSelf,hplevel)
            newSelf.handleOk(base.localAvatar.getHp())
            newSelf.exit()
            if self.shouldContinue:
                Sequence(Wait(2),Func(self.checkMerits)).start()
        except:
            pass
            
    def newSellbotInit(self,*args):
        self.oldSellbotInit(*args)
        if self.shouldContinue:
            self.walk()
            base.localAvatar.setWantBattles(False)
            Sequence(Wait(2),Func(self.checkMerits)).start()
    
    def newPostInvite(self,newSelf,leaderId,inviterId):
        if leaderId==base.localAvatar.doId:
            newSelf.sendUpdate('requestAcceptInvite',[inviterId,leaderId])
        else:
            self.oldPostInvite(newSelf,leaderId,inviterId)
        
    def checkMerits(self):
        if taskAutoer.isQuestComplete():
            self.stop()
            taskAutoer.checkWhatToDo()
        if self.onlyFactory:
            if self.onlyLast:
                base.localAvatar.cogMerits[3]+=self.getMeritsLeft()-1
            else:
                base.localAvatar.cogMerits[3]=-4000
        if self.shouldEnd:
            self.shouldContinue=False
        if self.shouldContinue:
            if self.getMeritsLeft()==0 and not self.onlyFactory:
                if base.cr.doFind('DistributedSellbotHQDoor') and base.localAvatar.getZoneId()>=11000 and base.localAvatar.getZoneId()<11100:
                    vpMaxer.vpAutoer.start()
                else:
                    vpMaxer.restock.restock()
                    vpMaxer.restock.collectLaff()
                    self.walk()
                    Sequence(Wait(2),Func(self.teleBack)).start()
            else:
                if base.cr.doFind('DistributedSellbotHQDoor') and base.localAvatar.getZoneId()>=11000 and base.localAvatar.getZoneId()<11100:
                    vpMaxer.factoryAutoer.goFactory()
                else:
                    vpMaxer.restock.restock()
                    vpMaxer.restock.collectLaff()
                    self.walk()
                    Sequence(Wait(2),Func(self.teleBack)).start()
        else:
            vpMaxer.restock.noToons.finish()
            base.cr.removeInterest(vpMaxer.restock.interest1)
            base.cr.removeInterest(vpMaxer.restock.interest2)
            vpMaxer.restock.unloaded=True
            vpMaxer.factoryAutoer.attackSeq.finish()
            vpMaxer.factoryAutoer.generateAgain()
    
    def getMeritsLeft(self):
        return CogDisguiseGlobals.getTotalMerits(base.localAvatar,3)-base.localAvatar.cogMerits[3]

    def walk(self):
        try:
            base.cr.playGame.getPlace().fsm.forceTransition('walk')
        except:
            pass
       
    def teleBack(self,zone=11000):
        try:
            self.walk()
            base.cr.playGame.getPlace().handleBookCloseTeleport(zone, zone)
        except:
            pass
            
    def onlyDoFactory(self):
        self.onlyFactory=True
        base.localAvatar.setSystemMessage(0,'The VP Maxer will do only factory runs')
        
    def doBoth(self):
        self.onlyFactory=False
        base.localAvatar.setSystemMessage(0,'The VP Maxer will do both factories and VPs')
        
    def haveJb(self):
        if base.localAvatar.cogLevels[0]==49:
            return True
        elif base.localAvatar.getTotalMoney()<100:
            return False
        else:
            return True
        
    def stop(self):
        base.localAvatar.died=lambda *args: None
        self.shouldContinue=True
        self.shouldEnd=True
    
    def start(self):
        DistributedObject.DistributedObject.sendUpdate=lambda newself, fieldName, args=[], sendToId=None: self.sendUpdateHook(newself, fieldName, args, sendToId)
        base.localAvatar.died=lambda *args: vpMaxer.factoryAutoer.newSafeZone(*args)
        self.shouldEnd=False
        self.shouldContinue=True
        self.bossCount=0
        vpMaxer.restock.noToons.loop()
        self.checkMerits()
        
    def revertFunctions(self):
        LocalToon.LocalToon.setAnimState=self.oldSetAnim
        DGPlayground.DGPlayground.__init__=self.oldGardensInit
        SellbotHQExterior.SellbotHQExterior.__init__=self.oldSellbotInit
        DistributedObject.DistributedObject.sendUpdate=self.oldSendUpdate
        HealthForceAcknowledge.HealthForceAcknowledge.enter=self.oldEnterHealth
        DistributedBoardingParty.DistributedBoardingParty.postInvite=self.oldPostInvite

class VpAutoer:
    oldBossEnterElevator=DistributedSellbotBoss.DistributedSellbotBoss.enterElevator
    oldEnterBattleThree=DistributedSellbotBoss.DistributedSellbotBoss.enterBattleThree
    oldEnterPrepareBattleTwo=DistributedSellbotBoss.DistributedSellbotBoss.enterPrepareBattleTwo
    oldEnterPrepareBattleThree=DistributedSellbotBoss.DistributedSellbotBoss.enterPrepareBattleThree
    oldEnterEpilogue=DistributedSellbotBoss.DistributedSellbotBoss.enterEpilogue
    oldEnterRollToBattleTwo=DistributedSellbotBoss.DistributedSellbotBoss.enterRollToBattleTwo
    oldEnterWaitForInput=DistributedBattleFinal.DistributedBattleFinal.enterWaitForInput
    oldBossEnterIntro=DistributedSellbotBoss.DistributedSellbotBoss.enterIntroduction
    oldAvatarExit=DistributedCogHQDoor.DistributedCogHQDoor.avatarExit
    oldEnterWalk=CogHQLobby.CogHQLobby.enterWalk
    
    def __init__(self):
        self.filter=False
        self.cardsWanted=['Flippy','Barnacle Bessie','Lil Oldman','Professor Pete','Stinky Ned','Daffy Don','Moe Zart','Sid Sonata','Franz Neckvein']
        
        DistributedSellbotBoss.DistributedSellbotBoss.enterElevator=lambda newSelf: self.newBossEnterElevator(newSelf)
        DistributedSellbotBoss.DistributedSellbotBoss.enterIntroduction=lambda newSelf,*args: self.newBossEnterIntro(newSelf,*args)
        DistributedSellbotBoss.DistributedSellbotBoss.enterRollToBattleTwo=lambda newSelf: self.newEnterRollToBattleTwo(newSelf)
        DistributedSellbotBoss.DistributedSellbotBoss.enterBattleThree=lambda newSelf: self.newEnterBattleThree(newSelf)
        DistributedBattleFinal.DistributedBattleFinal.enterWaitForInput=lambda *args: self.newEnterWaitForInput(*args)
        DistributedCogHQDoor.DistributedCogHQDoor.avatarExit=lambda newSelf,id: self.newAvatarExit(newSelf,id)
        CogHQLobby.CogHQLobby.enterWalk=lambda newSelf,*args,**kwds: self.newEnterWalk(newSelf,*args,**kwds)
        DistributedSellbotBoss.DistributedSellbotBoss.enterPrepareBattleThree=lambda newSelf: self.newEnterPrepareBattleThree(newSelf)
        DistributedSellbotBoss.DistributedSellbotBoss.enterPrepareBattleTwo=lambda newSelf: self.newEnterPrepareBattleTwo(newSelf)
        DistributedSellbotBoss.DistributedSellbotBoss.enterEpilogue=lambda newSelf: self.newEnterEpilogue(newSelf)
        
    def newBossEnterElevator(self,newSelf):
        self.oldBossEnterElevator(newSelf)
        if vpMaxer.otherFunctions.shouldContinue:
            newSelf._DistributedBossCog__doneElevator()
            
    def newBossEnterIntro(self,newSelf,*args):
        self.oldBossEnterIntro(newSelf,*args)
        if vpMaxer.otherFunctions.shouldContinue:
            if self.cardFilter():
                newSelf.exitIntroduction()
            else:
                Sequence(Wait(2),Func(vpMaxer.otherFunctions.teleBack)).start()
    
    def newEnterEpilogue(self,newSelf):
        self.oldEnterEpilogue(newSelf)
        if vpMaxer.otherFunctions.shouldContinue:
            vpMaxer.otherFunctions.bossCount+=1
            vpMaxer.otherFunctions.teleBack()
    
    def newEnterRollToBattleTwo(self,newSelf):
        self.oldEnterRollToBattleTwo(newSelf)
        if vpMaxer.otherFunctions.shouldContinue:
            newSelf.exitRollToBattleTwo()
    
    def newEnterPrepareBattleTwo(self,newSelf):
        self.oldEnterPrepareBattleTwo(newSelf)
        if vpMaxer.otherFunctions.shouldContinue:
            newSelf._DistributedSellbotBoss__onToBattleTwo(33)
    
    def newEnterPrepareBattleThree(self,newSelf):
        self.oldEnterPrepareBattleThree(newSelf)
        if vpMaxer.otherFunctions.shouldContinue:
            newSelf._DistributedSellbotBoss__onToBattleThree(33)
    
    def newEnterBattleThree(self,newSelf):
        self.oldEnterBattleThree(newSelf)
        if vpMaxer.otherFunctions.shouldContinue:
            self.endBattle()
    
    def newEnterWaitForInput(self,*args):
        self.oldEnterWaitForInput(*args)
        if vpMaxer.otherFunctions.shouldContinue:
            self.exploit()
    
    def newEnterWalk(self,newSelf,*args,**kwds):
        self.oldEnterWalk(newSelf,*args,**kwds)
        if len(args)>0:
            if vpMaxer.otherFunctions.shouldContinue and args[0]:
                self.goVpBattle()
            
        
    def newAvatarExit(self,newSelf,id):
        self.oldAvatarExit(newSelf,id)
        if base.cr.doFind('Elevator') and id==base.localAvatar.doId and vpMaxer.otherFunctions.shouldContinue:
            self.goVpBattle()

    def goVpBattle(self):
        vpMaxer.otherFunctions.walk()
        base.localAvatar.setWantBattles(True)
        base.cr.doFind('Boarding').sendUpdate('requestLeave',[base.localAvatar.doId])
        base.cr.doFind('Boarding').sendUpdate('requestInvite',[base.localAvatar.doId])
        base.cr.doFind('Boarding').sendUpdate('requestGoToSecondTime',[base.cr.doFind('Elevator').doId])
            
    def destroyBattle(self):
        base.cr.doFind('SafeZone').sendUpdate('enterSafeZone')
    
    def filterOn(self):
        self.filter=True
        self.cardsWanted=['Flippy','Barnacle Bessie','Lil Oldman','Professor Pete','Stinky Ned','Daffy Don','Moe Zart','Sid Sonata','Franz Neckvein']
        base.localAvatar.setSystemMessage(0,'The VP Maxer will filter bad cards')
    
    def filterOn16(self):
        self.filter=True
        self.cardsWanted=['Flippy', 'Daffy Don', 'Clerk Clara', 'Clerk Penny', 'Lil Oldman', 'Stinky Ned', 'Moe Zart', 'Sid Sonata', 'Barnacle Bessie',\
                          'Franz Neckvein', 'Madam Chuckle', 'Clerk Will', 'Nancy Gas', 'Mr. Freeze', 'Professor Pete', 'Soggy Nell']
        base.localAvatar.setSystemMessage(0,'The VP Maxer will filter for 16 cards')
    
    def filterOff(self):
        self.filter=False
        base.localAvatar.setSystemMessage(0,'The VP Maxer will not filter bad cards')

    def exploit(self):
        Sequence(Func(self.destroyBattle), Wait(.5), Func(vpMaxer.otherFunctions.walk)).start()
        
    def endBattle(self):
        if base.cr.doFind('V. P'):
            base.cr.doFind('V. P').sendUpdate('hitBossInsides')
            base.cr.doFind('V. P').sendUpdate('hitBoss', [100])
            base.cr.doFind('V. P').sendUpdate('finalPieSplat')

    def start(self):
        if vpMaxer.otherFunctions.isMember:
            base.localAvatar.collisionsOff()
            base.cr.doFind('DistributedSellbotHQDoor').sendUpdate('requestEnter')
        else:
            vpMaxer.otherFunctions.walk()
            base.cr.playGame.getPlace().requestTeleport(11000,11100,None,None)
            
    def cardFilter(self):
        if base.cr.doFind('V. P').cagedToon.getName() in self.cardsWanted or not self.filter:
            return True
        else:
            return False
    
    def revertFunctions(self):
        DistributedSellbotBoss.DistributedSellbotBoss.enterElevator=self.oldBossEnterElevator
        DistributedSellbotBoss.DistributedSellbotBoss.enterBattleThree=self.oldEnterBattleThree
        DistributedSellbotBoss.DistributedSellbotBoss.enterPrepareBattleTwo=self.oldEnterPrepareBattleTwo
        DistributedSellbotBoss.DistributedSellbotBoss.enterPrepareBattleThree=self.oldEnterPrepareBattleThree
        DistributedSellbotBoss.DistributedSellbotBoss.enterEpilogue=self.oldEnterEpilogue
        DistributedSellbotBoss.DistributedSellbotBoss.enterRollToBattleTwo=self.oldEnterRollToBattleTwo
        DistributedBattleFinal.DistributedBattleFinal.enterWaitForInput=self.oldEnterWaitForInput
        DistributedSellbotBoss.DistributedSellbotBoss.enterIntroduction=self.oldBossEnterIntro
        DistributedCogHQDoor.DistributedCogHQDoor.avatarExit=self.oldAvatarExit
        CogHQLobby.CogHQLobby.enterWalk=self.oldEnterWalk
            
class FactoryAutoer:
    oldFactoryInit=FactoryExterior.FactoryExterior.__init__
    oldDistributedFactoryInit=DistributedFactory.DistributedFactory.__init__
    oldEnterReward=DistributedBattleFactory.DistributedBattleFactory.enterReward
    oldEnterFactoryReward=DistributedBattleFactory.DistributedBattleFactory.enterFactoryReward
    
    def __init__(self,vpMaxer):
        self.roomNum=0
        self.zones=[4,7,8,13,22,24,34,32]
        self.roomValues=[28,36,32,56,32,40,80,56]
        self.gainLaffSeq=Sequence(Func(vpMaxer.restock.gainLaff),Wait(3.0))
        self.attackSeq=Sequence(Func(vpMaxer.restock.restock),Wait(1.0),Func(vpMaxer.otherFunctions.attack),Wait(1.0))
        
        FactoryExterior.FactoryExterior.__init__=lambda *args: self.newFactoryInit(*args)
        DistributedFactory.DistributedFactory.__init__=lambda *args: self.newDistributedFactoryInit(*args)
        DistributedBattleFactory.DistributedBattleFactory.enterReward=lambda newSelf,*args:self.newEnterReward(newSelf,*args)
        base.cr.doFind('SafeZone').d_enterSafeZone=lambda *args: self.newSafeZone(*args)
        DistributedBattleFactory.DistributedBattleFactory.d_toonDied=lambda *args: self.newSafeZone(*args)
        DistributedBattleFactory.DistributedBattleFactory.enterFactoryReward=lambda newSelf,*args:self.newEnterFactoryReward(newSelf,*args)
                
    def enterBattle(self):
        if base.localAvatar.getHp()>0:
            if base.cr.doFindAll('battle')==[]:
                battles = []
                cogList = base.cr.doFindAll("render")
                for x in cogList:
                    if isinstance(x, DistributedFactorySuit) or isinstance(x, DistributedSuit.DistributedSuit):
                        if x.activeState == 6:
                            battles.append(x)
                try:
                    if battles != []:
                        battle=battles[0]
                        pos, hpr = battle.getPos(), battle.getHpr()
                        vpMaxer.otherFunctions.walk()
                        vpMaxer.restock.wasInBattle=False
                        base.localAvatar.collisionsOn()
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
        self.oldEnterReward(newSelf,*args)
        if vpMaxer.otherFunctions.shouldContinue:
            newSelf.d_rewardDone(base.localAvatar.doId)
            vpMaxer.otherFunctions.walk()
            if self.roomNum>=len(self.roomsNeeded):
                self.attackSeq.finish()
                self.gainLaffSeq.finish()
                self.generateAgain()
                Sequence(Wait(1),Func(vpMaxer.otherFunctions.walk),Func(vpMaxer.otherFunctions.teleBack)).start()
            else:
                Sequence(Wait(5),Func(self.enterBattle)).start()
    
    def newEnterFactoryReward(self,newSelf,*args):
        self.oldEnterFactoryReward(newSelf,*args)
        if vpMaxer.otherFunctions.shouldContinue:
            self.attackSeq.finish()
            self.gainLaffSeq.finish()
            self.generateAgain()
            Sequence(Wait(1),Func(vpMaxer.otherFunctions.walk),Func(vpMaxer.otherFunctions.teleBack)).start()
                
    def newFactoryInit(self,*args):
        self.oldFactoryInit(*args)
        if vpMaxer.otherFunctions.shouldContinue:
            Sequence(Wait(2),Func(self.enterElevator)).start()
        
    def newDistributedFactoryInit(self,*args):
        self.oldDistributedFactoryInit(*args)
        if vpMaxer.otherFunctions.shouldContinue:
            vpMaxer.otherFunctions.walk()
            self.attackSeq.loop()
            self.gainLaffSeq.loop()
            self.roomNum=0
            self.workOutRoomsNeeded()
            Sequence(Wait(2),Func(self.warpToZone,self.roomsNeeded[self.roomNum])).start()
    
    def workOutRoomsNeeded(self):
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
                self.roomNum+=1
                break
        Sequence(Wait(1),Func(self.enterBattle)).start()
    
    def newSafeZone(self,*args):
        Sequence(Wait(1),Func(vpMaxer.otherFunctions.walk),Func(base.localAvatar.collisionsOff)).start()
        vpMaxer.restock.wasInBattle=True
        
    def preTele(self):
        exec hooks in __main__.__dict__
            
    def generateAgain(self):
        DistributedDoor.DistributedDoor.announceGenerate=_announceGenerate1
        DistributedPartyGate.DistributedPartyGate.announceGenerate=_announceGenerate2
        DistributedTrolley.DistributedTrolley.__init__=old__init__
        DistributedPartyGate.DistributedPartyGate.__init__=old__init__2
        DistributedDoor.DistributedDoor.__init__=old__init__3
        
    def goFactory(self):
        vpMaxer.otherFunctions.walk()
        base.localAvatar.setWantBattles(True)
        base.localAvatar.setPos(167.151, -157.024, -0.64781)
        
    def enterElevator(self):
        for elevator in base.cr.doFindAll("Elevator"):
            if elevator.getDestName()=='Front Entrance':
                vpMaxer.otherFunctions.walk()
                base.localAvatar.collisionsOff()
                base.cr.doFind('Boarding').sendUpdate('requestLeave',[base.localAvatar.doId])
                base.cr.doFind('Boarding').sendUpdate('requestInvite',[base.localAvatar.doId])
                base.cr.doFind('Boarding').sendUpdate('requestGoToSecondTime',[elevator.doId])
                return
                
    def revertFunctions(self):
        FactoryExterior.FactoryExterior.__init__=self.oldFactoryInit
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
        
    def revert(self):
        self.restock.revertFunctions()
        self.factoryAutoer.revertFunctions()
        self.vpAutoer.revertFunctions()
        self.otherFunctions.revertFunctions()
        DistributedNPCFisherman.DistributedNPCFisherman.handleCollisionSphereEnter=oldHandleEnterCollisionSphereFisherman
        DistributedNPCPartyPerson.DistributedNPCPartyPerson.handleCollisionSphereEnter=oldHandleEnterCollisionSphereParty
        DistributedNPCFisherman.DistributedNPCFisherman.announceGenerate=oldFisherAnnounceGenerate
        DistributedNPCPartyPerson.DistributedNPCPartyPerson.announceGenerate=oldPartyPlannerAnnounceGenerate
vpMaxer=VPMaxer()

import random
from direct.interval.IntervalGlobal import *
from direct.distributed import DistributedObject
from toontown.distributed import ToontownClientRepository
from toontown.battle import DistributedBattleFinal
from toontown.toonbase import ToontownBattleGlobals
from toontown.toon import *
from toontown.battle import DistributedBattle
from toontown.coghq import DistributedMintBattle
from toontown.coghq import DistributedMint
from toontown.coghq import DistributedCogHQDoor
from toontown.coghq import CogDisguiseGlobals
from toontown.coghq import MintInterior
from toontown.suit.DistributedMintSuit import DistributedMintSuit
from toontown.suit import DistributedSuit
from toontown.suit import DistributedCashbotBoss
from toontown.safezone import DLPlayground
from toontown.safezone import DistributedPartyGate
from toontown.safezone import DistributedTrolley
from toontown.building import DistributedDoor
from toontown.building import DistributedBoardingParty

ToontownBattleGlobals.SkipMovie=1
ToontownClientRepository.ToontownClientRepository.forbidCheesyEffects=lambda *x,**kwds: None

faceOffHook = lambda self, ts, name, callback:self.d_faceOffDone(self)
DistributedMintBattle.DistributedMintBattle._DistributedLevelBattle__faceOff = faceOffHook
DistributedBattle.DistributedBattle._DistributedBattle__faceOff = faceOffHook

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

oldHandleEnterCollisionSphereParty=DistributedNPCPartyPerson.DistributedNPCPartyPerson.handleCollisionSphereEnter
DistributedNPCPartyPerson.DistributedNPCPartyPerson.handleCollisionSphereEnter=lambda *args: None
oldHandleEnterCollisionSphereFisherman=DistributedNPCFisherman.DistributedNPCFisherman.handleCollisionSphereEnter
DistributedNPCFisherman.DistributedNPCFisherman.handleEnterCollisionSphere=lambda *args: None

class restock:

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
        self.maxCarryGags = base.localAvatar.getMaxCarry()
        self.gagshop_zoneId = 4503
        self.noToons=Sequence(Func(self.removeToons), Wait(1.5))
        self.noTrolley=False
        self.unloaded=True
        self.wasInBattle=False
        
        DistributedNPCFisherman.DistributedNPCFisherman.announceGenerate = newFishermanAnnounceGenerate
        DistributedNPCPartyPerson.DistributedNPCPartyPerson.announceGenerate = newPartyPlannerAnnounceGenerate
        
        self.lookAroundHookSeq = Sequence(Func(self.lookAroundHookFunc), Wait(2.5))
        self.lookAroundHookSeq.loop()
        ToonHead.ToonHead._ToonHead__lookAround = lambda *x:None
        
    def lookAroundHookFunc(self):
        if hasattr(base, 'localAvatar'):
            base.localAvatar.findSomethingToLookAt = lambda *x:None
            self.oldFindSomethingToLookAt = base.localAvatar.findSomethingToLookAt
            self.lookAroundHookSeq.finish()
        self.oldLookAround = ToonHead.ToonHead._ToonHead__lookAround
        
    def collectLaff(self):
        for treasure in base.cr.doFindAll('Treasure'):
            treasure.d_requestGrab()
            
    def removeToons(self):
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
                for clerk in base.cr.doFindAll('Clerk'):
                    clerk.setMovie=lambda *args,**kwds: None
                    clerk.freeAvatar=lambda *args: None
                    clerk.sendUpdate('avatarEnter')
                    clerk.sendUpdate('setInventory', [newString, change, 1])
                    
                money = base.localAvatar.getMoney()
                maxMoney = base.localAvatar.getMaxMoney()
                base.cr.bankManager.d_transferMoney(money - maxMoney)
        except:
            pass
    
    def unloadGagshop(self):
        if hasattr(self, 'contextId'):
            try:
                base.cr.removeInterest(self.contextId)
            except:
                pass
        
    def restock(self):
        try:
            if base.localAvatar.inventory.inventory[self.firstTrack][self.desiredLevel1]<2 or base.localAvatar.inventory.inventory[self.secondTrack][self.desiredLevel2]<2 or base.localAvatar.inventory.inventory[self.thirdTrack][self.desiredLevel3]<2:
                Sequence(Func(self.loadGagshop),Wait(1),Func(self.buyGags),Wait(0.5),Func(self.unloadGagshop)).start()
        
        except:
            pass
    
    def revertFunctions(self):
        self.noToons.finish()
        try:
            base.cr.removeInterest(self.interest1)
            base.cr.removeInterest(self.interest2)
            self.unloaded=True
        except:
            pass

class OtherFunctions:
    oldDreamlandInit=DLPlayground.DLPlayground.__init__
    oldHqDoorInit=DistributedCogHQDoor.DistributedCogHQDoor.__init__
    oldEnterReward=DistributedBattle.DistributedBattle.enterReward
    oldDenyBattle=DistributedSuit.DistributedSuit.denyBattle
    oldSendUpdate=DistributedObject.DistributedObject.sendUpdate
    oldEnterHealth=HealthForceAcknowledge.HealthForceAcknowledge.enter
    oldSetAnim=LocalToon.LocalToon.setAnimState
    oldPostInvite=DistributedBoardingParty.DistributedBoardingParty.postInvite
    
    def __init__(self):
        self.shouldContinue=False
        self.bossCount=0
        self.onlyMint=False
        self.onlyLast=False
        self.isHealing=False
        self.attackCogId=0
        self.canSetParentAgain=True
        self.numberToSuit={0:'Short Change',1:'Penny Pusher',2:'Tightwad',3:'Bean Counter',
                           4:'Number Cruncher',5:'Money Bags',6:'Loan Shark',7:'Robber Baron'}
        DLPlayground.DLPlayground.__init__=lambda *args:self.newDreamlandInit(*args)
        DistributedCogHQDoor.DistributedCogHQDoor.__init__=lambda *args: self.newHqDoorInit(*args)
        DistributedBattle.DistributedBattle.enterReward=lambda newSelf,*args: self.newEnterReward(newSelf,*args)
        DistributedSuit.DistributedSuit.denyBattle=lambda *args: self.newDenyBattle(*args)
        HealthForceAcknowledge.HealthForceAcknowledge.enter=lambda newSelf,hplevel: self.newEnterHealth(newSelf,hplevel)
        LocalToon.LocalToon.setAnimState=lambda *args,**kwds:self.newSetAnimState(*args,**kwds)
        DistributedBoardingParty.DistributedBoardingParty.postInvite=lambda newSelf,leaderId,inviterId: self.newPostInvite(newSelf,leaderId,inviterId)

    def attack(self):
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
                    
                if base.localAvatar.getHp()<(base.localAvatar.getMaxHp()*0.9) or self.isHealing:
                
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
        if fieldName=="requestAttack":
            self.oldSendUpdate(newself,"requestAttack", args, sendToId)
            self.oldSendUpdate(newself,"movieDone",[])
            newself.d_rewardDone(base.localAvatar.doId)
        else:
            self.oldSendUpdate(newself,fieldName, args, sendToId)
        
    def newDreamlandInit(self,*args):
        self.oldDreamlandInit(*args)
        if self.shouldContinue:
            cfoMaxer.mintAutoer.gainLaffSeq.finish()
            cfoMaxer.mintAutoer.attackSeq.finish()
            cfoMaxer.restock.wasInBattle=False
            self.checkCogbucks()
    
    def newSetAnimState(self,*args,**kwds):
        self.oldSetAnim(*args,**kwds)
        if self.canSetParentAgain and self.shouldContinue:
            base.localAvatar.d_setParent(1)
            self.canSetParentAgain=False
            Sequence(Wait(2),Func(self.doUnsetCanSetParentAgain)).start()
    
    def newPostInvite(self,newSelf,leaderId,inviterId):
        if leaderId==base.localAvatar.doId:
            newSelf.sendUpdate('requestAcceptInvite',[inviterId,leaderId])
        else:
            self.oldPostInvite(newSelf,leaderId,inviterId)
    
    def doUnsetCanSetParentAgain(self):
        self.canSetParentAgain=True
    
    def newEnterHealth(self,newSelf,hplevel):
        try:
            self.oldEnterHealth(newSelf,hplevel)
            newSelf.handleOk(base.localAvatar.getHp())
            newSelf.exit()
            if self.shouldContinue:
                Sequence(Wait(3),Func(self.checkCogbucks)).start()
        except:
            pass
            
    def newHqDoorInit(self,*args):
        self.oldHqDoorInit(*args)
        if self.shouldContinue and base.localAvatar.getZoneId()==12000:
            base.localAvatar.setWantBattles(False)
            Sequence(Wait(2),Func(self.checkCogbucks)).start()
    
    def newEnterReward(self,newSelf,*args):
        self.oldEnterReward(newSelf,*args)
        if self.shouldContinue and self.isHealing:
            if base.localAvatar.getHp()>70:
                cfoMaxer.mintAutoer.attackSeq.finish()
                self.isHealing=False
                self.checkCogbucks()
            else:
                Sequence(Wait(1),Func(self.enterRandomBattle)).start()
     
    def newDenyBattle(self,*args):
        self.oldDenyBattle(*args)
        if self.shouldContinue and self.isHealing and args[0].doId==self.attackCogId:
            self.enterRandomBattle()
        
    def checkCogbucks(self):
        if taskAutoer.isQuestComplete():
            self.stop()
            taskAutoer.checkWhatToDo()
        if self.onlyMint:
            if self.onlyLast:
                base.localAvatar.cogMerits[2]+=self.getCogbucksLeft()-1
            else:
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
                        Sequence(Wait(2),Func(self.teleBack)).start()
                else:
                    if base.cr.doFind('DistributedCogHQDoor') and base.localAvatar.getZoneId()>=12000 and base.localAvatar.getZoneId()<12100:
                        cfoMaxer.mintAutoer.start()
                    else:
                        cfoMaxer.restock.restock()
                        cfoMaxer.restock.collectLaff()
                        self.walk()
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
        else:
            base.localAvatar.setSystemMessage(0,'You have run out of jelly beans, please use the fishing code to gain some')
    
    def getCogbucksLeft(self):
        return CogDisguiseGlobals.getTotalMerits(base.localAvatar,2)-base.localAvatar.cogMerits[2]

    def walk(self):
        try:
            base.cr.playGame.getPlace().fsm.forceTransition('walk')
        except:
            pass
       
    def teleBack(self,zone=12000):
        try:
            self.walk()
            base.cr.playGame.getPlace().handleBookCloseTeleport(zone, zone)
        except:
            pass
                
    def onlyDoMint(self):
        self.onlyMint=True
        base.localAvatar.setSystemMessage(0,'CFO maxer set to only do the Mint')
    
    def doBoth(self):
        self.onlyMint=False
        base.localAvatar.setSystemMessage(0,'CFO maxer set to do both the Mint and the CFO')
        
    def haveJb(self):
        if base.localAvatar.cogLevels[0]==49:
            return True
        elif base.localAvatar.getTotalMoney()<100:
            return False
        else:
            return True
           
    def enterRandomBattle(self):
        battles = []
        cogList = base.cr.doFindAll("render")
        for x in cogList:
            if isinstance(x, DistributedSuit.DistributedSuit):
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
        
    def stop(self):
        self.shouldEnd=True
        base.localAvatar.died=lambda *args: None
    
    def start(self):
        DistributedObject.DistributedObject.sendUpdate=lambda newself, fieldName, args=[], sendToId=None: self.sendUpdateHook(newself, fieldName, args, sendToId)
        base.localAvatar.died=lambda *args: cfoMaxer.mintAutoer.newSafeZone(*args)
        self.bossCount=0
        self.shouldContinue=True
        self.shouldEnd=False
        self.checkCogbucks()
        cfoMaxer.restock.noToons.loop()
    
    def revertFunctions(self):
        LocalToon.LocalToon.setAnimState=self.oldSetAnim
        DLPlayground.DLPlayground.__init__=self.oldDreamlandInit
        DistributedCogHQDoor.DistributedCogHQDoor.__init__=self.oldHqDoorInit
        DistributedBattle.DistributedBattle.enterReward=self.oldEnterReward
        DistributedSuit.denyBattle=self.oldDenyBattle
        DistributedObject.DistributedObject.sendUpdate=self.oldSendUpdate
        HealthForceAcknowledge.HealthForceAcknowledge.enter=self.oldEnterHealth
        DistributedBoardingParty.DistributedBoardingParty.postInvite=self.oldPostInvite

class CfoAutoer:
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
        self.oldAvatarExit(newSelf,id)
        if base.cr.doFind('Elevator') and id==base.localAvatar.doId and cfoMaxer.otherFunctions.shouldContinue:
            cfoMaxer.otherFunctions.walk()
            base.cr.doFind('Boarding').sendUpdate('requestLeave',[base.localAvatar.doId])
            base.cr.doFind('Boarding').sendUpdate('requestInvite',[base.localAvatar.doId])
            base.cr.doFind('Boarding').sendUpdate('requestGoToSecondTime',[base.cr.doFind('Elevator').doId])
    
    def newBossEnterIntro(self,newSelf,*args):
        self.oldBossEnterIntro(newSelf,*args)
        if cfoMaxer.otherFunctions.shouldContinue:
            newSelf.exitIntroduction()
  
    def newEnterEpilogue(self,newSelf):
        self.oldEnterEpilogue(newSelf)
        if cfoMaxer.otherFunctions.shouldContinue:
            for i in range(5):
                newSelf._DistributedCashbotBoss__epilogueChatNext(i,1)
            cfoMaxer.otherFunctions.teleBack()
            cfoMaxer.otherFunctions.bossCount+=1
    
    def newEnterPrepareBattleThree(self,newSelf):
        self.oldEnterPrepareBattleThree(newSelf)
        newSelf.exitPrepareBattleThree()
    
    def destroyBattle(self):
        base.cr.doFind('SafeZone').sendUpdate('enterSafeZone')
    
    def exploit(self):
        Sequence(Func(self.destroyBattle), Wait(.5), Func(cfoMaxer.otherFunctions.walk)).start()
    
    def newEnterWaitForInput(self,*args):
        self.oldEnterWaitForInput(*args)
        if cfoMaxer.otherFunctions.shouldContinue:
            self.exploit()
            cfoMaxer.autoerGui.display.newLine('Skipping Battle')
    
    def newBossEnterElevator(self,newSelf):
        self.oldBossEnterElevator(newSelf)
        if cfoMaxer.otherFunctions.shouldContinue:
            cfoMaxer.autoerGui.display.newLine('Skipping Elevator')
            newSelf._DistributedBossCog__doneElevator()
    
    def newEnterBattleThree(self,newSelf):
        self.oldEnterBattleThree(newSelf)
        self.endBattle(newSelf)
        
    def start(self):
        base.localAvatar.collisionsOff()
        base.cr.doFind('DistributedCogHQDoor').sendUpdate('requestEnter')
        base.localAvatar.setWantBattles(True)
        cfoMaxer.autoerGui.display.newLine('Starting the CFO')
        cfoMaxer.autoerGui.display.newLine('Entering Lobby')
        
    def endBattle(self,newSelf):
        newSelf.cranes[0].sendUpdate('requestControl', [])
        for goon in base.cr.doFindAll('goon'):
            goon.sendUpdate('requestGrab', [])
            goon.sendUpdate('clearSmoothing', [0])
            goon.sendUpdate('hitBoss', [20.0])
        Sequence(Wait(1),Func(newSelf.exitBattleFour)).start()
        
    def revertFunctions(self):   
        DistributedCashbotBoss.DistributedCashbotBoss.enterElevator=self.oldBossEnterElevator
        DistributedCashbotBoss.DistributedCashbotBoss.enterBattleThree=self.oldEnterBattleThree
        DistributedCashbotBoss.DistributedCashbotBoss.enterPrepareBattleThree=self.oldEnterPrepareBattleThree
        DistributedCashbotBoss.DistributedCashbotBoss.enterEpilogue=self.oldEnterEpilogue
        DistributedBattleFinal.DistributedBattleFinal.enterWaitForInput=self.oldEnterWaitForInput
        DistributedCashbotBoss.DistributedCashbotBoss.enterIntroduction=self.oldBossEnterIntro
        DistributedCogHQDoor.DistributedCogHQDoor.avatarExit=self.oldAvatarExit
        
class MintAutoer:
    oldMintEnterWalk=MintInterior.MintInterior.enterWalk
    oldEnterReward=DistributedMintBattle.DistributedMintBattle.enterReward
    oldEnterMintReward=DistributedMintBattle.DistributedMintBattle.enterMintReward
    
    def __init__(self,cfoMaxer):
        self.attackSeq=Sequence(Func(cfoMaxer.restock.restock),Wait(1.0),Func(cfoMaxer.otherFunctions.attack),Wait(1.0))
        self.gainLaffSeq=Sequence(Func(cfoMaxer.restock.gainLaff),Wait(3.0))
        MintInterior.MintInterior.enterWalk=lambda newSelf,*args:self.newMintEnterWalk(newSelf,*args)
        DistributedMintBattle.DistributedMintBattle.enterReward=lambda *args:self.newEnterReward(*args)
        DistributedMintBattle.DistributedMintBattle.enterMintReward=lambda *args:self.newEnterMintReward(*args)
       
    def setType(self,zoneId):
        if zoneId==12500:
            self.floorNumToLastRoomNum=[17,22,19,24,21,18,23,20,25,22,19,24,21,17,23,20,25,22,18,24]
            self.elevatorName='Coin'
            self.laffNeeded=0
        elif zoneId==12600:
            self.floorNumToLastRoomNum=[17,18,20,22,23,25,18,19,21,23,24,17,19,20,22,24,25,18,20,21]
            self.elevatorName='Dollar'
            self.laffNeeded=66
        else:
            self.floorNumToLastRoomNum=[17,23,21,19,17,23,21,19,17,23,21,19,17,24,21,19,17,24,21,19]
            self.elevatorName='Bullion'
            self.laffNeeded=71
        
    def preTele(self):
        exec hooks in __main__.__dict__
            
    def generateAgain(self):
        DistributedDoor.DistributedDoor.announceGenerate=_announceGenerate1
        DistributedPartyGate.DistributedPartyGate.announceGenerate=_announceGenerate2
        DistributedTrolley.DistributedTrolley.__init__=old__init__
        DistributedPartyGate.DistributedPartyGate.__init__=old__init__2
        DistributedDoor.DistributedDoor.__init__=old__init__3

    def enterBattle(self):
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
                return True
            else:
                return False
        else:
            return True
            
    def boardElevator(self):
        if base.localAvatar.getHp()>self.laffNeeded:
            for elevator in base.cr.doFindAll("Elevator"):
                if self.elevatorName in elevator.getDestName():
                    base.cr.doFind('Boarding').sendUpdate('requestLeave',[base.localAvatar.doId])
                    base.cr.doFind('Boarding').sendUpdate('requestInvite',[base.localAvatar.doId])
                    base.cr.doFind('Boarding').sendUpdate('requestGoToSecondTime',[elevator.doId])
                    break
        else:
            self.attackSeq.loop()
            cfoMaxer.otherFunctions.isHealing=True
            cfoMaxer.otherFunctions.enterRandomBattle()
    
    def warpToRoom(self,room):
        if base.cr.doFind('DistributedMint.DistributedMint'):
            base.cr.doFind('DistributedMint.DistributedMint').warpToRoom(room)
                
    def newMintEnterWalk(self,newSelf,*args):
        self.oldMintEnterWalk(newSelf,*args)
        if cfoMaxer.otherFunctions.shouldContinue and len(args)>0:
            if args[0]:
                self.attackSeq.loop()
                self.gainLaffSeq.loop()
                self.workOutRoomsNeeded()
                self.enterBattle()
    
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
        if not self.battlesNeeded:
            self.finalDone=True
            self.warpToRoom(self.floorNumToLastRoomNum[base.cr.doFind('DistributedMint.DistributedMint').floorNum])
    
    def newEnterReward(self,*args):
        self.oldEnterReward(*args)
        if cfoMaxer.otherFunctions.shouldContinue:
            base.cr.doFind('battle').d_rewardDone(base.localAvatar.doId)
            self.battleNum+=1
            cfoMaxer.otherFunctions.walk()
            if self.battleNum>self.battlesNeeded and not self.finalDone:
                self.warpToRoom(self.floorNumToLastRoomNum[base.cr.doFind('DistributedMint.DistributedMint').floorNum])
                self.finalDone=True
                Sequence(Wait(0.5),Func(self.enterBattle)).start()
            elif self.enterBattle():
                pass
            else:
                cfoMaxer.otherFunctions.walk()
                self.generateAgain()
                self.attackSeq.finish()
                self.gainLaffSeq.finish()
                Sequence(Wait(1),Func(cfoMaxer.otherFunctions.teleBack)).start()
    
    def newSafeZone(self,*args):
        Sequence(Wait(1),Func(cfoMaxer.otherFunctions.walk),Func(base.localAvatar.collisionsOff)).start()
        cfoMaxer.restock.wasInBattle=True

    def newEnterMintReward(self,*args):
        self.oldEnterMintReward(*args)
        if cfoMaxer.otherFunctions.shouldContinue:
            cfoMaxer.otherFunctions.walk()
            self.generateAgain()
            self.attackSeq.finish()
            self.gainLaffSeq.finish()
            Sequence(Wait(1),Func(cfoMaxer.otherFunctions.teleBack)).start()
    
    def start(self):
        self.battleNum=1
        self.finalDone=False
        Sequence(Wait(1),Func(self.boardElevator)).start()
    
    def revertFunctions(self):
        MintInterior.MintInterior.enterWalk=self.oldMintEnterWalk
        DistributedMintBattle.DistributedMintBattle.enterReward=self.oldEnterReward
        DistributedMintBattle.DistributedMintBattle.enterCountryClubReward=self.oldEnterMintReward
        base.localAvatar.died=lambda *args: None
        self.attackSeq.finish()
        self.gainLaffSeq.finish()
        self.generateAgain()

class CFOmaxer:

    def __init__(self):
        self.restock=restock()
        self.otherFunctions=OtherFunctions()
        self.cfoAutoer=CfoAutoer()
        self.mintAutoer=MintAutoer(self)
        
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
cfoMaxer=CFOmaxer()

import random
from direct.interval.IntervalGlobal import *
from direct.distributed import DistributedObject
from toontown.distributed import ToontownClientRepository
from toontown.battle import DistributedBattleFinal
from toontown.battle import DistributedBattle
from toontown.toonbase import ToontownBattleGlobals
from toontown.toon import *
from toontown.coghq import DistributedCountryClubBattle
from toontown.coghq import DistributedCountryClub
from toontown.coghq import DistributedGolfGreenGame
from toontown.coghq import DistributedCogHQDoor
from toontown.coghq import CogDisguiseGlobals
from toontown.coghq import BossbotHQExterior
from toontown.coghq import CashbotHQExterior
from toontown.coghq import CountryClubInterior
from toontown.suit.DistributedMintSuit import DistributedMintSuit
from toontown.suit import DistributedSuit
from toontown.suit import DistributedBossbotBoss
from toontown.safezone import DDPlayground

ToontownBattleGlobals.SkipMovie=1
ToontownClientRepository.ToontownClientRepository.forbidCheesyEffects=lambda *x,**kwds: None

faceOffHook = lambda self, ts, name, callback:self.d_faceOffDone(self)
DistributedCountryClubBattle.DistributedCountryClubBattle._DistributedLevelBattle__faceOff = faceOffHook
DistributedBattle.DistributedBattle._DistributedBattle__faceOff = faceOffHook

oldHandleEnterCollisionSphereParty=DistributedNPCPartyPerson.DistributedNPCPartyPerson.handleCollisionSphereEnter
DistributedNPCPartyPerson.DistributedNPCPartyPerson.handleCollisionSphereEnter=lambda *args: None
oldHandleEnterCollisionSphereFisherman=DistributedNPCFisherman.DistributedNPCFisherman.handleCollisionSphereEnter
DistributedNPCFisherman.DistributedNPCFisherman.handleEnterCollisionSphere=lambda *args: None


class restock:

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
        self.maxCarryGags = base.localAvatar.getMaxCarry()
        self.gagshop_zoneId = 4503
        self.noToons=Sequence(Func(self.removeToons), Wait(1.5))
        self.noTrolley=False
        self.unloaded=True
        self.wasInBattle=False
        
        self.lookAroundHookSeq = Sequence(Func(self.lookAroundHookFunc), Wait(2.5))
        self.lookAroundHookSeq.loop()
        ToonHead.ToonHead._ToonHead__lookAround = lambda *x:None
        
    def lookAroundHookFunc(self):
        if hasattr(base, 'localAvatar'):
            base.localAvatar.findSomethingToLookAt = lambda *x:None
            self.oldFindSomethingToLookAt = base.localAvatar.findSomethingToLookAt
            self.lookAroundHookSeq.finish()
        self.oldLookAround = ToonHead.ToonHead._ToonHead__lookAround
        
    def collectLaff(self):
        for treasure in base.cr.doFindAll('Treasure'):
            treasure.d_requestGrab()
            
    def removeToons(self):
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
                for clerk in base.cr.doFindAll('Clerk'):
                    clerk.setMovie=lambda *args,**kwds: None
                    clerk.freeAvatar=lambda *args: None
                    clerk.sendUpdate('avatarEnter')
                    clerk.sendUpdate('setInventory', [newString, change, 1])
                    
                money = base.localAvatar.getMoney()
                maxMoney = base.localAvatar.getMaxMoney()
                base.cr.bankManager.d_transferMoney(money - maxMoney)
        except:
            pass
    
    def unloadGagshop(self):
        if hasattr(self, 'contextId'):
            try:
                base.cr.removeInterest(self.contextId)
            except:
                pass
        
    def restock(self):
        try:
            if base.localAvatar.inventory.inventory[self.firstTrack][self.desiredLevel1]<2 or base.localAvatar.inventory.inventory[self.secondTrack][self.desiredLevel2]<2 or base.localAvatar.inventory.inventory[self.thirdTrack][self.desiredLevel3]<2:
                Sequence(Func(self.loadGagshop),Wait(1),Func(self.buyGags),Wait(0.5),Func(self.unloadGagshop)).start()
        
        except:
            pass
    
    def revertFunctions(self):
        self.noToons.finish()
        try:
            base.cr.removeInterest(self.interest1)
            base.cr.removeInterest(self.interest2)
            self.unloaded=True
        except:
            pass

class OtherFunctions:
    oldDockEnterTeleportIn=DDPlayground.DDPlayground.enterTeleportIn
    oldBossEnterWalk=BossbotHQExterior.BossbotHQExterior.enterWalk
    oldCashEnterWalk=CashbotHQExterior.CashbotHQExterior.enterWalk
    oldEnterReward=DistributedBattle.DistributedBattle.enterReward
    oldDenyBattle=DistributedSuit.DistributedSuit.denyBattle
    oldSendUpdate=DistributedObject.DistributedObject.sendUpdate
    oldEnterHealth=HealthForceAcknowledge.HealthForceAcknowledge.enter
    oldSetAnim=LocalToon.LocalToon.setAnimState
    oldPostInvite=DistributedBoardingParty.DistributedBoardingParty.postInvite
    oldNpcFreeAvatar=DistributedNPCToonBase.DistributedNPCToonBase.freeAvatar
    
    def __init__(self):
        self.shouldContinue=False
        self.bossCount=0
        self.limit10=True
        self.onlyClub=False
        self.isHealing=False
        self.canSetParentAgain=True
        self.numberToSuit={0:'Flunky',1:'Pencil Pusher',2:'Yesman',3:'Micromanager',
                           4:'Downsizer',5:'Head Hunter',6:'Corporate Raider',7:'The Big Cheese'}
        DDPlayground.DDPlayground.enterTeleportIn=lambda newSelf,*args:self.newDockEnterTeleportIn(newSelf,*args)
        BossbotHQExterior.BossbotHQExterior.enterWalk=lambda newSelf,*args: self.newBossEnterWalk(newSelf,*args)
        CashbotHQExterior.CashbotHQExterior.enterWalk=lambda newSelf,*args: self.newCashEnterWalk(newSelf,*args)
        DistributedBattle.DistributedBattle.enterReward=lambda newSelf,*args: self.newEnterReward(newSelf,*args)
        DistributedSuit.DistributedSuit.denyBattle=lambda *args: self.newDenyBattle(*args)
        LocalToon.LocalToon.setAnimState=lambda *args,**kwds:self.newSetAnimState(*args,**kwds)
        HealthForceAcknowledge.HealthForceAcknowledge.enter=lambda newSelf,hplevel: self.newEnterHealth(newSelf,hplevel)
        DistributedBoardingParty.DistributedBoardingParty.postInvite=lambda newSelf,leaderId,inviterId: self.newPostInvite(newSelf,leaderId,inviterId)
        DistributedNPCToonBase.DistributedNPCToonBase.freeAvatar=lambda *args: None

    def attack(self):
        try:
            for battle in base.cr.doFindAll('battle'):
                if base.localAvatar.inventory.inventory[ceoMaxer.restock.firstTrack][ceoMaxer.restock.desiredLevel1]>0:
                    battle.sendUpdate('requestAttack', [ceoMaxer.restock.firstTrack, ceoMaxer.restock.desiredLevel1, battle.suits[0].doId])
                else:
                    break
                    
                if base.localAvatar.getHp()<(base.localAvatar.getMaxHp()*0.9) or self.isHealing:
                
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
        if fieldName=="requestAttack":
            self.oldSendUpdate(newself,"requestAttack", args, sendToId)
            self.oldSendUpdate(newself,"movieDone",[])
            newself.d_rewardDone(base.localAvatar.doId)
        else:
            self.oldSendUpdate(newself,fieldName, args, sendToId)
        
    def newDockEnterTeleportIn(self,newSelf,*args):
        self.oldDockEnterTeleportIn(newSelf,*args)
        if self.shouldContinue: 
            ceoMaxer.countryClubAutoer.gainLaffSeq.finish()
            ceoMaxer.countryClubAutoer.attackSeq.finish()
            Sequence(Wait(2),Func(self.checkStocks)).start()
    
    def newPostInvite(self,newSelf,leaderId,inviterId):
        if leaderId==base.localAvatar.doId:
            newSelf.sendUpdate('requestAcceptInvite',[inviterId,leaderId])
        else:
            self.oldPostInvite(newSelf,leaderId,inviterId)
    
    def newEnterHealth(self,newSelf,hplevel):
        try:
            self.oldEnterHealth(newSelf,hplevel)
            newSelf.handleOk(base.localAvatar.getHp())
            newSelf.exit()
            if self.shouldContinue:
                Sequence(Wait(2),Func(self.checkStocks)).start()
        except:
            pass
         
    def newCashEnterWalk(self,newSelf,*args):
        self.oldCashEnterWalk(newSelf,*args)
        if len(args)>0:
            if self.shouldContinue and args[0]:
                ceoMaxer.countryClubAutoer.attackSeq.loop()
                self.enterRandomBattle()
    
    def newBossEnterWalk(self,newSelf,*args):
        self.oldBossEnterWalk(newSelf,*args)
        if len(args)>0:
            if self.shouldContinue and args[0]:
                self.checkStocks()
    
    def newEnterReward(self,newSelf,*args):
        self.oldEnterReward(newSelf,*args)
        if self.shouldContinue and self.isHealing:
            if base.localAvatar.getHp()>20:
                self.isHealing=False
                ceoMaxer.countryClubAutoer.attackSeq.finish()
                Sequence(Wait(2),Func(self.teleBack)).start()
            else:
                self.enterRandomBattle()
     
    def newDenyBattle(self,*args):
        self.oldDenyBattle(*args)
        if self.shouldContinue and self.isHealing and self.lastCogId==args[0].doId:
            self.enterRandomBattle()
            
    def newSetAnimState(self,*args,**kwds):
        self.oldSetAnim(*args,**kwds)
        if self.canSetParentAgain:
            base.localAvatar.d_setParent(1)
            self.canSetParentAgain=False
            Sequence(Wait(1),Func(self.doUnsetCanSetParentAgain)).start()
            
    def doUnsetCanSetParentAgain(self):
        self.canSetParentAgain=True
        
    def checkStocks(self):
        if taskAutoer.isQuestComplete():
            self.stop()
            taskAutoer.checkWhatToDo()
        if self.onlyClub:
            base.localAvatar.cogMerits[0]=-4000
        if self.limit10 and self.bossCount>9:
            self.shouldContinue=False
        if self.shouldEnd:
            self.shouldContinue=False
        if self.shouldContinue:
            if self.getStocksLeft()==0 and not self.onlyClub:
                if base.cr.doFind('DistributedCogHQDoor') and base.localAvatar.getZoneId()>=10000 and base.localAvatar.getZoneId()<10100:
                    ceoMaxer.ceoAutoer.start()
                else:
                    ceoMaxer.restock.restock()
                    ceoMaxer.restock.collectLaff()
                    self.walk()
                    self.teleBack()
            else:
                if base.cr.doFind('DistributedCogHQDoor') and base.localAvatar.getZoneId()>=10000 and base.localAvatar.getZoneId()<10100:
                    if base.localAvatar.getHp()>20:
                        ceoMaxer.countryClubAutoer.start()
                    else:
                        self.isHealing=True
                        ceoMaxer.restock.restock()
                        ceoMaxer.restock.collectLaff()
                        self.walk()
                        self.teleBack(12000)
                else:
                    ceoMaxer.restock.restock()
                    ceoMaxer.restock.collectLaff()
                    self.walk()
                    if base.localAvatar.getHp()>20:
                        self.walk()
                        self.teleBack()
                    else:
                        self.isHealing=True
                        self.walk()
                        self.teleBack(12000)
        else:
            ceoMaxer.restock.noToons.finish()
            try:
                base.cr.removeInterest(ceoMaxer.restock.interest1)
                base.cr.removeInterest(ceoMaxer.restock.interest2)
                ceoMaxer.restock.unloaded=True
            except:
                pass
    
    def getStocksLeft(self):
        return CogDisguiseGlobals.getTotalMerits(base.localAvatar,0)-base.localAvatar.cogMerits[0]

    def walk(self):
        try:
            base.cr.playGame.getPlace().fsm.forceTransition('walk')
        except:
            pass
       
    def teleBack(self,zone=10000):
        try:
            self.walk()
            base.cr.playGame.getPlace().handleBookCloseTeleport(zone, zone)
        except:
            pass
                
    def onlyDoClub(self):
        self.onlyClub=True
        base.localAvatar.setSystemMessage(0,'CEO maxer set to only do the Country Club')
    
    def doBoth(self):
        self.onlyClub=False
        base.localAvatar.setSystemMessage(0,'CEO maxer set to do both the Country Club and the CEO')
        
    def haveJb(self):
        if base.localAvatar.cogLevels[0]==49:
            return True
        elif base.localAvatar.getTotalMoney()<100:
            return False
        else:
            return True
           
    def enterRandomBattle(self):
        battles = []
        cogList = base.cr.doFindAll("render")
        for x in cogList:
            if isinstance(x, DistributedSuit.DistributedSuit):
                if x.activeState == 6:
                    battles.append(x)
        if battles != []:
            self.walk()
            battle = random.choice(battles)
            pos, hpr = battle.getPos(), battle.getHpr()
            base.localAvatar.setPosHpr(pos, hpr)
            battle.d_requestBattle(pos, hpr)
            self.lastCogId=battle.doId
        else:
            pass
        
    def limiterOn(self):
        self.limit10=True
        base.localAvatar.setSystemMessage(0,'CEO maxer set to be limited to only 10 CEOs')
    
    def limiterOff(self):
        self.limit10=False
        base.localAvatar.setSystemMessage(0,'CEO maxer set to unlimited number of CEOs')
        
    def stop(self):
        base.localAvatar.died=lambda *args: None
        self.shouldContinue=True
        self.shouldEnd=True
    
    def start(self):
        DistributedObject.DistributedObject.sendUpdate=lambda newself, fieldName, args=[], sendToId=None: self.sendUpdateHook(newself, fieldName, args, sendToId)
        base.localAvatar.died=lambda *args: ceoMaxer.countryClubAutoer.newSafeZone(*args)
        self.bossCount=0
        self.shouldContinue=True
        self.shouldEnd=False
        ceoMaxer.restock.noToons.loop()
        self.checkStocks()
        
    
    def revertFunctions(self):
        DDPlayground.DDPlayground.enterTeleportIn=self.oldDockEnterTeleportIn
        BossbotHQExterior.BossbotHQExterior.enterWalk=self.oldBossEnterWalk
        CashbotHQExterior.CashbotHQExterior.enterWalk=self.oldCashEnterWalk
        DistributedBattle.DistributedBattle.enterReward=self.oldEnterReward
        DistributedSuit.DistributedSuit.denyBattle=self.oldDenyBattle
        DistributedObject.DistributedObject.sendUpdate=self.oldSendUpdate
        HealthForceAcknowledge.HealthForceAcknowledge.enter=self.oldEnterHealth
        DistributedBoardingParty.DistributedBoardingParty.postInvite=self.oldPostInvite
        LocalToon.LocalToon.setAnimState=self.oldSetAnim
        DistributedNPCToonBase.DistributedNPCToonBase.freeAvatar=self.oldNpcFreeAvatar
    
class CeoAutoer:
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
        self.oldAvatarExit(newSelf,id)
        if base.cr.doFind('Elevator') and id==base.localAvatar.doId and ceoMaxer.otherFunctions.shouldContinue:
            ceoMaxer.otherFunctions.walk()
            base.cr.doFind('Boarding').sendUpdate('requestInvite',[base.localAvatar.doId])
            base.cr.doFind('Boarding').sendUpdate('requestGoToSecondTime',[base.cr.doFind('Elevator').doId])
    
    def newBossEnterIntro(self,newSelf,*args):
        self.oldBossEnterIntro(newSelf,*args)
        if ceoMaxer.otherFunctions.shouldContinue:
            newSelf.exitIntroduction()
    
    def newEnterPrepareBattleTwo(self,newSelf):
        self.oldEnterPrepareBattleTwo(newSelf)
        if ceoMaxer.otherFunctions.shouldContinue:
            newSelf.exitPrepareBattleTwo()
    
    def newEnterEpilogue(self,newSelf):
        self.oldEnterEpilogue(newSelf)
        if ceoMaxer.otherFunctions.shouldContinue:
            ceoMaxer.otherFunctions.bossCount+=1
            ceoMaxer.otherFunctions.teleBack()
    
    def newEnterPrepareBattleThree(self,newSelf):
        self.oldEnterPrepareBattleThree(newSelf)
        newSelf.exitPrepareBattleThree()
    
    def newEnterPrepareBattleFour(self,newSelf):
        self.oldEnterPrepareBattleFour(newSelf)
        newSelf.exitPrepareBattleFour()
    
    def destroyBattle(self):
        base.cr.doFind('SafeZone').sendUpdate('enterSafeZone')
    
    def exploit(self):
        Sequence(Func(self.destroyBattle), Wait(.5), Func(ceoMaxer.otherFunctions.walk)).start()
    
    def newEnterWaitForInput(self,*args):
        self.oldEnterWaitForInput(*args)
        if ceoMaxer.otherFunctions.shouldContinue:
            self.exploit()
    
    def newBossEnterElevator(self,newSelf):
        self.oldBossEnterElevator(newSelf)
        if ceoMaxer.otherFunctions.shouldContinue:
            newSelf._DistributedBossCog__doneElevator()
    
    def newEnterBattleTwo(self,newSelf):
        self.oldEnterBattleTwo(newSelf)
        
    def newEnterBattleFour(self,newSelf):
        self.oldEnterBattleFour(newSelf)
        self.endBattle(newSelf)
        
    def start(self):
        base.cr.doFind('DistributedCogHQDoor').sendUpdate('requestEnter')
        
    def endBattle(self,newSelf):
        newSelf.sendUpdate('hitBoss', [250])
        newSelf.exitBattleFour()
        
    def revertFunctions(self):   
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
        DistributedCountryClubBattle.DistributedCountryClubBattle.enterCountryClubReward=lambda *args:self.newEnterCountryClubReward(*args)
    
    def setFrontThree(self):
        self.floorNumToKartRoomNum={0:17,1:17,2:18}
        self.battles=[1,3,5]
        self.greenRoom=9
        self.countryClubName='The Front Three'

    def setMiddleSix(self):
        self.greenRoom=29 
        self.battles=[1,3,5,7,9,11]
        self.floorNumToKartRoomNum={0:17,1:17,2:17,3:17,4:17,5:18}
        self.countryClubName='The Middle Six'
    
    def setBackNine(self):
        self.greenRoom=39
        self.battles=[1,3,5,7,9,11,13,15,17]
        self.floorNumToKartRoomNum={0:17,1:17,2:17,3:17,4:17,5:17,6:17,7:17,8:18}
        self.countryClubName='The Back Nine'
        
    def preTele(self):
        exec hooks in __main__.__dict__
            
    def generateAgain(self):
        DistributedDoor.DistributedDoor.announceGenerate=_announceGenerate1
        DistributedPartyGate.DistributedPartyGate.announceGenerate=_announceGenerate2
        DistributedTrolley.DistributedTrolley.__init__=old__init__
        DistributedPartyGate.DistributedPartyGate.__init__=old__init__2
        DistributedDoor.DistributedDoor.__init__=old__init__3

    def enterBattle(self):
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
                ceoMaxer.otherFunctions.walk()
                pos, hpr = battle.getPos(), battle.getHpr()
                base.localAvatar.collisionsOn()
                base.localAvatar.setPosHpr(pos, hpr)
                battle.d_requestBattle(pos, hpr)
                return True
            else:
                return False
        else:
            return True
    
    def doMoles(self):
        moleSeq=Sequence()
        for moleField in base.cr.doFindAll('MoleField'):
            for i in range(moleField.numMoles):
                moleSeq.append(Func(moleField.sendUpdate,'whackedMole', [0, i]))
                moleSeq.append(Wait(0.05))
        moleSeq.append(Wait(0.5))
        moleSeq.append(Func(self.enterBattle))
        moleSeq.start()
            
    def doGolf(self):
        gameSeq=Sequence()
        for greenGame in base.cr.doFindAll('GolfGreenGame'):
            for i in range(greenGame.boardsLeft):
                gameSeq.append(Func(greenGame.sendUpdate,'requestBoard', [1]))
        gameSeq.append(Wait(2))
        gameSeq.append(Func(self.endFloor))
        gameSeq.start()
        
    def enterCountryClub(self):
        for kart in base.cr.doFindAll('DistributedCogKart'):
            if kart.getDestName()==self.countryClubName:
                base.cr.doFind('Boarding').sendUpdate('requestInvite',[base.localAvatar.doId])
                base.cr.doFind('Boarding').sendUpdate('requestGoToSecondTime',[kart.doId])
                break
    
    def boardKart(self):
        ceoMaxer.otherFunctions.walk()
        self.attackSeq.finish()
        self.gainLaffSeq.finish()
        for kart in base.cr.doFindAll('DistributedClubElevator'):
            kart.handleEnterSphere(base.localAvatar.doId)
            return
        ceoMaxer.otherFunctions.walk()
        ceoMaxer.otherFunctions.teleBack()
        self.generateAgain()
    
    def warpToRoom(self,room):
        if base.cr.doFind('DistributedCountryClub.DistributedCountryClub'):
            base.cr.doFind('DistributedCountryClub.DistributedCountryClub').warpToRoom(room)
                
    def newCountryClubInit(self,*args):
        self.oldCountryClubInit(*args)
        self.attackSeq.loop()
        self.gainLaffSeq.loop()
        Sequence(Wait(3),Func(self.doMoles)).start()
    
    def newGolfGameToonEnter(self,*args):
        self.oldGolfGameToonEnter(*args)
        if ceoMaxer.otherFunctions.shouldContinue:
            Sequence(Wait(3),Func(self.doGolf)).start()
    
    def newEnterReward(self,*args):
        self.oldEnterReward(*args)
        if ceoMaxer.otherFunctions.shouldContinue:
            base.cr.doFind('battle').d_rewardDone(base.localAvatar.doId)
            self.battleNum+=1
            ceoMaxer.otherFunctions.walk()
            if not self.enterBattle():
                self.warpToRoom(self.greenRoom)
                ceoMaxer.otherFunctions.walk()
    
    def newSafeZone(self,*args):
        Sequence(Wait(1),Func(ceoMaxer.otherFunctions.walk)).start()
        ceoMaxer.restock.wasInBattle=True

    def newEnterCountryClubReward(self,*args):
        self.oldEnterCountryClubReward(*args)
        if ceoMaxer.otherFunctions.shouldContinue:
            Sequence(Wait(1.5),Func(self.boardKart)).start()

    def endFloor(self):
        ceoMaxer.otherFunctions.walk()
        self.warpToRoom(self.floorNumToKartRoomNum[base.cr.doFind('DistributedCountryClub.DistributedCountryClub').floorNum])
        Sequence(Wait(1),Func(self.boardKart)).start()
    
    def start(self):
        self.battleNum=1
        if ceoMaxer.otherFunctions.getStocksLeft()>953 and base.localAvatar.getCogParts()[0]!=0:
            self.setBackNine()
        elif ceoMaxer.otherFunctions.getStocksLeft()>386 and base.localAvatar.getCogParts()[0]!=0:
            self.setMiddleSix()
        else:
            self.setFrontThree()
        Sequence(Wait(1),Func(self.enterCountryClub)).start()
    
    def revertFunctions(self):
        DistributedCountryClub.DistributedCountryClub.__init__=self.oldCountryClubInit
        DistributedCountryClubBattle.DistributedCountryClubBattle.enterReward=self.oldEnterReward
        DistributedGolfGreenGame.DistributedGolfGreenGame._DistributedGolfGreenGame__handleToonEnter=self.oldGolfGameToonEnter
        DistributedCountryClubBattle.DistributedCountryClubBattle.enterCountryClubReward=self.oldEnterCountryClubReward
        base.localAvatar.died=lambda *args: None
        self.generateAgain()

class CEOMaxer:

    def __init__(self):
        self.restock=restock()
        self.otherFunctions=OtherFunctions()
        self.ceoAutoer=CeoAutoer()
        self.countryClubAutoer=CountryClubAutoer(self)
        
    def revert(self):
        self.restock.revertFunctions()
        self.countryClubAutoer.revertFunctions()
        self.ceoAutoer.revertFunctions()
        self.otherFunctions.revertFunctions()
        self.autoerGui.destroy()
        DistributedNPCFisherman.DistributedNPCFisherman.handleCollisionSphereEnter=oldHandleEnterCollisionSphereFisherman
        DistributedNPCPartyPerson.DistributedNPCPartyPerson.handleCollisionSphereEnter=oldHandleEnterCollisionSphereParty
        DistributedNPCFisherman.DistributedNPCFisherman.announceGenerate=oldFisherAnnounceGenerate
        DistributedNPCPartyPerson.DistributedNPCPartyPerson.announceGenerate=oldPartyPlannerAnnounceGenerate

ceoMaxer=CEOMaxer()


taskAutoer.checkWhatToDo()