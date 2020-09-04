import pandas as pd
import hashlib
import numpy as np
import os

def compareTool(wip_file_dir, stock_file_dir, files, info):
    # Input file path A: work in progress (older) --> wip_file_dir

    # Input file path B: stock (newer) --> stock_file_dir

    # Output file path: revisions file
    output_file_dir = stock_file_dir[:stock_file_dir.rfind('stock')] + 'wip'

    # info specified in config.ini
    info = {'advevnts.xlsx':([ "SUBJID", "STRTDT_1", "STOPDT_1", "AE_1", "AE_2" ],
        ["SAE_1",  "SAE_2", "SEV_1", "SEV_2", "REL_1", "ONGO_1"]),
            'conmeds.xlsx':(["SUBJID", "MEDNAME", "STARTDT", 'ENDDT'], ["INDIC", "ROUTE", "ONGOING"])}

    # files specified in the config.ini file --> files
    wip_file_list = []
    for file_name in files:
        wip_file_list.append(os.path.join(wip_file_dir, file_name))
        
    stock_file_list = []
    for file_name in files:
        stock_file_list.append(os.path.join(stock_file_dir, file_name))

    wip_df_list = []
    for wip_file in wip_file_list:
        wip_df_list.append(pd.read_excel(wip_file).astype(str))

    stock_df_list = []
    for stock_file in stock_file_list:
        stock_df_list.append(pd.read_excel(stock_file).astype(str))

    # Remove rows with column Compare='delete' and remove column compare
    new_list = []
    for wip_df in wip_df_list:
        wip_df = wip_df[wip_df['Compare'] != 'delete']
        wip_df.drop(['Compare'], inplace=True, axis=1)
        new_list.append(wip_df)
    wip_df_list = new_list

    # creating wip (A) file key column

    # create a list with the md5 key of each row based on the keys specificed in the config
    for wip_df, file in zip(wip_df_list, info.keys()):
        md5_list = []
        keys = info[file][0]
        for r in range(0, wip_df.shape[0]):
            hash_key = hashlib.md5()
            hash_string = ""
            for key in keys:
                hash_string += wip_df.iloc[r][key]
            hash_key.update(hash_string.encode('utf-8'))
            md5 = hash_key.hexdigest()
            md5_list.append(md5)
        wip_df['Key'] = md5_list

    # creating stock (B) file key column

    for stock_df, file in zip(stock_df_list, info.keys()):
        md5_list = []
        keys = info[file][0]
        for r in range(0, stock_df.shape[0]):
            hash_key = hashlib.md5()
            hash_string = ""
            for key in keys:
                hash_string += stock_df.iloc[r][key]
            hash_key.update(hash_string.encode('utf-8'))
            md5 = hash_key.hexdigest()
            md5_list.append(md5)
        stock_df['Key'] = md5_list

    # comparison
    for wip_df, stock_df, file in zip(wip_df_list, stock_df_list, info.keys()):
        contents = info[file][1]
        included_keys = []
        r_df = pd.DataFrame()
        for r in range(0, wip_df.shape[0]):

            # wip data
            wipl = wip_df.iloc[r].to_frame().T

            # key
            key = wipl.iloc[0]['Key']
            included_keys.append(key)

            # stock data
            stockl = stock_df[stock_df['Key'] == key]

            # comment
            comment = wip_df.iloc[r]['Comments']

            # result data
            r_data = wipl
            r_data.iloc[0]['Comments'] = comment
            cname = contents + ['Compare', 'Comments']
            r_data = r_data.reindex(columns=cname)

            # delete when key not found in stock file
            if key not in stock_df['Key'].tolist():
                #print('deleted')
                # update "Compare" value of result data
                r_data.iloc[0, r_data.columns.get_loc('Compare')] = 'deleted'
                # merge result data with result df
                r_df = pd.concat([r_df, r_data])
            else:
                # series
                wips = wipl.iloc[0]
                stocks = stockl.iloc[0]
                
                # list of "CONTENTS" data specified in config
                wip_contents = []
                for i in range(0, len(wips)):
                    if wips.index.to_list()[i] in contents:
                        wip_contents.append(wips.iloc[i])
                stock_contents = []
                for i in range(0, len(stocks)):
                    if stocks.index.to_list()[i] in contents:
                        stock_contents.append(stocks.iloc[i])

                # contents remain unchanged
                if wip_contents == stock_contents:
                    #print('nochange')
                    r_data.iloc[0, r_data.columns.get_loc('Compare')] = 'nochange'
                    r_df = pd.concat([r_df, r_data])

                # contents changed --> prechange and postchange data
                else:
                    #print('changed')
                    # pre change data
                    pre_r_data = r_data.copy()
                    pre_r_data.iloc[0, r_data.columns.get_loc('Compare')] = 'change-pre'
                    r_df = pd.concat([r_df, pre_r_data])
                    # post change data
                    post_r_data = r_data.copy()
                    # update data to the post 
                    for column_name in contents:
                        post_r_data.iloc[0, post_r_data.columns.get_loc(column_name)] = stockl.iloc[0][column_name]
                    post_r_data.iloc[0, r_data.columns.get_loc('Compare')] = 'change-post'
                    r_df = pd.concat([r_df, post_r_data])
        added_keys = np.setdiff1d(stock_df['Key'].tolist(), included_keys).tolist()
        for new_key in added_keys:
            new_data = stock_df[stock_df['Key'] == new_key]
            # result data
            r_data = new_data
            r_data = r_data.reindex(columns=cname)
            r_data.iloc[0, r_data.columns.get_loc('Compare')] = 'added'
            r_df = pd.concat([r_df, r_data])
        r_df.reset_index(drop=True, inplace=True)
        r_df.to_excel(os.path.join(output_file_dir, file), index=False)
