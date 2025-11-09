import numpy as np
from sklearn.linear_model import LinearRegression
import json
import csv


global model
global av_weights 
model = LinearRegression()
av_weights = np.array([0,0,0,0,0,0,0,0,0])
#team 0 = team 1
#team 1 = team 2



    

def input_data(match_data, player_datas):
    #initializes empty lists to store then pass to the model
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
    #loops through all time stamps
    for x in range(0, len(player_datas[0]["stats.time_stamp_s"])):
        one_worth_count = 0
        two_worth_count = 0
    
        one_kill_count = 0
        two_kill_count = 0
    
        one_obj_count = 0
        two_obj_count = 0
        
        #loops for each players timestamps 
        for i in range(0,11):
            t = player_datas[i]["team"]
            if(t == 0):
                one_worth_count += player_datas[i]["stats.net_worth"][x]
                one_kill_count += player_datas[i]["stats.kills"][x]
                
            else:
                two_worth_count += player_datas[i]["stats.net_worth"][x]
                two_kill_count += player_datas[i]["stats.kills"][x]
                
        #loops for each objective in the world, sees if it is destroyed at the timestamp
        for a in range(0,len(match_data["objectives"])):
            if(player_datas[0]["stats.time_stamp_s"][x]<=2100):
                if(x*180>=match_data["objectives.destroyed_time_s"][a]):
                    if("Team1"==match_data["objectives.team"][a]):
                        two_obj_count+=1
                    else:
                       one_obj_count+=1
            else:
                if(((x-11.667)+300*x)>=match_data["objectives.destroyed_time_s"][a]):
                    if(0==match_data["objectives.team"][a]):
                        two_obj_count+=1
                    else:
                       one_obj_count+=1
        #adds all data from this iteration into the lists that will be passed        
            
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
    #passes all data to the model
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
    model = model.fit(x, y)
    print("X: ", x)
    print("Y: ", y)
    print("coefficients: ", model.coef_)
    print("intercept: ", model.intercept_)
    params = np.concatenate(([model.intercept_], model.coef_), axis = 0)
    np.savetxt("save_model.csv", params, delimiter=',', header=str(model.intercept_), comments='')

def predict(x):
    global model
    coef_list = []
    new_x = []
    for thing in x:
        new_x = int(thing)

    new_x = np.array(new_x).reshape(1,-1)
    
    with open("save_model.csv") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            coef_list.append(float(row[0]))

        model.intercept_ = coef_list[0]
        model.coef_ = np.array(coef_list[1:])
        print((new_x).reshape(1,-1))
        prediction = model.predict(new_x)
        print(prediction)
