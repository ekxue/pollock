import numpy as np
import matplotlib.pyplot as plt
import math
from scipy import interpolate
from scipy.stats import truncexpon
from matplotlib.patches import Ellipse
#hello
def check_choice_okay(A,N):
    A = np.sort(A)
    #print(A)
    diffs = np.diff(A)
    #print(A[0], A[-1])
    if len(diffs) == 0:
        return True
    elif np.amin(diffs) <= 4 or (A[0] <= 5 or A[-1] >= N-5):
        return False
    else:
        return True

def angle(vec, deg = True):
    # given 2d thing, return positive angle in degrees
    # how is this not a standard thing???
    if vec[0] == 0:
        if vec[1] > 0:
            angle = np.pi/2
        elif vec[1] < -0:
            angle = -np.pi/2
        else:
            angle = 0
    elif vec[1] == 0:
        if vec[0] > 0:
            angle = 0
        elif vec[0] < 0:
            angle = np.pi
        else:
            angle = 0 
    else:
        if vec[0] > 0 and vec[1] > 0: # if first quadrant, arctan is ok
            angle = np.arctan(vec[1]/vec[0])
        elif vec[0] > 0 and vec[1] < 0: #if fourth quadrant, want positive angle value:
            angle = 2*np.pi + np.arctan(vec[1]/vec[0])
        elif vec[0] < 0 and vec[1] > 0: #if second quadrant, move it to first quadrant, then pi minus it
            angle = np.pi - np.arctan(-vec[1]/vec[0])
        elif vec[0] < 0 and vec[1] < 0: #if third quadrant, move it to fourth, then pi minus it
            angle = np.pi - np.arctan(-vec[1]/vec[0])
    if deg:
        angle = math.degrees(angle)
    return angle


def get_four_apart_random(N,k):
    '''
    get k numbers from [N], all of which are at least 4 apart
    '''
    choice_okay = False
    count = 0
    while choice_okay == False:
        choice = np.random.choice(N,k)
        if k == 1:
            choice_okay = True 
        else:
            choice_okay = check_choice_okay(choice,N)
        count += 1
        if count == 100:
            return -1

    return np.sort(choice)

class paint_line:
    def __init__(self,points,mit,fig,ax,color = 'k'):
        self.points = points #np array of points, N x 2 array
        self.mit = mit #minimum initial thickness, in pixels
        assert len(points) >= 5, "error: object paint_line has too few points!"
        self.fig = fig
        self.ax = ax
        self.color = color

    def split_points(self):
        N = len(self.points)
        num_partitions = np.random.choice([0,1,2], p = [0.2,0.4,0.4])
        # print(num_partitions)
        # num_partitions = np.random.choice([0,1,2,3,4], p = [1,0,0,0,0])

        #lst = np.arange(1,N-1)
        #np.random.shuffle(lst)
        #kink_indices = np.sort(lst[:num_partitions])
        #kink_indices = np.append(kink_indices, N)

        kink_indices = get_four_apart_random(N,num_partitions)
        if type(kink_indices) == int:
            return -1


        split_points = []

        if num_partitions != 0:
            begin = 0
            for i in kink_indices:
                end = i
                split_points.append(self.points[begin:end+1])
                begin = end
        else: 
            split_points = [self.points]
        # print(split_points)

        return split_points

    def gen_spline(self):
        split_points = self.split_points()
        if type(split_points) == int:
            return -1
        spline_list = []
        thick_list = []

        for lst in split_points:
            x = lst[:,0]
            y = lst[:,1]
            # print(x)
            # print(y)
            try:
                tck, u = interpolate.splprep([x,y], s = 0)
            except:
                return -1
            xnew,ynew = interpolate.splev(np.linspace(0, 1, 10000), tck, der = 0)
            N = len(x)
            spline_list.append([xnew,ynew])

            thickness = np.random.choice(np.arange(self.mit,self.mit+20))
            thick_sublist = []
            thick_sublist.append(thickness)

            if N < 15:
                lower_bound_critierion = np.random.choice([0,1],p=[0.05,0.95])
            else:
                lower_bound_critierion = np.random.choice([0,1],p=[0.95,0.05])


            #print(lower_bound_critierion)
            if lower_bound_critierion == 0:
                thresh = 0
                var = [-1,1]
            elif lower_bound_critierion == 1:
                thresh = 0.1*thickness
                var = [-thickness/12,thickness/12]
            for i in range(len(xnew)-1):
                perturbation = np.random.choice(var, p = [.70,.30])
                thickness = thickness + perturbation
                if thickness < thresh:
                    thickness = thresh
                thick_sublist.append(thickness)
            thick_list.append(thick_sublist)


        return (spline_list,thick_list)

    def plt_spline(self):
        spline = self.gen_spline()
        if spline == -1:
            return 
        spline_list = spline[0]
        thick_list = spline[1]

        segments = len(spline_list)
        #print(spline_list)
        #print(thick_list)
        for i in range(segments):
            x = spline_list[i][0]
            y = spline_list[i][1]
            xnew = spline_list[i][0]
            ynew = spline_list[i][1]


            thick_sublist = thick_list[i]


            self.ax.scatter(xnew,ynew, s = thick_sublist, color = self.color)

