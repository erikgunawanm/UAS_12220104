##IMPORT LIBRARY
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib import cm

##FUNGSI KHUSUS KONVERSI KODE KE NEGARA
def code_country (tuple_country_code, code) :
    for i in tuple_country_code :
        if i[1]==code :
            country = i[0]
    return country

#LAYOUT WEB SEBELUM FITUR
#import gambar dan pasang
image = Image.open('oil_rig3.png')
st.image (image, use_column_width=True)
#membuat judul
st.title ("PUSAT DATA PRODUKSI MINYAK DUNIA")
#membuat desc program
st.markdown ("Sebuah web-apps penyedia data histori produksi minyak dunia yang diolah dari sumber terpercaya dan dikembangkan oleh organisasi oil and gas data center mgoildatacenter.org." 
             "Web ini terdiri atas berbagai fitur, yakni :")
st.markdown("1. Grafik history produksi suatu negara.") 
st.markdown("2. Grafik history produksi suatu negara terhadap rata-rata produksi minyak tahunan dunia.") 
st.markdown("3. Status produksi minyak suatu negara di tahun tertentu") 
st.markdown("4. Urutan negara dengan produksi terbesar di tahun tertentu.")
st.markdown("5. Urutan negara dengan produksi akumulatif.")
st.markdown("6. Data negara dengan produksi tertinggi, terendah, dan nol produksi di tahun tertentu")

#LAYOUT SIDE BAR
#membuat judul side bar
st.sidebar.title ("Cari data")
st.sidebar.subheader("Cari data Anda dengan mudah dengan cukup beberapa kali klik")

#IMPORT DATA
df = pd.read_csv("produksi_minyak_mentah.csv")

#IMPORT DATA JSON KODE NEGARA
import json
code_fhand = open ('kode_negara_lengkap.json', 'r')
all_data = code_fhand.read()
all_data = json.loads (all_data)

#AMBIL ELEMEN KODE DAN NAMA NEGARA MENJADI LIST
i = 0
list_country = list()
list_code = list ()
while (i<len(all_data)) :
    list_country.append (all_data[i]['name'])
    list_code.append (all_data[i]['alpha-3'])
    i=i+1

#MEMBUAT DICTIONARY KHUSUS KODE, REGION, SUB-REGION, DENGAN KEYS-NYA NAMA NEGARA
country_code = dict ()
country_region = dict()
country_subreg=dict()
j = 0
for i in list_country :
    country_code [i]=all_data[j]['alpha-3'] # membuat kamus kode
    country_region[i]=all_data[j]['region'] # membuat kamus region
    country_subreg[i]=all_data[j]['sub-region'] # membuat kamus sub-region
    j = 1+j
   
#MENGHAPUS DATA PRODUKSI MINYAK DARI ORGANISASI, (BUKAN INDIVIDU NEGARA)
for i in range(len(df)):
    if df.loc[i, 'kode_negara'] not in list_code : #indikasi produksi dari organisasi : kode tidak ada di kode negara
        df = df.drop (i)

#AMBIL LIST CODE DAN LIST COUNTRY YANG DARI CSV SAJA TANPA ORGANISASI, DAN TANPA NEGARA YANG TIDAK ADA DI CSV
list_code = df['kode_negara'].tolist() #ambil list code negara pasca dihapus
ct_cd_tup = country_code.items() #buat tuple kamus kode
list_country = list () #list negara dikosongkan lagi (sebelumnya sudah dipakai)
for i in ct_cd_tup: #
    if i[1] in list_code :
        list_country.append (i[0]) #ambil negara yang di kamus kode yang kodenya ada di csv saja

#SLICING TAHUN PRODUKSI CSV UNTUK DROPDOWN PILIH TAHUN INPUTAN
uniq_year = df.drop_duplicates (subset ='tahun') #hilangkan duplikat tahun
list_year = list ()
i = 0
while (i < len (uniq_year.index)) : #membuat list tahun untuk input user
    list_year.append (uniq_year.loc[i,'tahun'])
    i = 1+i

