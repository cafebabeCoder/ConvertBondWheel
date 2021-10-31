# 筛选当日有效样本
def selByAmt(obj, date, other=None, noCrazy=True):
    t = obj.DB['Amt'].loc[date] > 0
    t *= obj.DB['Amt'].loc[date] < (obj.DB['Close'].loc[date] * obj.DB['Outstanding'].loc[date] / 100.0)
    
    if other:
        for k, v in other.iteritems():
            t *= obj.DB[k].loc[date].between(v[0], v[1])
            
    codes = list(t[t].index)
    return codes

# 目标区间所有成交的样本
def selByAmtPq(obj, start, end):
    t = obj.DB['Amt'].loc[start:end].sum() > 0            
    codes = list(t[t].index)
    return codes

# 提取当日有效样本的涨跌幅
def getCBReturn(date, codes=None, obj=None):
    
    if not obj:
        obj = cb.cb_data()
    if not codes:
        codes = selByAmt(obj, date)
    
    loc = obj.DB['Amt'].index.get_loc(date)
    
    return 100.0 * (obj.DB['Close'][codes].iloc[loc] / obj.DB['Close'][codes].iloc[loc-1] - 1.0)

# 得到转债对应的正股代码
def getUnderlyingCodeTable(codes):
    '''
    输入转债代码list
    返回正股代码list
    '''
    sql = '''select a.s_info_windcode cbCode,b.s_info_windcode underlyingCode
    from winddf.ccbondissuance a,winddf.asharedescription b
    where a.s_info_compcode = b.s_info_compcode and
    length(a.s_info_windcode) = 9 and
    substr(a.s_info_windcode,8,2) in ('SZ','SH') and
    substr(a.s_info_windcode,1,3) not in ('137','117') '''
    con = login(1) # 为我们的万得数据链接对象
    ret = pd.read_sql(sql, con, index_col='CBCODE')
    return  ret.loc[codes]

# 返回正股其对应的行业
def cbInd(codes):
    dfUd = getUnderlyingCodeTable(codes)
    sql = '''select a.s_info_windcode as udCode,
    b.industriesname indName
    from 
    winddf.ashareindustriesclasscitics a,
    winddf.ashareindustriescode b
    where substr(a.citics_ind_code,1,4) = substr(b.industriescode,1,4) and
    b.levelnum = '2' and
    a.cur_sign = '1' and
    a.s_info_windcode in ({_codes})
    '''.format(_codes = rsJoin(list(set(dfUd['UNDERLYINGCODE']))))
    con = login(1) # 为我们的万得数据链接对象
    dfInd = pd.read_sql(sql, con, index_col='UDCODE')
    dfUd['Ind'] = dfUd['UNDERLYINGCODE'].apply(lambda x: dfInd.loc[x, 'INDNAME'] if x in dfInd.index else None)
    return dfUd['Ind']

def factorInd(codes, cbInd=None):
    if not cbInd:        
        cbInd = pd.DataFrame({'ind':_cbInd(codes)})
    cbInd = pd.merge(cbInd, indCls, left_on='ind', right_index=True) 
    dfRet = pd.DataFrame(index=codes, columns=set(cbInd['ind']))
    for c in dfRet.columns:
        tempCodes = cbInd.loc[cbInd['ind'].apply(lambda x:x.encode('gbk')) == c.encode('gbk')].index
        dfRet.loc[tempCodes, c] = 1.0
    return dfRet.fillna(0)


# 处理异常值
def factorSize_cb_outstanding(codes, start, end, obj=None):
    
    if not obj:
        obj = cb.cb_data()
    
    ost_mv = obj.DB['Close'].loc[start:end, codes] * obj.DB['Outstanding'].loc[start:end, codes] / 100.0
    
    return ost_mv
def rankCV(df):
    rk = df.rank(axis=1, pct=True)
    return (rk - 0.5).div(rk.std(axis=1), axis='rows')

# 单因子测试
def oneFactorReg(start, end, dfFactor, factorName='ToBeTest',dfFctInd=None, obj=None):
    
    if not obj:
        obj = cb.cb_data()
    if not dfFctInd:
        codes = selByAmtPq(obj, start, end)
        codes = list(set(codes).intersection(list(dfFactor.columns)))
        dfFctInd = factorInd(codes)
    
    arrDates = list(obj.DB['Amt'].loc[start:end].index)[1:]
    lr = LinearRegression(fit_intercept=True)
    dfRet = pd.DataFrame(index=arrDates, columns=['One'] + list(dfFctInd.columns) + [factorName, 't','score'])
    dfCBMV = factorSize_cb_outstanding(codes, start, end, obj)
    
    for date in arrDates:
        print date
        
        tCodes = selByAmt(obj, date)
        srsReturn = getCBReturn(date, tCodes, obj)
        
        dfX = pd.DataFrame(index=tCodes)        
        dfX[list(dfFctInd.columns)] = dfFctInd
        
        dfX[factorName] = dfFactor.loc[date]
        dfX.dropna(inplace=True)
        idx = dfX.index
        
        arrW = pd.np.sqrt(dfCBMV.loc[date, idx])
        arrW /= arrW.sum()
        
        lr.fit(dfX.loc[:,:], srsReturn[idx], arrW)
        
        dfRet.loc[date,list(dfFctInd.columns) + [factorName]] = lr.coef_
        dfRet.loc[date, 'One'] = lr.intercept_
        dfRet.loc[date, 't'] = t_test(lr, dfX.loc[:,:], srsReturn[idx])
        
        dfRet.loc[date, 'score'] = lr.score(dfX.loc[:,:], srsReturn[idx], arrW)

    
    print pd.np.abs(dfRet['t']).mean()
    print pd.np.abs(dfRet['score']).mean()
    return dfRet

# 
def t_test(lr, x, y):
    
    n = len(x) * 1.0
    
    predY = lr.predict(x)
    e2 = sum((predY - y) ** 2)
    varX = pd.np.var(x) * n
    
    t = lr.coef_ * pd.np.sqrt(varX) / pd.np.sqrt(e2 / n)
    
    return t[-1]    