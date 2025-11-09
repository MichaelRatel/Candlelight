import db_connect
import locktuah
import sys
import numpy as np

def train_model(matches):
    db_connect.load_data_into_model(matches)


def main() :
    argument = sys.argv[1]
    count = sys.argv[2]
    
    print(argument)

    if argument == "train_model":
        print("training model with", count, " matches")
        train_model(count)
    if argument == "predict" :
        x = np.array[sys.argv[2:8]]
        locktuah.predict(x)


if __name__ == "__main__":
    main()