import urllib.request
import zipfile
import pandas as pd
import re
import os
import sys


def URL_DL_ZIP(targetzip, targetdir, url):
    # Saving Zip file
    urllib.request.urlretrieve(url, targetzip)

    # Unzipping file
    with zipfile.ZipFile(targetzip, 'r') as zip_ref:
        zip_ref.extractall(targetdir)
        # Get list of files names in zip
        files = zip_ref.namelist()
        
    # Return list of locations of extracted files   
    file_locs = [] 
    for file in files:
        file_locs.append(targetdir + file)
    
    return file_locs

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
    
def NYFedSCE_load(targetdir):
    # Saves consumer expectation data as DF
    targetexcel = targetdir + 'NYFedSCE_2017-present_data.xlsx'
    url = 'https://www.newyorkfed.org/medialibrary/interactives/sce/sce/downloads/data/frbny-sce-public-microdata-complete-17-present.xlsx'

    # Saving excel
    urllib.request.urlretrieve(url, targetexcel)
    
    # Read as dataframe
    df = pd.read_excel(targetexcel, skiprows=1)
    
    return df

def Livingston_load(targetdir):
    # Saves academic expectations as DF
    targetexcel = targetdir + 'Livingston_allmicrodata.xlsx'
    url = 'https://www.philadelphiafed.org/-/media/research-and-data/real-time-center/livingston-survey/historical-data/individualdata.xlsx?la=en'

    # Saving excel
    urllib.request.urlretrieve(url, targetexcel)
    
    # Read as dataframe
    df = pd.read_excel(targetexcel)
    
    return df

def BLS_CES_load_qtr(targetdir, year, qtr, subset):
    
    # Retrieve URL and set target zip
    yy = str(year)[-2:]
    url = f'https://www.bls.gov/cex/pumd/data/stata/intrvw{yy}.zip'
    targetzip = targetdir + f'BLS_CES_{year}.zip'
    
    # Retrieve files
    CES_file_locs = URL_DL_ZIP(targetzip, targetdir, url) 
    
    # create df with relevant .dta files
    target_len = len(targetdir + 'intrvw19/intrvw19/')
    inter_df = pd.DataFrame
    df = pd.DataFrame
    for file in CES_file_locs:

        # Use only .dta files that match subset arg
        if ((file[:(target_len)] == (targetdir + 'intrvw19/intrvw19/'))
            & (file[-3:] == 'dta')
            & (file[target_len:target_len+4] == str(subset))
            & (file[-5] == str(qtr))):
            print(file)
            # Read into pandas df    
            df = pd.read_stata(
                file,
                columns=None)
            
            # Include source data
            df['report_year'] = [int(file[target_len+4:target_len+6]) for i in range(df.shape[0])]
            df['report_qtr'] = [int(file[-5]) if RepresentsInt(qtr) else 5 for i in range(df.shape[0])]
            break


    return df



def UMich_load():
    # Saves UMich consumer expec. data as df
    targetcsv = 'data/external/UMich_Consumers.csv'
    
    # Read as dataframe
    df = pd.read_csv(targetcsv)
    
    return df

def SCF_load_stata(targetdir, year, series):
    ## Saves SCF data from 1989 as df
    # Set target zip file and relevant url
    targetzip = targetdir + f'SCF{year}_data_public.zip'
    panel_string = 'p' if ((int(year)%3) != 0) else ''
    year = str(year)[-2:] if year < 2002 else year
    url = f'https://www.federalreserve.gov/econres/files/scf{year}{panel_string}s.zip'
        
    # Return list of locations of extracted files   
    SCF_file_locs = URL_DL_ZIP(targetzip, targetdir, url) 
        
    # Read into pandas df    
    SCF_data = pd.read_stata(
        SCF_file_locs[0],
        #insert a list of variables or 'None' to get all
        columns=series)
    
    return SCF_data

def SHED_load_stata(targetdir, year, series, month_supp):
    ## Saves SHED data from 2013 as df
    # Set target zip file and relevant url
    targetzip = targetdir + f'SHED{year}_data_public.zip'
    if (month_supp == 7) & (int(year) == 2020):
        supp = True
        url = f'https://www.federalreserve.gov/consumerscommunities/files/SHED_public_use_data_2019_supplemental_survey_sept_2020_(STATA).zip'
    elif (month_supp == 4) & (int(year) == 2020):
        supp = True
        url = f'https://www.federalreserve.gov/consumerscommunities/files/SHED_public_use_data_2019_supplemental_survey_april_2020_(STATA).zip'
    else:
        supp = False
        url = f'https://www.federalreserve.gov/consumerscommunities/files/SHED_public_use_data_{year}_(STATA).zip'
        
    # Return list of locations of extracted files   
    SHED_file_locs = URL_DL_ZIP(targetzip, targetdir, url) 
        
    # Read into pandas df    
    SHED_data = pd.read_stata(
        SHED_file_locs[0],
        #insert a list of variables or 'None' to get all
        columns=series)
    
    # Add month/year data
    SHED_data['year'] = [int(year) for i in range(SHED_data.shape[0])]
    if supp == True:
        SHED_data['month'] = [month_supp for i in range(SHED_data.shape[0])]
        SHED_data['supp'] = [1 for i in range(SHED_data.shape[0])]
    else:
        ## for non-supplement data surveys conducted in oct/nov.
        SHED_data['month'] = [11 for i in range(SHED_data.shape[0])]
        SHED_data['supp'] = [0 for i in range(SHED_data.shape[0])]
        

        
    return SHED_data