class splash_point:
    def __init__(self,center,angle,fig,ax,max_size, color='k'):
        self.center = center
        self.angle = angle #unit vector
        self.fig = fig
        self.ax = ax
        self.color = color
        self.max_size = max_size

    def paint_ellipse(self,sf):
        w = np.random.uniform(low = self.max_size/2, high = self.max_size) * sf
        h = np.random.uniform(low=w/4, high = 3*w/4) * sf * 1.5
        ell = Ellipse(self.center, w, h, self.angle, color=self.color)
        self.ax.add_artist(ell)

class flick:
    def __init__(self,start,end,fig,ax, spread_const,thickness_const,color = 'k'):
        self.start = start
        self.end = end
        self.fig = fig
        self.ax = ax
        self.spread_const = spread_const #real number that adjusts spreadiness, something between 0 and 0.4
        self.color = color
        self.thickness_const = thickness_const # real number between 0.8 and 4


    def get_angle(self):
        return angle(self.end - self.start)

    def get_length(self):
        return math.sqrt((self.start[1]-self.end[1])**2 + (self.start[0]-self.end[0])**2)

    def get_splatter_centers(self):
        '''
        constants to tune:
            spreadiness

        '''
        x1 = self.start[0]
        x2 = self.end[0]
        y1 = self.start[1]
        y2 = self.end[1]
    

        num_splatters = np.random.randint(20,200)
        centers = []
        l = self.get_length()
        #print(l)
        lhats = []
        for i in range(num_splatters):
            sector = np.random.choice([0,1,2,3],p=[0.50,0.25,0.15,0.10])
            if sector == 0:
                lhat = np.random.uniform(0,0.25)*l
            elif sector == 1:
                lhat = np.random.uniform(0.25,0.5)*l
            elif sector == 2:
                lhat = np.random.uniform(0.5,0.75)*l
            else:
                lhat = np.random.uniform(0.75,1.0)*l

            #lhat = np.random.exponential() * l
            #lhat = truncexpon.rvs(l)
            lhats.append(lhat)
            base = np.array([x1 + (1-lhat/l)*x1 + lhat/l*x2, y1 + (1-lhat/l)*y1 + lhat/l*y2])
            spreadiness = lhat*self.spread_const*np.random.uniform(0.5,1.5)
            random = np.array([1,(x1-x2)/(y2-y1+0.0001)])/np.linalg.norm([1,(x1-x2)/(y2-y1+0.0001)]) * np.random.uniform(0,spreadiness) * np.random.choice([-1,1], p = [.50,.50])


            centers.append(base+random)
        centers = np.array(centers)
        #print(lhats)

        xs = centers[:,0]
        ys = centers[:,1]
        # print(xs)
        # print(ys)

        #plt.axis('equal')
        #plt.scatter(xs,ys, color = 'k')

        return (centers,lhats)

    def draw_ellipses(self):
        centers_and_lhats = self.get_splatter_centers()
        n = len(centers_and_lhats[0])
        l = self.get_length()
        #print(centers_and_lhats)
        for i in range(n):
            sp = splash_point(centers_and_lhats[0][i],self.get_angle() + np.random.uniform(0,10), self.fig,self.ax, (l-centers_and_lhats[1][i])**(1/self.thickness_const),color = self.color)
            sp.paint_ellipse(0.3)
            #sp.paint_ellipse((l-centers_and_lhats[1][i])/(0.5*l))

