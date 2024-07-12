def get_variable_from_dataset(ds):
    '''
        Extract the target variable from the dataset. Convert to target units
        
            Parameters
                ds: xarray dataset
            Returns
                da: subsetted dataArray in
    '''
    for name in ['z' , 'Z' , 'gh' , 'z500' , 'Z500']:
        if name in list(ds.keys()):
            break
    da = ds[name]
        
    
    return da
    raise RuntimeError("Couldn't find a 2-meter temperature variable name")