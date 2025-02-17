import cv2
import numpy as np
import os
import streamlit as st
import regex as re

def is_line(lst):
    x1,y1,x2,y2 = lst[0][0],lst[0][1],lst[-1][0],lst[-1][1]
    m = (y2-y1)/(x2-x1)
    num = np.sqrt(int(m**2+1))
    d = np.abs((lst[:,0]*m-m*x1+y1-lst[:,1])/num)
    if len(d[d>10])>1:
        return False
    return True
    
def is_circle(lst):
    if np.sqrt(np.sum(np.square(lst[0]-lst[-1])))<10:
        D = np.sqrt(np.sum(np.square(lst-lst[0]),axis=1))
        r=np.max(D)/2
        max_d = lst[np.argmax(D)]
        mid_point = (lst[0][0]+max_d[0])/2,(lst[0][1]+max_d[1])/2
        d = np.sqrt(np.sum(np.square(lst-mid_point),axis=1))
        d = np.abs(d-r)
        if len(d[d<r/4])/len(d)>0.8:
            return True,lst[np.argmax(D)]
    return False,None
#-------------------------------------------------------

def draw(shape,x1,x2,y1,y2,color,thickness):
    if shape == "line":
        cv2.line(img,(x1,y1),(x2,y2),color,thickness)
    elif shape=="circle":
        cv2.circle(img,((x2+x1)//2,(y2+y1)//2),int((np.sqrt((x2-x1)**2+(y2-y1)**2))/2),color,thickness)
    elif shape == "rectangle":
        cv2.rectangle(img, (x1,y1), (x2,y2),color, thickness)
    elif shape == "ellipse":
        cv2.ellipse(img, ((x1+x2)//2,(y1+y2)//2), (100, 50) ,0, 0, 360,  color,  thickness)

# ----------------------------------------------------

division = 40
n=0
grid_lines = 0
def select_option(x1,y1):
    global colors,n,shapes_active,text,division,dct,grid_lines,grid_check,img_grid,height,width,background_color
    m=0
    if y1<100:
        if y1<50:
            try:
                for i in range(1,len(colors)+1):
                    if x1> (40*i)-15 and x1< (40*i)+15:
                        dct['color'] = colors[i][1]
                        colors[i][2]=12
                        m,n=1,i
                    else:
                        colors[i][2]=10
                if m==0:
                    colors[n][2]=12
            except Exception as e:
                print(e)
        else:
            if x1<15*division:
                shapes_active= np.full(6,2)
                text = False
                if x1<division+10:
                    print("line")
                    dct["parameters"] = "line"
                    shapes_active[0]=4
                elif x1>2*division and x1<3*division:
                    print("rectangle")
                    dct["parameters"] = "rectangle"
                    shapes_active[1]=4
                elif x1>3*division and x1<4*division+10:
                    print("circle")
                    dct["parameters"] = "circle"
                    shapes_active[2]=4
                elif x1>4*division and x1<6*division:
                    text = True
                    print("exit text input")
                    shapes_active[3]=4
                elif x1>6*division and x1<8*division:
                    print("erase")
                    dct["parameters"] = "erase"
                    shapes_active[4]=4
                elif x1>8*division and x1<10*division:
                    print("marker")
                    dct["parameters"] = "marker"
                    shapes_active[5]=4
                elif x1>10*division and x1<11*division:
                    img_grid = np.full((height,width,3),background_color,dtype=np.uint8)
                    if grid_lines==0:
                        grid_lines = 35
                    elif grid_lines == 35:
                        grid_lines = 49
                    else:
                        grid_lines = 0
                    grid_check = 1

# ------------------------------------------------------------

def thickness_bar(x1,y1):
    global thickness_ball
    if y1>50 and y1<100 and x1>14*division and x1< 19*division:
        thickness_ball = x1
        thickness = int((x1-division*15)/10)
        if thickness>=0:
            dct['thickness'] = thickness
        else:
            dct['thickness'] = -1


# ----------------------------------------------------------------

def check_thickness():
    global dct,text
    if (dct["parameters"] in ['line','erase','marker'] or text) and dct["thickness"] in [-1,0]:
        dct["thickness"] = 1

# ----------------------------------------------------------------

thickness_ball = 14*division
def nav_bar():
    global division,grid_lines,abcd
    top_bar = 100
    division = 40
    img[:top_bar,:]=(0,0,0)
    
    # colors
    for i,j in colors.items():
        cv2.circle(img,((i)*division,25),j[2],j[1],-1)    
    
    # shapes
    cv2.line(img,(30,15+50),(division+5,35+50),dct['color'],shapes_active[0])
    cv2.rectangle(img, (2*division,15+50), (3*division,35+50),dct['color'], shapes_active[1])
    cv2.circle(img,(4*division,25+50),12,dct['color'],shapes_active[2])
    
    cv2.putText(img, 'text', (5*division,29+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, dct['color'],1*int(shapes_active[3]/2), cv2.LINE_AA)
    cv2.putText(img, 'erase', (6*division+5,29+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5 , dct['color'],1*int(shapes_active[4]/2), cv2.LINE_AA)
    cv2.putText(img, 'marker', (8*division,29+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, dct['color'],1*int(shapes_active[5]/2), cv2.LINE_AA)
    cv2.putText(img, 'grid', (10*division,29+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, dct['color'],1, cv2.LINE_AA)
    
    cv2.putText(img, f'thickness :{dct['thickness']}', (11*division,29+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, dct['color'],1, cv2.LINE_AA)
    cv2.line(img,(14*division,75),(division*19,75),dct['color'],shapes_active[0])
    if dct['color']!=(255,255,255):
        cv2.circle(img,(thickness_ball,75),10,(255,255,255),-1)
    else:
        cv2.circle(img,(thickness_ball,75),10,(0,0,255),-1)
    
    cv2.line(img,(0,100),(width,100),(255,255,255),2)
    
def grid():
    global grid_check,img_grid
    if grid_lines!=0 and grid_check:
        grid_check = 0
        for i in range(100,height,grid_lines):
            cv2.line(img_grid,(0,i),(width,i),(100,100,100),1)

# --------------------------------------------------------------


x1,y1 = 0,0
a,b,c,d = 0,0,0,0
count,count1 = 0,0
points = []
def mouse_tracking(event,x,y,flags,param):
    global x1, y1
    global img,img2
    global height,width,background_color,count,count1,points
    global a,b,c,d,dct,text,lst,points,tab,grid_check
    global colors,shapes_active,prev_img,img_show,img_grid

    check_thickness()
    if event==1:
        points.clear()
        lst.clear()
        x1,y1,b = x,y,1
        select_option(x1,y1)
        img2 = img.copy()
        prev_img = img.copy()
    elif event == 4:
        x2,y2 = x,y
        a=1
        b=0
    
    if text:
        a =0
        img = prev_img.copy()
        cv2.putText(img, ''.join(lst), (x1,y1), cv2.FONT_HERSHEY_SIMPLEX, 1, dct['color'], dct['thickness'], cv2.LINE_AA)
        if event==1:
            cv2.putText(img, ''.join(lst), (x1,y1), cv2.FONT_HERSHEY_SIMPLEX, 1, dct['color'], dct['thickness'], cv2.LINE_AA)
    if count1%10==0:
        count1=0
        c,d=x,y
    if b:
        if y1<100:
            thickness_bar(x,y)
        points.append((x,y))
    if b==1 or tab:
        if dct["parameters"]=="marker":
            cv2.circle(img,(x,y),dct['thickness'],dct['color'],-1)
            if ((c == x and d==y) or tab) and len(points)>5:
                aa = points.copy()
                if count >=5 or tab:
                    count = 0 
                    if is_line(np.array(points)):
                        img = img2.copy()
                        draw(shape = "line", x1 = x1,x2 = x,y1 = y1,y2 = y,color = dct['color'],thickness = dct['thickness'])
                        
                    is_c = is_circle(np.array(points))
                    if is_c[0]:
                        img = img2.copy()
                        draw(shape = "circle", x1 = x1,x2 = is_c[1][0],y1 = y1,y2 = is_c[1][1],color = dct['color'],thickness = dct['thickness'])
                count +=1
            count1=count1+1
        elif dct["parameters"] == "erase":
            grid_check=1
            cv2.circle(img,(x,y),dct['thickness'],background_color,-1)
        tab = 0
    if y1>100:
        if a == 1 and not text:
            a,b=0,0
            draw(shape = dct["parameters"],x1 = x1,x2 = x,y1 = y1,y2 = y,color = dct['color'],thickness = dct['thickness'])
        if b == 1 and dct["parameters"]!="marker" and dct["parameters"]!="erase":
            img = prev_img.copy()
            draw(shape = dct["parameters"], x1 = x1,x2 = x,y1 = y1,y2 = y,color = dct['color'],thickness = dct['thickness'])
    else:
        a=0
    nav_bar()
    grid()
    img_show = cv2.add(img , img_grid)
    
#------------------------------------------------------

def find_path(file_path,img_count):
    while True:
        if not os.path.exists(file_path+str(img_count)+'.jpg'):
            return img_count
        img_count+=1

#-------------------------------------------------------------

def create_folder():
    current_path = os.getcwd()
    new_folder_name = "dawing_pad"
    new_floder_path = os.path.join(current_path, new_folder_name)
    if not os.path.exists(new_floder_path):
        os.makedirs(new_floder_path)
    return new_floder_path

# -----------------------------------------------------------

def give_parameters(flag=1,height=500,width=500,background_color=(0,0,0)):
    try:
        height = int(st.number_input(label="height",min_value = 500,max_value=1920))
        width = int(st.number_input(label="width",min_value = 800,max_value=1080))
        background_color = st.text_input(label="background_color",placeholder="ex: black background --> 0,0,0 ",value="0,0,0")
        add_colors = st.text_input(label="add_colors",placeholder="[color_name,bgr value] ex:  ['white',(255,255,255)] , ['red',(0,0,255)] ")
        background_color = tuple(map(int,background_color.split(',')))
        ab = background_color
        if height<500 or width<500:
            st.write("height and width should be greater than 500")
            flag=0
        elif ab[0]<0 or ab[1]<0 or ab[2]<0 or ab[0]>255 or ab[1]>255 or ab[2]>255:
            st.write("values should be 0 to 255. three values must be passed")
            flag = 0
        else:
            flag = 1
        no_col = 9
        new_colors = {}
        for i in re.findall(r"\['.*?'\s*,\s*\(.*?\)\]",add_colors):
            col = eval(i)
            if len(col[1])>2:
                col.append(10)
                new_colors[no_col] = col
                no_col = no_col+1
            else :
                st.write("incorrect value",str(col))

    except Exception as e:
        flag = 0
        print(e)
        st.write("please enter correct values")
    return flag,height,width,background_color,new_colors

# -------------------------------------------------------------------

flag,height,width,background_color,new_colors = give_parameters()

#----------------------------------------------------------
if flag ==1:
    st.write("press 'del' button to close" )
    lst = []
    text = False
    tab = 0
    floder_path = '' 
    img_count = 1
    shapes_active = np.full(6,2)
    colors = {1:["red",(0,0,255),15],2:['green',(0,255,0),10],3:['blue',(255,0,0),10],4:["white",(255,255,255),10],5:["yellow",(0,225,255),10],6:["orange",(0, 165, 255),10],7:['violet', (238, 130, 238), 10],8:['indigo', (130, 0, 75), 10]}
    if len(new_colors):
        colors.update(new_colors)
        st.write(f"{len(new_colors)} new colors added")
    dct = {"parameters" : "marker","thickness":3,"color":(0,0,255)}
    shapes = {"c":(160,75),"l":(40,75),"r":(100,75),'m':(349,75),"e":(270,75),'text':(220,75)}
    cv2.namedWindow("drawing_pad")
    cv2.setMouseCallback("drawing_pad",mouse_tracking)
    img = np.full((height,width,3),background_color,dtype=np.uint8)
    prev_img = np.full((height,width,3),background_color,dtype=np.uint8)
    img_show = np.full((height,width,3),background_color,dtype=np.uint8)
    img_grid = np.full((height,width,3),background_color,dtype=np.uint8)

    if st.button(label="draw"):

        while True:
            # print("a")
            cv2.imshow("drawing_pad",img_show)
            
            key = cv2.waitKey(1)
            # succ,img2 = vid.read()
            # if succ == False:
            #     break
            # cv2.imshow("img1",img)

            
            try:
                if (key>=97 and key <= 122) or (key>=45 and key<=57):
                    if key>47 and key <=57:
                        lst.append(chr(key))
                    else:
                        lst.append(chr(key))
                        
                if key == ord('s') and not text:
                    if os.path.exists(floder_path):
                        file_path = os.path.join(floder_path, 'drawing')
                        if not os.path.exists(file_path+str(img_count)+'.jpg'):
                            cv2.imwrite(file_path+str(img_count)+'.jpg',img[102:,])
                            img_count+=1
                            print('img saved')
                        else:
                            img_count = find_path(file_path,img_count)
                            cv2.imwrite(file_path+str(img_count)+'.jpg',img[102:])
                            print('img saved')
                    else:
                        print('given path is invalid')
                        floder_path = create_folder()
                        print(f'file will be stored in {floder_path}')
                        file_path = os.path.join(floder_path, 'drawing')
                        img_count = find_path(file_path,img_count)
                        cv2.imwrite(file_path+str(img_count)+'.jpg',img[102:])
                        print('img saved')
                    lst.clear()
                        
                if key == 13 and not text: # enter

                    if ''.join(lst).startswith('text'):
                        x1,y1 = shapes[''.join(lst)]
                        select_option(x1,y1)
                        if dct["thickness"]<2:
                            dct["thickness"] = 3
                    elif lst[0] == 't' and len(lst)>1:
                        try:
                            dct['thickness'] = int(''.join(lst[1:]))
                        except:
                            pass
                    else : 
                        x1,y1 = shapes[lst[0]]
                        select_option(x1,y1)
                    lst.clear()
                elif key == 9:
                    tab = 1
                else:
                    if key == 8: # (back space )clear text 
                        lst.pop()
            except Exception as e:
                print('invalid value')
                lst.clear()
                print(e)
            if key == 0:
                break
cv2.destroyAllWindows()