import streamlit as st
import joblib
import pandas as pd
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import io
from datetime import datetime

model = joblib.load('water_quality_model.pkl')

SAFE_LIMITS = {
    'aluminium': 0.2, 'ammonia': 1.5, 'arsenic': 0.01, 'barium': 2.0,
    'cadmium': 0.003, 'chloramine': 4.0, 'chromium': 0.05, 'copper': 1.3,
    'flouride': 4.0, 'bacteria': 0.0, 'viruses': 0.0, 'lead': 0.015,
    'nitrates': 10.0, 'nitrites': 1.0, 'mercury': 0.002, 'perchlorate': 15.0,
    'radium': 5.0, 'selenium': 0.05, 'silver': 0.1, 'uranium': 0.03
}

def safe_pct(v, c):
    limit = SAFE_LIMITS[c]
    if limit == 0:
        return 100 if v > 0 else 0
    return min((v / limit) * 100, 200)

def generate_pdf(values, cols, pred, confidence):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=24, textColor=colors.HexColor('#667eea'))
    story.append(Paragraph("Water Quality Analysis Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    result_color = colors.HexColor('#155724') if pred == 1 else colors.HexColor('#721c24')
    result_text = f"Result: {'SAFE' if pred == 1 else 'UNSAFE'} — Confidence: {confidence}%"
    result_style = ParagraphStyle('Result', parent=styles['Normal'], fontSize=16, textColor=result_color, fontName='Helvetica-Bold')
    story.append(Paragraph(result_text, result_style))
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("Chemical Analysis", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))

    table_data = [['Chemical', 'Your Value', 'Safe Limit', 'Status']]
    for col, val in zip(cols, values):
        limit = SAFE_LIMITS[col]
        if limit == 0:
            status = 'DETECTED' if val > 0 else 'OK'
        else:
            status = 'OK' if val <= limit else 'HIGH'
        table_data.append([col.capitalize(), f"{val:.4f}", f"{limit}", status])

    table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8f9fa'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return buffer

st.set_page_config(page_title="💧 Water Quality Analyzer", layout="wide", page_icon="💧")

dark = st.sidebar.toggle("🌙 Dark Mode")

if dark:
    st.markdown("""
    <style>
    .stApp { background-color: #1a1a2e; color: #eee; }
    .stNumberInput input { background-color: #16213e; color: #eee; border-color: #667eea; }
    .stButton>button { background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; }
    </style>""", unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f5f7fa, #c3cfe2); }
    .stButton>button { background: linear-gradient(135deg, #667eea, #764ba2) !important; color: white !important; border: none !important; font-weight: bold !important; }
    </style>""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#667eea;'>💧 Water Quality Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#888;'>Enter chemical levels to predict if water is safe to drink</p>", unsafe_allow_html=True)

st.sidebar.title("⚡ Quick Presets")
preset = st.sidebar.radio("Load a sample:", ["Custom", "Tap Water", "River Water", "Well Water"])

presets = {
    "Tap Water":   [0.05, 0.5, 0.005, 0.3, 0.001, 0.8, 0.02, 0.2, 0.3, 0.0, 0.0, 0.002, 2.0, 0.05, 0.0005, 1.0, 0.2, 0.01, 0.005, 0.005],
    "River Water": [0.15, 2.0, 0.02, 0.8, 0.005, 1.5, 0.08, 0.5, 1.0, 0.05, 0.02, 0.01, 5.0, 0.3, 0.002, 3.0, 1.0, 0.02, 0.02, 0.01],
    "Well Water":  [0.1, 1.0, 0.008, 1.2, 0.002, 0.5, 0.03, 0.8, 2.0, 0.01, 0.005, 0.008, 8.0, 0.5, 0.001, 5.0, 2.0, 0.03, 0.01, 0.02],
    "Custom":      [0.07, 1.5, 0.01, 0.5, 0.003, 0.2, 0.05, 0.3, 0.5, 0.01, 0.001, 0.005, 3.0, 0.2, 0.001, 2.0, 0.5, 0.01, 0.01, 0.01]
}

p = presets[preset]
cols = ['aluminium','ammonia','arsenic','barium','cadmium','chloramine',
        'chromium','copper','flouride','bacteria','viruses','lead',
        'nitrates','nitrites','mercury','perchlorate','radium','selenium','silver','uranium']

st.markdown("### 🧪 Chemical Parameters")
c1, c2, c3, c4 = st.columns(4)
inputs = []
for i, col in enumerate(cols):
    with [c1, c2, c3, c4][i % 4]:
        val = st.number_input(col.capitalize(), value=float(p[i]), format="%.4f", key=col)
        inputs.append(val)

st.markdown("---")

if st.button("🔍 Analyze Water Quality", use_container_width=True):
    df = pd.DataFrame([inputs], columns=cols)
    pred = model.predict(df)[0]
    prob = model.predict_proba(df)[0]
    confidence = round(float(prob[1] if pred == 1 else prob[0]) * 100, 1)

    if pred == 1:
        st.success(f"## ✅ SAFE Water — Confidence: {confidence}%")
    else:
        st.error(f"## ❌ UNSAFE Water — Confidence: {confidence}%")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 📊 Chemical vs Safe Limits")
        pct = [safe_pct(v, c) for v, c in zip(inputs, cols)]
        bar_colors = ['#dc3545' if p > 100 else '#28a745' for p in pct]
        fig = go.Figure(go.Bar(
            x=cols, y=pct,
            marker_color=bar_colors,
            text=[f"{p:.0f}%" for p in pct],
            textposition='outside'
        ))
        fig.add_hline(y=100, line_dash="dash", line_color="orange", annotation_text="Safe Limit")
        fig.update_layout(
            yaxis_title="% of Safe Limit",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_tickangle=-45,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("#### 🕸️ Parameter Radar")
        pct_radar = [safe_pct(v, c) for v, c in zip(inputs, cols)]
        fig2 = go.Figure(go.Scatterpolar(
            r=pct_radar + [pct_radar[0]],
            theta=cols + [cols[0]],
            fill='toself',
            fillcolor='rgba(102,126,234,0.3)',
            line_color='#667eea'
        ))
        fig2.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 200])),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### 🧬 Detailed Chemical Status")
    status_data = []
    for c, v in zip(cols, inputs):
        limit = SAFE_LIMITS[c]
        if limit == 0:
            pct_val = 100 if v > 0 else 0
            status = '⚠️ DETECTED' if v > 0 else '✅ OK'
        else:
            pct_val = (v / limit) * 100
            status = '✅ OK' if v <= limit else '❌ HIGH'
        status_data.append({
            'Chemical': c.capitalize(),
            'Your Value': round(v, 4),
            'Safe Limit': limit,
            '% of Limit': f"{pct_val:.1f}%",
            'Status': status
        })
    st.dataframe(pd.DataFrame(status_data), use_container_width=True, hide_index=True)

    st.markdown("---")
    pdf = generate_pdf(inputs, cols, pred, confidence)
    st.download_button(
        label="📄 Download PDF Report",
        data=pdf,
        file_name=f"water_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )