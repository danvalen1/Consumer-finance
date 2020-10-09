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

def SCF2019_load_stata(targetzip, targetdir):
    # Saves SCF2019 data as stata file

    # URL for SCF 2019 Stata Zip file
    url = 'https://www.federalreserve.gov/econres/files/scf2019s.zip'
        
    # Extract files and return locations  
    SCF_file_locs = URL_DL_ZIP(targetzip, targetdir, url)
    
    return SCF_file_locs


def SCF2019_weights_load(targetzip, targetdir):
    # Saves SCF2019 data weights as stata file

    # URL for SCF 2019 Stata Zip file using revised weights
    url = 'https://www.federalreserve.gov/econres/files/scf2019rw1s.zip'

    # Extract files and return locations  
    SCF_file_locs = URL_DL_ZIP(targetzip, targetdir, url)
    
    return SCF_file_locs

def UI_demo_data_to_df(targetcsv):
    # Saves UI demographic data from DOL as df

    # URL for UI demographic data
    url = 'https://oui.doleta.gov/unemploy/csv/ar203.csv'

    # Saving csv
    urllib.request.urlretrieve(url, targetcsv)
    
    # Read as dataframe
    df = pd.read_csv(targetcsv)
    
    return df


def CPS_Apr2020(targetzip, targetdir, series):
    # Saves CPS Apr 2020 data

    # URL for CPS Apr 2020 survey
    url = 'https://www2.census.gov/programs-surveys/cps/datasets/2020/basic/apr20pub.zip'

    # Extract files and return locations  
    file_locs = URL_DL_ZIP(targetzip, targetdir, url)
    
    # Data dictionary 
    dd_file = '../data/2020_Basic_CPS_Public_Use_Record_Layout_plus_IO_Code_list.txt'
    dd_full = open(dd_file, 'r', encoding='iso-8859-1').read()

    # Regular expression finds rows with variable location details
    p = re.compile('\n(\w+)\s+(\d+)\s+(.*?)\t+.*?(\d\d*).*?(\d\d+)')

    # Keep adjusted results for series of interest
    dd_sel_var = [(i[0], int(i[3])-1, int(i[4])) 
                  for i in p.findall(dd_full) if i[0] in series]

    # Convert raw data into a list of tuples
    data = [tuple(int(line[i[1]:i[2]]) for i in dd_sel_var) 
            for line in open(file_locs[0], 'rb')]

    # Convert to pandas dataframe, add variable ids as heading
    CPS_df = pd.DataFrame(data, columns=[v[0] for v in dd_sel_var])
    
    
    return CPS_df
