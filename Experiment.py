### places marked with ? needs attention ###
#Import modules
from psychopy import core, visual, event, gui, monitors, event, sound
from datetime import datetime
#import module for randomization
import random
import pandas as pd
#creates new directory
import os
#scaling images
from PIL import Image
import text as t #script with text instructions
from imotion import changeEvent, sendup #script with imotion stuff
from pathlib import Path
import gc #to clean environment


gc.collect()


#Set Variables
#These are not set in stone! Depend on iMotions + COBE ?
FRAME_RATE = 60 # Hz  [120]
SAVE_FOLDER = "eotp_exp_data"
AOI_FOLDER = "AOI_dataframes"
# make sure that there is a logfile directory and otherwise make one
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)
    
if not os.path.exists(AOI_FOLDER):
    os.makedirs(AOI_FOLDER)

# define dialogue box (important that this happens before you define window)
box = gui.Dlg(title = "Eyes on the Past")
box.addField("EXPERIMENT ID: ") 
box.addField("Age: ")
box.addField("Gender: ", choices=["Female", "Male", "Other" ])
box.addField("First language: ")
box.addField("Group:",choices=["A","B","C","D","E","F"])
box.show()
if box.OK: # To retrieve data from popup window
    ID = box.data[0]
    AGE = box.data[1]
    GENDER = box.data[2]
    LANG = box.data[3]
    GROUP = box.data[4]
elif box.Cancel: # To cancel the experiment if popup is closed
    core.quit()

# PREPARE LOG FILES
# Get the current date
current_date = datetime.today().date()
now = datetime.now()
utc_time = now.strftime("%H_%M")

# prepare pandas data frame for recorded data
list_of_columns = ['time','assigned-id','age','gender','language','group','task', 'train/test', 'trial', 'reaction_time', 'answer','accuracy', 'nat_image','out','species','action','trigger']
logfile = pd.DataFrame(columns=list_of_columns)
logfile_name = "logfile_{}_{}_{}.csv".format(ID, current_date,utc_time)

#AOI
columns = ['Repondent Name','Stimulus Name','AOI Name','Color','Group','Timestamp (ms)','Is active', 'Points', 'Translation', 'Scale', 'Rotation','Interpolate']
aoifile = pd.DataFrame(columns=columns)
aoifile_name = "aoi_{}_{}_{}.csv".format(ID, current_date,utc_time)

## Monitor Specifications ##
MON_DISTANCE=60 #centimeters from eyes to screen
my_monitor = monitors.Monitor('testMonitor', distance=MON_DISTANCE)  # Create monitor object from the variables above. Size of stimuli in degrees.
MON_WIDTH, MON_HEIGHT = my_monitor.getSizePix()
MON_SIZE = [MON_WIDTH, MON_HEIGHT]
win = visual.Window(monitor=my_monitor, units='deg', size=(1920,1080), color='grey') #? went from degrees to norm, check with Kristian, fullscre=T removed for imotion to screen record
win.mouseVisible = False #remove cursor from screen

## Define stimuli and orders
### Defining Stimulus Images from Folder
out_directory = os.path.join('experiment_images','out')
nat_directory = os.path.join('experiment_images','nat')

### Filter files based on jpg and png extensions
out_stimuli = [file for file in os.listdir(out_directory) if file.lower().endswith(('.jpg','.png'))]
nat_stimuli = [file for file in os.listdir(nat_directory) if file.lower().endswith(('.jpg', '.png'))]

#directories of images
out={}
nat ={}
#img
columns = ['stim','xpix','ypix']
imgfile = pd.DataFrame(columns=columns)
imgfile_name = "img_size.csv"

for file in out_stimuli:
    #find image
    image_path = os.path.join(out_directory, file)
    ### Scale ###
    # Open the image
    img = Image.open(image_path)
    # Get the current dimensions
    width, height = img.size
    # Define the maximum dimensions
    max_width = MON_SIZE[0]
    max_height = MON_SIZE[1]
    # Calculate the scaling factor
    scale = min(max_width/width, max_height/height)
    # Resize the image
    img = img.resize((int(width*scale), int(height*scale)))
    x,y=img.size
    imgfile = imgfile.append({
        'stim': file,
        'xpix':x,
        'ypix': y
        }, ignore_index = True)
    out[file]=img