def CPS_raw(targetdir, list_of_mmmyyyy, series):
    
    ### Retrieves monthly CPS data from 1998 on
    
    
    # Begin stack of data with series of intereest
    dfs=[]
    
    # loops through data to get individual dataframes
    for mmmyyyy in list_of_mmmyyyy:
        # converts input to lowercase
        mmmyyyy = mmmyyyy.lower()
        
        ## Retrieves variables of interest for given month
        dd_sel_var = CPS_vars(targetdir, mmmyyyy, series)
            
        # Saves CPS data for given month
        targetfile = targetdir + f'CPS-{mmmyyyy}.zip'

        # URL for given month
        url = f'https://www2.census.gov/programs-surveys/cps/datasets/{mmmyyyy[-4:]}/basic/{mmmyyyy[0:3] + mmmyyyy[5:7]}pub.zip'

        # Extract files and return locations  
        file_locs = URL_DL_ZIP(targetfile, targetdir, url)
        
                
                

        # Convert raw data into a list of tuples
        data_final = [tuple
                      (
                          (-1
                           # Account for insertion of chars in .dat file 
                           if 
                           (
                               not(RepresentsInt(line[i[1]:i[2]]))
                           )
                           else int(line[i[1]:i[2]])
                              
                          )
                          for i in dd_sel_var
                      ) 
                      for line in open(file_locs[0], 'rb')]

        # Convert to pandas dataframe, add variable ids as heading
        CPS_df = pd.DataFrame(data_final, columns=[v[0] for v in dd_sel_var])
            
        dfs.append(CPS_df)
    
    # Merge stack
    df = pd.concat(dfs)
     
    return df

