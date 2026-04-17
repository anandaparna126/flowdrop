#!/usr/bin/env python
"""
FlowDrop startup script
Run: python run.py
"""
import os, subprocess, sys, webbrowser, time, threading

def open_browser():
    time.sleep(2)
    webbrowser.open('http://localhost:8000/frontend')

os.environ['DJANGO_SETTINGS_MODULE'] = 'flowchart_backend.settings'
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Add frontend serving
print("Starting FlowDrop server on http://localhost:8000")
print("Open http://localhost:8000/frontend in your browser")
threading.Thread(target=open_browser, daemon=True).start()
subprocess.run([sys.executable, '-m', 'daphne', '-p', '8000', '-b', '0.0.0.0', 'flowchart_backend.asgi:application'])
