from jqdatasdk import *
import datetime
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.font_manager import *
from bokeh.models import ColumnDataSource, ranges, LabelSet, ColorBar
from bokeh.plotting import figure, output_file, show
from bokeh.transform import linear_cmap
from bokeh.palettes import RdYlGn
import math

#定义自定义字体，文件名从1.b查看系统中文字体中来
# forch matplotlib display chinese 
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['font.serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# check if log in JoinQuant
# connect to JoinQuant
auth('18328314344', '314344')
is_auth = is_auth()
print(is_auth)

# set up data timeframe
today = datetime.datetime.today().strftime('%Y-%m-%d')

#* output to static HTML file
output_file("Market_Daily_Review.html")
# set up the side tools 
TOOLS = "pan,wheel_zoom,reset,hover,save"

#! plot daily industry change
# download SW1 daily changing data from JoinQuant
df_sw1=finance.run_query(query(finance.SW1_DAILY_PRICE).filter(finance.SW1_DAILY_PRICE.date=="2021-02-10"))
df_sw1.sort_values(by=['change_pct'], ascending = False, inplace = True)

# data for displaying
source_sw1 = ColumnDataSource(dict(X = df_sw1['name'], Y = df_sw1['change_pct']))
#set up color mapper, red when > 0, green when < 0
mapper = linear_cmap(field_name='Y', low = 0, high = 0 , palette=RdYlGn[3])
#set up plot figures
plot = figure(plot_height=600, plot_width=1000 ,tools = TOOLS,
        x_axis_label = "Sectors",
        y_axis_label = "Change%",
        title= "SW1_Daily_Change",
        x_range = source_sw1.data["X"])

# plotting 
plot.vbar(source=source_sw1,x='X',top='Y',bottom=0,width=0.3, color=mapper)
# rotate x-axis labers 
plot.xaxis.major_label_orientation = math.pi/4
#add labels 
labels = LabelSet(x='X', y='Y', text='Y', level='overlay',text_font_size='10pt',
        x_offset=-13.5, y_offset=0, source=source_sw1, render_mode='canvas')
plot.add_layout(labels)

#! hot concept sector 
#! plot index 
#! top10 & btm10
#! watch list 
#! money flow 
show(plot)



# p = figure(plot_height=400, title = "SW1 Daily Change")
# p.vbar(source = source, )

# show(p)
# plt.bar(x, y, color ='r' )

# # label data above each bar 
# for index,data in enumerate(y):
#     plt.text(x=index , y =data+1 , s=f"{data}" , fontdict=dict(fontsize=10))
    
# plt.show()

# print(df)