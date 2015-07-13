import numpy as np
import matplotlib.pyplot as plt
import os,re,sys,os.path,glob

from scipy.integrate import quad

import keplerfpp as kfpp
import koiutils as ku

import plotutils as plu
import statutils as statu

import numpy.random as rand

import pandas as pd

def fpp_of_b(fig=None,symbol='+',dbin=0.05,plot_points=True):
    plu.setfig(fig)

    cands = FPPDATA[OK_CANDIDATE]

    #xbins = np.arange(0,1.01,dbin)
    xbins = np.array([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95,1])
    xvals = xbins*0
    yvals = xbins*0
    yerrs_p = xbins*0
    yerrs_m = xbins*0
    for i in np.arange(len(xbins)):
        lo = xbins[i]
        if i==len(xbins)-1:
            hi = np.inf
        else:
            hi = xbins[i+1]
        
        inbin = (cands['b'] >= lo) & (cands['b'] < hi)
        xvals[i] = lo + dbin/2
        data = cands[inbin]['fpp']
        yvals[i] = data.median()
        yerrs_p[i] = data.quantile(0.84) - data.median()
        yerrs_m[i] = data.median() - data.quantile(0.16)
        
    ax = plt.subplot(111)
    ax.set_yscale('log')

    if plot_points:
        n = len(cands)
        ax.plot(cands['b']+rand.normal(size=n)*0.01,
                cands['fpp']*(1+rand.normal(size=n)*0.01),
                'o',ms=1,mew=1,alpha=0.5)

    ax.errorbar(xvals,yvals,yerr=[np.abs(yerrs_m),np.abs(yerrs_p)],
                fmt='o',color='k',lw=3)
    ax.plot(xvals,yvals,'wo',ms=15)
    ax.plot(xvals,yvals,'ko',ms=13)
    ax.plot(xvals,yvals,'co',ms=12)


    ax.set_ylim((1e-4,1))
    ax.set_xlim((0,1.1))

    plt.xlabel('Impact Parameter')
    plt.ylabel('False Positive Probability')

def goodcandidate_summaryplot(fig=None,nbins=10,showcc=True,
                              markrs=[1,1.5,2,2.5,3,4,10],
                              **kwargs):
    data = FPPDATA[GOOD_CANDIDATE]
    fpp_summaryplot(data=data,fig=fig,nbins=nbins,
                    title='Candidates with\ngood logg',
                    markrs=markrs,showcc=showcc,
                    **kwargs)
    

def knownfp_summaryplot(fig=None,nbins=12,markrs=[1,1.5,2,3,5,10,20],
                        **kwargs):
    data = FPPDATA[OK_FP]
    fpp_summaryplot(data=data,fig=fig,
                    title='Known FPs',titlexy=(0.25,0.25),
                    nbins=nbins,markrs=markrs,**kwargs)
    
def knownfp_ontarget_summaryplot(fig=None,nbins=6,useb=False,
                                 markrs=[1,1.5,3,10,30,40],
                                 **kwargs):
    if useb:
        data = FPPDATA[OK_FP & ONTARGET & ~PEM & LOWB]
        fpp_summaryplot(data=data,fig=fig,titlexy=(0.25,0.25),
                        title='Known FPs\n(on target, b<0.9)',
                        nbins=nbins,markrs=markrs,**kwargs)
    else:
        data = FPPDATA[OK_FP & ONTARGET & ~PEM]
        fpp_summaryplot(data=data,fig=fig,titlexy=(0.25,0.25),
                        title='Known FPs\n(on target)',
                        nbins=nbins,markrs=markrs,**kwargs)
        

def confirmed_summaryplot(fig=None,nbins=8,**kwargs):
    fpp_summaryplot(data=FPPDATA[ISCONFIRMED],fig=fig,
                    title='Confirmed Planets',
                    nbins=nbins,**kwargs)


def cand_summaryplot(fig=None,nbins=12,showcc=True,**kwargs):
    fpp_summaryplot(data=FPPDATA[OK_CANDIDATE],fig=fig,
                    title='Good Candidates',
                    nbins=nbins,showcc=showcc,**kwargs)

