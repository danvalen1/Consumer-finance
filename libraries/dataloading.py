import urllib.request
import zipfile

# Setting data loading targets
targetSCFzip = '../data/extracted/SCF2019_data_public.zip'
targetdir = '../data/extracted/'


def SCF2019_load_stata(targetzip, targetdir):
    # Saves SCF2019 data as stata file

    # URL for SCF 2019 Stata Zip file
    url = 'https://www.federalreserve.gov/econres/files/scf2019rw1s.zip'

    # Saving Zip file
    urllib.request.urlretrieve(url, targetzip)

    # Unzipping file
    with zipfile.ZipFile(targetzip, 'r') as zip_ref:
        zip_ref.extractall(targetdir)
        # Get list of files names in zip
        files = zip_ref.namelist()
        
    # Return list of locations of extracted files   
    SCF_file_locs = [] 
    for file in files:
        SCF_file_locs.append(targetdir + files)
    
    return SCF_file_locs