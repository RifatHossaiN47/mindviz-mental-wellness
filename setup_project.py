"""MindViz Project Setup Script
Run this once to set up everything automatically"""

import os
import sys

def create_folders():
    """Create all necessary folders"""
    print("📁 Creating project folders...")
    
    folders = [
        "data",
        "data/sessions",
        "data/techniques",
        "backend",
        "backend/modules",
        "frontend",
        "frontend/screens",
        "frontend/opengl",
        "frontend/utils"
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"  ✓ Created {folder}")
    
    print("✅ All folders created!\n")

def create_remaining_techniques():
    """Create remaining technique files (7-20)"""
    print("📝 Creating additional technique files...")
    
    techniques = {
        "07_deep_breathing.txt": """DEEP BREATHING BASICS
Simple deep breathing to calm your nervous system immediately.

INSTRUCTIONS:
1. Sit or lie comfortably
2. Place one hand on your chest, one on your belly
3. Breathe in slowly through your nose for 4 counts
4. Your belly should rise more than your chest
5. Exhale slowly through your mouth for 6 counts
6. Repeat for 5-10 minutes

BENEFITS: Instant calm, reduced heart rate, lower blood pressure
DURATION: 5-10 minutes
BEST FOR: Quick stress relief, anxiety""",

        "07_mindful_walking.txt": """MINDFUL WALKING
Walking meditation that combines movement with awareness.

INSTRUCTIONS:
1. Walk slowly in a quiet place
2. Focus on the sensation of each step
3. Notice how your feet touch the ground
4. Pay attention to your breathing
5. When mind wanders, return focus to steps
6. Continue for 10-15 minutes

BENEFITS: Combines exercise with mindfulness, reduces rumination
DURATION: 10-15 minutes
BEST FOR: Restlessness, combining movement with mindfulness""",

        "08_gratitude_practice.txt": """GRATITUDE PRACTICE
Daily practice to shift focus toward positive aspects of life.

INSTRUCTIONS:
1. Set aside 5 minutes daily
2. Write or think of 3 things you're grateful for
3. Be specific (not just "family" but "my sister helped me today")
4. Feel the emotion of gratitude
5. Reflect on why you're grateful for each item

BENEFITS: Improved mood, better relationships, increased optimism
DURATION: 5 minutes daily
BEST FOR: Low mood, negative thinking""",

        "09_visualization.txt": """VISUALIZATION TECHNIQUE
Mental imagery to reduce anxiety and improve mood.

INSTRUCTIONS:
1. Close your eyes and relax
2. Imagine a peaceful, safe place
3. Engage all senses - what do you see, hear, smell, feel?
4. Stay in this place for 5-10 minutes
5. Return slowly, bringing the calm with you

BENEFITS: Reduces anxiety, improves mood, enhances performance
DURATION: 5-10 minutes
BEST FOR: Anxiety, stress, performance preparation""",

        "10_positive_affirmations.txt": """POSITIVE AFFIRMATIONS
Replace negative self-talk with empowering statements.

INSTRUCTIONS:
1. Choose affirmations that resonate:
   - "I am capable and strong"
   - "I handle challenges with grace"
   - "I am worthy of good things"
2. Repeat each 10 times
3. Say them with feeling and belief
4. Practice morning and night

BENEFITS: Improved self-esteem, reduced negative thinking
DURATION: 3-5 minutes
BEST FOR: Low self-esteem, negative self-talk""",

        "11_journaling.txt": """STRESS JOURNALING
Write to process emotions and gain clarity.

INSTRUCTIONS:
1. Set aside 10-15 minutes
2. Write freely about your feelings
3. Don't worry about grammar or structure
4. Include: What happened? How did I feel? What can I learn?
5. Review weekly to notice patterns

BENEFITS: Emotional release, self-understanding, problem clarity
DURATION: 10-15 minutes
BEST FOR: Processing emotions, self-reflection""",

        "12_music_therapy.txt": """MUSIC FOR RELAXATION
Use music to regulate emotions and reduce stress.

INSTRUCTIONS:
1. Choose calming music (classical, nature sounds, lo-fi)
2. Sit or lie comfortably
3. Close your eyes and listen actively
4. Focus on different instruments
5. Let the music wash over you for 10-15 minutes

BENEFITS: Mood improvement, stress reduction, emotional release
DURATION: 10-15 minutes
BEST FOR: Emotional regulation, relaxation""",

        "13_physical_exercise.txt": """PHYSICAL ACTIVITY FOR MENTAL HEALTH
Movement to boost mood and reduce stress.

INSTRUCTIONS:
1. Choose any activity you enjoy (walking, dancing, sports)
2. Aim for 20-30 minutes
3. Focus on how your body feels
4. Notice your breathing and heartbeat
5. Cool down with stretching

BENEFITS: Endorphin release, better sleep, reduced anxiety
DURATION: 20-30 minutes
BEST FOR: Mood boost, stress relief, energy""",

        "14_social_connection.txt": """SOCIAL CONNECTION PRACTICE
Strengthen relationships to boost mental wellness.

INSTRUCTIONS:
1. Reach out to someone you care about
2. Have a meaningful conversation (not just texting)
3. Share how you're feeling
4. Listen actively to them
5. Plan regular connection time

BENEFITS: Reduced loneliness, emotional support, better mood
DURATION: 15-30 minutes
BEST FOR: Loneliness, isolation, needing support""",

        "15_sleep_hygiene.txt": """SLEEP HYGIENE PRACTICES
Improve sleep quality for better mental health.

INSTRUCTIONS:
1. Set consistent sleep/wake times
2. Avoid screens 1 hour before bed
3. Keep bedroom cool and dark
4. No caffeine after 2 PM
5. Practice relaxation before sleep

BENEFITS: Better mood, improved focus, reduced anxiety
DURATION: Ongoing practice
BEST FOR: Insomnia, poor sleep, fatigue""",

        "16_time_in_nature.txt": """NATURE THERAPY
Spend time outdoors for mental restoration.

INSTRUCTIONS:
1. Spend 15-30 minutes outside
2. Notice natural elements around you
3. Breathe fresh air deeply
4. Walk barefoot if possible
5. Minimize distractions (phone away)

BENEFITS: Reduced stress, improved mood, better focus
DURATION: 15-30 minutes
BEST FOR: Stress, mental fatigue, disconnection""",

        "17_digital_detox.txt": """DIGITAL DETOX
Reduce screen time to improve mental clarity.

INSTRUCTIONS:
1. Set specific "no phone" times
2. Remove social media apps temporarily
3. Use grayscale mode
4. Replace scrolling with other activities
5. Track your screen time

BENEFITS: Better sleep, reduced anxiety, improved focus
DURATION: Ongoing practice
BEST FOR: Phone addiction, sleep issues, anxiety""",

        "18_healthy_eating.txt": """NUTRITION FOR MENTAL HEALTH
Eat to support your emotional wellbeing.

INSTRUCTIONS:
1. Eat regular, balanced meals
2. Include omega-3s (fish, nuts)
3. Stay hydrated (8 glasses water)
4. Limit sugar and caffeine
5. Notice how foods affect your mood

BENEFITS: Stable mood, better energy, reduced anxiety
DURATION: Ongoing practice
BEST FOR: Mood swings, energy levels""",

        "19_stretching.txt": """GENTLE STRETCHING
Release physical tension through stretching.

INSTRUCTIONS:
1. Start with neck rolls
2. Shoulder shrugs and rolls
3. Side bends
4. Forward fold
5. Hold each stretch 20-30 seconds
6. Breathe deeply throughout

BENEFITS: Reduced muscle tension, improved circulation
DURATION: 5-10 minutes
BEST FOR: Physical tension, desk work stress""",

        "20_professional_support.txt": """SEEKING PROFESSIONAL HELP
Know when and how to get professional support.

WHEN TO SEEK HELP:
- Persistent sad or anxious feelings (2+ weeks)
- Thoughts of self-harm
- Unable to do daily activities
- Substance use to cope
- Overwhelming stress

HOW TO GET HELP:
1. Talk to your doctor
2. Contact a therapist or counselor
3. Call mental health helplines
4. Reach out to trusted adults
5. Use university counseling services

RESOURCES:
- Mental Health Helpline: Available 24/7
- University Counseling: Free for students
- Online Therapy: BetterHelp, Talkspace

BENEFITS: Expert guidance, evidence-based treatment, support
NOTE: Seeking help is a sign of strength, not weakness"""
    }
    
    for filename, content in techniques.items():
        filepath = f"data/techniques/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Created {filename}")
    
    print("✅ All technique files created!\n")