path_to_log = os.path.join(SAVE_FOLDER, imgfile_name)
imgfile.to_csv(path_to_log)
for file in nat_stimuli:
        #find image
    image_path = os.path.join(nat_directory, file)
        
    ### Scale ###
    # Open the image
    img = Image.open(image_path)
    # Get the current dimensions
    width, height = img.size
    # Define the maximum dimensions
    max_width = MON_SIZE[0]
    max_height = MON_SIZE[1]
    # Calculate the scaling factor
    scale = min(max_width/width, max_height/height)
    # Resize the image
    img = img.resize((int(width*scale), int(height*scale)))
    nat[file]=img
    
# Create a white rectangle
white_rectangle = visual.Rect(win, width=40, height=25, fillColor='white', lineColor=None) #note specific monitor size?


### Place holders for image names before storing in logfile
task =None
task1 = None
reaction_time = None
response=None
accurate=None
out_image=None
species=None
action=None
nat_image=None
trigger_name=None
seed=[ID*10,ID*11,ID*12]

tone = sound.Sound("E", octave = 4, sampleRate=44100, secs=0.1, stereo=True)



def shuffle_stim(stim):
    global seed, task
    i=0
    if task == 'recog':
        i = 0
    if task == 'act':
        i = 1
    if task == 'style':
        i = 2
    stim1 = stim.copy()
    stim2 = stim.copy()
    stim3 = stim.copy() #?edit out if only 2 runs
    random.seed(seed[i])
    random.shuffle(stim1)
    random.shuffle(stim2)
    random.shuffle(stim3)#? edit out if only 2 runs
    
    stim_complete = stim1 + stim2 + stim3
    return stim_complete

# define stop watch
stopwatch = core.Clock()

## FUNCTIONS ##
### Create a fixation cross
def show_fixation():
    fixation_cross = visual.TextStim(win, text='+', color='white', height=6)
    # Draw the fixation cross
    fixation_cross.draw()
    # Update the window to show the fixation cross
    win.flip()
    # Wait for a key press (or a certain duration)
    core.wait(1)  # Display for 2 seconds??
    

### function for showing text and waiting for key press
def msg(txt):
    win.flip()
    message = visual.TextStim(win, text = txt, height = 0.9,wrapWidth= 50)
    message.draw()
    win.flip()
    key = event.waitKeys()
    if 'escape' in key:
        save_and_escape(task, task1, reaction_time, response, accurate, out_image, species, action, nat_image)

### function to make text for feedback
def feedback(task,species,action,accuracy,answer,reaction_time): 
    success = 'You were correct! \n\n' 
    failure = 'Try again \n' 
    contin = '\n\n Press any key to continue' 
    time = '\n in '+ str(round(reaction_time, 2)) +' seconds' 
    four ='You spent more than 4 seconds, try to answer a bit faster.' 
    if task == 'recog': 
        remb = '\n\n\n\n Here is a reminder for the corresponding keys: \n S: Hind \n C: Horse \n M: Bison \n L: Ibex \n' 
        if answer == 'timelimit exceeded': 
            txt = four + contin + remb 
        else: 
            if accuracy == 1: 
                txt = success + time + contin + remb 
            if accuracy == 0: 
                txt = failure + 'You have answered ' + answer + ' to match a ' + species + time + contin + remb 
    if task == 'act': 
        remb = '\n\n\n\n Here is a reminder for the corresponding keys: \n S: Standing \n M: Moving \n L: Laying \n ' 
        if answer == 'timelimit exceeded': 
            txt = four + contin + remb
        else: 
            if action == 'l':
                movement = 'laying'
            elif action == 'm':
                movement = 'moving'
            elif action =='s':
                movement = 'standing'
            if accuracy == 1: 
                txt = success + time+contin + remb 
            if accuracy == 0: 
                txt = failure + 'You answered ' + answer + ' to match the ' + movement+ ' animal' +time+ contin + remb 
    if task == 'style': 
        remb ='\n\n\n\n Here is a reminder for the corresponding keys: \n S: Not beautiful \n C: Neutral \n M: Beautiful \n L: Very beautiful \n' 
        if answer == 'timelimit exceeded': 
            txt = four + contin + remb 
        else: 
            txt = 'You have answered ' + answer + ' to say the animal was ' + accuracy +time + contin + remb 
    return txt 
    
