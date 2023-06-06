import streamlit as st
import pandas as pd
import math #for rounding numbers

st.title("Player Data Analysis")

uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx'])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, skiprows=1)

    # Assign each column into a list 
    cols = list(df.columns.values)

    # Getting list of players
    players = df[4:len(df)-1].reset_index(drop=True)
    players.index += 1
    players['This Week'] = players['This Week'].astype(int) 

    # List of losers
    st.subheader('LOSERS')
    losers = players.loc[players['This Week'] < -99]
    losers = losers[[cols[0]]+[cols[2]]]
    losers = losers.sort_values('This Week', ascending = False).reset_index(drop=True)
    n_losers = losers.shape[0]
    for i in range(0,n_losers):
        losers.iloc[i,1] = -losers.iloc[i,1]
    st.dataframe(losers)

    # List of winners
    st.subheader('WINNERS')
    winners = players.loc[players['This Week'] > 100]
    winners = winners[[cols[0]]+[cols[2]]]
    winners = winners.sort_values('This Week', ascending = False).reset_index(drop=True)
    n_winners = winners.shape[0]

    # Calculate profit
    total_win = sum(winners.iloc[i,1] for i in range(n_winners))
    total_lost = sum(losers.iloc[i,1] for i in range(n_losers))

    #Adding fees and organizers into winners
    fees = float(st.text_input('Insert this week fees: '))
    fees_row = {'Agent':'fees','This Week':fees}
    winners = winners.append(fees_row,ignore_index=True)
    early_moneyZ = float(st.text_input('Amount paid early this week to Zane: '))
    early_moneyA = float(st.text_input('Amount paid early this week to Austin: '))
    
    profit_i = math.floor((total_lost - total_win - fees + early_moneyZ + early_moneyA) / 2 )
    organizer_1_row = {'Agent':'Zane','This Week':profit_i - early_moneyZ}
    organizer_2_row = {'Agent':'Austin','This Week':profit_i - early_moneyA}
    winners = winners.append(organizer_1_row,ignore_index=True)
    winners = winners.append(organizer_2_row,ignore_index=True)

    payment_extra = total_lost - total_win - fees - 2*profit_i  + early_moneyZ + early_moneyA
    st.write(f'This is the money that was left in order to make round distribution between organizers: {payment_extra}')

    st.dataframe(winners)
    n_winners = winners.shape[0]

    #list of NotApplicable
    na = players.loc[(players['This Week'] > -99) & (players['This Week'] < 100)]
    na = na[[cols[0]]+[cols[2]]]
    na = na.sort_values('This Week', ascending = True).reset_index(drop=True)
    n_na = na.shape[0]

    ####################################################################################################################
    ####################################################################################################################
    #########################                   PAYING ALGORITHM               #########################################
    ####################################################################################################################
    ####################################################################################################################

    count_w=0
    count_l=0
    END1 = False
    output_text = ""

    for j in range(0,n_winners):
        if count_w == n_winners:
            break
        else:
            wini = winners.iloc[count_w,1]

        for i in range(0,n_losers):
            losti = losers.iloc[count_l,1]
            # Simplifying the condition logic
            if losti >= wini:
                while losti >= wini and count_w < n_winners-1:
                    tempwini = wini
                    losti -= wini
                    output_text += f"{losers.iloc[count_l,0]} pays {winners.iloc[count_w,0]} {tempwini}\n"
                    count_w += 1
                    wini = winners.iloc[count_w,1]

                if losti < wini or count_w >= n_winners-1:
                    output_text += f"{losers.iloc[count_l,0]} pays {winners.iloc[count_w,0]} {losti}\n"
                    wini -= losti
                    count_l += 1

            elif losti < wini and count_w < n_winners-1:
                templosti = losti
                output_text += f"{losers.iloc[count_l,0]} pays {winners.iloc[count_w,0]} {templosti}\n"
                wini -= losti
                count_l += 1

        # End condition logic
        if count_w == n_winners-1 and count_l == n_losers-1 and not END1:
            output_text += f"{losers.iloc[count_l,0]} pays {winners.iloc[count_w,0]} {losti}\n"
            END1 = True

    st.text(output_text)

# This streamlit script needs to be run using `streamlit run your_script.py`