#SELECTBOX UNTUK TAMPILAN TAHUN
year = st.sidebar.selectbox("Pilih tahun", list_year)

#SELECT BOX UNTUK PILIH NEGARA
country = st.sidebar.selectbox('Pilih negara', list_country)

# FITUR 1 : MEMBUAT LINE PLOT HISTORI PRODUKSI BERDASARKAN NEGARA 
#Membuat pivot data agar terkategorisasi berdasarkan negara sebagai index tabel
pivot_data = (df.groupby(['kode_negara', 'tahun'])['produksi'].sum().unstack())

#Membuat list sumbu x dan sumbu y sejarah produksi sesuai negara yang dipilih user
x_lyear = list_year
y_ctrprod = list ()
for i in list_year :
    y_ctrprod.append (pivot_data.loc[country_code[country], int (i)])
#Judul line plot
title_lplot = ('Histori Produksi Minyak Negara ' + country)
st.header (title_lplot)
#Membuat line plot
fig, ax = plt.subplots()
ax.plot(x_lyear,y_ctrprod, color = 'red')
fig.set_figwidth(32)
fig.set_figheight(8)
ax.tick_params(axis='both', labelsize=25)
ax.grid()
ax.set_title('Histori Produksi Minyak Negara ' + country, fontsize = 25)
ax.set_xlabel("Tahun", fontsize=23)
ax.set_ylabel("Jumlah produksi (barrel)", fontsize=23)
#Membagi kolom bagian histori produksi jadi 2
hist1, hist2 = st.columns([4, 1]) #rasio lebar kolom 6:1
hist1.markdown ('Grafik dan tabel ini sangat membantu Anda dalam melihat tren produksi minyak setiap tahun di suatu negara')
hist1.subheader('Grafik')
hist1.pyplot(fig)#menampilkan line chart
#Membuat tabel dengan sumbu tegak adalah tahun dan menyampingnya adalah negara
#Membuat pivot data agar terkategorisasi berdasarkan tahun (sumbu tegak) dan negara (sumbu datar)
pivot_data2 = (df.groupby(['tahun', 'kode_negara'])['produksi'].sum().unstack())
tab_spcountry = pd.DataFrame(pivot_data2[country_code[country]])
tab_spcountry = tab_spcountry.dropna() #nilai nan dihilangkan agar estetik di tampilan tabel
tab_spcountry.rename(columns = {country_code[country] : country}, inplace = True)
hist2.subheader ('Tabel Produksi (barrel)')
hist2.write (tab_spcountry) #menampilkan tabel disamping line chart

#FITUR 2: MEMBANDINGKAN PRODUKSI MINYAK DI SUATU NEGARA DENGAN PRODUKSI RATA-RATA MINYAK DUNIA DI THN TERTENTU
#Membuat rata-rata produksi tahunan
pivot_data3 = pivot_data2.replace(np.nan, 0, regex = False) #semua nilai nan diganti nol
peryr_prod = dict()
mean_prod = dict()
for i in list_year :
    peryr_prod[i]=0 
    mean_prod[i]=0 
    n_ct = 0
    for ctr in pivot_data3.columns.tolist() :
        if pivot_data3.loc[i, ctr] !=0 : #membuat kamus akumulasi produksi dengan tahun sebagai keys
            peryr_prod[i]=peryr_prod[i]+ (pivot_data3.loc[i, ctr])
            n_ct = n_ct + 1
    mean_prod[i]=peryr_prod[i]/n_ct #membuat kamus rata-rata produksi dunia dengan tahun sebagai keys
