# -*- coding: utf-8 -*-
"""
Created on Sat Mar 10 19:59:01 2018

@author: liao
"""


import numpy as np
import random

TotalColor = 5
TotalPlayer = 3


class Item(object):
    def __init__(self,color,crown,biddingmethod,blackindicator):
        self.Color = color  #{1,2,3,...,TotalColor}
        self.Crown = crown  #{1,2,3,4,5}
        self.BiddingMethod = biddingmethod
        #'PUBLICBIDDING' 公开竞价 'ONEOFF' 一口价 'PRECEDENCEBIDDING'优先承购 'SEALEDBIDDING'暗标
        self.BlackIndication = blackindicator # 1:正品 0:假货

    def GetColor(self):
        return self.Color

    def GetCrown(self):
        return self.Crown

    def GetBiddingMethod(self):
        return self.BiddingMethod

    def GetBlackIndication(self):
        return self.BlackIndication


class Game(object):
    def __init__(self,current_round,board,currentitem,players):
        self.Current = current_round #当前第几轮
        self.Board = board   #面板上前几轮的记录
        self.CurrentItem = currentitem   #当前轮次所公开的竞品
        self.Players = players #存储玩家对象的list
        
    def GetPoint(self,color):  #获取颜色的分数
        point = 0
        for i in range(self.Current -1,0,-1):
            if self.Board[i][color] != 0:
                point += self.Board[i][color]
            else:
                break
        return point
    
    def UpdateBoard(self,new):
        self.Board = np.concatenate((self.Board,new))

    def UpdateItem(self,item):
        self.CurrentItem = np.concatenate((self.CurrentItem,item))

    def GetColorOder(self):
        ColorArray = np.zeros(TotalColor)
        for i in self.CurrentItem:
            ColorArray[i.Color] +=1
        order = ColorArray.argsort('heapsort')[::-1]
        #颜色次序，第一个元素为数量最多的颜色，第二个元素为数量第二多的颜色，以此类推

    #拍卖函数中不更新面板物品和玩家财富，调用完拍卖函数再更新(Game.UpdateItem) 和Player.ObtainItem Player.UpdateWealth

    def PublicBiddingProcess(self,host,item):
        Bidding = np.zeros(TotalPlayer)
        position = self.Players.index(host)
        currentplayer_index = position+1
        highest_bidding = 0
        zerobidding_times = 0
        stop = 0

        while stop == 0 :
            player = self.Players[currentplayer_index]
            currentplayer_index = (currentplayer_index+1)%TotalPlayer

            Thebidding = player.PublicBidding(self,highest_bidding,item)

            if Thebidding ==0: #放弃竞价
                zerobidding_times +=1
            else: #高于目前最高价格，更新最高价格
                zerobidding_times = 0
                highest_bidding = Thebidding

            if zerobidding_times == TotalPlayer -1:
                stop =1
                winner = self.Players[currentplayer_index]

        #winner.ObtainItem(item)
        #winner.UpdateWealth(highest_bidding)
        #self.UpdateItem(item)
        return winner,highest_bidding #返回得标者和价格

    def OneOffProcess(self,host,item):
        position = self.Players.index(host)
        currentplayer_index = position
        declaring_price = host.OneOff_host(item,self)
        #flag = 0
        winner = host
        for i in range(TotalPlayer-1):
            currentplayer_index +=1
            currentplayer_index = currentplayer_index % TotalPlayer
            if self.Players.OneOff_bidder(item,self,declaring_price) ==1:
                winner = self.Players[currentplayer_index]
                #flag = 1 #表示物品被其他玩家买下
                break

        #if flag: #表示物品被其他玩家买下
            #winner.ObtainItem(item)
            #winner.UpdateWealth(declaring_price)
            #return winner,declaring_price
        #else:  #若无其他玩家买下，则主持人买下
            #host.ObtainItem(item)
            #host.UpdateWealth(declaring_price)
            #return host,declaring_price
        #self.UpdateItem(item)
        return winner,declaring_price #返回得标者和价格

    def PrecedenceBiddingProcess(self,host,item):
        position = self.Players.index(host)
        currentplayer_index = position
        bidding = 0
        winner_index = 0
        for i in range(TotalPlayer):
            currentplayer_index += 1
            currentplayer_index = currentplayer_index % TotalPlayer
            bidding = self.Players[currentplayer_index].PrecedenceBidding(item,self,bidding)
            if bidding != 0 :
                winner_index = currentplayer_index

        winner = self.Players[winner_index]
        #winner.ObtainItem(item)
        #winner.UpdateWealth(bidding)

        return winner,bidding  #返回得标者和价格
        #self.UpdateItem(item)

    def SealedBiddingProcess(self,host,item):
        BiddingArracy = np.zeros(TotalPlayer)
        for i in range(TotalPlayer):
            BiddingArracy[i] = self.Players.SealedBidding(item,self)

        winner_index = np.argmax(BiddingArracy)
        winner = self.Players[winner_index]
        bidding = BiddingArracy[winner_index]

        return winner,bidding #返回得标者和价格
        #winner.ObtainItem(item)
        #winner.UpdateWealth(bidding)

        #self.UpdateItem(item)


    def UnitedBiddingProcess(self,host,item):
        position = self.Players.index(host)
        flag = 0
        currentplayer_index = position
        for i in range(TotalPlayer-1):
            currentplayer_index += 1
            currentplayer_index = currentplayer_index % TotalPlayer
            res = self.Players[currentplayer_index].UnitedBidding(item,self)
            if res[0] ==1:
                flag = 1 #有竞标者表示愿意进行联合拍卖
                collaborator = self.Players[currentplayer_index]
                uniteditem = res[1]
                break

        if flag == 0:
            host.ObtainItem(item)
        else:
            newitem = Item(item.Color,item.Crown+uniteditem.Crown,uniteditem.BiddingMethod,1)
            if newitem.BiddingMethod == 'PUBLICBIDDING':
                winner,bidding = PublicBiddingProcess(collaborator,newitem)

            if newitem.BiddingMethod == 'ONEOFF':
                winner, bidding = OneOffProcess(collaborator,newitem)

            if newitem.BiddingMethod == 'PRECEDENCEBIDDING':
                winner,bidding = PrecedenceBiddingProcess(collaborator,newitem)

            if newitem.BiddingMethod == 'SEALEDBIDDING  ':
                winner,bidding = SealedBiddingProcess(collaborator,newitem)



        self.UpdateItem(item)





        


    
    
    
