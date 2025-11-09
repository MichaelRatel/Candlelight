import numpy as np
from sklearn.linear_model import LinearRegression
import json
import csv


global model
global av_weights 

#team 0 = team 1
#team 1 = team 2
filename = "store_data"

def initialize():
    global model, av_weights
    model = LinearRegression()
    av_weights = np.array([0,0,0,0,0,0,0,0,0])

def input_data(match_data, player_datas):
    win_list = []
    time_list = []
    team_one_worth = []
    team_two_worth = []
    team_one_kills = []
    team_two_kills = []
    team_one_obj_count = []
    team_two_obj_count = []
    
    winner = match_data["winning_team"]
    time_data = match_data["duration_s"]
    
    for x in range(0, len(player_datas[0]["stats"])-1):
        one_worth_count = 0
        two_worth_count = 0
    
        one_kill_count = 0
        two_kill_count = 0
    
        one_obj_count = 0
        two_obj_count = 0
        for i in range(0,11):
            t = player_datas[i]["team"]
            if(t == 0):
                one_worth_count += player_datas[i]["stats.net_worth"][x]
                one_kill_count += player_datas[i]["stats.kills"][x]
                
            else:
                two_worth_count += player_datas[i]["stats.net_worth"][x]
                two_kill_count += player_datas[i]["stats.kills"][x]
        for a in range(0,len(match_data["objectives"])-1):
            if(player_datas[0]["stats.time_stamp_s"][x]<=2100):
                if(x*180>=match_data["objectives.destroyed_time_s"][a]):
                    if(0==match_data["objectives.team"][a]):
                        two_obj_count+=1
                    else:
                       one_obj_count+=1
            else:
                if(((x-11.667)+300*x)>=match_data["objectives.destroyed_time_s"][a]):
                    if(0==match_data["objectives.team"][a]):
                        two_obj_count+=1
                    else:
                       one_obj_count+=1
                
            
        team_one_worth.append(one_worth_count)
        team_one_obj_count.append(one_obj_count)
        team_one_kills.append(one_kill_count)
        
        team_two_worth.append(two_worth_count)
        team_two_obj_count.append(two_obj_count)
        team_two_kills.append(two_kill_count)
        
        time_list.append(player_datas[0]["stats.time_stamp_s"][x])
        win_list.append(winner)
    
    #num_players = len(inter["match_info"]["players"])
    
                
    #train_reg([team_one_worth,team_two_worth,team_one_kills,team_two_kills,team_one_obj_count,team_two_obj_count,time_list],win_list)  
    X = np.column_stack([
      team_one_worth,
      team_two_worth,
      team_one_kills,
      team_two_kills,
      team_one_obj_count,
      team_two_obj_count,
      time_list
    ])
    train_reg(X, win_list)
    


def train_reg(x, y):
    global model
    model.fit(x, y)
    