'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on Jan 1, 2011

@author:Drew Bratcher
@contact: dbratcher@gatech.edu
@summary: Contains tutorial for backtester and report.

'''

from os import path, makedirs
from os import sys
from qstkutil import DataAccess as da
from qstkutil import qsdateutil as du
from qstkutil import tsutil as tsu
from qstkutil import fundutil as fu
import numpy as np
from math import log10
import converter
from pylab import savefig
from matplotlib import pyplot
from matplotlib import gridspec
import matplotlib.dates as mdates
import cPickle
import datetime as dt


def print_header(html_file, name):
    """
    @summary prints header of report html file
    """
    html_file.write("<HTML>\n")
    html_file.write("<HEAD>\n")
    html_file.write("<TITLE>QSTK Generated Report:" + name + "</TITLE>\n")
    html_file.write("</HEAD>\n\n")
    html_file.write("<BODY>\n\n")

def print_footer(html_file):
    """
    @summary prints footer of report html file
    """
    html_file.write("</BODY>\n\n")
    html_file.write("</HTML>")

def print_annual_return(fund_ts, years, ostream):
    """
    @summary prints annual return for given fund and years to the given stream
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    for year in years:
        year_vals = []
        for date in fund_ts.index:
            if(date.year ==year):
                year_vals.append([fund_ts.ix[date]])
        day_rets = tsu.daily1(year_vals)
        ret = tsu.get_ror_annual(day_rets[1:-1])
        ostream.write("   % + 6.2f%%" % (ret*100))

def print_winning_days(fund_ts, years, ostream):
    """
    @summary prints winning days for given fund and years to the given stream
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    for year in years:
        year_vals = []
        for date in fund_ts.index:
            if(date.year==year):
                year_vals.append([fund_ts.ix[date]])
        ret = fu.get_winning_days(year_vals)
        ostream.write("   % + 6.2f%%" % ret)

def print_max_draw_down(fund_ts, years, ostream):
    """
    @summary prints max draw down for given fund and years to the given stream
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    for year in years:
        year_vals = []
        for date in fund_ts.index:
            if(date.year==year):
                year_vals.append(fund_ts.ix[date])
        ret = fu.get_max_draw_down(year_vals)
        ostream.write("   % + 6.2f%%" % (ret*100))

def print_daily_sharpe(fund_ts, years, ostream):
    """
    @summary prints sharpe ratio for given fund and years to the given stream
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    for year in years:
        year_vals = []
        for date in fund_ts.index:
            if(date.year==year):
                year_vals.append([fund_ts.ix[date]])
        ret = fu.get_sharpe_ratio(year_vals)
        ostream.write("   % + 6.2f " % ret)

def print_daily_sortino(fund_ts, years, ostream):
    """
    @summary prints sortino ratio for given fund and years to the given stream
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    for year in years:
        year_vals = []
        for date in fund_ts.index:
            if(date.year==year):
                year_vals.append([fund_ts.ix[date]])
        ret = fu.get_sortino_ratio(year_vals)
        ostream.write("   % + 6.2f " % ret)
        
def print_std_dev(fund_ts, ostream):
    """
    @summary prints standard deviation of returns for a fund
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    fund_ts=fund_ts.fillna(method='pad')
    ret=np.std(tsu.daily(fund_ts.values))*10000
    ostream.write("  % + 6.2f bps " % ret)

def print_industry_coer(fund_ts, ostream):
    """
    @summary prints standard deviation of returns for a fund
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    industries = [['$DJUSBM', 'Materials'],
    ['$DJUSNC', 'Goods'],
    ['$DJUSCY', 'Services'],
    ['$DJUSFN', 'Financials'],
    ['$DJUSHC', 'Health'],
    ['$DJUSIN', 'Industrial'],
    ['$DJUSEN', 'Oil & Gas'],
    ['$DJUSTC', 'Technology'],
    ['$DJUSTL', 'TeleComm'],
    ['$DJUSUT', 'Utilities']]
    for i in range(0, len(industries) ):
        if(i%3==0):
            ostream.write("\n")
        #load data
        norObj = da.DataAccess('Norgate')
        ldtTimestamps = du.getNYSEdays( fund_ts.index[0], fund_ts.index[-1], dt.timedelta(hours=16) )
        ldfData = norObj.get_data( ldtTimestamps, [industries[i][0]], ['close'] )
        #get corelation
        ldfData[0]=ldfData[0].fillna(method='pad')
        a=np.corrcoef(ldfData[0][industries[i][0]],fund_ts.values)
        ostream.write("%10s(%s):%+6.2f   " % (industries[i][1], industries[i][0], a[0,1]))

def print_benchmark_coer(fund_ts, benchmark_close, sym,  ostream):
    """
    @summary prints standard deviation of returns for a fund
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    fund_ts=fund_ts.fillna(method='pad')
    benchmark_close=benchmark_close.fillna(method='pad')
    faCorr=np.corrcoef(fund_ts.values,np.ravel(benchmark_close));
    b=np.ravel(tsu.daily(benchmark_close))
    f=np.ravel(tsu.daily(fund_ts))
    fBeta, unused = np.polyfit(b,f, 1);
    ostream.write("\n\n%4s Correlation:   %+6.2f" % (sym, faCorr[0,1]))
    ostream.write("\n%4s Beta:          %+6.2f\n" % (sym, fBeta))

def print_monthly_returns(fund_ts, years, ostream):
    """
    @summary prints monthly returns for given fund and years to the given stream
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    ostream.write("    ")
    month_names = du.getMonthNames()
    for name in month_names:
        ostream.write("    " + str(name))
    ostream.write("\n")
    i = 0
    mrets = tsu.monthly(fund_ts)
    for year in years:
        ostream.write(str(year))
        months = du.getMonths(fund_ts, year)
        for k in range(1, months[0]):
            ostream.write("       ")
        for month in months:
            ostream.write(" % + 6.2f" % (mrets[i]*100))
            i += 1
        ostream.write("\n")

def print_stats(fund_ts, benchmark, name, directory = False, leverage = False, \
commissions = 0, slippage = 0, ostream = sys.stdout):
    """
    @summary prints stats of a provided fund and benchmark
    @param fund_ts: fund value in pandas timeseries
    @param benchmark: benchmark symbol to compare fund to
    @param name: name to associate with the fund in the report
    @param directory: parameter to specify printing to a directory
    @param leverage: time series to plot with report
    @param commissions: value to print with report
    @param slippage: value to print with report
    @param ostream: stream to print stats to, defaults to stdout
    """
    fund_ts=fund_ts.fillna(method='pad')
    if directory != False :
        if not path.exists(directory):
            makedirs(directory)
        
        sfile = path.join(directory, "report-%s.html" % name )
        splot = "plot-%s.png" % name
        splot_dir =  path.join(directory, splot)
        ostream = open(sfile, "wb")
        ostream.write("<pre>")
        print "writing to ", sfile
        if type(leverage)!=type(False):
            print_plot(fund_ts, benchmark, name, splot_dir, 
                       leverage=leverage)
        else:
            print_plot(fund_ts, benchmark, name, splot_dir) 
    start_date = fund_ts.index[0].strftime("%m/%d/%Y")
    end_date = fund_ts.index[-1].strftime("%m/%d/%Y")
    ostream.write("Performance Summary for "\
	 + str(path.basename(name)) + " Backtest\n")
    ostream.write("For the dates " + str(start_date) + " to "\
                                       + str(end_date) + "\n\n")
    if directory != False :
        ostream.write("<img src="+splot+" width=450>\n\n")
        
    mult = 1000000/fund_ts.values[0]
    ostream.write("Initial Fund Value: %10s\n" % ("$"+str(int(round(fund_ts.values[0]*mult)))))
    ostream.write("Ending Fund Value:  %10s\n\n" % ("$"+str(int(round(fund_ts.values[-1]*mult)))))
    ostream.write("Transaction Costs\n\n")
    ostream.write("Total Comissions:   %10s\n" % ("$"+str(int(round(commissions)))))
    ostream.write("Total Slippage:     %10s\n\n" % ("$"+str(int(round(slippage)))))
    ostream.write("Yearly Performance Metrics \n")
    years = du.getYears(fund_ts)
    ostream.write("\n                            ")
    for year in years:
        ostream.write("      " + str(year))
    ostream.write("\n")
    
    
    ostream.write("Fund Annualized Return:      ")
    
    print_annual_return(fund_ts, years, ostream)
    
    ostream.write("\n%-4s Annualized Return:      " % str(benchmark[0]))
    timeofday = dt.timedelta(hours = 16)
    timestamps = du.getNYSEdays(fund_ts.index[0], fund_ts.index[-1], timeofday)
    dataobj = da.DataAccess('Norgate')
    benchmark_close = dataobj.get_data(timestamps, benchmark, "close", \
                                                     verbose = False)
    
    benchmark_close=benchmark_close.fillna(method='pad')
    print_annual_return(benchmark_close, years, ostream)
    
    ostream.write("\n\nFund Winning Days:           ")                
    
    print_winning_days(fund_ts, years, ostream)

    ostream.write("\n%-4s Winning Days:           " % str(benchmark[0]))                
    print_winning_days(benchmark_close, years, ostream)

    ostream.write("\n\nFund Max Draw Down:          ")
    
    print_max_draw_down(fund_ts, years, ostream)

    ostream.write("\n%-4s Max Draw Down:          " % str(benchmark[0]))

    print_max_draw_down(benchmark_close, years, ostream)

    ostream.write("\n\nFund Daily Sharpe Ratio:     ")

    print_daily_sharpe(fund_ts, years, ostream)

    ostream.write("\n%-4s Daily Sharpe Ratio:     " % str(benchmark[0]))       

    print_daily_sharpe(benchmark_close, years, ostream)

    ostream.write("\n\nFund Daily Sortino Ratio:    ")

    print_daily_sortino(fund_ts, years, ostream)

    ostream.write("\n%-4s Daily Sortino Ratio:    " % str(benchmark[0]))         

    print_daily_sortino(benchmark_close, years, ostream)
    
    ostream.write("\n\nFund Std Dev of Returns:     ")
    
    print_std_dev(fund_ts, ostream)
    
    ostream.write("\n%-4s Std Dev of Returns:     " % str(benchmark[0]))    
    
    print_std_dev(benchmark_close, ostream)
    
    ostream.write("\n\nCorrelation and Beta with Dow Jones Industries")
    
    print_industry_coer(fund_ts,ostream)
    
    print_benchmark_coer(fund_ts, benchmark_close, str(benchmark[0]), ostream)
    
    ostream.write("\n\nMonthly Returns %\n")
    
    print_monthly_returns(fund_ts, years, ostream) 
    if directory != False:
        ostream.write("</pre>")           

def print_plot(fund, benchmark, graph_name, filename, leverage=False):
    """
    @summary prints a plot of a provided fund and benchmark
    @param fund: fund value in pandas timeseries
    @param benchmark: benchmark symbol to compare fund to
    @param graph_name: name to associate with the fund in the report
    @param filename: file location to store plot1
    """
    pyplot.clf()
    if type(leverage)!=type(False): 
        gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1]) 
        pyplot.subplot(gs[0])
    start_date = 0
    end_date = 0
    if(type(fund)!= type(list())):
        if(start_date == 0 or start_date>fund.index[0]):
            start_date = fund.index[0]    
        if(end_date == 0 or end_date<fund.index[-1]):
            end_date = fund.index[-1]    
        mult = 1000000/fund.values[0]
        pyplot.plot(fund.index, fund.values * mult, label = \
                                 path.basename(graph_name))
    else:    
        if(start_date == 0 or start_date>fund[0].index[0]):
            start_date = fund[0].index[0]    
        if(end_date == 0 or end_date<fund[0].index[-1]):
            end_date = fund[0].index[-1]    
        mult = 1000000/fund[0].values[0]
        pyplot.plot(fund[0].index, fund[0].values * mult, label = \
                                  path.basename(graph_name))
    timeofday = dt.timedelta(hours = 16)
    timestamps = du.getNYSEdays(start_date, end_date, timeofday)
    dataobj = da.DataAccess('Norgate')
    benchmark_close = dataobj.get_data(timestamps, benchmark, "close", \
                                            verbose = False)
    benchmark_close = benchmark_close.fillna(method='pad')
    mult = 1000000 / benchmark_close.values[0]
    pyplot.plot(benchmark_close.index, \
                benchmark_close.values*mult, label = benchmark[0])
    pyplot.gcf().autofmt_xdate()
    pyplot.gca().fmt_xdata = mdates.DateFormatter('%m-%d-%Y')
    pyplot.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d %Y'))
    pyplot.xlabel('Date')
    pyplot.ylabel('Fund Value')
    pyplot.legend(loc = "best")
    if type(leverage)!=type(False):
        pyplot.subplot(gs[1])
        pyplot.plot(leverage.index, leverage.values, label="Leverage")
        pyplot.gcf().autofmt_xdate()
        pyplot.gca().fmt_xdata = mdates.DateFormatter('%m-%d-%Y')
        pyplot.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d %Y'))
        labels=[]
        max_label=max(leverage.values)
        min_label=min(leverage.values)
        rounder= -1*(round(log10(max_label))-1)
        labels.append(round(min_label*0.9, int(rounder)))
        labels.append(round((max_label+min_label)/2, int(rounder)))
        labels.append(round(max_label*1.1, int(rounder)))
        pyplot.yticks(labels)
        pyplot.legend(loc = "best")
        pyplot.title(graph_name + " Leverage")
        pyplot.xlabel('Date')
        pyplot.legend()
    pyplot.draw()
    savefig(filename, format = 'png')
     

def generate_report(funds_list, graph_names, out_file):
    """
    @summary generates a report given a list of fund time series
    """
    html_file  =  open("report.html","w")
    print_header(html_file, out_file)
    html_file.write("<IMG SRC = \'./funds.png\' width = 400/>\n")
    html_file.write("<BR/>\n\n")
    i = 0
    pyplot.clf()
    #load spx for time frame
    symbol = ["$SPX"]
    start_date = 0
    end_date = 0
    for fund in funds_list:
        if(type(fund)!= type(list())):
            if(start_date == 0 or start_date>fund.index[0]):
                start_date = fund.index[0]    
            if(end_date == 0 or end_date<fund.index[-1]):
                end_date = fund.index[-1]    
            mult = 10000/fund.values[0]
            pyplot.plot(fund.index, fund.values * mult, label = \
                                 path.basename(graph_names[i]))
        else:    
            if(start_date == 0 or start_date>fund[0].index[0]):
                start_date = fund[0].index[0]    
            if(end_date == 0 or end_date<fund[0].index[-1]):
                end_date = fund[0].index[-1]    
            mult = 10000/fund[0].values[0]
            pyplot.plot(fund[0].index, fund[0].values * mult, label = \
                                      path.basename(graph_names[i]))    
        i += 1
    timeofday = dt.timedelta(hours = 16)
    timestamps = du.getNYSEdays(start_date, end_date, timeofday)
    dataobj = da.DataAccess('Norgate')
    benchmark_close = dataobj.get_data(timestamps, symbol, "close", \
                                            verbose = False)
    mult = 10000/benchmark_close.values[0]
    i = 0
    for fund in funds_list:
        if(type(fund)!= type(list())):
            print_stats(fund, ["$SPX"], graph_names[i])
        else:    
            print_stats( fund[0], ["$SPX"], graph_names[i])
        i += 1
    pyplot.plot(benchmark_close.index, \
                 benchmark_close.values*mult, label = "SSPX")
    pyplot.ylabel('Fund Value')
    pyplot.xlabel('Date')
    pyplot.legend()
    pyplot.draw()
    savefig('funds.png', format = 'png')
    print_footer(html_file)

def generate_robust_report(fund_matrix, out_file):
    """
    @summary generates a report using robust backtesting
    @param fund_matrix: a pandas matrix of fund time series
    @param out_file: filename where to print report
    """
    html_file  =  open(out_file,"w")
    print_header(html_file, out_file)
    converter.fundsToPNG(fund_matrix,'funds.png')
    html_file.write("<H2>QSTK Generated Report:" + out_file + "</H2>\n")
    html_file.write("<IMG SRC = \'./funds.png\'/>\n")
    html_file.write("<IMG SRC = \'./analysis.png\'/>\n")
    html_file.write("<BR/>\n\n")
    print_stats(fund_matrix, "robust funds", html_file)
    print_footer(html_file)

if __name__  ==  '__main__':
    # Usage
    #
    # Normal:
    # python report.py 'out.pkl' ['out2.pkl' ...]
    #
    # Robust:
    # python report.py -r 'out.pkl'
    #
    
    ROBUST = 0

    if(sys.argv[1] == '-r'):
        ROBUST = 1

    FILENAME  =  "report.html"
    
    if(ROBUST == 1):
        ANINPUT = open(sys.argv[2],"r")
        FUNDS = cPickle.load(ANINPUT)
        generate_robust_report(FUNDS, FILENAME)
    else:
        FILES = sys.argv
        FILES.remove(FILES[0])
        FUNDS = []
        for AFILE in FILES:
            ANINPUT = open(AFILE,"r")
            FUND = cPickle.load(ANINPUT)
            FUNDS.append(FUND)
        generate_report(FUNDS, FILES, FILENAME)


