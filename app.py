
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

# Helper: Check if text contains English characters
def contains_english(text):
    # Check for English letters (a-z, A-Z)
    import re
    return bool(re.search(r'[a-zA-Z]', text))

# Helper: Check if text is valid Bangla
def is_valid_bangla(text):
    # Remove spaces, punctuation, and digits
    cleaned = text.replace(' ', '').replace('\n', '')
    # Check if contains any English letters
    if contains_english(cleaned):
        return False
    return True

# Streamlit UI
st.set_page_config(page_title="Detection of Textual Similarity in Bangla Literature for Plagiarism Analysis using Text Mining Techniques", layout="centered")
st.title("Detection of Textual Similarity in Bangla Literature for Plagiarism Analysis using Text Mining Techniques")
st.markdown("Paste paragraphs in both fields. Each sentence in the suspected paragraph will be compared individually.")

# Input fields
original_paragraph = st.text_area("Original Paragraph", height=200)
suspected_paragraph = st.text_area("Suspected Paragraph", height=200)

# Button to analyze
if st.button("🔍 Analyze Plagiarism"):
    if not original_paragraph.strip() or not suspected_paragraph.strip():
        st.warning("Please enter both paragraphs.")
    elif not is_valid_bangla(original_paragraph):
        st.error("❌ Original Paragraph contains English text. Please enter only Bangla text.")
    elif not is_valid_bangla(suspected_paragraph):
        st.error("❌ Suspected Paragraph contains English text. Please enter only Bangla text.")
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

                # Determine plagiarism level based on cosine similarity thresholds
                if pred_label == 1:  # Plagiarized
                    if max_sim >= 0.95:
                        plagiarism_level = "Direct Plagiarism"
                        severity = "🔴 Critical"
                    elif max_sim >= 0.798:
                        plagiarism_level = "Paraphrased Plagiarism"
                        severity = "🟠 High"
                    elif max_sim >= 0.621:
                        plagiarism_level = "Semantic Similarity"
                        severity = "🟡 Medium"
                    else:
                        plagiarism_level = "Plagiarized"
                        severity = "🟢 Low"
                else:
                    plagiarism_level = "Original"
                    severity = "✅ Clear"

                results.append({
                    "sentence": suspected_sentences[i],
                    "similarity": max_sim,
                    "label": "Plagiarized" if pred_label == 1 else "Original",
                    "plagiarism_level": plagiarism_level,
                    "severity": severity,
                    "pred_label": pred_label
                })

        # Show results
        st.success("✅ Analysis Complete")
        
        # Calculate statistics for final report
        total_sentences = len(results)
        plagiarized_count = sum(1 for res in results if res['label'] == "Plagiarized")
        original_count = total_sentences - plagiarized_count
        plagiarism_percentage = (plagiarized_count / total_sentences) * 100 if total_sentences > 0 else 0
        avg_similarity = np.mean([res['similarity'] for res in results if res['label'] == "Plagiarized"]) if plagiarized_count > 0 else 0
        max_similarity = max([res['similarity'] for res in results if res['label'] == "Plagiarized"]) if plagiarized_count > 0 else 0
        
        # Count plagiarism levels
        direct_plagiarism = sum(1 for res in results if res['plagiarism_level'] == "Direct Plagiarism")
        paraphrased_plagiarism = sum(1 for res in results if res['plagiarism_level'] == "Paraphrased Plagiarism")
        semantic_similarity = sum(1 for res in results if res['plagiarism_level'] == "Semantic Similarity")
        original_clear = sum(1 for res in results if res['plagiarism_level'] == "Original")
        
        # Show individual sentence results
        st.subheader("📝 Sentence-by-Sentence Analysis")
        for idx, res in enumerate(results):
            if res["label"] == "Plagiarized":
                color = "red"
                similarity_html = f"<b>Cosine Similarity:</b> {res['similarity']:.4f}<br>"
            else:
                color = "green"
                similarity_html = ""  # Don't show similarity for original text
            
            st.markdown(f"""
                <div style="border:1px solid #ddd; padding:10px; margin-bottom:10px; border-left:4px solid {color};">
                <b>Sentence {idx+1}:</b> <span style="color:{color};"><b>{res['severity']} - {res['plagiarism_level']}</b></span><br>
                {similarity_html}<i>{res['sentence']}</i>
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
            if plagiarized_count > 0:
                st.metric("Average Similarity", f"{avg_similarity:.4f}")
                st.metric("Max Similarity", f"{max_similarity:.4f}")
        
        # Plagiarism Breakdown by Level
        st.markdown("---")
        st.subheader("📊 Plagiarism Level Breakdown")
        
        breakdown_col1, breakdown_col2, breakdown_col3, breakdown_col4 = st.columns(4)
        with breakdown_col1:
            st.metric("🔴 Direct Plagiarism", direct_plagiarism)
        with breakdown_col2:
            st.metric("🟠 Paraphrased", paraphrased_plagiarism)
        with breakdown_col3:
            st.metric("🟡 Semantic Similar", semantic_similarity)
        with breakdown_col4:
            st.metric("✅ Original/Clear", original_clear)
        
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
