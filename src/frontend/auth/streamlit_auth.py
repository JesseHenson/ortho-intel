"""
Simple authentication for Streamlit Cloud deployment
"""

import streamlit as st
import hashlib
import hmac

class StreamlitAuth:
    """Simple password authentication for demos"""
    
    def __init__(self, password="ortho2025"):
        self.password = password
    
    def check_password(self):
        """Returns True if user entered correct password"""
        
        def password_entered():
            """Checks whether a password entered by the user is correct."""
            if hmac.compare_digest(st.session_state["password"], self.password):
                st.session_state["password_correct"] = True
                del st.session_state["password"]  # Don't store password
            else:
                st.session_state["password_correct"] = False

        # First run, show input for password
        if "password_correct" not in st.session_state:
            st.markdown("### 🔐 Demo Access Required")
            st.markdown("*This is a private demo for marketing professionals*")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.text_input(
                    "Demo Password", 
                    type="password", 
                    on_change=password_entered, 
                    key="password",
                    placeholder="Enter demo password"
                )
                st.caption("Contact your demo provider for access")
            return False
        
        # Password not correct, show input + error
        elif not st.session_state["password_correct"]:
            st.markdown("### 🔐 Demo Access Required")
            st.error("Incorrect password. Please try again.")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.text_input(
                    "Demo Password", 
                    type="password", 
                    on_change=password_entered, 
                    key="password",
                    placeholder="Enter demo password"
                )
                st.caption("Contact your demo provider for access")
            return False
        
        # Password correct
        else:
            return True