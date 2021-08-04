import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
import seaborn as sns

class Pitch:
    def __init__(self, players):
        self.players = players
        self.position_data = None

    def marketvalue_sum_by_position(self):
        return (self.players.groupby('sub_position')['market_value'].sum().reset_index())
        
    def marketvalue_mean_by_position(self):
        return (self.players.groupby('sub_position')['market_value'].mean().reset_index())

    def marketvalue_max_by_position(self):
        return (self.players.groupby('sub_position')['market_value'].max().reset_index())

    def convert_position_to_coordinates(self):
        position_coords = {
            'Goalkeeper': (10,45),
            'Right-Back': (25, 20), 'Centre-Back': (25, 45), 'Left-Back': (25, 70),
            'Right Midfield': (65, 20), 'Defensive Midfield': (45, 45), 'Central Midfield': (65, 45), 'Attacking Midfield': (90, 45), 'Left Midfield': (65, 70),
            'Right Winger': (100, 20), 'Second Striker': (100, 45), 'Centre-Forward': (110, 45), 'Left Winger': (100, 70)
        }
        
        self.position_data = self.position_data.dropna(subset=['sub_position'])

        self.position_data['X'] = 0
        self.position_data['Y'] = 0
        
        for ind, row in self.position_data.iterrows():
            position = row['sub_position']
            self.position_data.at[ind, 'X'] = position_coords[position][0]
            self.position_data.at[ind, 'Y'] = position_coords[position][1]
        return self.position_data[["X", "Y", "market_value"]]

    def draw(self):
        #Create figure
        fig=plt.figure()
        fig.set_size_inches(13, 9)
        ax=fig.add_subplot(1,1,1)

        #Pitch Outline & Centre Line
        plt.plot([0,0],[0,90], color="black")
        plt.plot([0,130],[90,90], color="black")
        plt.plot([130,130],[90,0], color="black")
        plt.plot([130,0],[0,0], color="black")
        plt.plot([65,65],[0,90], color="black")

        #Left Penalty Area
        plt.plot([16.5,16.5],[65,25],color="black")
        plt.plot([0,16.5],[65,65],color="black")
        plt.plot([16.5,0],[25,25],color="black")

        #Right Penalty Area
        plt.plot([130,113.5],[65,65],color="black")
        plt.plot([113.5,113.5],[65,25],color="black")
        plt.plot([113.5,130],[25,25],color="black")

        #Left 6-yard Box
        plt.plot([0,5.5],[54,54],color="black")
        plt.plot([5.5,5.5],[54,36],color="black")
        plt.plot([5.5,0.5],[36,36],color="black")

        #Right 6-yard Box
        plt.plot([130,124.5],[54,54],color="black")
        plt.plot([124.5,124.5],[54,36],color="black")
        plt.plot([124.5,130],[36,36],color="black")

        #Prepare Circles
        centreCircle = plt.Circle((65,45),9.15,color="black",fill=False)
        centreSpot = plt.Circle((65,45),0.8,color="black")
        leftPenSpot = plt.Circle((11,45),0.8,color="black")
        rightPenSpot = plt.Circle((119,45),0.8,color="black")

        #Draw Circles
        ax.add_patch(centreCircle)
        ax.add_patch(centreSpot)
        ax.add_patch(leftPenSpot)
        ax.add_patch(rightPenSpot)

        #Prepare Arcs
        leftArc = Arc((11,45),height=18.3,width=18.3,angle=0,theta1=310,theta2=50,color="black")
        rightArc = Arc((119,45),height=18.3,width=18.3,angle=0,theta1=130,theta2=230,color="black")

        #Draw Arcs
        ax.add_patch(leftArc)
        ax.add_patch(rightArc)

        #Prepare Positions
        gk = plt.Circle((10,45), 3, color="red", fill=True)
        lb = plt.Circle((25,20), 3, color="red", fill=True)
        cb = plt.Circle((25,45), 3, color="red", fill=True)
        rb = plt.Circle((25,70), 3, color="red", fill=True)
        lm = plt.Circle((65,20), 3, color="red", fill=True)
        cdm = plt.Circle((45,45), 3, color="red", fill=True)
        cm = plt.Circle((65,45), 3, color="red", fill=True)
        cam = plt.Circle((90,45), 3, color="red", fill=True)
        rm = plt.Circle((65,70), 3, color="red", fill=True)
        lw = plt.Circle((100,20), 3, color="red", fill=True)
        cf = plt.Circle((110,45), 3, color="red", fill=True)
        rw = plt.Circle((100,70), 3, color="red", fill=True)


        #Draw Positions
        ax.add_patch(gk)
        ax.add_patch(lb)
        ax.add_patch(cb)
        ax.add_patch(rb)
        ax.add_patch(lm)
        ax.add_patch(cdm)
        ax.add_patch(cm)
        ax.add_patch(cam)
        ax.add_patch(rm)
        ax.add_patch(lw)
        ax.add_patch(cf)
        ax.add_patch(rw)

        #Add Annotations
        ax.annotate("GK", xy=(10, 45), fontsize=12, ha="center", va="center")
        ax.annotate("RB", xy=(25, 20), fontsize=12, ha="center", va="center")
        ax.annotate("CB", xy=(25, 45), fontsize=12, ha="center", va="center")
        ax.annotate("LB", xy=(25, 70), fontsize=12, ha="center", va="center")
        ax.annotate("RM", xy=(65, 20), fontsize=12, ha="center", va="center")
        ax.annotate("DM", xy=(45, 45), fontsize=12, ha="center", va="center")
        ax.annotate("CM", xy=(65, 45), fontsize=12, ha="center", va="center")
        ax.annotate("OM", xy=(90, 45), fontsize=12, ha="center", va="center")
        ax.annotate("LM", xy=(65, 70), fontsize=12, ha="center", va="center")
        ax.annotate("RW", xy=(100, 20), fontsize=12, ha="center", va="center")
        ax.annotate("CF", xy=(110, 45), fontsize=12, ha="center", va="center")
        ax.annotate("LW", xy=(100, 70), fontsize=12, ha="center", va="center")


        #Tidy Axes
        plt.axis('off')

        plt.ylim(0, 90)
        plt.xlim(0, 130)

        # Remove Space around Pitch
        plt.subplots_adjust(left=0.0, right=1.0, bottom=0.0, top=1.0)

        plt.savefig('pitch.jpg')