#Membuat stacked transparent chart
y_mean = mean_prod.values() # list sumbu y adalah values dari kamus rata-rata produksi dunia
x = mean_prod.keys() #list sumbu x adalah keys dari kamus rata-rata produksi dunia
fig2, ax2 = plt.subplots()
ax2.grid()
titlestack = "Perbandingan histori produksi negara " + country + " dengan histori rata-rata produksi dunia"
ax2.set_title(label = titlestack, fontsize = 25)
ax2.set_xlabel("Tahun", fontsize=23)
ax2.set_ylabel("Produksi (barrel)", fontsize=23)
ax2.fill_between(x, y_mean, color="lightpink", alpha = 0.5, label='rata-rata')
ax2.fill_between(x, y_ctrprod, color="darkblue", alpha = 0.5, label= country)
ax2.legend(fontsize=25)
ax2.tick_params(axis='both', labelsize=25)
fig2.set_figwidth(32)
fig2.set_figheight(8)
#membuat judul fitur dan desc nya
st.header("Perbandingan histori produksi negara " + country + " dengan histori rata-rata produksi dunia")
st.markdown("Negara dengan produksi 0 dan none tidak dilibatkan dalam perhitungan rata-rata produksi tahunan")
st.markdown ('Grafik ini sangat membantu Anda dalam melihat posisi produksi minyak suatu negara terhadap rata-rata produksi dunia tiap tahun')
#menampilkan plot ke streamlit
st.pyplot(fig2)

#FITUR 3 : MEMBUAT STATUS PRODUKSI SUATU NEGARA
#membuat judul fitur
st.header("Status Produksi Minyak Negara " + country + " pada tahun " + str(year))
stcol1, stcol2, stcol3 = st.columns (3) #membagi menjadi 3 kolom
code = country_code[country] #memanggil kamus kode dengan imputan negara dari user
stcol1.metric ('Kode', code)  #menampilkan kode negara inputan
if year != 1971 : #jika bukan di awal data tahun -> bisa dibandingkan produksinya
    if pivot_data3.loc[year, code] == 0 and pivot_data3.loc[year-1, code] == 0 : #Jika produksi 0 atau nan
        stcol2.metric ('Produksi tahunan (barrel)', pivot_data3.loc[year, code])
    else : #jika valuenya berupa angka>0
        inc = (pivot_data3.loc[year, code]-pivot_data3.loc[year-1, code])/pivot_data3.loc[year-1, code]
        inc = (round(inc*100, 2))
        inc = str(inc) + '%'
        #menampilkan produksi di tahun inputan dan peningkatan/penurunannya
        stcol2.metric ('Produksi tahunan (barrel)', pivot_data3.loc[year, code], inc)
else : #jika diawal tahun -> tak usah dibandingkan
    stcol2.metric ('Produksi tahunan (barrel)', pivot_data3.loc[year, code])
cbt = str(round(pivot_data3.loc[year, code]/peryr_prod[year]*100, 5))+ '%'
stcol3.metric ('Kontribusi terhadap produksi tahunan', cbt)

#FITUR 4: MENYAJIKAN DATA N BESAR NEGARA DENGAN PRODUKSI MINYAK TERTINGGI DI THN TERTENTU
#Membuat batas input untuk N-besar negara dari user di sidebar
max_number = len (df.drop_duplicates(subset = 'kode_negara')) #batas = jumlah negara unik di data csv
#Membuat tempat number input pengguna
top_n = st.sidebar.number_input ('Masukkan nilai N besar negara dengan produksi minyak tertinggi', min_value = 1, max_value = max_number)
#ambil pivot_data dengan indeks year, dan panggil sesuai inputan pengguna, urutkan produksinya
sorted_data = pivot_data[year].sort_values(ascending = False) 
sorted_data = sorted_data.replace(np.nan,"", regex = True) # ganti variable nan jadi "
sorted_data = sorted_data.to_frame() #ubah dari pd series ke bentuk dataframe
top_code = sorted_data.index.values #ambil kode negara setelah produksinya diurutkan
#membuat list negara yang sudah urut dan list produksi yang sudah urut
prod = list()
top_country = list()
for i in top_code :
    top_country.append (code_country(ct_cd_tup,i))
    prod.append (sorted_data.loc[i, year])
#membuat indeks ranking
rank_list = list(range(1, len(sorted_data)+1,1))
#membuat dataframe urutan negara dengan produksi minyak tertinggi
top_prod ={"Negara" : pd.Series(top_country, index = rank_list),
           "Produksi (barrel)" : pd.Series(prod, index = rank_list)}