def save_data(task,task1,j,reaction_time,response,accurate,out_image,species,action,nat_image,trigger):
    global logfile, logfile_name
    logfile = logfile.append({
        'time': datetime.now().strftime("%H_%M_%S"),
        'assigned-id':ID,
        'age':AGE,
        'gender': GENDER,
        'language': LANG,
        'group':GROUP,
        'task':task,
        'train/test':task1,
        'trial':j,
        'reaction_time':round(reaction_time, 6),
        'answer': response,
        'accuracy': accurate,
        'out':out_image,
        'species': species,
        'action':action,
        'nat_image': nat_image,
        'trigger': trigger
        }, ignore_index = True)
    path_to_log = os.path.join(SAVE_FOLDER, logfile_name)
    logfile.to_csv(path_to_log)


def save_and_escape(task,task1,reaction_time,response,accurate,out_image,species,action,nat_image):
    message=changeEvent(name='escape',end=1)
    sendup(message)
    if task1 == 'test':
        save_aoi(out_image,start=0,time=reaction_time)
    save_data(task,task1,'exit',reaction_time,'escape',None,out_image,species,action,nat_image,'escape')
    message = visual.TextStim(win, text = t.escape, alignText='center',height = 0.8)
    message.draw()
    win.flip()
    core.wait(2)
    core.quit()

def save_aoi(img,start,time):
    global aoifile, aoifile_name
    animal_parts=['Headdress','Torso','Head+neck','Backlegs','Frontlegs','Tail']

    for i in range(len(animal_parts)):
        aoifile = aoifile.append({
            'Respondent Name': ID,
            'Stimulus Name': "ScreenRecording",
            'AOI Name':animal_parts[i], #?figure out what to put here
            'Color':None, #?figure out what to put here
            'Group': img,
            'Timestamp (ms)':time, #? time of stimulus onset and offset
            'Is active':start, #? figure how to put 1 (on) and (0) off
            'Points':None, #?figure out how to put points here
            'Translation':None, 
            'Scale':"1;1", 
            'Rotation':0,
            'Interpolate':0
            }, ignore_index = True)
    path_to_log = os.path.join(AOI_FOLDER, aoifile_name)
    aoifile.to_csv(path_to_log)

## showing one naturalistic at a time
def show_nat(nxt_img):
    global species, action, nat_image
    nat_split = nxt_img.split("_")
    species = nat_split[0]
    action = nat_split[1]
    print(f"nat image shown {nxt_img}")
    nat_image=nxt_img

    # Load and display the selected image
    stim = visual.ImageStim(win, image=nat[nxt_img])
    stim.draw()
    win.flip()

    core.wait(1)
    tone.play()
    core.wait(0.12)

### showing one outline at a time with beep sound
def show_out(nxt_img):
    global species, action, out_image, trigger_name, task1
    #find matching outlines depending on condition
    out_split = nxt_img.split("_")
    species = out_split[0]
    action = out_split[1]
    #save to environment
    out_image = nxt_img

    print(f"selected: {nxt_img}, path: {out[nxt_img]}")

    # Draw the rectangle
    white_rectangle.draw()
    # Load and display the selected image
    stim = visual.ImageStim(win, image=out[nxt_img])
    stim.draw()
    win.flip()
    
    core.wait(1)
    tone.play()
    core.wait(0.12)

# function for getting and evaluyating a key response
def get_response(task, time_limit):
    if task != 'act':
        key = event.waitKeys(keyList=['s', 'c', 'm', 'l', 'escape'], maxWait=time_limit)
    else:
        key = event.waitKeys(keyList=['s', 'm', 'l', 'escape'], maxWait=time_limit)
    if not key:
        return 'timelimit exceeded'
    answer = key[0]

    if answer == 'escape':# Handle the case where the experiment is ended
        save_and_escape(task, task1, reaction_time, response, accurate, out_image, species, action, nat_image)
    return answer

### function for evaluating a key response
def interpret_answer(img, task, answer):
    if answer == 'timelimit exceeded':
        accuracy = 'NA'
    else:
        if task == "recog":
            if (answer=='s' and img.split("_")[0] == 'hind') or (answer=='c' and img.split("_")[0] == 'horse') or (answer=='m' and img.split("_")[0] == 'bison') or (answer=='l' and img.split("_")[0] == 'ibex'):
                accuracy = 1
            else:
                accuracy = 0 
        if task == 'act':
            if (answer=='m' and img.split("_")[1] == 'm') or (answer=='s' and img.split("_")[1] == 's') or (answer=='l' and img.split("_")[1] == 'l'):
                accuracy = 1
            else:
                accuracy = 0    
        if task == 'style':
            if answer=='s':
                accuracy = 'not beautiful'
            elif answer=='c':
                accuracy = 'neutral'
            elif answer=='m':
                accuracy = 'beautiful'
            else:
                accuracy = 'very beautiful'
    global accurate
    accurate=accuracy
    return accuracy
    
