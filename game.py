import streamlit as st
import pandas as pd
import math

####################################################################################################################
#########################         READING EXCEL SHEET                      #########################################
####################################################################################################################
uploaded_file = st.file_uploader("Upload your excel file", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, skiprows=1)
    cols = list(df.columns.values)

    # Getting list of players
    players = df[4:len(df)-1].reset_index(drop=True)
    players.index += 1 #i make it start in 1 as index
    players['This Week'] = players['This Week'].astype(int)

    # List of losers
    st.write('LOSERS')
    losers = players.loc[players['This Week'] < -99]
    losers = losers[[cols[0]]+[cols[2]]]
    losers = losers.sort_values('This Week', ascending = False).reset_index(drop=True)
    n_losers = losers.shape[0]
    for i in range(0,n_losers):
        losers.iloc[i,1] = -losers.iloc[i,1]
    st.dataframe(losers)

    # List of winners
    st.write('WINNERS')
    winners = players.loc[players['This Week'] > 100]
    winners = winners[[cols[0]]+[cols[2]]]
    winners = winners.sort_values('This Week', ascending = False).reset_index(drop=True)
    n_winners = winners.shape[0]

    total_win = sum(winners['This Week'])

    total_lost = sum(losers['This Week'])

    # User inputs
    fees = st.number_input('Insert this week fees: ', step=1.0)
    early_moneyZ = st.number_input('Amount paid early this week to Zane: ', step=1.0)
    early_moneyA = st.number_input('Amount paid early this week to Austin: ', step=1.0)

    total_funds = early_moneyZ + early_moneyA + fees
    winners = winners.append({'Agent':'Zane','This Week':early_moneyZ}, ignore_index=True)
    winners = winners.append({'Agent':'Austin','This Week':early_moneyA}, ignore_index=True)

    # Check if total winnings are greater than total funds
    if total_win > total_funds:
        st.write("Warning: Total winnings are greater than total funds available. Remaining debt will be split between Zane and Austin.")
    
    st.write('PAYMENTS')
    output_text = ""
    count_w=0
    count_l=0
    total_debt = 0

    for j in range(0, n_winners):
        if count_w == n_winners:
            break
        else:
            wini = winners.iloc[count_w,1]
    
        for i in range(0, n_losers):
            losti = losers.iloc[count_l,1]

            if losti >= wini:
                while losti >= wini and count_w < n_winners-1:
                    tempwini = wini
                    losti -= wini
                    output_text += f"{losers.iloc[count_l,0]} pays {winners.iloc[count_w,0]} {tempwini}\n"
                    count_w += 1
                    wini = winners.iloc[count_w,1]

                if losti < wini or count_w == n_winners-1:
                    wini -= losti
                    output_text += f"{losers.iloc[count_l,0]} pays {winners.iloc[count_w,0]} {losti}\n"
                    if count_l < n_losers-1:
                        count_l += 1
                    losti = losers.iloc[count_l,1]

            elif losti < wini:
                wini -= losti
                output_text += f"{losers.iloc[count_l,0]} pays {winners.iloc[count_w,0]} {losti}\n"
                if count_l < n_losers-1:
                    count_l += 1
                losti = losers.iloc[count_l,1]

        if count_w == n_winners - 1 and wini > 0:
            total_debt += wini
            count_w += 1

    if total_debt > 0:
        debt_each = total_debt / 2
        output_text += f"\nRemaining Debt to be split: {total_debt}\n"
        output_text += f"Zane's debt: {debt_each}\n"
        output_text += f"Austin's debt: {debt_each}\n"

    st.text(output_text)

                
                
                