class Player(object):
    def __init__(self,wealth, boarditem, handitem, type):
        self.Wealth = wealth
        self.BoardItem = boarditem
        self.HandItem = handitem #list
        self.Type = type # {Aggressive,moderate,conservative}
        
    def GetValuation(self, item, current_state):
        #Valuation = np.array([0,0]) #[下限，上限]#
        previous_point = current_state.GetPoint(item.Color)
        colororder = current_state.GetColorOder()
        current_point = 3 - np.argwhere(colororder == item.Color)

        if current_point <=0:
            Valuation = np.array([0,1])*10*item.Crown
            return Valuation
        else:
            total = previous_point + current_point
            Valuation = np.array([1,total])*10*item.Crown
            return Valuation

        #should be improved

    def GetColor(self):
        ColorArray = np.zeros(TotalColor)
        for i in self.HandItem:
            ColorArray[i.Color]+=1
        return ColorArray

    def ObtainItem(self, item):
        self.HandItem.append(item)

    def UpdateWealth(self, price):
        self.Wealth -= price

    def PublicBidding(self, current_state, previous_bidding, item): #公开竞价

        valuation = self.GetValuation(item,current_state)
        #lower_valuation = valuation[0]
        upper_valuation = valuation[1]
        if previous_bidding < upper_valuation:
            max = min(upper_valuation - previous_bidding -1,self.Wealth)
            bidding = previous_bidding + random.randint(1,max)
        else:
            bidding = 0

        return bidding

    def OneOff_host(self, item, current_state, sharing=0.6):    #一口价，主持人
        valuation = self.GetValuation(item,current_state)
        price = random.randint(valuation[0],valuation[1])
        declaring_price = int(price * random.uniform(0.4,sharing))
        declaring_price = min(declaring_price,self.Wealth)
        return declaring_price

    def OneOff_bidder(self, item, current_state, declaring_price, sharing=0.6 ):  #一口价，竞标者

        if declaring_price > self.Wealth:
            accept = 0
            return accept
        else:
            valuation = self.GetValuation(item,current_state)
            price = random.randint(valuation[0],valuation[1])
            if declaring_price < price*random.uniform(0.5,sharing):
                accept = 1
            else:
                accept = 0

            return accept

    def PrecedenceBidding(self, item, current_state, previous_price, sharing = 0.6): #优先承购，主持人或竞标者
        if previous_price > self.Wealth:
            bidding = 0
            return bidding

        valuation = self.GetValuation(item, current_state)
        bidding = random.randint(valuation[0], valuation[1])* random.uniform(0.4, sharing)
        if bidding > self.Wealth:
            bidding = 0
            return bidding
        if previous_price < bidding:
            return bidding
        else:
            bidding = 0
            return bidding

    def SealedBidding(self, item, current_state,sharing = 0.6): #暗标
        valuation = self.GetValuation(item, current_state)
        bidding = random.randint(valuation[0], valuation[1]) * random.uniform(0.4, sharing)
        if bidding > self.Wealth:
            bidding = random.ranint(1, self.Wealth)

        return bidding

    def UnitedBidding(self,item,current_state):
        uniteditem = Item(0,0,0,0)
        highestcrown = 0
        for handitem in self.HandItem:
            if handitem.Color == item.Color:
                #选择皇冠数最多的那个物品
                if handitem.Crown > highestcrown:
                    highestcrown = handitem.Crown
                    uniteditem = handitem

        if highestcrown == 0:
            return 0,uniteditem  #不选择联合拍卖
        else
            retunn 1,uniteditem   #选择联合拍卖


    def Strategy(self,current_state):
        num = len(self.HandItem)
        merits = np.zeros(num)
        for i in range(num):
            merits[i]= self.GetValuation(self.HandItem[i],current_state)[1]

        Probabilities = meris/np.sum(meris)

        temp = random.uniform(0,1)
        index = 0
        init = 0
        for i in range(num):
            init += Probabilities[i]
            if temp < init:
                index = i
                break

        return self.HandItem(i)





    
    

    """
def GetPoint(arr):
    point =0
    for i in range(arr.shape[0]-1,-1,-1):
        if arr[i][2]!=0:
            point +=arr[i][2]
        else:
            break
    return point
"""

#print(GetPoint(e))