top_prod = pd.DataFrame(top_prod)
#Membagi page jadi 2 kolom
prodcol, accol = st.columns(2) #kiri untuk produksi di tahun tertentu, kanan untuk akumulasi produksi
prod_hdr = (str (top_n) + ' Negara dengan produksi minyak tertinggi di dunia pada tahun ' + str (year))
ac_hdr = (str (top_n) + ' Negara dengan akumulasi produksi minyak tertinggi di dunia')
prodcol.header(prod_hdr)
accol.header(ac_hdr)
accol.markdown ('Data dihitung dari tahun 1971 s.d. 2015')
#Menampilkan negara dengan produksi B besar tertinggi dengan horizontal bar chart
y_topprd = top_prod.loc[0:top_n,'Negara'] #membuat sumbu y dari horizontal bar chart (negara)
x_topprd = top_prod.loc[0:top_n,'Produksi (barrel)'] #membuat sumbu x dari horizontal bar chart (values produksi tahun tertentu)
fig3, ax3 = plt.subplots()
for i in range(len (y_topprd)): #membuat label bar chart agar tampil value juga
    ax3.text(x_topprd.tolist()[i],y_topprd.tolist()[i],x_topprd.tolist()[i])
cmap_name = 'tab20' 
cmap = cm.get_cmap(cmap_name)
colors = cmap.colors[:len(y_topprd)] #memberi warna ke bar chart
ax3.barh(y_topprd,x_topprd, color = colors)
ax3.set_xlabel("Produksi (barrel)")
ax3.set_ylabel("Negara")
ax3.invert_yaxis() #inversi bar chart urut dari terbesar (atas) ke terkecil
prodcol.pyplot(fig3) #menampilkan bar chart ke streamlit

#FITUR 5 : MENYAJIKAN DATA N BESAR NEGARA DENGAN AKUMULASI PRODUKSI MINYAK TERTINGGI
acc_prod = dict()
#membuat pivot data dengan nilai ditampilkan semua dan ganti nan dengan ""
acc_pivot_data = pivot_data.replace(np.nan, "", regex = True) 
for code in acc_pivot_data.index.values : 
    country_key = code_country(ct_cd_tup,code)
    acc_prod[country_key]=0
    for yr in list_year : #membuat kamus yang memuat produksi akumulatif di negara tertentu dengan negara sebagai keys
        if acc_pivot_data.loc[code,yr] !="" :
            acc_prod[country_key] = acc_prod[country_key]+acc_pivot_data.loc[code,yr]
        else :
            continue
#membuat list indeks untuk negara dengan akumulasi produksi tertinggi -> u/ data frame
acc_prod_index = list(range(1, len(acc_prod)+1, 1))
acc_prod = {"Negara": pd.Series(acc_prod.keys(), index = acc_prod_index),
            "Produksi kumulatif (barrel)" : pd.Series(acc_prod.values(), index = acc_prod_index)}
acc_prod = pd.DataFrame(acc_prod) #membuat dataframe negara dan akumulasi produksi (belum urut)
#membuat dataframe baru yang urut
top_acc_prod = pd.DataFrame(acc_prod.sort_values(["Produksi kumulatif (barrel)", "Negara"], ascending = False).to_numpy(),
                               index = acc_prod_index, columns = acc_prod.columns)
#Menampilkan negara dengan produksi B besar tertinggi
y_topaprd = top_acc_prod.loc[0:top_n,'Negara'] #membuat sumbu y dari horizontal bar chart (negara)
x_topaprd = top_acc_prod.loc[0:top_n,'Produksi kumulatif (barrel)'] #membuat sumbu x dari horizontal bar chart (akumulasi produksi)
fig4, ax4 = plt.subplots()
for i in range(len (y_topaprd)):  #membuat label bar chart agar tampil value juga
    ax4.text(x_topaprd.tolist()[i],y_topaprd.tolist()[i],x_topaprd.tolist()[i])
