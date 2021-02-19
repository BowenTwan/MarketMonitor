from jqdatasdk import *
import datetime
import pandas as pd
from bokeh.models import ColumnDataSource, LabelSet, ColorBar
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import column
from bokeh.transform import linear_cmap
from bokeh.palettes import RdYlGn
import math
import os

# check if log in JoinQuant
# connect to JoinQuant
auth('18328314344', '314344')
is_auth = is_auth()
print(is_auth)

# set up data timeframe
today = datetime.datetime.today().strftime('%Y-%m-%d')

# create foder to save recordd
cwd = os.getcwd()
new_daily_dir = cwd+'/'+'DailyReviewRecord/'+today
try:
    os.makedirs(new_daily_dir)
except FileExistsError:
    # directory already exists
    pass


#* output to static HTML file
output_file("Market_Daily_Review.html")
# set up the side tools 
TOOLS = "pan,wheel_zoom,reset,hover,save"

# downlaoding stock list 
print('downlaoding stock list \n')
stock_list = get_all_securities(types=['stock'])
stock_list.to_csv(f'{cwd}/stock_list.csv')



#* setting stock watch list 
stk_watchlist = ['万科A','平安银行','牧原股份','海天味业','贵州茅台','迈瑞医疗']
selected_stk = stock_list[stock_list['display_name'].isin(stk_watchlist)].index.tolist()
#* setting index watch list 
# get sh and sz market index code
index = get_all_securities(types=['index'], date=None)
indexs_watchlist = ['上证指数','A股指数','上证金融', '上证消费','上证医药', '沪深300', '深证指数']
selected_index = index[index['display_name'].isin(indexs_watchlist)].index.tolist()

plots = []
#! plot daily industry change
# download SW1 daily changing data from JoinQuant
df_sw1=finance.run_query(query(finance.SW1_DAILY_PRICE).filter(finance.SW1_DAILY_PRICE.date==today))
df_sw1.sort_values(by=['change_pct'], ascending = False, inplace = True)
# save sw1 daily data
df_sw1.to_csv(f'{new_daily_dir}/sw1{today}.csv')
print(f'{today} sw1 data downloaded and saved.')

# data for displaying
source_sw1 = ColumnDataSource(dict(X = df_sw1['name'], Y = df_sw1['change_pct']))
#set up color mapper, red when > 0, green when < 0
mapper = linear_cmap(field_name='Y', low = 0, high = 0 , palette=RdYlGn[3])
#set up plot figures
plot_sw1 = figure(plot_height=600, plot_width=1000 ,tools = TOOLS,
        x_axis_label = "Sectors",
        y_axis_label = "Change%",
        title= "SW1_Daily_Change",
        x_range = source_sw1.data["X"])

# plotting 
plot_sw1.vbar(source=source_sw1,x='X',top='Y',bottom=0,width=0.3, color=mapper)
# rotate x-axis labers 
plot_sw1.xaxis.major_label_orientation = math.pi/4
#add labels 
labels = LabelSet(x='X', y='Y', text='Y', level='overlay',text_font_size='10pt',
        x_offset=-13.5, y_offset=0, source=source_sw1, render_mode='canvas')
plot_sw1.add_layout(labels)
plots.append(plot_sw1)
print('sw1 plot generated')


#! plot index
index_df = pd.DataFrame()
i = 0
# download index daily data
for index_code, index_name in zip(index.index, index.display_name):
    data0 = get_price(index_code, start_date='2021-02-17', end_date=today, frequency='daily', fields=None, skip_paused=False, fq='pre')
    data0['close_pct_chg'] = data0['close'].pct_change() # caculate daily pecentage change 
    data0['index_name'] = index_code                 # add index code
    data0['name'] = index_name
    index_df = pd.concat([index_df,data0.iloc[1]], axis =1)
    i += 1
    print(f'No.{i} index {index_name} checked, {i} out of {len(index)} processed')

index_df = index_df.T.set_index('index_name')

# check watchlist changes
index_watchlist = index_df.loc[selected_index]
# check top10 volume index changes
index_vol_top10 = index_df.sort_values(by='volume', ascending = False )[:10]
# check top10 price index changes
index_up10 = index_df.sort_values(by='close_pct_chg',ascending = False )[:10]
# check btm10 price index changes
index_down10 = index_df.sort_values(by='close_pct_chg',ascending = False )[-10:-1]
print('wachtlist, top10 list, btm10 list of index daily updated')



# save daily file
index_watchlist.to_csv(f'{new_daily_dir}/watchlist{today}.csv')
index_vol_top10.to_csv(f'{new_daily_dir}/index_vol_top10{today}.csv')
index_up10.to_csv(f'{new_daily_dir}/index_up10{today}.csv')
index_down10.to_csv(f'{new_daily_dir}/index_down10{today}.csv')
print('All Index Daily Files Saved!')


