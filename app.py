import streamlit as st
 
# Helper Functions
from src.helper import get_pdf_text, get_text_chunks, get_vector_store, user_input
 
def main():
    st.set_page_config('DocuBOT')
    st.header('PDF Document Q&A ChatBot')
 
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chatHistory" not in st.session_state:
        st.session_state.chatHistory = []
    
    user_question = st.text_input("Ask a question to the PDF File(s)")
    if user_question:
        response = user_input(user_question)
        st.session_state.chatHistory.append({
            'question': user_question,
            'answer': response['output_text']
        })
 
    if st.session_state.chatHistory:
        st.subheader("Conversation History:")
        for chat in st.session_state.chatHistory:
            st.write(f"**Q:** {chat['question']}")
            st.write(f"**A:** {chat['answer']}")
            st.markdown("---")
 
    with st.sidebar:
        st.title("Menu:")
        pdf_docs = st.file_uploader("Upload Your PDF File(s)", accept_multiple_files=True)
        if st.button("Submit & Proceed"):
            with st.spinner("Processing..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                st.session_state.conversation = get_vector_store(text_chunks)
 
                st.success("Done")
 
 
if __name__ == "__main__":
    main()
