"""Spain Territorial AI Explorer — SDG 11 academic prototype."""
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import streamlit as st

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title='Spain Territorial AI Explorer',page_icon='🏘️',layout='wide')
@st.cache_data
def get_data():
    return pd.read_csv(ROOT/'data/municipalities.csv',dtype={'ine_code':str,'province_code':str})
@st.cache_resource
def get_model():
    return joblib.load(ROOT/'models/population_growth_rf.joblib')

def fmt(v,digits=1,suffix=''):
    return f'{v:,.{digits}f}{suffix}' if pd.notna(v) else 'Not available'

def predict_for_row(row,artifact):
    values=pd.DataFrame([{name:row[name] for name in artifact['features']}])
    return float(artifact['model'].predict(values)[0])

try:
    df=get_data();artifact=get_model()
except Exception as exc:
    st.error(f'Unable to load local data/model: {exc}');st.stop()

st.title('🏘️ Spain Territorial AI Explorer')
st.caption('SDG 11 · Sustainable Cities and Communities | Academic research prototype')
st.info('**Historical backtest, not a future forecast.** The AI uses population information available by 2015 to estimate 2015–2025 growth. Rental and economic indicators are descriptive 2024–2025 context and are NOT inputs to the trained model.')

page=st.sidebar.radio('Explore', ['Municipality AI estimate','Compare municipalities','Territorial screening','Model evaluation','Methods and ethics'])
valid=df.loc[(df.pop2015>0)&df.actual_growth_2015_2025_pct.notna()].copy()
valid['choice']=valid['municipality'].fillna('Unnamed municipality')+' · '+valid['province_code'].fillna('??')+' · '+valid['ine_code']

if page=='Municipality AI estimate':
    st.header('Municipality AI estimate')
    selected=st.selectbox('Select municipality',valid['choice'].tolist(),index=0)
    row=valid.loc[valid.choice==selected].iloc[0]
    prediction=predict_for_row(row,artifact)
    a,b,c=st.columns(3)
    a.metric('AI-estimated growth (2015–2025)',fmt(prediction,1,'%'))
    b.metric('Observed growth (2015–2025)',fmt(row.actual_growth_2015_2025_pct,1,'%'))
    c.metric('Absolute prediction error',fmt(abs(prediction-row.actual_growth_2015_2025_pct),1,' pp'))
    st.subheader('Historical population')
    history=pd.DataFrame({'Year':[1996,2005,2010,2015,2025],'Population':[row[f'pop{y}'] for y in [1996,2005,2010,2015,2025]]}).dropna()
    st.line_chart(history.set_index('Year'))
    st.subheader('Territorial context (not AI predictors)')
    c1,c2,c3,c4=st.columns(4)
    c1.metric('Median rent 2024',fmt(row.rent_2024_eur_m2,2,' EUR/m²'))
    c2.metric('Industry workers share 2025',fmt(row.industry_share_2025,1,'%'))
    c3.metric('Total workers 2025',fmt(row.total_workers_2025,0))
    c4.metric('Population density 2025',fmt(row.density_2025,1))
    st.caption('This model estimates a historical outcome. The observed outcome is displayed for transparent comparison; it was not supplied as a prediction input.')

elif page=='Compare municipalities':
    st.header('Compare municipalities')
    options=st.multiselect('Choose 2–5 municipalities',valid['choice'].tolist(),default=valid['choice'].head(2).tolist(),max_selections=5)
    if options:
        chosen=valid[valid.choice.isin(options)].copy()
        chosen['AI-estimated growth (%)']=[predict_for_row(r,artifact) for _,r in chosen.iterrows()]
        comparison=chosen[['municipality','province_code','pop2015','pop2025','actual_growth_2015_2025_pct','AI-estimated growth (%)','rent_2024_eur_m2','industry_share_2025']].rename(columns={'actual_growth_2015_2025_pct':'Observed growth (%)'})
        st.dataframe(comparison,hide_index=True,use_container_width=True)
        st.bar_chart(comparison.set_index('municipality')[['Observed growth (%)','AI-estimated growth (%)']])

elif page=='Territorial screening':
    st.header('Exploratory territorial screening')
    st.warning('This is a transparent rules-based filter, **not an AI ranking**. It does not measure transport access, schools, healthcare, available housing supply, or causal impacts.')
    lo,hi=st.slider('Population in 2025',min_value=0,max_value=100000,value=(1000,20000),step=500)
    min_growth=st.slider('Minimum observed population growth, 2015–2025 (%)',-30,50,0)
    max_rent=st.slider('Maximum 2024 median rent (EUR/m²)',1.0,20.0,5.22,0.1)
    min_ind=st.slider('Minimum 2025 industry worker share (%)',0.0,60.0,6.9,0.5)
    filtered=df.loc[df.pop2025.between(lo,hi)&(df.actual_growth_2015_2025_pct>min_growth)&(df.rent_2024_eur_m2<=max_rent)&(df.industry_share_2025>=min_ind)].copy()
    st.metric('Matching municipalities',len(filtered))
    st.dataframe(filtered[['ine_code','municipality','province_code','pop2025','actual_growth_2015_2025_pct','rent_2024_eur_m2','industry_share_2025']].sort_values('actual_growth_2015_2025_pct',ascending=False),hide_index=True,use_container_width=True)
    st.download_button('Download filtered municipalities (CSV)',filtered.to_csv(index=False).encode('utf-8'),file_name='territorial_screening_results.csv',mime='text/csv')

elif page=='Model evaluation':
    st.header('Model evaluation')
    metrics=pd.read_csv(ROOT/'data/validation_metrics.csv')
    st.dataframe(metrics.rename(columns={'MAE_pp':'MAE (percentage points)','RMSE_pp':'RMSE (percentage points)'}),hide_index=True,use_container_width=True)
    st.markdown('The Random Forest was evaluated on **1,624 municipalities** excluded from its training split. The deployable model was subsequently refitted on all 8,117 valid historical examples. Metrics shown here are from the original held-out evaluation, **not** from evaluating the refitted model on its training data.')
    st.markdown('**Model features:** 2015 population (log-transformed), growth 2005–2015, growth 2010–2015, growth 1996–2015 and growth 2005–2010. All available by the end of 2015.')

else:
    st.header('Methods and ethical limitations')
    st.markdown('''
**Purpose:** Explore demographic patterns to inform SDG 11 research, not to automate public investment decisions.

**Intended users:** students, urban researchers and planners evaluating Spanish municipal population trends.

**Sources:** INE municipal population series (1996–2025), Urban Areas Atlas, SERPAVI rental indicators. The machine-learning model uses **only** historical population values through 2015.

**Risks:** Historical patterns may reproduce territorial inequalities; missing rental values can bias screening; population growth does not prove sustainability; models can be inaccurate for small municipalities or areas affected by unusual events.

**Mitigations:** Show actual versus predicted growth, error and held-out metrics; label the retrospective time horizon; retain missing values; disclose screening rules; do not present the outputs as policy recommendations or causal effects.

**Next steps:** Add transport access, public services and labor-market indicators measured before the forecast horizon; validate on genuinely future years and diverse municipalities; interview potential users.
''')
