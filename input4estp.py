#!/usr/bin/env python3
## Made by Joonhyeok Choi 2023.05.25
## Converting modified sparky CEST data to ESTP input format
## python input4estp.py -h

import pandas as pd
import csv
import argparse

parser = argparse.ArgumentParser(description='Converting modified sparky CEST data to ESTP input format')
parser.add_argument('-f', '--file', type=str, help='Input file path', required=True)
parser.add_argument('-o', '--output', type=str, help='Output file path', required=True)
parser.add_argument('-frq', '--frequency', type=float, help='Nitrogen Frequency (MHz) [Default = 80.12]',default='80.12')
parser.add_argument('-sf', '--sat_freq', type=float, help='Saturation Frequncy (Hz) [Default = 15]',default='15')
parser.add_argument('-mix', '--mixing_time', type=float, help='Mixing Time of CEST (s) [Default = 0.4]',default='0.4')
parser.add_argument('-r2a', '--ini_R2a', type=float, help='Initial value of R2a (s) [Default = 25]',default='25')
parser.add_argument('-r2b', '--ini_R2b', type=float, help='Initial value of R2b (s) [Default = 0]',default='0')
parser.add_argument('-dw', '--ini_dw', type=float, help='Initial value of dw (s) [Default = 0]',default='0')
group = parser.add_mutually_exclusive_group()
group.add_argument('-s', '--select_number', nargs='+',type=float, help='Residue number list from the input data list')
group.add_argument('-sn', '--select_name', nargs='+',type=str, help='Residue name list from the input data list')

if __name__ == '__main__':
    args = parser.parse_args()

result_name = args.output

data_ori = pd.read_csv(filepath_or_buffer=args.file,delimiter='\t')
if args.select_number:
    selected_data = [x-1 for x in args.select]    
    data = data_ori.iloc[selected_data,:]
elif args.select_name:
    indi = []
    for i,row in data_ori.iterrows():
        for j in args.select_name:
            if any(row.astype(str).str.contains(j)):
                indi.append((i))
    if not len(indi)==len(args.select_name):
        print ("Please check residue name!\nInput name:", args.select_name)
        exit()
    selected_data = indi
    data = data_ori.iloc[selected_data,:]
else :
    data=data_ori    

## baseinform
f=open (result_name,'w',newline='')
out = csv.writer(f,delimiter='\t')
out.writerow([args.frequency])
out.writerow([args.mixing_time])
out.writerow([args.sat_freq, args.sat_freq/10])
out.writerow(['#offset(ppm)     Intensity     error'])
f.close()

## list generation
i,j = data.shape
for resn in range(i) :
    f=open (result_name,'a',newline='')
    out = csv.writer(f,delimiter='\t')
    out.writerow(['#',data.iloc[resn][0],'R2a:',args.ini_R2a,'R2b:',args.ini_R2b,'dw:',args.ini_dw])
    err_std1=data.iloc[resn][1:10].std()
    err_std2=data.iloc[resn][-10:-1].std()
    if err_std1<err_std2:
        error = err_std1
    else :
        error = err_std2
    for num in range(j-1) :
       freq = float(data.columns[num+1])
       out.writerow([freq,data.iloc[resn][num+1],error])
f.close()

print ("The conversion process is complete. Output file: ",result_name)
