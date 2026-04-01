import math

def map_to_visualization(metrics):
    """Convert emotional metrics to rich visual parameters for the garden renderer"""
    
    anxiety = metrics['anxiety']
    mood = metrics['mood']
    stress = metrics['stress']
    
    # Calculate overall wellbeing (0=bad, 1=good)
    wellbeing = (1 - anxiety + mood + (1 - stress)) / 3
    
    # --- SKY & ATMOSPHERE ---
    # Sky color: stormy gray when bad, vivid blue when good, warm sunset when moderate
    if wellbeing > 0.7:
        # Bright clear sky
        sky_color = [0.35, 0.65, 0.95]
    elif wellbeing > 0.5:
        # Partly cloudy warm sky
        sky_color = [0.45, 0.6, 0.85]
    elif wellbeing > 0.3:
        # Overcast grayish
        sky_color = [0.5, 0.52, 0.6]
    else:
        # Dark stormy
        sky_color = [0.3, 0.32, 0.4]
    
    # Time of day effect (mood affects lighting warmth)
    time_of_day = max(0.0, min(1.0, mood))  # 0=night, 1=bright day
    
    # Sun intensity (higher mood = brighter sun)
    sun_intensity = 0.3 + (mood * 0.7)
    sun_color = [
        min(1.0, 0.8 + mood * 0.2),
        min(1.0, 0.6 + mood * 0.35),
        0.1 + mood * 0.3
    ]
    
    # Horizon glow color
    if wellbeing > 0.6:
        horizon_color = [0.95, 0.85, 0.6]  # Warm golden
    elif wellbeing > 0.4:
        horizon_color = [0.7, 0.6, 0.5]  # Muted warm
    else:
        horizon_color = [0.4, 0.38, 0.4]  # Cold gray
    
    # --- CLOUDS & WEATHER ---
    cloud_darkness = 0.15 + (stress * 0.7)
    cloud_count = int(2 + stress * 8)
    
    # Rain intensity (combined anxiety + stress)
    rain_intensity = max(0.0, ((anxiety + stress) / 2) - 0.15)
    
    # Lightning for extreme anxiety
    lightning = anxiety > 0.8
    
    # Rainbow appears when transitioning from bad (shows hope)
    show_rainbow = (wellbeing > 0.35 and wellbeing < 0.65 and rain_intensity > 0.2)
    
    # Fog/mist (more when stressed/anxious)
    fog_density = max(0.0, (anxiety + stress) / 2 - 0.2)
    
    # --- WIND ---
    wind_speed = anxiety * 3.5
    
    # --- FLORA ---
    # Flowers
    flower_droop = max(0.0, 1.0 - mood)
    flower_health = mood
    flower_count = int(4 + mood * 8)  # More flowers when mood is good
    flower_bloom = max(0.0, mood - 0.2)  # How open the flowers are
    
    # Trees
    tree_health = (mood + (1 - stress)) / 2
    leaf_density = 0.3 + tree_health * 0.7
    leaf_fall_rate = max(0.0, stress - 0.3)  # Leaves fall when stressed
    
    # Grass color (brown when sad, vibrant green when happy)
    grass_color = [
        max(0.15, 0.35 - (mood * 0.2)),   # R (less red = greener)
        min(0.75, 0.25 + (mood * 0.5)),    # G (more green when happy)
        max(0.1, 0.15 + (mood * 0.15))     # B
    ]
    
    # --- WATER FEATURE ---
    water_clarity = wellbeing  # Clear when well, murky when not
    water_ripple_speed = 0.5 + anxiety * 2.0  # Choppy when anxious
    
    # --- CREATURES ---
    butterfly_count = int(max(0, (mood - 0.4) * 12))  # Butterflies when mood > 0.4
    bird_count = int(max(0, (wellbeing - 0.3) * 8))
    firefly_count = int(max(0, ((1 - anxiety) - 0.3) * 10))
    
    # --- SPECIAL EFFECTS ---
    # Light rays through clouds (hope) — only at clearly positive wellbeing
    god_rays = wellbeing > 0.65 and cloud_count > 3
    
    # Stars visible (low mood = night time feel)
    star_count = int(max(0, (1 - mood) * 15)) if mood < 0.4 else 0
    
    # Particle sparkle (high wellbeing)
    sparkle_intensity = max(0.0, wellbeing - 0.5) * 2
    
    # Ground features
    path_visibility = 0.5 + wellbeing * 0.5  # Clearer path when well
    
    # Mountains in background
    mountain_snow = max(0.0, 1.0 - stress)  # Snow-capped when calm
    mountain_color = [
        0.3 + stress * 0.15,
        0.3 + (1 - stress) * 0.15,
        0.35 + (1 - stress) * 0.1
    ]
    
    return {
        "sky_color": [round(c, 3) for c in sky_color],
        "horizon_color": [round(c, 3) for c in horizon_color],
        "sun_intensity": round(sun_intensity, 2),
        "sun_color": [round(c, 3) for c in sun_color],
        "time_of_day": round(time_of_day, 2),
        "cloud_darkness": round(cloud_darkness, 2),
        "cloud_count": cloud_count,
        "rain_intensity": round(rain_intensity, 2),
        "lightning": lightning,
        "show_rainbow": show_rainbow,
        "fog_density": round(fog_density, 2),
        "wind_speed": round(wind_speed, 2),
        "flower_droop": round(flower_droop, 2),
        "flower_health": round(flower_health, 2),
        "flower_count": flower_count,
        "flower_bloom": round(flower_bloom, 2),
        "tree_health": round(tree_health, 2),
        "leaf_density": round(leaf_density, 2),
        "leaf_fall_rate": round(leaf_fall_rate, 2),
        "grass_color": [round(c, 3) for c in grass_color],
        "water_clarity": round(water_clarity, 2),
        "water_ripple_speed": round(water_ripple_speed, 2),
        "butterfly_count": butterfly_count,
        "bird_count": bird_count,
        "firefly_count": firefly_count,
        "god_rays": god_rays,
        "star_count": star_count,
        "sparkle_intensity": round(sparkle_intensity, 2),
        "path_visibility": round(path_visibility, 2),
        "mountain_snow": round(mountain_snow, 2),
        "mountain_color": [round(c, 3) for c in mountain_color],
        "wellbeing": round(wellbeing, 2)
    }