ax4.barh(y_topaprd,x_topaprd, color = colors)
ax4.set_xlabel("Produksi kumulatif (barrel)")
ax4.set_ylabel("Negara")
ax4.invert_yaxis() #inversi bar chart urut dari terbesar (atas) ke terkecil 
accol.pyplot(fig4) #gambarkan chart ke streamlit

#FITUR 6A : MENAMPILKAN DATA PRODUKSI TERBESAR, TERKECIL, NOL DI THN X
#Menampilkan data produksi terbesar di tahun X
highest = top_prod.loc[1, 'Produksi (barrel)']
highest_ctry = top_prod.loc[1, 'Negara']
acc_prod_ctrindeks = top_acc_prod.set_index('Negara')
highest_acc_prod = acc_prod_ctrindeks.loc[highest_ctry,'Produksi kumulatif (barrel)' ]
highest_code = country_code[highest_ctry]
highest_reg = country_region[highest_ctry]
highest_subreg = country_subreg[highest_ctry]
#GUI ke streamlit
st.header("Rincian Produksi Minyak Tertinggi, Terendah, dan Nol pada Tahun " + str(year))
col1, col2 = st.columns(2)
col1.subheader("Produksi Minyak Tertinggi")
col2.subheader("Produksi Minyak Terendah")
ct_col1, ct_col2 = st.columns(2)
ct_col1.metric ("Negara", highest_ctry)
cd_col1, cd_col2 = st.columns(2)
cd_col1.metric ("Kode negara", highest_code)
reg_col1, reg_col2 = st.columns(2)
reg_col1.metric ("Region", highest_reg)
sr_col1, sr_col2 = st.columns(2)
sr_col1.metric ("Sub-region", highest_subreg)
prd_col1, prd_col2 = st.columns(2)
prd_col1.metric ("Produksi pada tahun tersebut (barrel)", highest)
acc_col1, acc_col2 = st.columns(2)
acc_col1.metric ("Produksi kumulatif s.d. 2015 (barrel)", highest_acc_prod)
#Menampilkan data produksi terendah di tahun X
for i in range(len(top_prod)):
    if top_prod.loc[i+1, 'Produksi (barrel)'] != 0 or top_prod.loc[i+1, "Produksi (barrel)"]=="":
        continue
    else :
        lowest = top_prod.loc[i, 'Produksi (barrel)']
        lowest_ctry = top_prod.loc[i, 'Negara']
        break
lowest_acc_prod = acc_prod_ctrindeks.loc[lowest_ctry,'Produksi kumulatif (barrel)' ]
lowest_code = country_code[lowest_ctry]
lowest_reg = country_region[lowest_ctry]
lowest_subreg = country_subreg[lowest_ctry]
#GUI ke streamlit
ct_col2.metric ("Negara", lowest_ctry)
cd_col2.metric ("Kode negara", lowest_code)
reg_col2.metric ("Region", lowest_reg)
sr_col2.metric ("Sub-region", lowest_subreg)
prd_col2.metric ("Produksi pada tahun tersebut (barrel)", lowest)
acc_col2.metric ("Produksi kumulatif s.d. 2015 (barrel)", lowest_acc_prod)
#Menanpilkan data produksi = 0
zero_ctry = list()
for i in range(len(top_prod)):
    if top_prod.loc[i+1, 'Produksi (barrel)'] == 0 :
        zero_ctry.append(top_prod.loc[i+1, 'Negara'])
    else : 
        continue
zero_reg = list()
zero_subreg = list()
zero_code = list()
for ct in zero_ctry :
    zero_reg.append(country_region[ct])
    zero_subreg.append(country_subreg[ct])
    zero_code.append(country_code[ct])
#Membuat dataframe untuk nol produksi
zero_prod = pd.DataFrame({'Negara': zero_ctry,
                  'Kode negara': zero_code,
                  'Region' : zero_reg,
                  'Sub-region': zero_subreg},
                  index=list(range(1, len(zero_ctry)+1, 1)))
