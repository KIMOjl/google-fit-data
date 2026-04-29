#!/usr/bin/env python3
"""
Chart Image Generator for Telegram
Generates PNG charts using matplotlib and saves for sending.
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

OUTPUT_DIR = Path("/home/openclaw/.openclaw/workspace/charts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_fitness_chart(steps_data, sleep_data, hr_data, dates):
    """Generate comprehensive fitness chart."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.patch.set_facecolor('#1a1a2e')
    
    # Steps chart
    ax1 = axes[0, 0]
    ax1.set_facecolor('#16213e')
    bars = ax1.bar(dates, steps_data, color='#00d4ff', alpha=0.8)
    ax1.axhline(y=10000, color='#ff4444', linestyle='--', alpha=0.7, label='Goal')
    ax1.set_title('👟 Daily Steps', color='white', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Steps', color='white')
    ax1.tick_params(colors='white')
    ax1.legend(facecolor='#16213e', edgecolor='white', labelcolor='white')
    for spine in ax1.spines.values():
        spine.set_color('white')
    
    # Sleep chart
    ax2 = axes[0, 1]
    ax2.set_facecolor('#16213e')
    ax2.plot(dates, sleep_data, color='#7b2cbf', marker='o', linewidth=2, markersize=8)
    ax2.axhline(y=7.5, color='#00ff88', linestyle='--', alpha=0.7, label='Optimal')
    ax2.fill_between(dates, sleep_data, alpha=0.3, color='#7b2cbf')
    ax2.set_title('😴 Sleep Hours', color='white', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Hours', color='white')
    ax2.tick_params(colors='white')
    ax2.legend(facecolor='#16213e', edgecolor='white', labelcolor='white')
    for spine in ax2.spines.values():
        spine.set_color('white')
    
    # Heart rate chart
    ax3 = axes[1, 0]
    ax3.set_facecolor('#16213e')
    ax3.plot(dates, hr_data, color='#ff6b6b', marker='o', linewidth=2, markersize=8)
    ax3.axhline(y=80, color='#ffc107', linestyle='--', alpha=0.7, label='Elevated')
    ax3.axhline(y=60, color='#00ff88', linestyle='--', alpha=0.7, label='Resting')
    ax3.fill_between(dates, hr_data, alpha=0.3, color='#ff6b6b')
    ax3.set_title('❤️ Heart Rate (bpm)', color='white', fontsize=14, fontweight='bold')
    ax3.set_ylabel('BPM', color='white')
    ax3.tick_params(colors='white')
    ax3.legend(facecolor='#16213e', edgecolor='white', labelcolor='white')
    for spine in ax3.spines.values():
        spine.set_color('white')
    
    # Training load gauge
    ax4 = axes[1, 1]
    ax4.set_facecolor('#16213e')
    
    # Create a simple gauge visualization
    categories = ['Z1\nRecovery', 'Z2\nEndurance', 'Z3\nTempo', 'Z4\nThreshold', 'Z5\nVO2 Max']
    values = [20, 45, 20, 10, 5]  # Example distribution
    colors = ['#00ff88', '#00d4ff', '#ffc107', '#ff6b6b', '#ff4444']
    
    bars = ax4.barh(categories, values, color=colors, alpha=0.8)
    ax4.set_title('🏋️ Training Zones', color='white', fontsize=14, fontweight='bold')
    ax4.set_xlabel('% of Training', color='white')
    ax4.tick_params(colors='white')
    for spine in ax4.spines.values():
        spine.set_color('white')
    
    plt.tight_layout()
    
    # Save
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M')
    filepath = OUTPUT_DIR / f'fitness_chart_{timestamp}.png'
    plt.savefig(filepath, dpi=150, bbox_inches='tight', 
                facecolor='#1a1a2e', edgecolor='none')
    plt.close()
    
    return str(filepath)

def generate_weekly_summary_chart(weekly_data):
    """Generate weekly summary chart."""
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#16213e')
    
    days = list(weekly_data.keys())
    steps = [d['steps'] for d in weekly_data.values()]
    
    # Create gradient bars
    bars = ax.bar(days, steps, color='#00d4ff', alpha=0.8)
    
    # Color bars based on goal achievement
    for bar, step_count in zip(bars, steps):
        if step_count >= 10000:
            bar.set_color('#00ff88')
        elif step_count >= 5000:
            bar.set_color('#ffc107')
        else:
            bar.set_color('#ff4444')
    
    ax.axhline(y=10000, color='white', linestyle='--', alpha=0.5, label='Goal')
    ax.set_title('📊 Weekly Step Progress', color='white', fontsize=16, fontweight='bold')
    ax.set_ylabel('Steps', color='white')
    ax.tick_params(colors='white')
    ax.legend(facecolor='#16213e', edgecolor='white', labelcolor='white')
    for spine in ax.spines.values():
        spine.set_color('white')
    
    plt.tight_layout()
    
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M')
    filepath = OUTPUT_DIR / f'weekly_chart_{timestamp}.png'
    plt.savefig(filepath, dpi=150, bbox_inches='tight',
                facecolor='#1a1a2e', edgecolor='none')
    plt.close()
    
    return str(filepath)

def generate_single_metric_chart(metric_name, values, dates, goal_value=None, color='#00d4ff'):
    """Generate a single metric chart."""
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#16213e')
    
    ax.plot(dates, values, color=color, marker='o', linewidth=3, markersize=10)
    ax.fill_between(dates, values, alpha=0.3, color=color)
    
    if goal_value:
        ax.axhline(y=goal_value, color='white', linestyle='--', alpha=0.5, label='Goal')
    
    ax.set_title(f'{metric_name}', color='white', fontsize=16, fontweight='bold')
    ax.tick_params(colors='white')
    ax.legend(facecolor='#16213e', edgecolor='white', labelcolor='white')
    for spine in ax.spines.values():
        spine.set_color('white')
    
    plt.tight_layout()
    
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M')
    safe_name = metric_name.replace(' ', '_').replace(':', '').lower()
    filepath = OUTPUT_DIR / f'{safe_name}_{timestamp}.png'
    plt.savefig(filepath, dpi=150, bbox_inches='tight',
                facecolor='#1a1a2e', edgecolor='none')
    plt.close()
    
    return str(filepath)

if __name__ == "__main__":
    # Test with sample data
    dates = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    steps = [5200, 8100, 3165, 0, 0, 0, 0]
    sleep = [7.5, 6.8, 0, 0, 0, 0, 0]
    hr = [62, 65, 63.9, 0, 0, 0, 0]
    
    chart_path = generate_fitness_chart(steps, sleep, hr, dates)
    print(f"✅ Chart generated: {chart_path}")
    
    weekly = {
        'Mon': {'steps': 5200},
        'Tue': {'steps': 8100},
        'Wed': {'steps': 3165},
    }
    weekly_path = generate_weekly_summary_chart(weekly)
    print(f"✅ Weekly chart: {weekly_path}")