##### experiment functions #####
### test function for recognition trial ###
def recog_train():
    global task, task1, spec
    task="recog"
    task1="train"
    test_stim=shuffle_stim(nat_stimuli)
    msg(t.r1)
    msg(t.r2)
    msg(t.r3)
    print(f"current task is {task} {task1}")
    i = 0
    correct_count = []
    end_trial=False
    while not end_trial:
        global reaction_time
        nxt_img =test_stim[i % len(test_stim)]
        show_fixation()
        
        show_nat(nxt_img)
        stopwatch.reset()

        answer = get_response(task,4)
        reaction_time = stopwatch.getTime()
        
        print(f"answer was: {answer} in {reaction_time} seconds")
        
        accuracy=interpret_answer(nat_image,task,answer=answer)
        if accuracy == 1:
            correct_count += [1]
        else:
            correct_count += [0]
        i = i+1
        
        msg(feedback(task,species, action, accuracy, answer,reaction_time))

        save_data(task,task1,i,reaction_time,answer,accuracy,None,species,action,nat_image,None)
        
        if len(correct_count)>10 and sum(correct_count[-10:])==10:
            end_trial=True

        if i % 20 == 19:
            msg(t.break_text)

def recog_test(n_times):
    test_stim = shuffle_stim(out_stimuli)
    global task, task1
    task="recog"
    task1="test"
    msg(t.r4)
    msg(t.r5)
    print(f"current task is {task} test")
    for i in range(n_times):
        global reaction_time, trigger_name
        trigger_name = test_stim[i]+'_'+task
        message1=changeEvent(trigger_name,end=1)
        message0=changeEvent(trigger_name,end=0)
        
        #flow
        show_fixation()
        sendup(message0)
        save_aoi(trigger_name,start=1,time=0)
        show_out(test_stim[i])
        stopwatch.reset()

        answer = get_response(task,4)
        reaction_time = stopwatch.getTime()
        
        sendup(message1)
        save_aoi(trigger_name,start=0,time=reaction_time)
        print(f"answer was: {answer}")

        save_data(task,task1,i+1,reaction_time,answer,None,out_image,species,None,None,trigger_name) 
        
        if i % 20 == 19:
            msg(t.break_text)

def act_train():
    global task, task1, acti
    task="act"
    task1="train"
    test_stim=shuffle_stim(nat_stimuli)
    i = 0
    msg(t.m1)
    msg(t.m2)
    msg(t.m3)
    correct_count =[]
    end_trial = False
    while not end_trial:
        global reaction_time
        nxt_img = test_stim[i % len(test_stim)]

        show_fixation()
        show_nat(nxt_img)
        stopwatch.reset()
        
        answer = get_response(task,4)
        reaction_time = stopwatch.getTime()
        
        print(f"answer was: {answer} in {reaction_time} seconds")
        
        accuracy=interpret_answer(nat_image,task,answer=answer)
        if accuracy == 1:
            correct_count += [1]
        else:
            correct_count += [0]
        i = i+1
        
        msg(feedback(task,species, action, accuracy, answer,reaction_time))
        
        save_data(task,task1,i,reaction_time,answer,accuracy,None,species,action,nat_image,None)
        
        if len(correct_count)>10 and sum(correct_count[-10:])==10:
            end_trial=True
        
        if i % 20 == 19:
            msg(t.break_text)

def act_test(n_times):
    test_stim = shuffle_stim(out_stimuli)
    global task, task1
    task="act"
    task1="test"
    msg(t.m4)
    msg(t.m5)
    print(f"current task is {task} test")
    for i in range(n_times): 
        global reaction_time, trigger_name
        #trigger
        trigger_name = test_stim[i]+'_'+task
        message1=changeEvent(trigger_name,end=1)
        message0=changeEvent(trigger_name,end=0)
        
        #flow
        show_fixation()
        sendup(message0)
        save_aoi(trigger_name,start=1,time=0)

        show_out(test_stim[i])
        stopwatch.reset()
        answer = get_response(task,4)
                
        reaction_time = stopwatch.getTime()

        print(f"answer was: {answer}")

        sendup(message1)
        save_aoi(trigger_name,start=0,time=reaction_time)

        save_data(task,task1,i+1,reaction_time,answer,None,out_image,species,None,None,trigger_name)
        
        if i % 20 == 19:
            msg(t.break_text)

