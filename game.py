import streamlit as st
import pandas as pd

@st.cache(allow_output_mutation=True)
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file, skiprows=1)
    df = df[4:len(df)-1].reset_index(drop=True)
    df.index += 1
    df['This Week'] = df['This Week'].astype(int)
    return df

def get_winners_and_losers(df):
    cols = list(df.columns.values)
    
    losers = df.loc[df['This Week'] < -99]
    losers = losers[[cols[0]]+[cols[2]]]
    losers = losers.sort_values('This Week', ascending = False).reset_index(drop=True)
    losers.iloc[:,1] *= -1

    winners = df.loc[df['This Week'] > 100]
    winners = winners[[cols[0]]+[cols[2]]]
    winners = winners.sort_values('This Week', ascending = False).reset_index(drop=True)
    
    return winners, losers

def add_early_payments(winners, early_moneyZ, early_moneyA):
    zane = pd.DataFrame([{'Agent':'Zane', 'This Week':early_moneyZ}], columns=winners.columns)
    austin = pd.DataFrame([{'Agent':'Austin', 'This Week':early_moneyA}], columns=winners.columns)
    winners = pd.concat([winners, zane, austin], ignore_index=True)
    return winners



def generate_payments(winners, losers):
    n_winners = winners.shape[0]
    n_losers = losers.shape[0]

    payments = pd.DataFrame(columns=['Payer', 'Receiver', 'Amount'])
    count_winner, count_loser = 0, 0
    total_debt = 0

    while count_winner < n_winners:
        winner_amount = winners.iloc[count_winner, 1]
        loser_amount = losers.iloc[count_loser, 1]

        while loser_amount >= winner_amount and count_winner < n_winners:
            loser_amount -= winner_amount
            payments = payments.append({'Payer': losers.iloc[count_loser, 0], 'Receiver': winners.iloc[count_winner, 0], 'Amount': winner_amount}, ignore_index=True)
            count_winner += 1
            winner_amount = winners.iloc[count_winner, 1]

        if loser_amount > winner_amount or count_loser == n_losers:
            loser_amount -= winner_amount
            payments = payments.append({'Payer': losers.iloc[count_loser, 0], 'Receiver': winners.iloc[count_winner, 0], 'Amount': winner_amount}, ignore_index=True)
            if count_winner < n_winners - 1:
                count_winner += 1
                winner_amount = winners.iloc[count_winner, 1]

        if count_winner == n_winners and winner_amount > 0:
            total_debt += winner_amount
            count_winner += 1

    return payments, total_debt


def main():
    uploaded_file = st.file_uploader("Upload your excel file", type=["xlsx"])
    if uploaded_file is not None:
        df = load_data(uploaded_file)

        winners, losers = get_winners_and_losers(df)
        
        st.write('LOSERS')
        st.dataframe(losers)
        st.write('WINNERS')
        st.dataframe(winners)

        fees = st.number_input('Insert this week fees: ', step=1.0)
        early_moneyZ = st.number_input('Amount paid early this week to Zane: ', step=1.0)
        early_moneyA = st.number_input('Amount paid early this week to Austin: ', step=1.0)

        total_funds = early_moneyZ + early_moneyA + fees
        winners = add_early_payments(winners, early_moneyZ, early_moneyA)

        total_winning = sum(winners['This Week'])
        if total_winning > total_funds:
            st.write("Warning: Total winnings are greater than total funds available. Remaining debt will be split between Zane and Austin.")

        st.write('PAYMENTS')
        payments, total_debt = generate_payments(winners, losers)

        if total_debt > 0:
            debt_each = total_debt / 2
            st.write(f"Remaining Debt to be split: {total_debt}")
            st.write(f"Zane's debt: {debt_each}")
            st.write(f"Austin's debt: {debt_each}")

        st.dataframe(payments)

if __name__ == "__main__":
    main()

