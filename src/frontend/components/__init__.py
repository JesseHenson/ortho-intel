"""
Frontend Components - Reusable UI components and demo interfaces
"""

# Import progressive disclosure components (always available)
try:
    from .progressive_disclosure import *
except ImportError:
    pass

# NOTE: Demo components are commented out to prevent st.set_page_config() conflicts
# Import them directly when needed instead of through __init__.py

# try:
#     from .demo_frontend import *
# except ImportError:
#     pass

# try:
#     from .demo_frontend_adapter import *
# except ImportError:
#     pass

# try:
#     from .demo_frontend_enhanced import *
# except ImportError:
#     pass

# try:
#     from .demo_frontend_fixed import *
# except ImportError:
#     pass 