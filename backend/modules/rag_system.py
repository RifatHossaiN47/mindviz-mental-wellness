import os

# Complete RAG - reads ALL 20 technique files and matches to user needs
TECHNIQUES = {
    "breathing_478": {
        "name": "4-7-8 Breathing Exercise",
        "duration": 1,
        "file": "01_breathing_478.txt",
        "good_for": ["anxiety", "stress"],
        "effects": {"anxiety": -0.25, "stress": -0.20, "mood": 0.10}
    },
    "progressive_relaxation": {
        "name": "Progressive Muscle Relaxation",
        "duration": 1,
        "file": "02_progressive_relaxation.txt",
        "good_for": ["stress", "anxiety"],
        "effects": {"anxiety": -0.30, "stress": -0.35, "mood": 0.15}
    },
    "cognitive_reframe": {
        "name": "Cognitive Reframing",
        "duration": 1,
        "file": "03_cognitive_reframing.txt",
        "good_for": ["mood", "anxiety"],
        "effects": {"anxiety": -0.15, "mood": 0.30, "stress": -0.10}
    },
    "box_breathing": {
        "name": "Box Breathing (4-4-4-4)",
        "duration": 1,
        "file": "04_box_breathing.txt",
        "good_for": ["anxiety", "stress"],
        "effects": {"anxiety": -0.20, "stress": -0.18, "mood": 0.08}
    },
    "grounding_54321": {
        "name": "5-4-3-2-1 Grounding",
        "duration": 1,
        "file": "05_grounding_54321.txt",
        "good_for": ["anxiety"],
        "effects": {"anxiety": -0.35, "stress": -0.15, "mood": 0.12}
    },
    "body_scan": {
        "name": "Body Scan Meditation",
        "duration": 1,
        "file": "06_body_scan.txt",
        "good_for": ["stress", "anxiety"],
        "effects": {"anxiety": -0.25, "stress": -0.30, "mood": 0.20}
    },
    "deep_breathing": {
        "name": "Deep Breathing Basics",
        "duration": 1,
        "file": "07_deep_breathing.txt",
        "good_for": ["anxiety", "stress"],
        "effects": {"anxiety": -0.20, "stress": -0.22, "mood": 0.08}
    },
    "mindful_walking": {
        "name": "Mindful Walking",
        "duration": 1,
        "file": "07_mindful_walking.txt",
        "good_for": ["stress", "mood"],
        "effects": {"anxiety": -0.15, "stress": -0.20, "mood": 0.20}
    },
    "gratitude_practice": {
        "name": "Gratitude Practice",
        "duration": 1,
        "file": "08_gratitude_practice.txt",
        "good_for": ["mood"],
        "effects": {"anxiety": -0.10, "stress": -0.10, "mood": 0.35}
    },
    "visualization": {
        "name": "Visualization Technique",
        "duration": 1,
        "file": "09_visualization.txt",
        "good_for": ["anxiety", "stress", "mood"],
        "effects": {"anxiety": -0.22, "stress": -0.20, "mood": 0.18}
    },
    "positive_affirmations": {
        "name": "Positive Affirmations",
        "duration": 1,
        "file": "10_positive_affirmations.txt",
        "good_for": ["mood"],
        "effects": {"anxiety": -0.08, "stress": -0.05, "mood": 0.30}
    },
    "journaling": {
        "name": "Stress Journaling",
        "duration": 1,
        "file": "11_journaling.txt",
        "good_for": ["stress", "mood"],
        "effects": {"anxiety": -0.15, "stress": -0.25, "mood": 0.20}
    },
    "music_therapy": {
        "name": "Music for Relaxation",
        "duration": 1,
        "file": "12_music_therapy.txt",
        "good_for": ["stress", "mood"],
        "effects": {"anxiety": -0.18, "stress": -0.25, "mood": 0.22}
    },
    "physical_exercise": {
        "name": "Physical Activity",
        "duration": 1,
        "file": "13_physical_exercise.txt",
        "good_for": ["mood", "stress"],
        "effects": {"anxiety": -0.20, "stress": -0.30, "mood": 0.30}
    },
    "social_connection": {
        "name": "Social Connection Practice",
        "duration": 1,
        "file": "14_social_connection.txt",
        "good_for": ["mood"],
        "effects": {"anxiety": -0.10, "stress": -0.15, "mood": 0.30}
    },
    "sleep_hygiene": {
        "name": "Sleep Hygiene Practices",
        "duration": 1,
        "file": "15_sleep_hygiene.txt",
        "good_for": ["stress", "anxiety"],
        "effects": {"anxiety": -0.18, "stress": -0.20, "mood": 0.15}
    },
    "time_in_nature": {
        "name": "Nature Therapy",
        "duration": 1,
        "file": "16_time_in_nature.txt",
        "good_for": ["stress", "mood"],
        "effects": {"anxiety": -0.18, "stress": -0.25, "mood": 0.22}
    },
    "digital_detox": {
        "name": "Digital Detox",
        "duration": 1,
        "file": "17_digital_detox.txt",
        "good_for": ["anxiety", "stress"],
        "effects": {"anxiety": -0.15, "stress": -0.20, "mood": 0.12}
    },
    "healthy_eating": {
        "name": "Nutrition for Mental Health",
        "duration": 1,
        "file": "18_healthy_eating.txt",
        "good_for": ["mood", "stress"],
        "effects": {"anxiety": -0.08, "stress": -0.12, "mood": 0.20}
    },
    "stretching": {
        "name": "Gentle Stretching",
        "duration": 1,
        "file": "19_stretching.txt",
        "good_for": ["stress"],
        "effects": {"anxiety": -0.12, "stress": -0.25, "mood": 0.12}
    },
    "professional_support": {
        "name": "Seeking Professional Help",
        "duration": 1,
        "file": "20_professional_support.txt",
        "good_for": ["anxiety", "stress", "mood"],
        "effects": {"anxiety": -0.15, "stress": -0.15, "mood": 0.15}
    }
}

