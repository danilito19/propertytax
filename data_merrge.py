import pandas as pd
import csv
import numpy as np 
import matplotlib.pyplot as plt
import pylab
import os
import glob
import Levenshtein as lev


def merge_data(appeals_path, tax_path, sales_path, community_path, year, outpath):

    tax = pd.read_csv(tax_path,index_col=None, header=0)
    print "tax file shape ", tax.shape

    tax = tax[tax['BillYear'] == year]
    print "tax df after keeping by year is ", tax.shape

    appeals = pd.read_csv(appeals_path,index_col=None, header=0)
    print "appeals file shape ", appeals.shape

    appeals['PIN_pretty'] = appeals['pin'].apply(lambda x: "0" + str(x) if len(str(x)) == 13 else x)
    tax['PIN_pretty'] = tax['PIN'].apply(lambda x: "0" + str(x) if len(str(x)) == 13 else x)

    tax = tax.drop_duplicates('PIN_pretty')
    print "tax df after dropping duplicate PIN14 is  ", tax.shape

    #should be 0 with 13 digit
    print appeals[appeals['PIN_pretty'].apply(lambda x: len(str(x))) == 13]

    appeals["appeal"] = 1
    tax_appeals = appeals.merge(tax, on='PIN_pretty', how='inner')

    print "merging tax and appeals give shape ", tax_appeals.shape

    tax_appeals["clean_lawyer"] = tax_appeals["attorneytaxrep"].str.replace("\.|\s|,", "")
    tax_appeals["clean_owner"] = tax_appeals["TaxpayerName"].str.replace("\.|\s|,", "")
    tax_appeals['self_represent'] = 0

    ## have to make na blank
    print "making lawyer and owner empty string for APPEALS only"

    print tax_appeals[tax_appeals['appeal'] == 1][['clean_lawyer', 'clean_owner']].isnull().sum()
    tax_appeals.clean_lawyer  = np.where((tax_appeals.clean_lawyer.isnull()) & (tax_appeals.appeal == 1), "", tax_appeals.clean_lawyer)
    tax_appeals.clean_owner  = np.where((tax_appeals.clean_owner.isnull()) & (tax_appeals.appeal == 1), "", tax_appeals.clean_owner)
    print tax_appeals[tax_appeals['appeal'] == 1][['clean_lawyer', 'clean_owner']].isnull().sum()

    empty_lawyers = tax_appeals[(tax_appeals["clean_lawyer"] == "") & (tax_appeals.appeal == 1)].shape[0]
    print "number of rows with empty lawyers in appeals only ", empty_lawyers

    print "will make empty lawyer in appeals == self.represent = 1"
    tax_appeals.ix[(tax_appeals.clean_lawyer=="") & (tax_appeals.appeal==1), 'self_represent'] = 1

    print "counts of self_represent"
    print tax_appeals["self_represent"].value_counts()

    print "just out of curiosity, how many empty owners there are"
    print tax_appeals[tax_appeals["clean_owner"] == ""].shape

    for row in range(len(tax_appeals)):
        #print result.iloc[row]['clean_lawyer'], result.iloc[row]['clean_owner']
        lawyer = tax_appeals.iloc[row]['clean_lawyer']
        owner = tax_appeals.iloc[row]['clean_owner']
        di = lev.ratio(lawyer, owner)
        if di > 0.79:
            tax_appeals.loc[row, 'self_represent'] = 1

    print "counts of self_represent"
    print tax_appeals['self_represent'].value_counts()

    ## now to outer join
    tax_appeals = tax_appeals.merge(tax, on='PIN_pretty', how='outer')


    print "loading and merging with sales data"
    sales = pd.read_csv(sales_path,index_col=None, header=0)
    print "sales file shape ", sales.shape

    sales = sales.drop_duplicates('pin')
    sales["sale"] = 1

    sales['PIN_pretty'] = sales['pin'].apply(lambda x: "0" + str(x) if len(str(x)) == 13 else x)

    tax_appeals_sale = tax_appeals.merge(sales, on = "PIN_pretty", how = "outer")
    print "shape of tax appeals sales df", tax_appeals_sale.shape

    #make pin10 a string 
    tax_appeals_sale['pin10'] = tax_appeals_sale['pin10'].apply(lambda x: str(x)[0:10])

    tax_appeals_sale['pin10'] = np.where(tax_appeals_sale['pin10'] == 'nan', tax_appeals_sale['PIN_pretty'], tax_appeals_sale['pin10'])
    tax_appeals_sale['pin10'] = tax_appeals_sale['pin10'].apply(lambda x: str(x)[0:10])

    print "loading community file"
    community = pd.read_csv(community_path,index_col=None, header=0)
    print "community file shape ", community.shape

    community = community.drop_duplicates('pin10')
    community['pin10'] = community['pin10'].apply(lambda x: "0" + str(x) if len(str(x)) == 9 else str(x))
    
    community['PIN_pretty'] = community['pin14'].apply(lambda x: "0" + str(x) if len(str(x)) == 13 else x)

    aptaxsalecom = tax_appeals_sale.merge(community, on='pin10', how='outer')

    aptaxsalecom.PIN_pretty_x = np.where(aptaxsalecom.PIN_pretty_x.isnull(), aptaxsalecom.PIN_pretty_y, aptaxsalecom.PIN_pretty_x)

    print 'final merge is of shape ', aptaxsalecom.shape

    ### DROP ALL X EXCEPT PIN PRETTY X and keep all Y
    to_drop = ["Unnamed: 0_x",
    "Unnamed: 0_y",
    "Unnamed: 0_x",
    "paste3"
    "SegmentCode_x",
    "PIN_pretty_y",
    "PIN_x",
    "pin14",
    "area_x"
    "classification_x",
    "PIN_x",
    "pin_x",
    "Volume_x",
    "Classification_x",
    "TaxpayerName_x",
    "TaxpayerMailingAddress_x",
    "TaxpayerMailingCity_x",
    "TaxpayerMailingState_x",
    "TaxpayerMailingZip_x",
    "TaxpayerPropertyHouse_x",
    "TaxpayerPropertyDirection_x",
    "TaxpayerPropertyStreet_x",
    "TaxpayerPropertySuffix_x",
    "TaxpayerPropertyCity_x",
    "TaxpayerPropertyState_x",
    "TaxpayerPropertyZip_x",
    "TaxpayerPropertyTown_x",
    "TaxCode_x",
    "TaxStatus_x",
    "HomeownerExempt_x",
    "SeniorExempt_x",
    "SeniorFreezeExempt_x",
    "LongtimeHomeownersExempt_x",
    "TaxInfoType_x",
    "TaxType_x",
    "TaxYear_x",
    "BillYear_x",
    "AccountStatus_x",
    "BillType_x",
    "SegmentCode2_x",
    "InstallmentNumber1_x",
    "AdjustedAmountDue1_x",
    "TaxAmountDue1_x",
    "RefundTaxAmountDueIndicator1_x",
    "InterestAmountDue1_x",
    "RefundInterestDueIndicator1_x",
    "CostAmountDue1_x",
    "RefundCostDueIndicator1_x",
    "TotalAmountDue1_x",
    "RefundTotalDueIndicator1_x",
    "LastPaymentDate1_x",
    "LastPaymentSource1_x",
    "InstallmentNumber2_x",
    "OriginalTaxDue2_x",
    "AdjustedTaxDue2_x",
    "TaxAmountDue2_x",
    "RefundTaxAmountDueIndicator2_x",
    "InterestAmountDue2_x",
    "RefundInterestDueIndicator2_x",
    "CostAmountDue2_x",
    "RefundCostDueIndicator2_x",
    "TotalAmountDue2_x",
    "RefundTaxDueIndicator2_x",
    "LastPaymentDate2_x",
    "LastPaymentSource2_x",
    "CofENumber_x",
    "PastTaxSaleStatus_x",
    "AssessedValuation_x",
    "EqualizedEvaluation_x",
    "TaxRate_x",
    "RecordCount_x",
    "CondemnationStatus_x",
    "MunicipalAcquisitionStatus_x",
    "AcquisitionStatus_x",
    "ExemptStatus_x",
    "BankruptStatus_x",
    "RefundStatus_x",
    "LastPaymentReceivedAmount1_x",
    "LastPaymentReceivedAmount2_x",
    "EndMarker_x",
    "TaxDueEstimated1_x",
    "ReturningVetExemptionAmount_x",
    "DisabledPersonExemptionAmount_x",
    "DisabledVetExemptionAmount_x",
    "DisabledPersonVetExemptionAmount_x",
    "HomeownerExemptAmount_x",
    "SeniorExemptAmount_x",
    "SeniorFreezeExemptAmount_x",
    "LongtimeHomeownersExemptAmount_x",
    "VeteranExempt_x",
    "totaltax_due_x",
    "totaltax_paid_x",
    "HomeOwner_x",
    "taxyear_x",
    "pin_x",
    "classification",
    "Classification"
    ]
    to_drop = [c for c in to_drop if c in aptaxsalecom.columns]
    aptaxsalecom.drop(to_drop, axis=1, inplace=True)
    print 'final merge AFTER DROPPING COLS ', aptaxsalecom.shape

     ##rename pinprettyx to pin14
    aptaxsalecom.rename(columns={'PIN_pretty_x': 'pin14', "Classification_y": "classification"}, inplace=True)

    aptaxsalecom.to_csv(outpath)