def create_env_template():
    """Create .env template file"""
    print("🔐 Creating .env template...")
    
    env_content = """# MindViz Environment Variables
# Get your free API key from: https://aistudio.google.com/app/apikey

GEMINI_API_KEY=your_api_key_here

# Backend URL (don't change)
BACKEND_URL=http://localhost:8000"""
    
    with open("backend/.env.example", 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("  ✓ Created backend/.env.example")
    print("\n⚠️  IMPORTANT: You need to:")
    print("  1. Go to https://aistudio.google.com/app/apikey")
    print("  2. Click 'Create API Key'")
    print("  3. Copy the key")
    print("  4. Create backend/.env file")
    print("  5. Add: GEMINI_API_KEY=your_key_here\n")

def create_readme():
    """Create README with instructions"""
    print("📖 Creating README...")
    
    readme_content = """# 🌱 MindViz - Mental Wellness Visualization

AI-powered mental health visualization system with 3D graphics and guided therapy.

## 🚀 Quick Start

### 1. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
pip install -r requirements.txt
```

### 2. Get Gemini API Key (FREE)

1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Create `backend/.env` file with:
```
GEMINI_API_KEY=your_key_here
```

### 3. Run the Project

**Terminal 1 - Backend:**
```bash
cd backend
python server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python main.py
```

## ✨ Features

- 🧠 AI-powered emotion analysis
- 🌦️ 3D garden visualization
- 💊 20 evidence-based techniques
- 🧘 Guided breathing exercises
- 📊 Progress tracking
- 🔒 100% local data storage

## 🆘 Troubleshooting

**Backend not connecting:**
- Make sure backend runs first
- Check http://localhost:8000

**Gemini API error:**
- System falls back to keyword analysis
- Check .env file

**OpenGL issues:**
- Update graphics drivers
- Visualization optional

---
Made with ❤️ for mental wellness
"""
    
    with open("README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("  ✓ Created README.md\n")

def main():
    print("=" * 60)
    print("🌱 MindViz Project Setup")
    print("=" * 60)
    print()
    
    try:
        create_folders()
        create_remaining_techniques()
        create_env_template()
        create_readme()
        
        print("=" * 60)
        print("✅ SETUP COMPLETE!")
        print("=" * 60)
        print()
        print("📋 NEXT STEPS:")
        print()
        print("1. Get Gemini API key:")
        print("   https://aistudio.google.com/app/apikey")
        print()
        print("2. Create backend/.env file with your key")
        print()
        print("3. Install dependencies:")
        print("   cd backend && pip install -r requirements.txt")
        print("   cd frontend && pip install -r requirements.txt")
        print()
        print("4. Run backend: cd backend && python server.py")
        print("5. Run frontend: cd frontend && python main.py")
        print()
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        print(f"Details: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()