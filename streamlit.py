# dependencies
import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st
from PIL import Image
from millify import prettify

# customize Streamlit page
im = Image.open('content/migration.png')

st.set_page_config(page_title='ACS Migration', layout="wide", page_icon=im)

hide_default_format = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        section.main > div:has(~ footer ) {
        padding-bottom: 5px;}
        div.block-container{padding-top:1.5rem;}
       </style>
       """

st.markdown(hide_default_format, unsafe_allow_html=True)


# this will form the dropdown list
clist = ['Cherokee County',
         'Clayton County',
         'Cobb County',
         'DeKalb County',
         'Douglas County',
         'Fayette County',
         'Forsyth County',
         'Fulton County',
         'Gwinnett County',
         'Henry County',
         'Rockdale County']

county_st = st.sidebar.selectbox("Select a metro county:", clist)

# this will form the radio buttons & dictionary which will drive the functionality
mig_direction = [
    'Total In Migration',
    'Total Out Migration',
    'Net Migration (Positive)',
    'Net Migration (Negative)'
]

mig_dict = {
    mig_direction[0]:'B-A_Estimate',
    mig_direction[1]:'A-B_Estimate',
    mig_direction[2]:'Net_Estimate',
    mig_direction[3]:'Net_Estimate'
}

mig_st = st.sidebar.radio("Select migration direction: ", mig_direction)

# header text
st.header("Metro Atlanta Migration by County")
st.subheader("2020 5-Year ACS")


# sidebar image
image = Image.open('content/ARC_logo.png')
col1, col2, col3 = st.sidebar.columns([1,3,1])
with col1:
    st.sidebar.write("")

with col2:
    st.sidebar.write(""
    )

with col3:
    st.sidebar.write("")



# set the text of the sub-heading under the header
if mig_st == 'Total In Migration':
    st.write(f"Top 10 Origins of Inflow: **{county_st}**")
elif mig_st == 'Total Out Migration':
    st.write(f"Top 10 Destinations of Outflow: **{county_st}**")
elif mig_st == 'Net Migration (Positive)':
    st.write(f"Top 10 Origins of Net Inflow: **{county_st}**")
else:
    st.write(f"Top 10 Destinations of Net Outflow: **{county_st}**")

# color of the plotly bars
color_in_state = '#262730'
color_oo_state = '#F28C28'

# get the dataframe ready
df = pd.read_csv('Migration_16-20.csv', thousands=',', encoding = "ISO-8859-1")
df = df.loc[:, ~df.columns.str.startswith('MOE')]
df = df[['County Name of Geography A',
         'State of Geography A',
         'County Name of Geography B',
         'State of Geography B',
         'B-A_Estimate',
         'A-B_Estimate',
         'Net_Estimate',
        ]]

# filter down to just get the county that's selected
df = df[df['County Name of Geography A'] == county_st]

# --------------------------------------------------------------------------
# grab the bottom / top 10
if mig_st == 'Net Migration (Negative)':
    df = df.dropna(subset=['Net_Estimate'])
    df2 = df.sort_values(by=[mig_dict[mig_st]], ascending=False).tail(10)
    # create the column which will be a unique identifier for each county (account for states that have an identical county name)
    df2['unique'] = df2['County Name of Geography B'] + "-" + df2['State of Geography B']

    # for any continents, fill in the name of the continent for 'state'
    df2['County Name of Geography B'] = np.where(df2['County Name of Geography B'] == '-',
                                                df2['State of Geography B'],
                                                df2['County Name of Geography B'])

    # decide which regions are outside the state of GA
    df2['OO_state'] = np.where(df2['State of Geography B'] == 'Georgia',
                            'No',
                            'Yes')

    # calculate the migration totals using Pandas, which will populate the metric
    mig_total = df[mig_dict[mig_st]].sum().astype(int)
    mig_prettify = prettify(mig_total)

    # get a migration total to use as metric
    if mig_st == 'Total In Migration':
        col2.metric(label='**Total In Migration:**', value=mig_prettify)
    elif mig_st == 'Total Out Migration':
        col2.metric(label='Total Out Migration:', value=mig_prettify)
    else:
        col2.metric(label='Total Net Migration:', value=mig_prettify)

    # sidebar text
    st.sidebar.markdown(
    '*Note:  \nWhile the ACS tracks international in-migration, it does *not* track international out-migration. Thus, each county\'s \
    Total Net Migration is calculated from its domestic in-migration minus its domestic out-migration.*'
    )

    # instantiate the plot that will populate the app
    fig = px.bar(
        df2, 
        text=mig_dict[mig_st], 
        x=df2['unique'].tolist(),
        y=mig_dict[mig_st],
        labels={
            'x':" "
            # 'x':f"<br><i>(Out-Of-State Regions Shown in <b><span style='color:{color_oo_state}'>Orange</span></b>)</i>"
            },
        color=df2['OO_state'],
        color_discrete_map={
            'No':color_in_state,
            'Yes':color_oo_state
        },
        custom_data=['State of Geography B']
    )

    # this will create the hover text over each bar
    custom_template = "<br>".join([
            "<b>State or Region</b>: %{customdata[0]}<br>",
            "<extra></extra>"
        ])

    # do a buncha shit
    fig.update_layout(
        width=1200,
        height=660,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,80,0,0)',
        font_color='white',
        font_size=20,
        showlegend=False,
        yaxis=dict(
            showgrid=False
            ),
        yaxis_title=None,
        xaxis=dict(
            side = 'top',
            tickfont={"size":16},
            tickmode = 'array',
            tickvals = df2['unique'],
            ticktext = df2['County Name of Geography B']
            ),
        hoverlabel=dict(
            font_size=16,
            # font_color="#586e75",
            )
    )

    fig.update_traces(
        # have a thousands separator for the data labels
        texttemplate='<b>%{text:,}</b>',
        # thicken the bar outline
        marker_line_width = 2,
        # color of bar outline
        marker_line_color = 'white',
        # force data labels to outside end
        textposition='outside',
        # customize the interactive tooltip
        hovertemplate=custom_template,
        )

    # force the graph to show largest migration numbers to smaller
    fig.update_xaxes(categoryarray = df2['unique'].tolist(),
                    title_font={"size":18})

    # draw the horizontal line across the plot nice & strong
    fig.update_yaxes(
        zeroline=True, 
        zerolinewidth=2, 
        zerolinecolor='#FFFFFF',
        showticklabels=False,
        range=[-4000,0]
        )

    fig.add_annotation(
        showarrow=False,
        yref='paper',
        x=4.25,
        y=0,
        font_size=18,
        text=f"<br><i>(Out-Of-State Regions Shown in <b><span style='color:{color_oo_state}'>Orange</span></b>)</i>"
        )

    # customize the Plotly modebar
    config={
        'displaylogo':False,
        'toImageButtonOptions': {
            'format':'png',
            'filename':'my_download'
            },
        'modeBarButtonsToRemove':['autoScale','lasso2d','zoom','select2d']
    }

    # Draw it.
    st.plotly_chart(
        fig,
        config=config
        )
else:
    df2 = df.sort_values(by=[mig_dict[mig_st]], ascending=False).head(10)

# ----------------------------------------------------------------

    # create the column which will be a unique identifier for each county (account for states that have an identical county name)
    df2['unique'] = df2['County Name of Geography B'] + "-" + df2['State of Geography B']

    # for any continents, fill in the name of the continent for 'state'
    df2['County Name of Geography B'] = np.where(df2['County Name of Geography B'] == '-',
                                                df2['State of Geography B'],
                                                df2['County Name of Geography B'])

    # decide which regions are outside the state of GA
    df2['OO_state'] = np.where(df2['State of Geography B'] == 'Georgia',
                            'No',
                            'Yes')

    # calculate the migration totals using Pandas, which will populate the metric
    mig_total = df[mig_dict[mig_st]].sum().astype(int)
    mig_prettify = prettify(mig_total)

    # get a migration total to use as metric
    if mig_st == 'Total In Migration':
        col2.metric(label='Total In Migration:', value=mig_prettify)
    elif mig_st == 'Total Out Migration':
        col2.metric(label='Total Out Migration:', value=mig_prettify)
    else:
        col2.metric(label='Total Net Migration:', value=mig_prettify)

       # sidebar text
    st.sidebar.markdown(
    '*Note:  \nWhile the ACS tracks international in-migration, it does *not* track international out-migration. Thus, each county\'s \
    Total Net Migration is calculated from its domestic in-migration minus its domestic out-migration.*'
    )

    # instantiate the plot that will populate the app
    fig = px.bar(
        df2, 
        text=mig_dict[mig_st], 
        x=df2['unique'].tolist(),
        y=mig_dict[mig_st],
        labels={
            'x':f"<br><i>(Out-Of-State Regions Shown in <b><span style='color:{color_oo_state}'>Orange</span></b>)</i>"
            },
        color=df2['OO_state'],
        color_discrete_map={
            'No':color_in_state,
            'Yes':color_oo_state
        },
        custom_data=['State of Geography B']
    )

    # this will create the hover text over each bar
    custom_template = "<br>".join([
            "<b>State or Region</b>: %{customdata[0]}<br>",
            "<extra></extra>"
        ])

    # do a buncha shit
    fig.update_layout(
        width=1200,
        height=650,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,80,0,0)',
        font_color='white',
        font_size=20,
        showlegend=False,
        yaxis=dict(
            showgrid=False
            ),
        yaxis_title=None,
        xaxis=dict(
            tickfont={"size":16},
            tickmode = 'array',
            tickvals = df2['unique'],
            ticktext = df2['County Name of Geography B']
            ),
        hoverlabel=dict(
            font_size=16,
            # font_color="#586e75",
            )
    )

    fig.update_traces(
        # have a thousands separator for the data labels
        texttemplate='<b>%{text:,}</b>',
        # thicken the bar outline
        marker_line_width = 2,
        # color of bar outline
        marker_line_color = 'white',
        # force data labels to outside end
        textposition='outside',
        # customize the interactive tooltip
        hovertemplate=custom_template,
        )

    # force the graph to show largest migration numbers to smaller
    fig.update_xaxes(categoryarray = df2['unique'].tolist(),
                    title_font={"size":18})

    # draw the horizontal line across the plot nice & strong
    fig.update_yaxes(zeroline=True, 
                    zerolinewidth=2, 
                    zerolinecolor='#FFFFFF',
                    showticklabels=False)

    # customize the Plotly modebar
    config={
        'displaylogo':False,
        'toImageButtonOptions': {
            'format':'png',
            'filename':'my_download'
            },
        'modeBarButtonsToRemove':['autoScale','lasso2d','zoom','select2d']
    }

    # Draw it.
    st.plotly_chart(
        fig,
        config=config
        )