# outpath = "/Users/Dani/Downloads/tax-appeals-sales-community-2015.csv"
# community_path = "/Users/Dani/Downloads/join_T15.csv"
# sales_path = "/Users/Dani/Dropbox/Muni_Finance_Lab/Raw_Data/Sales_Ratios/1st_pass/res15.csv"
# tax_path = "/Users/Dani/Downloads/bills15.csv" 
# appeals_path = "/Users/Dani/Dropbox/Muni_Finance_Lab/Raw_Data/Appeals/appeals15.csv"
# year = 2015

# print 'STARTING YEAR %s' % year
# merge_data(appeals_path, tax_path, sales_path, community_path, year, outpath)

outpath = "/Users/Dani/Downloads/tax-appeals-sales-community-2014.csv"
community_path = "/Users/Dani/Downloads/join_T14.csv"
sales_path = "/Users/Dani/Dropbox/Muni_Finance_Lab/Raw_Data/Sales_Ratios/1st_pass/res14.csv"
tax_path = "/Users/Dani/Downloads/PropTax2014.csv" 
appeals_path = "/Users/Dani/Dropbox/Muni_Finance_Lab/Raw_Data/Appeals/appeals14.csv"
year = 2014

print 'STARTING YEAR %s' % year
merge_data(appeals_path, tax_path, sales_path, community_path, year, outpath)