# plot daily data
plots_index = []
titles = ('index_watchlist', 'index_vol_top10', 'index_up10')
for i,t in zip((index_watchlist, index_vol_top10, index_up10), titles):
    source0  = ColumnDataSource(dict(X = i['name'], Y =i['close_pct_chg']))
    #set up color mapper, red when > 0, green when < 0
    mapper = linear_cmap(field_name='Y', low = min(i['close_pct_chg']), high = max(i['close_pct_chg']) , palette=RdYlGn[3])
    #set up plot figures
    TOOLS = "pan,wheel_zoom,reset,hover,save"
    p = figure(plot_height=600, plot_width=1000 ,tools = TOOLS,
            x_axis_label = "index",
            y_axis_label = "Change%",
            title= t,
            x_range = source0.data["X"])

    # plotting 
    p.vbar(source=source0,x='X',top='Y',bottom=0,width=0.3, color=mapper)
    # rotate x-axis labers 
    p.xaxis.major_label_orientation = math.pi/4
    #add labels 
    labels = LabelSet(x='X', y='Y', text='Y', level='glyph',text_font_size='10pt',
            x_offset=0, y_offset=0.1, source=source0, render_mode='canvas')
    p.add_layout(labels)
    plots.append(p)
print('index plot generated')

#! top10 & btm10
#! Trade volumn change % 

stk_df = pd.DataFrame()
# downloading data from JoinQuant
i = 0
for stock_code, name in zip(stock_list.index, stock_list.display_name):
    data0 = get_price(stock_code, start_date=today, end_date=today, frequency='daily', 
            fields=('open', 'close', 'pre_close','high', 'low', 'volume', 'money','paused'),
            skip_paused=False, fq='pre')
    data0['stock_code'] =  stock_code
    data0['display_name'] = name
    stk_df = pd.concat([stk_df, data0])
    i += 1
    print(f'No.{i} stock {name} checked, {i} out of {len(stock_list)} processed')
# add stock code
stk_df['close_pct_chg'] = round(stk_df['close']/stk_df['pre_close'] *100,4) - 100
# reset index
stk_df = stk_df.set_index('stock_code')
stk_df = stk_df.dropna(thresh=8)
#save all stock daily data
stk_df.to_csv(f'{new_daily_dir}/DailyChanges{today}.csv')
print('all stock daily data saved')

# check watchlist changes
stk_watchlist = stk_df.loc[selected_stk]
# check top10 volume index changes
stk_vol_top10 = stk_df.sort_values(by='volume', ascending = False )[:10]
# check top10 price index changes
stk_up10 = stk_df.sort_values(by='close_pct_chg',ascending = False )[:10]
# check btm10 price index changes
stk_down10 = stk_df.sort_values(by='close_pct_chg',ascending = False )[-10:-1]
print('wachtlist, top10 stock, btm10 stock list of stock daily updated')

stk_plots = []
stk_title = ('stk_watchlist', 'stk_vol_top10', 'stk_up10','stk_down10')
for i,t in zip((stk_watchlist, stk_vol_top10, stk_up10,stk_down10), stk_title):
    source0  = ColumnDataSource(dict(X = i['display_name'], Y =i['close_pct_chg']))
    #set up color mapper, red when > 0, green when < 0
    mapper = linear_cmap(field_name='Y', low = min(i['close_pct_chg']), high = max(i['close_pct_chg']) , palette=RdYlGn[3])
    #set up plot figures
    TOOLS = "pan,wheel_zoom,reset,hover,save"
    p = figure(plot_height=600, plot_width=1000 ,tools = TOOLS,
            x_axis_label = "stock",
            y_axis_label = "Change%",
            title= t,
            x_range = source0.data["X"])

    # plotting 
    p.vbar(source=source0,x='X',top='Y',bottom=0,width=0.3, color=mapper)
    # rotate x-axis labers 
    p.xaxis.major_label_orientation = math.pi/4
    #add labels 
    labels = LabelSet(x='X', y='Y', text='Y', level='glyph',text_font_size='10pt',
            x_offset=0, y_offset=0.1, source=source0, render_mode='canvas')
    p.add_layout(labels)
    plots.append(p)
print('stock plot generated')

#! watch list 
# plot candstick for watchlist 
candle_plots = []
i = 0 
for stk in selected_stk:
    df = get_price(stk, start_date='2021-01-01', end_date=today, frequency='daily', 
                fields=('open', 'close', 'pre_close','high', 'low', 'volume', 'money','paused'),
                skip_paused=False, fq='pre')

    df["date"] = pd.to_datetime(df.index)

    inc = df.close > df.open
    dec = df.open > df.close
    w = 12*60*60*1000 # half day in ms

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1000, plot_height=300, title = f"{stock_list.loc[stk].display_name} Candlestick")
    p.xaxis.major_label_orientation = math.pi/4
    p.grid.grid_line_alpha=0.3

    p.segment(df.date, df.high, df.date, df.low, color="black")
    # green for price up, red for price down
    p.vbar(df.date[inc], w, df.open[inc], df.close[inc], fill_color="#26d923", line_color="black")
    p.vbar(df.date[dec], w, df.open[dec], df.close[dec], fill_color="#F2583E", line_color="black")
    plots.append(p)
print('stock watchlist plot generated')

# make a grid
# grid = gridplot([[plot_sw1],
#                 [plots_index[0],plots_index[1],plots_index[2]],
#                 [stk_plots[0],stk_plots[2],stk_plots[3],stk_plots[1]],
#                 [candle_plots[0],candle_plots[1]]], 
#                 plot_width=400, plot_height=250)
show(column(plots),plot_width=400, plot_height=250)

print('Daily Market Review Complete!')