def fpp_summaryplot(data=FPPDATA,fig=None,symbol='o',ms=1,color='k',
                    markrs=[1,1.5,2,2.5,3,4,10],nbins=None,alpha=0.5,
                    title=None,hlineval=0.01,labelpos=(0.75,0.15),
                    summarylabel=True,erasedata=None,titlefontsize=20,
                    titlexy=(0.25,0.85),showcc=False,cc_symbol='o',
                    cc_ms=2,cc_color='b',rao_color='c',prelim=True,
                    **kwargs):
    plu.setfig(fig)

    
    inds = np.argsort(data['rp'])
    ypts = data['FPP'][inds].clip(1e-4,1)
    xpts = np.arange(len(data))
    plt.semilogy(ypts,symbol,ms=ms,color=color,alpha=alpha,**kwargs)
    if showcc:
        hascc = data['AO'][inds] != 'None'
        has_rao = data['RAO'][inds]
        plt.semilogy(xpts[np.where(hascc & ~has_rao)],ypts[hascc & ~has_rao],
                     cc_symbol,ms=cc_ms,color=cc_color,
                     mec=cc_color)
        plt.semilogy(xpts[np.where(has_rao)],ypts[has_rao],cc_symbol,
                     ms=cc_ms,color=rao_color,
                     mec=rao_color)

        
    if erasedata is not None:
        plt.semilogy(ypts,symbol,ms=ms,color=color,alpha=alpha,**kwargs)
    plt.ylim(ymin=8e-5)
    xmax = inds.max()+1
    plt.xlim(xmax=xmax)
    plt.xticks([])

    ax = plt.gca()

    plt.axhline(hlineval,color='k',lw=2)

    for r in markrs:
        i = np.argmin(np.absolute(data['rp'][inds]-r))
        ax.axvline(i,color='k',lw=3,ls=':')
        ax.annotate(r'%.1f' % r,xy=(float(i)/xmax,-0.05),xycoords='axes fraction',ha='center',
                    annotation_clip=False,fontsize=14)
        

    if nbins is not None:
        N = len(ypts)
        binsize = N/nbins
        xbins = []
        ybins = []
        yerrs = []
        for i in range(nbins):
            xbins.append((xpts[i*binsize:(i+1)*binsize]).mean())
            ybins.append(np.median(ypts[i*binsize:(i+1)*binsize]))
            yerrs.append((ypts[i*binsize:(i+1)*binsize]).std())
        #plt.errorbar(xbins,ybins,yerr=yerrs,color=linecolor,fmt='o',ms=5)
        plt.plot(xbins,ybins,'wo',ms=15)
        plt.plot(xbins,ybins,'ko',ms=13)
        plt.plot(xbins,ybins,'ro',ms=12)

    plt.xlabel('Planet Radius [$R_\oplus$]',labelpad=30)
    plt.ylabel('False Positive Probability')

    if title is not None:
        plt.annotate(title,xy=titlexy,xycoords='axes fraction',
                     fontsize=titlefontsize,
                     bbox=dict(boxstyle='round',fc='w',lw=2),ha='center')

    if summarylabel:
        N = float(len(data))
        gt_50pct = (data['fpp'] > 0.5).sum()
        lt_1pct = (data['fpp'] < 0.01).sum()
        #lt_03pct = (data['fpp'] < 0.003).sum()
        plt.annotate('%i/%i FPP > 50%%\n%i/%i FPP < 1%%' % 
                     (gt_50pct,N,lt_1pct,N),xy=labelpos,xycoords='axes fraction',
                     fontsize=15,bbox=dict(boxstyle='round',fc='w',lw=2),ha='center')

    if prelim:
        plt.annotate('Preliminary',xy=(0.05,0.12),xycoords='axes fraction',
                     fontsize=14,color='r',rotation=-30,
                     bbox=dict(boxstyle='round',fc='w',lw=2,color='r'),va='center')

        
def all_piechart(fig=None):
    plu.setfig(fig)

    nconf = ISCONFIRMED.sum()
    ncand = ISCANDIDATE.sum()
    nfp = ISFP.sum()

    labels = ['Confirmed (%i)' % nconf,'Candidate (%i)' % ncand,
              'False Positive (%i)' % nfp]
    sizes = [nconf,ncand,nfp]
    #explode = (0.05,0.05,0.05)
    explode = (0.,0.1,0.)
    colors = ['g','y','r']

    ax = plt.axes([0.2,0.2,0.6,0.6])

    #ax.pie(sizes,explode=explode,labels=labels,shadow=True,startangle=90)
    ax.pie(sizes,explode=explode,labels=labels,shadow=True)
    ax.axis('equal')