outpath = "/Users/Dani/Downloads/tax-appeals-sales-community-2013.csv"
community_path = "/Users/Dani/Downloads/join_T13.csv"
sales_path = "/Users/Dani/Dropbox/Muni_Finance_Lab/Raw_Data/Sales_Ratios/1st_pass/res13.csv"
tax_path = "/Users/Dani/Downloads/PropTax2013.csv" 
appeals_path = "/Users/Dani/Dropbox/Muni_Finance_Lab/Raw_Data/Appeals/appeals13.csv"
year = 2013
print 'STARTING YEAR %s' % year
merge_data(appeals_path, tax_path, sales_path, community_path, year, outpath)

# outpath = "/Users/Dani/Downloads/tax-appeals-sales-community-2012.csv"
# community_path = "/Users/Dani/Downloads/join_T12.csv"
# sales_path = "/Users/Dani/Dropbox/Muni_Finance_Lab/Raw_Data/Sales_Ratios/1st_pass/res12.csv"
# tax_path = "/Users/Dani/Downloads/PropTax2012.csv" 
# appeals_path = "/Users/Dani/Dropbox/Muni_Finance_Lab/Raw_Data/Appeals/appeals12.csv"
# year = 2012
# print 'STARTING YEAR %s' % year
# merge_data(appeals_path, tax_path, sales_path, community_path, year, outpath)

# outpath = "/Users/Dani/Downloads/tax-appeals-sales-community-2011.csv"
# community_path = "/Users/Dani/Downloads/join_T11.csv"
# sales_path = "/Users/Dani/Dropbox/Muni_Finance_Lab/Raw_Data/Sales_Ratios/1st_pass/res11.csv"
# tax_path = "/Users/Dani/Downloads/PropTax2011.csv" 
# appeals_path = "/Users/Dani/Dropbox/Muni_Finance_Lab/Raw_Data/Appeals/appeals11.csv"
# year = 2011
# print 'STARTING YEAR %s' % year
# merge_data(appeals_path, tax_path, sales_path, community_path, year, outpath)
