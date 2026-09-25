"""
Modern Dark Cobalt & Cyan Aesthetic CSS Design System for Phani AI.
Guarantees high-contrast readable typography, glowing indicators, responsive HUD cards, and sleek button interactions.
"""

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fira+Code:wght@500;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Radial Deep Cobalt Slate Theme */
    .stApp {
        background: radial-gradient(circle at top left, #0f172a 0%, #070a12 60%, #020408 100%) !important;
        color: #f8fafc !important;
    }
    
    /* Ensure ALL text elements maintain high-contrast visibility */
    p, span, label, h1, h2, h3, h4, h5, h6, li, small, legend {
        color: #f8fafc !important;
    }

    /* Headings Accent Cyan */
    [data-testid="stMarkdownContainer"] h1, 
    [data-testid="stMarkdownContainer"] h2, 
    [data-testid="stMarkdownContainer"] h3 {
        color: #38bdf8 !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    [data-testid="stMarkdownContainer"] strong {
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }

    /* Buttons Styling */
    div.stButton > button {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 10px 16px !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
        width: 100% !important;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #0284c7 0%, #06b6d4 100%) !important;
        color: #ffffff !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.5) !important;
        transform: translateY(-2px) !important;
    }

    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"] {
        background-color: rgba(11, 17, 32, 0.95) !important;
        border-right: 1px solid rgba(56, 189, 248, 0.25) !important;
        backdrop-filter: blur(16px);
    }

    /* Chat Messages Styling */
    [data-testid="stChatMessage"] {
        background-color: rgba(15, 23, 42, 0.85) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        padding: 16px 20px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3) !important;
    }

    /* Brand Header Badge */
    .brand-badge {
        display: flex;
        align-items: center;
        gap: 12px;
        background: rgba(30, 41, 59, 0.8);
        padding: 12px 16px;
        border-radius: 12px;
        border: 1px solid rgba(6, 182, 212, 0.3);
        margin-bottom: 20px;
    }
    
    .project-num {
        background: linear-gradient(135deg, #06b6d4, #3b82f6);
        color: #ffffff !important;
        font-weight: 800;
        font-size: 1.3rem;
        padding: 4px 10px;
        border-radius: 8px;
    }
    
    .brand-title {
        font-weight: 800;
        font-size: 1.25rem;
        letter-spacing: 1px;
        color: #38bdf8 !important;
    }

    /* Live HUD Card */
    .hud-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 14px;
        border-radius: 12px;
        margin-bottom: 12px;
    }

    .hud-label {
        font-size: 0.75rem;
        color: #94a3b8 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }

    .intent-val {
        font-family: 'Fira Code', monospace;
        font-size: 1.05rem;
        font-weight: 700;
        color: #38bdf8 !important;
    }

    .entity-chip {
        display: inline-block;
        background: rgba(6, 182, 212, 0.25);
        color: #67e8f9 !important;
        font-family: 'Fira Code', monospace;
        font-size: 0.78rem;
        padding: 4px 8px;
        border-radius: 6px;
        margin: 2px;
        border: 1px solid rgba(6, 182, 212, 0.4);
    }

    /* Result Card Grids */
    .phani-card {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }

    .phani-card-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #38bdf8 !important;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
</style>
"""
