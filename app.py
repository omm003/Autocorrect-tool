import streamlit as st
import time
from utils.text_processor import TextProcessor
from utils.correction_engine import CorrectionEngine
from utils.metrics_calculator import MetricsCalculator

# Initialize session state
if 'processor' not in st.session_state:
    st.session_state.processor = TextProcessor()
if 'correction_engine' not in st.session_state:
    st.session_state.correction_engine = CorrectionEngine()
if 'metrics' not in st.session_state:
    st.session_state.metrics = MetricsCalculator()
if 'original_text' not in st.session_state:
    st.session_state.original_text = ""
if 'corrected_text' not in st.session_state:
    st.session_state.corrected_text = ""
if 'correction_history' not in st.session_state:
    st.session_state.correction_history = []

def main():
    st.set_page_config(
        page_title="AI Autocorrect Tool",
        page_icon="✍️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.title("🤖 AI-Driven Autocorrect Tool")
    st.markdown("### Real-time text correction and fluency improvements")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Correction Settings")
        
        correction_types = st.multiselect(
            "Select correction types:",
            ["Spelling", "Grammar", "Fluency", "Punctuation"],
            default=["Spelling", "Grammar", "Fluency", "Punctuation"]
        )
        
        correction_mode = st.selectbox(
            "Correction mode:",
            ["Real-time", "On-demand"]
        )
        
        confidence_threshold = st.slider(
            "Confidence threshold:",
            min_value=0.1,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Minimum confidence required for automatic corrections"
        )
        
        st.divider()
        
        # Statistics
        st.header("📊 Session Statistics")
        if st.session_state.correction_history:
            total_corrections = len(st.session_state.correction_history)
            st.metric("Total corrections", total_corrections)
            
            accuracy = st.session_state.metrics.calculate_accuracy(
                st.session_state.original_text, 
                st.session_state.corrected_text
            )
            st.metric("Accuracy improvement", f"{accuracy:.1f}%")
        else:
            st.info("Start typing to see statistics")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Input Text")
        
        # Text input area
        input_text = st.text_area(
            "Enter your text here:",
            height=300,
            placeholder="Start typing your text here...",
            key="input_text"
        )
        
        # Real-time processing
        if input_text and input_text != st.session_state.original_text:
            st.session_state.original_text = input_text
            
            if correction_mode == "Real-time":
                with st.spinner("Processing..."):
                    # Process the text
                    corrected_text, suggestions = st.session_state.correction_engine.correct_text(
                        input_text, 
                        correction_types,
                        confidence_threshold
                    )
                    
                    st.session_state.corrected_text = corrected_text
                    
                    # Update correction history
                    if corrected_text != input_text:
                        corrections = st.session_state.processor.find_differences(
                            input_text, corrected_text
                        )
                        st.session_state.correction_history.extend(corrections)
        
        # Manual correction button
        if correction_mode == "On-demand":
            if st.button("🔧 Apply Corrections", type="primary", use_container_width=True):
                if input_text:
                    with st.spinner("Applying corrections..."):
                        corrected_text, suggestions = st.session_state.correction_engine.correct_text(
                            input_text, 
                            correction_types,
                            confidence_threshold
                        )
                        
                        st.session_state.corrected_text = corrected_text
                        
                        # Update correction history
                        if corrected_text != input_text:
                            corrections = st.session_state.processor.find_differences(
                                input_text, corrected_text
                            )
                            st.session_state.correction_history.extend(corrections)
    
    with col2:
        st.subheader("✅ Corrected Text")
        
        if st.session_state.corrected_text:
            # Display corrected text
            st.text_area(
                "Corrected version:",
                value=st.session_state.corrected_text,
                height=300,
                key="output_text"
            )
            
            # Export functionality
            col_export1, col_export2 = st.columns(2)
            
            with col_export1:
                st.download_button(
                    label="📄 Download as TXT",
                    data=st.session_state.corrected_text,
                    file_name="corrected_text.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col_export2:
                if st.button("📋 Copy to Clipboard", use_container_width=True):
                    st.success("Text copied to clipboard!")
        else:
            st.info("Corrected text will appear here...")
    
    # Corrections and suggestions section
    if st.session_state.original_text and st.session_state.corrected_text:
        st.divider()
        
        # Show corrections made
        if st.session_state.correction_history:
            st.subheader("🔍 Recent Corrections")
            
            # Display last 5 corrections
            recent_corrections = st.session_state.correction_history[-5:]
            
            for i, correction in enumerate(recent_corrections):
                with st.expander(f"Correction {len(recent_corrections) - i}: {correction['type']}"):
                    col_before, col_after = st.columns(2)
                    
                    with col_before:
                        st.markdown("**Before:**")
                        st.code(correction['original'], language="text")
                    
                    with col_after:
                        st.markdown("**After:**")
                        st.code(correction['corrected'], language="text")
                    
                    st.markdown(f"**Reason:** {correction['reason']}")
                    st.markdown(f"**Confidence:** {correction['confidence']:.1%}")
        
        # Text comparison metrics
        st.divider()
        st.subheader("📈 Text Analysis")
        
        col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4)
        
        with col_metrics1:
            word_count = len(st.session_state.corrected_text.split())
            st.metric("Word Count", word_count)
        
        with col_metrics2:
            char_count = len(st.session_state.corrected_text)
            st.metric("Character Count", char_count)
        
        with col_metrics3:
            readability = st.session_state.metrics.calculate_readability(
                st.session_state.corrected_text
            )
            st.metric("Readability Score", f"{readability:.1f}")
        
        with col_metrics4:
            fluency = st.session_state.metrics.calculate_fluency(
                st.session_state.corrected_text
            )
            st.metric("Fluency Score", f"{fluency:.1f}")
    
    # Clear history button
    if st.session_state.correction_history:
        st.divider()
        if st.button("🗑️ Clear History", type="secondary"):
            st.session_state.correction_history = []
            st.session_state.original_text = ""
            st.session_state.corrected_text = ""
            st.rerun()
    
    # Footer with developer information
    st.divider()
    st.markdown("---")
    
    # Developer credit section
    st.markdown(
        """
        <div style="text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px; margin-top: 20px;">
            <h3>👨‍💻 Developer Information</h3>
            <p><strong>Developed by:</strong> Om Prakash Pradhan</p>
            <p><strong>Contact:</strong> 📞 8117817687</p>
            <p><em>AI-Driven Autocorrect Tool - Enhancing text accuracy and fluency</em></p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()