def paint(filename):
	num_features = np.random.randint(70,400)

    # initialize canvas
	fig = plt.figure()
	ax = fig.add_subplot(111)
    
    #plt.axis('off')
	ax.get_xaxis().set_visible(False)
	ax.get_yaxis().set_visible(False)
	#plt.savefig('pict.png', bbox_inches='tight', pad_inches = 0)
	plt.xlim(-1600,1600)
	plt.ylim(-1200,1200)
	bg_colors = ["#e5e2cc","#dddac1","#efeee1","#d8d5c7","#f7f4ea","#f2f1ed","#efebdc","#edebe1","#f2f1ea","#edeada","#e5e3da","#eae8e3"]

	wild_color = (np.random.randint(255)/255,np.random.randint(255)/255,np.random.randint(255)/255)

	blue = ["#2d79bc","#1d3be2","#5eb2d6","#4786e5","#0e1eb2","#96bc38"][np.random.randint(0,6)]
	red = ["#e07f74","#d8433e","#d14e34","#d65428","#ce6750","#bf7070"][np.random.randint(0,6)]
	yellow = ["#dda91a","#ffd507","#edd57d","#fff884","#e8d27a","#e0bb35"][np.random.randint(0,6)]
	feature_colors = ["#ffffff","#000000",blue,red,yellow,wild_color]

	ax.set_facecolor(bg_colors[np.random.randint(0,12)])

	bg_line_color = ["#ffffff","#000000"][np.random.choice([0,1], p = [0,1])]
	bg_line_N = np.random.randint(100,500)
	bg_line_xs  = np.random.randint(-1600,1600, bg_line_N)
	bg_line_ys = np.random.randint(-1200,1200,bg_line_N)
	bg_line_points = np.dstack((bg_line_xs,bg_line_ys))[0]
	bg_line_mit = np.random.randint(1,10)
	bg_line = paint_line(bg_line_points,bg_line_mit,fig,ax,color=bg_line_color)
	bg_line.plt_spline()

	for i in range(num_features):
		color = feature_colors[np.random.choice([0,1,2,3,4,5], p = [0.25,0.25,0.16,0.16,0.16,0.02])]

		line_or_splatter = np.random.choice([0,1],p=[0.10,0.90])

		if line_or_splatter == 0: #then it's a line
			N = np.random.randint(8,32)
			xs  = np.random.randint(-1600,1600, N)
			ys = np.random.randint(-1200,1200,N)
			points = np.dstack((xs,ys))[0]

			if N > 10:
				mit = np.random.uniform(1,50)

			else:
				mit = np.random.uniform(30,150)

			pl = paint_line(points,mit,fig,ax,color=color)
			pl.plt_spline()
            
		else: #then it's a splatter
			start = np.array([np.random.randint(-1600, 1600), np.random.randint(-1200, 1200)])
			end = np.array([np.random.randint(-1600, 1600), np.random.randint(-1200, 1200)])
			spreadiness = np.random.uniform(0,0.4)
			thickness = np.random.uniform(0.95,4)

			my_flick = flick(start,end,fig,ax,spreadiness,thickness, color = color)
			my_flick.draw_ellipses()

	plt.savefig(filename,bbox_inches='tight',dpi = 800)

def main():
    paint("pollock")


if __name__=="__main__":
  main()
