import urllib.request
import zipfile
import pandas as pd
import re

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



def SCF2019_load_stata(targetdir, series):
    #insert a list of variables or 'None' to get all
  
    # Saves SCF2019 data as stata file
    targetzip = targetdir + 'SCF2019_data_public.zip'

    url = 'https://www.federalreserve.gov/econres/files/scf2019s.zip'
        
    # Return list of locations of extracted files   
    SCF_file_locs = URL_DL_ZIP(targetzip, targetdir, url) 
        
    # Read into pandas df    
    SCF2019_data = pd.read_stata(
        SCF_file_locs[0],
        columns=series)
    
    return SCF2019_data



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

def CPS_raw(targetdir, list_of_mmmyy, series):
    
    ## Retrieves variables of interest
    dd_sel_var = CPS_vars(targetdir, series)
    
    
    ## Stack together data with series of intereest
    dfs=[]
    
    # loops through data to get individual dataframes
    for mmmyy in list_of_mmmyy:
        # converts input to lowercase
        mmmyy = mmmyy.lower()
            
        # Saves CPS data for given month
        targetfile = targetdir + f'CPS-{mmmyy}.zip'

        # URL for given month
        url = f'https://www2.census.gov/programs-surveys/cps/datasets/2000/basic/{mmmyy}pub.zip'

        # Extract files and return locations  
        file_locs = URL_DL_ZIP(targetfile, targetdir, url)

        # Convert raw data into a list of tuples
        data_final = [tuple(int(line[i[1]:i[2]]) for i in dd_sel_var) 
                for line in open(file_locs[0], 'rb')]

        # Convert to pandas dataframe, add variable ids as heading
        CPS_df = pd.DataFrame(data_final, columns=[v[0] for v in dd_sel_var])
            
        dfs.append(CPS_df)
    
    df = pd.concat(dfs)
     
    return df

def CPS_vars(targetdir, series):
    
    ## Retrieves variables of interest
    # Download and open data dictionary 
    url = 'https://www2.census.gov/programs-surveys/cps/datasets/2020/basic/2020_Basic_CPS_Public_Use_Record_Layout_plus_IO_Code_list.txt'
    dd_file = targetdir + '2020_01_CPS_DataDict.txt'
    urllib.request.urlretrieve(url, dd_file)
    dd_full = open(dd_file, 'r', encoding='iso-8859-1').read()

    # Regular expression finds rows with variable location details
    p = re.compile('\n(\w+)\s+(\d+)\s+(.*?)\t+.*?(\d\d*).*?(\d\d+)')
    data = p.findall(dd_full)
    
    series_final = []
    if series == None:
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
        
        series_final = df_vars['name'].tolist()
        
    else:
        # Import only series vars
        for i in series:
            series_final.append(i.upper())

    # Keep adjusted results for series of interest
    dd_sel_var = [(i[0], int(i[3])-1, int(i[4])) 
                  for i in p.findall(dd_full) if i[0] in series_final]

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


