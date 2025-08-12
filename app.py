
import streamlit as st
import joblib
from sentence_transformers import SentenceTransformer, util
import numpy as np

# Load model metadata
with open('model_metadata.txt') as f:
    model_name = f.read().strip().split('=')[1]

# Load model and classifier
@st.cache_resource
def load_model():
    clf = joblib.load('bangla_plagiarism_model.pkl')
    model = SentenceTransformer(model_name)
    return clf, model

clf, model = load_model()

# Helper: Split paragraph into Bangla sentences by "।"
def split_sentences(paragraph):
    # Split by Bengali danda punctuation, strip whitespace, ignore empties
    sentences = [s.strip() for s in paragraph.split('।') if s.strip()]
    return sentences

# Streamlit UI
st.set_page_config(page_title="Bangla Plagiarism Checker", layout="centered")
st.title("Bangla Plagiarism Checker")
st.markdown("Paste paragraphs in both fields. Each sentence in the suspected paragraph will be compared individually.")

# Input fields
original_paragraph = st.text_area("Original Paragraph", height=200)
suspected_paragraph = st.text_area("Suspected Paragraph", height=200)

# Button to analyze
if st.button("🔍 Analyze Plagiarism"):
    if not original_paragraph.strip() or not suspected_paragraph.strip():
        st.warning("Please enter both paragraphs.")
    else:
        with st.spinner("Analyzing..."):
            # Split paragraphs into sentences
            original_sentences = split_sentences(original_paragraph)
            suspected_sentences = split_sentences(suspected_paragraph)

            # Encode original sentences once
            original_embs = model.encode(original_sentences, convert_to_tensor=True)
            suspected_embs = model.encode(suspected_sentences, convert_to_tensor=True)

            results = []
            for i, suspected_emb in enumerate(suspected_embs):
                # cosine similarity of suspected sentence vs all original sentences
                sims = util.cos_sim(suspected_emb, original_embs).cpu().numpy()
                max_sim = np.max(sims)
                pred_label = clf.predict([[max_sim]])[0]

                results.append({
                    "sentence": suspected_sentences[i],
                    "similarity": max_sim,
                    "label": "Plagiarized" if pred_label == 1 else "Original"
                })

        # Show results
        st.success("✅ Analysis Complete")
        
        # Calculate statistics for final report
        total_sentences = len(results)
        plagiarized_count = sum(1 for res in results if res['label'] == "Plagiarized")
        original_count = total_sentences - plagiarized_count
        plagiarism_percentage = (plagiarized_count / total_sentences) * 100 if total_sentences > 0 else 0
        avg_similarity = np.mean([res['similarity'] for res in results])
        max_similarity = max([res['similarity'] for res in results])
        
        # Show individual sentence results
        st.subheader("📝 Sentence-by-Sentence Analysis")
        for idx, res in enumerate(results):
            color = "red" if res["label"] == "Plagiarized" else "green"
            st.markdown(f"""
                <div style="border:1px solid #ddd; padding:10px; margin-bottom:10px;">
                <b>Sentence {idx+1}:</b> <span style="color:{color};"><b>{res['label']}</b></span><br>
                <b>Similarity:</b> {res['similarity']:.4f}<br>
                <i>{res['sentence']}</i>
                </div>
            """, unsafe_allow_html=True)
        
        # Final Plagiarism Report
        st.markdown("---")
        st.subheader("📊 Final Plagiarism Report")
        
        # Determine overall verdict
        if plagiarism_percentage >= 50:
            verdict = "HIGH PLAGIARISM DETECTED"
            verdict_color = "red"
            verdict_icon = "🚨"
        elif plagiarism_percentage >= 25:
            verdict = "MODERATE PLAGIARISM DETECTED"
            verdict_color = "orange"
            verdict_icon = "⚠️"
        else:
            verdict = "LOW/NO PLAGIARISM DETECTED"
            verdict_color = "green"
            verdict_icon = "✅"
        
        # Display the report
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Sentences", total_sentences)
            st.metric("Plagiarized Sentences", plagiarized_count)
            st.metric("Original Sentences", original_count)
        
        with col2:
            st.metric("Plagiarism Percentage", f"{plagiarism_percentage:.1f}%")
            st.metric("Average Similarity", f"{avg_similarity:.4f}")
            st.metric("Max Similarity", f"{max_similarity:.4f}")
        
        # Overall Verdict
        st.markdown(f"""
            <div style="border:2px solid {verdict_color}; padding:20px; margin:20px 0; border-radius:10px; text-align:center; background-color:rgba(255,255,255,0.1);">
                <h2 style="color:{verdict_color}; margin:0;">{verdict_icon} {verdict}</h2>
                <p style="font-size:18px; margin:10px 0;"><b>Overall Plagiarism: {plagiarism_percentage:.1f}%</b></p>
                <p style="margin:0;">Based on analysis of {total_sentences} sentences</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Recommendations
        st.subheader("💡 Recommendations")
        if plagiarism_percentage >= 50:
            st.error("🚨 **High plagiarism detected!** This document requires significant revision. Most sentences appear to be copied from the original source.")
        elif plagiarism_percentage >= 25:
            st.warning("⚠️ **Moderate plagiarism detected.** Please review and revise the flagged sentences to ensure proper paraphrasing and citation.")
        else:
            st.success("✅ **Good work!** The document shows minimal plagiarism. Continue to ensure proper citation for any borrowed ideas.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; margin-top: 50px;'>
        <p>Green University Of Bangladesh</p>
        <p style='font-size: 12px;'>By Jalal Uddin Taj, Bijoy Chandra Das, Sakibul Islam Adil</p>
    </div>
    """,
    unsafe_allow_html=True
)
