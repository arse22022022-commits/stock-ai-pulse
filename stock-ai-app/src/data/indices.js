// European Indices
const IBEX_35 = [
    'ANA.MC', 'BBVA.MC', 'BKT.MC', 'CABK.MC', 'CLNX.MC', 'ACS.MC', 'ELE.MC',
    'ENG.MC', 'FER.MC', 'GRF.MC', 'IAG.MC', 'IBE.MC', 'ITX.MC', 'IDR.MC',
    'COL.MC', 'LOG.MC', 'MAP.MC', 'MEL.MC', 'MTS.MC', 'NTGY.MC', 'RED.MC',
    'REP.MC', 'ROVI.MC', 'SAB.MC', 'SAN.MC', 'SCYR.MC', 'TEF.MC', 'UNI.MC',
    'ACX.MC', 'AENA.MC', 'AMS.MC', 'ANE.MC', 'CIE.MC', 'FDR.MC', 'MRL.MC',
    'PUIG.MC', 'SLR.MC'
];

const CAC_40 = [
    'AC.PA', 'AI.PA', 'AIR.PA', 'ALO.PA', 'BNP.PA', 'ACA.PA', 'CAP.PA',
    'CS.PA', 'DG.PA', 'DSY.PA', 'EDEN.PA', 'EL.PA', 'EN.PA', 'ENGI.PA', 'ERF.PA',
    'GLE.PA', 'HO.PA', 'KER.PA', 'LR.PA', 'MC.PA', 'ML.PA', 'OR.PA', 'ORA.PA',
    'RI.PA', 'RNO.PA', 'SAF.PA', 'SGO.PA', 'SAN.PA', 'STLAP.PA', 'SU.PA', 'SW.PA',
    'TEP.PA', 'TTE.PA', 'VIE.PA', 'VIV.PA', 'WLN.PA', 'PUB.PA', 'URW.AS', 'STM.PA', 'LR.PA'
];

const DAX_40 = [
    'ADS.DE', 'AIR.DE', 'ALV.DE', 'BAS.DE', 'BAYN.DE', 'BEI.DE', 'BMW.DE',
    'BNR.DE', 'CBK.DE', 'CON.DE', '1COV.DE', 'DTG.DE', 'DBK.DE', 'DB1.DE',
    'DPW.DE', 'DTE.DE', 'EOAN.DE', 'FRE.DE', 'HNR1.DE', 'HEI.DE', 'HEN3.DE',
    'IFX.DE', 'LIN.DE', 'MBG.DE', 'MRK.DE', 'MTX.DE', 'MUV2.DE', 'P911.DE', 'PAH3.DE',
    'QIA.DE', 'RHM.DE', 'RWE.DE', 'SAP.DE', 'SRT3.DE', 'SIE.DE', 'ENR.DE', 'SY1.DE',
    'VNA.DE', 'VOW3.DE', 'ZAL.DE'
];

const FTSE_MIB = [
    'A2A.MI', 'AMP.MI', 'AZM.MI', 'BAMI.MI', 'BPE.MI', 'BZU.MI', 'CPR.MI',
    'CNHI.MI', 'DIA.MI', 'ENEL.MI', 'ENI.MI', 'ERG.MI', 'EXO.MI', 'RACE.MI',
    'FBK.MI', 'G.MI', 'HER.MI', 'ISP.MI', 'IG.MI', 'IVG.MI', 'LDO.MI',
    'MB.MI', 'MONC.MI', 'NEXI.MI', 'PIRC.MI', 'PST.MI', 'PRY.MI', 'REC.MI',
    'SPM.MI', 'SRG.MI', 'STLAM.MI', 'TEN.MI', 'TRN.MI', 'UCG.MI', 'UNI.MI',
    'BMED.MI', 'BMPS.MI', 'BPSO.MI', 'BC.MI', 'INW.MI', 'IP.MI', 'LTMC.MI', 'TIT.MI'
];

// US Indices
const DOW_JONES = [
    'MMM', 'AXP', 'AMGN', 'AAPL', 'BA', 'CAT', 'CVX', 'CSCO', 'KO', 'DIS',
    'GS', 'HD', 'HON', 'IBM', 'JNJ', 'JPM', 'MCD', 'MRK',
    'MSFT', 'NKE', 'PG', 'CRM', 'TRV', 'UNH', 'VZ', 'V', 'WMT',
    'AMZN', 'NVDA', 'SHW'
];

const NASDAQ_100 = [
    'AAPL', 'ABNB', 'ADBE', 'ADI', 'ADP', 'ADSK', 'AEP', 'ALGN', 'AMAT', 'AMD',
    'AMGN', 'AMZN', 'ANSS', 'ASML', 'AVGO', 'AZN', 'BIIB', 'BKNG', 'BKR', 'CDNS',
    'CEG', 'CHTR', 'CMCSA', 'COST', 'CPRT', 'CRWD', 'CSCO', 'CSX', 'CTAS', 'CTSH',
    'DDOG', 'DLTR', 'DXCM', 'EA', 'EBAY', 'ENPH', 'EXC', 'FAST', 'META', 'FISV',
    'FTNT', 'GILD', 'GOOG', 'GOOGL', 'HON', 'IDXX', 'ILMN', 'INTU', 'ISRG',
    'JD', 'KDP', 'KHC', 'KLAC', 'LCID', 'LRCX', 'LULU', 'MAR', 'MCHP', 'MDLZ',
    'MELI', 'MNST', 'MRNA', 'MRVL', 'MSFT', 'MU', 'NFLX', 'NVDA', 'NXPI', 'ODFL',
    'ORLY', 'PANW', 'PAYX', 'PCAR', 'PDD', 'PEP', 'PYPL', 'QCOM', 'REGN', 'ROST',
    'SBUX', 'SGEN', 'SIRI', 'SNPS', 'TEAM', 'TMUS', 'TSLA', 'TXN', 'VRSK', 'VRSN',
    'VRTX', 'WBA', 'WDAY', 'XEL', 'ZM', 'ZS', 'GEHC', 'TTD', 'MDB'
];

const SP_100 = [
    'AAPL', 'ABBV', 'ABT', 'ACN', 'ADBE', 'AIG', 'AMD', 'AMGN', 'AMT', 'AMZN',
    'AVGO', 'AXP', 'BA', 'BAC', 'BK', 'BKNG', 'BLK', 'BMY', 'BRK.B', 'C',
    'CAT', 'CHTR', 'CL', 'CMCSA', 'COF', 'COP', 'COST', 'CRM', 'CSCO', 'CVS',
    'CVX', 'DE', 'DHR', 'DIS', 'DOW', 'DUK', 'EMR', 'EXC', 'F', 'FDX',
    'GD', 'GE', 'GILD', 'GM', 'GOOG', 'GOOGL', 'GS', 'HD', 'HON', 'IBM',
    'INTC', 'JNJ', 'JPM', 'KHC', 'KO', 'LIN', 'LLY', 'LMT', 'LOW', 'MA',
    'MCD', 'MDLZ', 'MDT', 'MET', 'META', 'MMM', 'MO', 'MRK', 'MS', 'MSFT',
    'NEE', 'NFLX', 'NKE', 'NVDA', 'ORCL', 'PEP', 'PFE', 'PG', 'PM', 'PYPL',
    'QCOM', 'RTX', 'SBUX', 'SCHW', 'SO', 'SPG', 'T', 'TGT', 'TMO', 'TMUS',
    'TSLA', 'TXN', 'UNH', 'UNP', 'UPS', 'USB', 'V', 'VZ', 'WFC', 'WMT', 'XOM',
    'PLTR', 'UBER', 'PANW', 'BX'
];

// Composite Indices (Deduped)
const EUROPA = [...new Set([...IBEX_35, ...CAC_40, ...DAX_40, ...FTSE_MIB])];
const USA = [...new Set([...DOW_JONES, ...NASDAQ_100, ...SP_100])];

export const INDICES_CONSTITUENTS = {
    'Europa': EUROPA,
    'USA': USA,
    'IBEX 35': IBEX_35,
    'CAC 40': CAC_40,
    'DAX 40': DAX_40,
    'FTSE MIB': FTSE_MIB,
    'DOW JONES': DOW_JONES,
    'NASDAQ 100': NASDAQ_100,
    'S&P 100': SP_100
};