def style_train():
    test_stim=shuffle_stim(nat_stimuli)
    global task, task1
    task="style"
    task1="train"
    msg(t.s1)
    msg(t.s2)
    msg(t.s3)
    print(f"current task is {task} train")
    i = 0
    correct_count = []
    end_trial=False
    while not end_trial:
        global reaction_time
        nxt_img =test_stim[i % len(test_stim)]
        show_fixation()
        
        show_nat(nxt_img)
        stopwatch.reset()

        answer = get_response(task,4)
        reaction_time = stopwatch.getTime()
        
        print(f"answer was: {answer} in {reaction_time:.6f} seconds")
        
        accuracy=interpret_answer(nat_image,task,answer=answer)
        if accuracy != 'NA':
            correct_count += [1]
        else:
            correct_count += [0]
        i = i+1
        
        msg(feedback(task,species, action, accuracy, answer,reaction_time))

        save_data(task,task1,i,reaction_time,answer,accuracy,None,species,action,nat_image,None)
        
        if len(correct_count)>10 and sum(correct_count[-10:])==10:
            end_trial=True

        if i % 20 == 19:
            msg(t.break_text)

def style_test(n_times):
    test_stim = shuffle_stim(out_stimuli)
    global task, task1
    task="style"
    task1="test"
    msg(t.s4)
    msg(t.s5)
    print(f"current task is {task} test")
    for i in range(n_times):
        global reaction_time, trigger_name
        trigger_name = test_stim[i]+'_'+task
        message1=changeEvent(trigger_name,end=1)
        message0=changeEvent(trigger_name,end=0)
        
        #flow
        show_fixation()
        sendup(message0)
        save_aoi(trigger_name,start=1,time=0)

        show_out(test_stim[i])
        stopwatch.reset()
        
        answer = get_response(task,4)
                
        reaction_time = stopwatch.getTime()
        sendup(message1)
        save_aoi(trigger_name,start=0,time=reaction_time)

        print(f"answer was: {answer}")

        accuracy=interpret_answer(out_image,task,answer=answer)
        
        save_data(task,task1,i+1,reaction_time,answer,accuracy,out_image,species,None,None,trigger_name) 
        
        if i % 20 == 19:
            msg(t.break_text)

### collected function ###
def recog(times_procent):
    recog_train()
    recog_test(int(len(out_stimuli*3)*times_procent))

def act(times_procent):
    act_train()
    act_test(int(len(out_stimuli*3)*times_procent))

def style(times_procent):
    style_train()
    style_test(int(len(out_stimuli*3)*times_procent))
    
###  experiment function loop ####
#### 1 means fullblown experiment = 100%, want to only do 50% input 0.5, smallest number is 0.25 = 1 training trial and 20 test trials
def experiment(GROUP,procent):
    msg(t.i1)
    msg(t.i2)
    msg(t.i3)
    if GROUP == 'A':
        recog(procent)
        msg(t.r6)
        act(procent)
        msg(t.m6)
        style(procent)
    if GROUP == 'B':
        act(procent)
        msg(t.m6)
        style(procent)
        msg(t.s6)
        recog(procent)
    if GROUP == 'C':
        style(procent)
        msg(t.s6)
        recog(procent)
        msg(t.r6)
        act(procent)
    if GROUP == 'D':
        recog(procent)
        msg(t.r6)
        style(procent)
        msg(t.s6)
        act(procent)
    if GROUP == 'E':
        act(procent)
        msg(t.m6)
        recog(procent)
        msg(t.r6)
        style(procent)
    if GROUP == 'F':
        style(procent)
        msg(t.s6)
        act(procent)
        msg(t.m6)
        recog(procent)
    #experiment is done, save and quit
    
    message = visual.TextStim(win, text = t.goodbye , alignText='center',height = 0.8)
    message.draw()
    win.flip()
    core.wait(2)
    core.quit()
    

#### run experiment ####
#### 1 means fullblown experiment = 100%, want to only do 50% input 0.5, smallest number is 0.25 = 1 training trial and 20 test trials
experiment(GROUP,1)