zero_prod = pd.DataFrame(zero_prod.sort_values([("Negara")], ascending = True).to_numpy(),
                               index = zero_prod.index, columns = zero_prod.columns)
st.subheader("Produksi Nol")
st.table(zero_prod)

#FITUR 6B : MENAMPILKAN DATA AKUMULASI PRODUKSI TERBESAR, TERKECIL, NOL
#Menampilkan data produksi akumulatif terbesar 
achighest = top_acc_prod.loc[1, 'Produksi kumulatif (barrel)']
achighest_ctry = top_acc_prod.loc[1, 'Negara']
achighest_code = country_code[achighest_ctry]
achighest_reg = country_region[achighest_ctry]
achighest_subreg = country_subreg[achighest_ctry]
#GUI ke streamlit
st.header("Rincian Produksi Minyak Tertinggi, Terendah, dan Nol Kumulatif")
col1, col2 = st.columns(2)
col1.subheader("Produksi Minyak Akumulatif Tertinggi")
ct_col1, ct_col2 = st.columns(2)
ct_col1.metric ("Negara", achighest_ctry)
cd_col1, cd_col2 = st.columns(2)
cd_col1.metric ("Kode negara", achighest_code)
reg_col1, reg_col2 = st.columns(2)
reg_col1.metric ("Region", achighest_reg)
sr_col1, sr_col2 = st.columns(2)
sr_col1.metric ("Sub-region", achighest_subreg)
prd_col1, prd_col2 = st.columns(2)
prd_col1.metric ("Produksi akumulatif dari 1971 s.d. 2015 (barrel)", achighest)
#Menampilkan data produksi akumulatif terendah
for i in range(len(top_acc_prod)):
    if top_acc_prod.loc[i+1, 'Produksi kumulatif (barrel)'] != 0 or top_acc_prod.loc[i+1, "Produksi kumulatif (barrel)"]=="":
        continue
    else :
        aclowest = top_acc_prod.loc[i, 'Produksi kumulatif (barrel)']
        aclowest_ctry = top_acc_prod.loc[i, 'Negara']
        break
aclowest_code = country_code[aclowest_ctry]
aclowest_reg = country_region[aclowest_ctry]
aclowest_subreg = country_subreg[aclowest_ctry]
#GUI ke streamlit
col2.subheader("Produksi Minyak Akumulatif Terendah")
ct_col2.metric ("Negara", aclowest_ctry)
cd_col2.metric ("Kode negara", aclowest_code)
reg_col2.metric ("Region", aclowest_reg)
sr_col2.metric ("Sub-region", aclowest_subreg)
prd_col2.metric ("Produksi akumulatif dari 1971 s.d. 2015 (barrel)", aclowest)
#Menanpilkan data produksi akumulatif = 0
st.subheader("Produksi Nol Kumulatif")
aczero_ctry = list()
for i in range(len(top_acc_prod)):
    if top_acc_prod.loc[i+1, 'Produksi kumulatif (barrel)'] == 0 :
        aczero_ctry.append(top_acc_prod.loc[i+1, 'Negara'])
    else : 
        continue
aczero_reg = list()
aczero_subreg = list()
aczero_code = list()
for ct in aczero_ctry :
    aczero_reg.append(country_region[ct])
    aczero_subreg.append(country_subreg[ct])
    aczero_code.append(country_code[ct])
#Membuat dataframe khusus akumulasi produksi minyak = 0
aczero_prod = pd.DataFrame({'Negara': aczero_ctry,
                  'Kode negara': aczero_code,
                  'Region' : aczero_reg,
                  'Sub-region': aczero_subreg},
                  index=list(range(1, len(aczero_ctry)+1, 1)))
aczero_prod = pd.DataFrame(aczero_prod.sort_values([("Negara")], ascending = True).to_numpy(),
                               index = aczero_prod.index, columns = aczero_prod.columns)
st.table(aczero_prod)

#LAYOUT WEB SETELAH SEMUA FITUR
#import gambar dan pasang
image = Image.open('data_quote.jpg')
st.image (image, use_column_width=True)