def cand_piechart(fig=None):
    plu.setfig(fig)

    badstar = ISCANDIDATE & ((FPPDATA['error']=='AllWithinRocheError') | \
                             (FPPDATA['error']=='EmptyPopulationError') | \
                             (FPPDATA['error']=='NoStellarPropsError'))
    nophot = ISCANDIDATE & ((FPPDATA['error'] == 'MissingKOIError') | \
                            (FPPDATA['error'] == 'BadPhotometryError'))
    badmcmc = ISCANDIDATE & (FPPDATA['error'] == 'MCMCNotConvergedError')

    companion = ISCANDIDATE & (FPPDATA['error'] == 'DetectedCompanionError')

    offtarget = ISCANDIDATE & HASFPP & ~ONTARGET

    good = ISCANDIDATE & HASFPP & ONTARGET

    n_badstar = badstar.sum()
    n_nophot = nophot.sum()
    n_mcmc = badmcmc.sum()
    n_comp = companion.sum()
    n_offtarget = offtarget.sum()
    n_good = good.sum()


    labels = ['Stellar properties (%i)' % n_badstar,
              'Bad/missing photometry (%i)' % n_nophot,
              'MCMC not converged (%i)' % n_mcmc,
              'Transit off target (%i)' % n_offtarget,
              'AO-detected companion (%i)' % n_comp,
              'Calculated FPPs (%i)' % n_good]
    sizes = [n_badstar,n_nophot,n_mcmc,n_offtarget,
             n_comp,n_good]
    ax = plt.axes([0.2,0.2,0.6,0.6])
    explode = [0,0,0,0,0,0.1]

    colors = ['y','c','m','b','r','g']

    #ax.pie(sizes,explode=explode,shadow=True,startangle=90,colors=colors)
    ax.pie(sizes,explode=explode,shadow=True,colors=colors)
    plt.legend(labels,loc='lower right',bbox_to_anchor=[1.,0.0],prop={'size':12})

    ax.axis('equal')


    
def list_badfps():
    data = FPPDATA[OK_FP & ONTARGET & ~PEM]
    badkois = data[(data['fpp'] < 0.01) & (data['rp'] < 10)]['KOI']
    for k in badkois:
        print k,ku.DATA[k]['kepid'],ku.DATA[k]['koi_srad'],data.ix[k,'rp']

def allplots():
    plt.ioff()

    fp_plot()
    plt.savefig('figures/fp_specific.pdf')

    fpphist(annotated=False)
    plt.savefig('figures/fpphist.pdf')
    fpphist()
    plt.savefig('figures/fpphist_annotated.pdf')

    fpp_of_b()
    plt.savefig('figures/fpp_of_b.pdf')

    goodcandidate_summaryplot(showcc=False)
    plt.savefig('figures/goodcandidate_summary.pdf')

    knownfp_summaryplot()
    plt.savefig('figures/knownfp_summary.pdf')

    knownfp_ontarget_summaryplot()
    plt.savefig('figures/knownfp_ontarget_summary.pdf')

    confirmed_summaryplot()
    plt.savefig('figures/confirmed_summary.pdf')

    cand_summaryplot()
    plt.savefig('figures/cand_summary_AO.pdf')
    cand_summaryplot(showcc=False)
    plt.savefig('figures/cand_summary.pdf')

    fpp_summaryplot(nbins=12)
    plt.savefig('figures/all_summary.pdf')

    all_piechart()
    plt.savefig('figures/pie_all.pdf')

    cand_piechart()
    plt.savefig('figures/pie_cand.pdf')

    plt.ion()

def count_validated():
    val = FPPDATA['fpp'] < 0.01
    print '%i with fpp < 0.01' % val.sum()
    print '%i do not have good centroid data' % (val & ~HASCENTROID).sum()
    print '%i have centroids inconsistent with target' % (val & ~ONTARGET).sum()
    print '%i are known FPs' % (val & ISFP).sum()
    print '%i are previously confirmed planets' % (val & ISCONFIRMED).sum()
    print '%i new validations' % (val & OK_CANDIDATE & ~ISCONFIRMED).sum()

    