def get_recommendations(metrics):
    """Get top 3 techniques based on user's metrics using ALL 20 techniques"""
    
    anxiety = metrics['anxiety']
    mood = metrics['mood']
    stress = metrics['stress']
    
    print(f"[RAG] Analyzing metrics - Anxiety: {anxiety}, Mood: {mood}, Stress: {stress}")
    print(f"[RAG] Scanning ALL {len(TECHNIQUES)} techniques for best match...")
    
    # Load all technique content for RAG-based matching
    technique_contents = {}
    for tech_id, tech_data in TECHNIQUES.items():
        content = load_technique_content(tech_data['file'])
        technique_contents[tech_id] = content
    
    # Score each technique across all 20
    scored_techniques = []
    
    for tech_id, tech_data in TECHNIQUES.items():
        score = 0
        content = technique_contents.get(tech_id, "").lower()
        
        # --- Primary condition matching (weighted heavily) ---
        
        # High anxiety? Recommend anxiety-reducing techniques
        if anxiety > 0.6 and 'anxiety' in tech_data['good_for']:
            score += 4
        elif anxiety > 0.4 and 'anxiety' in tech_data['good_for']:
            score += 2
        
        # High stress? Recommend stress-reducing techniques
        if stress > 0.6 and 'stress' in tech_data['good_for']:
            score += 4
        elif stress > 0.4 and 'stress' in tech_data['good_for']:
            score += 2
        
        # Low mood? Recommend mood-boosting techniques
        if mood < 0.4 and 'mood' in tech_data['good_for']:
            score += 4
        elif mood < 0.6 and 'mood' in tech_data['good_for']:
            score += 2
        
        # --- RAG content-based scoring ---
        # Check if the technique content mentions relevant conditions
        anxiety_keywords = ['anxiety', 'anxious', 'worried', 'panic', 'fear', 'nervous', 'racing thoughts']
        stress_keywords = ['stress', 'overwhelmed', 'pressure', 'tension', 'burnout', 'overload']
        mood_keywords = ['mood', 'sad', 'depressed', 'down', 'negative', 'low mood', 'unhappy']
        
        if anxiety > 0.5:
            for kw in anxiety_keywords:
                if kw in content:
                    score += 0.3
        
        if stress > 0.5:
            for kw in stress_keywords:
                if kw in content:
                    score += 0.3
        
        if mood < 0.5:
            for kw in mood_keywords:
                if kw in content:
                    score += 0.3
        
        # --- Effect magnitude scoring ---
        # Prefer techniques with stronger effects on the most needed dimension
        if anxiety > 0.5:
            score += abs(tech_data['effects'].get('anxiety', 0)) * 3
        if stress > 0.5:
            score += abs(tech_data['effects'].get('stress', 0)) * 3
        if mood < 0.5:
            score += tech_data['effects'].get('mood', 0) * 3
        
        # General effectiveness bonus
        score += abs(tech_data['effects'].get('anxiety', 0))
        score += abs(tech_data['effects'].get('stress', 0))
        score += tech_data['effects'].get('mood', 0)
        
        scored_techniques.append((score, tech_id, tech_data))
        print(f"[RAG]   {tech_data['name']:40s} → score: {score:.2f}")
    
    # Sort by score (highest first)
    scored_techniques.sort(reverse=True, key=lambda x: x[0])
    
    # Return top 3
    recommendations = []
    for score, tech_id, tech_data in scored_techniques[:3]:
        content = technique_contents.get(tech_id, "")
        
        recommendations.append({
            "id": tech_id,
            "name": tech_data['name'],
            "duration": tech_data['duration'],
            "effects": tech_data['effects'],
            "content": content,
            "relevance_score": round(score, 2)
        })
    
    print(f"\n[RAG] ✓ Top 3 recommendations from {len(TECHNIQUES)} techniques:")
    for i, rec in enumerate(recommendations, 1):
        print(f"[RAG]   {i}. {rec['name']} (score: {rec['relevance_score']})")
    
    return recommendations

def load_technique_content(filename):
    """Load technique instructions from file"""
    filepath = f"../data/techniques/{filename}"
    
    if not os.path.exists(filepath):
        return "Technique content not found."
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return "Error loading technique content."