def CPS_vars(targetdir, mmmyyyy, series):
    
    ### Retrieves variables of interest from 1998 on
    
    ## Download relevant data dictionary 
    # Parsing out mmmyyyy for use
    yyyy = int(mmmyyyy[-4:])
    mmmyy = mmmyyyy[0:3] + mmmyyyy[5:7]
    mmm = mmmyyyy[0:3]
    monthdict = {'jan': 1, 
                 'feb': 2, 
                 'mar': 3, 
                 'apr': 4, 
                 'may': 5,
                 'jun': 6,
                 'jul': 7,
                 'aug': 8,
                 'sep': 9,
                 'oct': 10,
                 'nov': 11,
                 'dec': 12}
    # Relevant URLs
    if yyyy == 2020: 
        url = 'https://www2.census.gov/programs-surveys/cps/datasets/2020/basic/2020_Basic_CPS_Public_Use_Record_Layout_plus_IO_Code_list.txt'
    elif yyyy > 2016:
        url = 'https://www2.census.gov/programs-surveys/cps/datasets/2017/basic/January_2017_Record_Layout.txt'
    elif yyyy > 2014:
        url = 'https://www2.census.gov/programs-surveys/cps/datasets/2015/basic/January_2015_Record_Layout.txt'
    elif yyyy > 2013:
        url = 'https://www2.census.gov/programs-surveys/cps/datasets/2014/basic/January_2014_Record_Layout.txt'
    elif yyyy > 2012:
        url = 'https://www2.census.gov/programs-surveys/cps/datasets/2013/basic/January_2013_Record_Layout.txt'
    elif (yyyy == 2012) & (monthdict[mmm] > 4):
        url = 'https://www2.census.gov/programs-surveys/cps/datasets/2012/basic/may12dd.txt'
    elif yyyy > 2009:
        url = 'https://www2.census.gov/programs-surveys/cps/datasets/2010/basic/jan10dd.txt'
    elif yyyy > 2008:
        url = 'https://www2.census.gov/programs-surveys/cps/datasets/2009/basic/jan09dd.txt'
    elif yyyy > 2006:
        url = 'https://www2.census.gov/programs-surveys/cps/datasets/2007/basic/jan07dd.txt'
    elif (((yyyy == 2005) & (monthdict[mmm] > 7))
          | yyyy > 2005):
        url = 'https://www2.census.gov/programs-surveys/cps/datasets/2005/basic/augnov05dd.txt'
    elif ((yyyy == 2004) & (monthdict[mmm] > 4)
         | (yyyy == 2005) & (monthdict[mmm] < 8)):
        url = 'https://www2.census.gov/programs-surveys/cps/datasets/2004/basic/may04dd.txt'
    elif yyyy > 2002:
        url = 'https://www2.census.gov/programs-surveys/cps/datasets/2003/basic/jan03dd.txt'
    elif yyyy > 1997:
        url = 'https://www2.census.gov/programs-surveys/cps/datasets/2002/basic/jan98dd.asc'
        
    # Create file
    
    dd_file = targetdir + f'{yyyy}_{mmm}_CPS_DataDict.txt'
    urllib.request.urlretrieve(url, dd_file)
    
    ## Open file and parse out relevant lines  
    
    dd_full = open(dd_file, 'r', encoding='iso-8859-1').read()
    if yyyy > 2008:
        p = re.compile('\n(\w+)\s+(\d+)\s+(.*?)(?!\s\d)\s+(\d\d*).*?(\d\d+)')
    elif yyyy > 2002:
        p = re.compile('\n(\w+)\s+(\d+)\s+(.*?)\s+\((\d\d*).*?(\d\d+)\)')
    else:
        p = re.compile('\n[D]\s+(\w*)\s+(\d*)\s+(\d*)\n[T]\s(.*?)\n')
    
        
    data = p.findall(dd_full)
    
    ## Retrive list of relevant vars based on series arg
    series_final = []
    if (series == None) & (yyyy > 2002):
        # Import all vars as pd.df
        df_vars = pd.DataFrame(data, 
                               columns = ['name', 
                                          'size', 
                                          'description', 
                                          'loc_range_min', 
                                          'loc_range_max'])
        # Clean df and convert into list
        df_vars = df_vars[
            (df_vars.name != 'FILLER') 
            & (df_vars.name != 'PADDING')]
        df_vars['name'] = df_vars['name'].str.strip()
        
        series_final = df_vars['name'].tolist()
    
    elif series == None:
         # Import all vars as pd.df
        df_vars = pd.DataFrame(data, 
                               columns = ['name',
                                          'size', 
                                          'loc_range_min',
                                          'description'])
        # Clean df and convert into list
        df_vars = df_vars[
            (df_vars.name != 'FILLER') 
            & (df_vars.name != 'PADDING')]
        df_vars['name'] = df_vars['name'].str.strip()
        
        series_final = df_vars['name'].tolist()      
        
    else:
        # Import only series vars
        for i in series:
            series_final.append(i.upper())
    
    ## Create list of tuples with vars and locs to retrieve from .dat
    dd_sel_var = []
    adj_above_2002 = -1 if yyyy > 2002 else 0
    adj_below_2003 = -1 if yyyy < 2003 else 0
    for i in p.findall(dd_full):
        if yyyy < 2003:
            loc = [int(i[2]), int(i[2]) + int(i[1])]
        else:
            loc = [int(i[3]), int(i[4])]
            
        
        if i[0] in series_final:
            ## Account for certain data dict nits
            if loc[0] == loc[1]:
                dd_sel_var.append((i[0], 
                                   loc[0], 
                                   loc[1]+2))
            else:
                dd_sel_var.append((i[0], 
                                   loc[0]+(adj_below_2003)+(adj_above_2002), 
                                   loc[1]+(adj_below_2003)))
                    
                                  
                                  
    return dd_sel_var

# UNUSED FUNCS
def NBER_CPS_vars(targetdir):
    
    # Saves CPS vars from NBER as TXT and into pandas.df
    targetfile = targetdir + 'NBER_CPS_Vars.txt'
    url = 'https://data.nber.org/data/progs/cps-basic/cpsbjan2015.dct'
    
    # Saving file
    urllib.request.urlretrieve(url, targetfile)
    
    # Read into df 
    df = pd.read_csv(targetfile,
                    sep="\s+",
                    nrows=387,
                    skiprows=6, 
                    header=None,
                    )
    
    # Clean up df to remove extra info, label and prep for comparison
    df.drop([df.columns[0], df.columns[1]], axis=1, inplace=True)
    df.columns = ['type', 'var', 'limit', 'description']
    df['var'] = [x.upper() for x in df['var']]
    
    return df

def UI_demo_data_to_df(targetdir):
    # Saves UI demographic data from DOL as df
    targetcsv = targetdir + 'UI_data.csv'
    url = 'https://oui.doleta.gov/unemploy/csv/ar203.csv'

    # Saving csv
    urllib.request.urlretrieve(url, targetcsv)
    
    # Read as dataframe
    df = pd.read_csv(targetcsv)
    
    return df

def SCF2019_weights_load(targetdir):
    # Saves SCF2019 data revised weights as stata file 
    targetzip = targetdir + 'SCF2019_data_public_weights.zip'
    url = 'https://www.federalreserve.gov/econres/files/scf2019rw1s.zip'

    # Extract files and return locations  
    SCF_file_locs = URL_DL_ZIP(targetzip, targetdir, url)
    
    # Read in file to dataframe    
    SCF2019_weights = pd.read_stata(
        SCF_file_locs[0])
    
    return SCF2019_weights

