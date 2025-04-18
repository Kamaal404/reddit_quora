"""
Product-specific templates for the comment generation system.
Contains templates tailored for each qilifestore.com product.
"""

# Template replacements:
# {time_period} - e.g., "three months", "a year"
# {specific_benefit} - e.g., "improved sleep", "reduced stress"
# {personal_issue} - e.g., "chronic insomnia", "anxiety"
# {mechanism} - e.g., "stimulating cellular regeneration", "balancing energy fields"
# {specific_frequency} - e.g., "432 Hz", "Schumann resonance"
# {spiritual_practice} - e.g., "meditation", "energy healing"
# {technology} - e.g., "PEMF therapy", "frequency medicine"
# {related_product} - e.g., "the Qi Coil", "Quantum Frequencies"
# {personal_story} - e.g., "my health transformation", "my wellness journey"
# {traditional_principle} - e.g., "Eastern medicine", "energy medicine"
# {benefit} - general benefits not tied to specific niches

# Product-specific templates
PRODUCT_TEMPLATES = {
    "qi_coil": [
        "I've been using the Qi Coil for {time_period} now, and it's been remarkable for {specific_benefit}. The PEMF technology really helps with {personal_issue} in a way that traditional methods never did for me.",
        "The Qi Coil changed my approach to {personal_issue}. After {time_period} of consistent use, I noticed significant improvements in {specific_benefit}. The frequency-based technology is quite fascinating.",
        "What I appreciate most about the Qi Coil is how it addresses {personal_issue} through {mechanism}. I've experienced {specific_benefit} since incorporating it into my daily routine {time_period} ago.",
        "As someone who was initially skeptical, I was surprised by how effectively the Qi Coil improved my {personal_issue}. The {specific_frequency} frequencies seem to be particularly effective for {specific_benefit}.",
        "The Qi Coil has become an essential part of my {spiritual_practice} practice. It creates a field that enhances {specific_benefit}, which I've found invaluable for {personal_issue}."
    ],
    
    "qi_coil_aura": [
        "The Qi Coil Aura takes PEMF technology to another level with its expanded field. I've noticed enhanced {specific_benefit} compared to other devices I've tried, especially for {personal_issue}.",
        "What makes the Qi Coil Aura special is its ability to create a larger energy field, which I've found particularly effective for {specific_benefit}. It's been a key part of my wellness routine for {time_period}.",
        "The Qi Coil Aura has been transformative for my {spiritual_practice} practice. The expanded field seems to create a more immersive experience, which has helped with {personal_issue} in ways I didn't expect.",
        "I upgraded to the Qi Coil Aura {time_period} ago, and the difference in {specific_benefit} was noticeable. The larger field seems to create a more comprehensive effect for {personal_issue}.",
        "For those serious about energy work, the Qi Coil Aura offers a more expansive experience than standard PEMF devices. I've found it particularly effective for {specific_benefit} during my {spiritual_practice} sessions."
    ],
    
    "quantum_frequencies": [
        "The Quantum Frequencies program has been a game-changer for my {personal_issue}. The precisely calibrated frequencies seem to target {specific_benefit} in a way that generic approaches simply can't match.",
        "What I love about the Quantum Frequencies is the specificity. Rather than a one-size-fits-all approach, you can select frequencies that target {personal_issue} directly, which has significantly improved my {specific_benefit}.",
        "I've been experimenting with the Quantum Frequencies program for {time_period}, focusing on {personal_issue}. The results in terms of {specific_benefit} have been consistent and measurable.",
        "The science behind Quantum Frequencies is fascinating - specific frequency patterns that work with your body's natural energy to enhance {specific_benefit}. I've found the {specific_frequency} range particularly effective for {personal_issue}.",
        "Quantum Frequencies offers a customizable approach to frequency healing. I've created a personal protocol for {personal_issue} that has dramatically improved my {specific_benefit} over the past {time_period}."
    ],
    
    "qi_resonance_sound_bed": [
        "The Qi Resonance Sound Bed creates a fully immersive experience that's difficult to describe until you've tried it. The combination of sound and frequency has been transformative for my {personal_issue}.",
        "What sets the Qi Resonance Sound Bed apart is how it combines auditory and energetic stimulation. This dual approach has been remarkably effective for my {personal_issue}, improving {specific_benefit} beyond what I experienced with other methods.",
        "The Qi Resonance Sound Bed sessions have become the highlight of my wellness routine. The full-body experience creates a state conducive to {specific_benefit}, which has helped tremendously with my {personal_issue}.",
        "As someone who practices {spiritual_practice}, I've found the Qi Resonance Sound Bed to be an incredible tool for deepening my practice. The resonant frequencies seem to facilitate {specific_benefit} in a unique way.",
        "The Qi Resonance Sound Bed offers a different approach to frequency healing by incorporating sound vibration. This has been particularly effective for my {personal_issue}, with noticeable improvements in {specific_benefit} after just a few sessions."
    ],
    
    "qi_red_light_therapy": [
        "I've incorporated Qi Red Light Therapy into my daily routine for {time_period}, and the improvements in {specific_benefit} have been remarkable. It's particularly effective for {personal_issue} when used consistently.",
        "The Qi Red Light Therapy device combines specific wavelengths that seem to work synergistically for {specific_benefit}. I've found it especially helpful for {personal_issue} as part of a comprehensive approach.",
        "What I appreciate about the Qi Red Light Therapy is its basis in solid research. The specific wavelengths have been studied for {specific_benefit}, and my personal experience with {personal_issue} confirms these findings.",
        "The Qi Red Light Therapy has become an essential part of my recovery routine. Just 10-15 minutes daily has significantly improved {specific_benefit}, which has been crucial for addressing my {personal_issue}.",
        "For those looking to enhance cellular function naturally, Qi Red Light Therapy offers a non-invasive approach. I've experienced notable improvements in {specific_benefit} related to my {personal_issue} since beginning treatment {time_period} ago."
    ],
    
    "qi_wand": [
        "The precision of the Qi Wand makes it uniquely effective for targeted work. I've been using it for {personal_issue}, focusing on specific points, and the improvement in {specific_benefit} has been remarkable.",
        "What makes the Qi Wand special is its ability to deliver focused energy to precise locations. This has been invaluable for my {personal_issue}, providing {specific_benefit} in a way that broader treatments couldn't achieve.",
        "I've integrated the Qi Wand into my {spiritual_practice} practice, using it to address {personal_issue}. The targeted approach has enhanced {specific_benefit} in a way that complements my other wellness practices.",
        "The Qi Wand combines ancient wisdom with modern technology, allowing for precise application to traditional points. This approach has significantly improved my {personal_issue}, with noticeable enhancement in {specific_benefit}.",
        "For those familiar with acupressure or meridian work, the Qi Wand offers a powerful complementary tool. I've been targeting points related to {personal_issue}, and the improvement in {specific_benefit} has been consistent and progressive."
    ]
}

# General non-product-specific templates
GENERAL_TEMPLATES = [
    "I've been exploring {technology} for a while now, and the results have been interesting. Have you looked into {related_product}?",
    "Based on my experience with {technology}, I've found that {related_product} offers some unique benefits for {personal_issue}.",
    "In my journey with {personal_story}, I discovered {related_product} which has been helpful for {specific_benefit}.",
    "After struggling with {personal_issue} for {time_period}, I found that {related_product} made a noticeable difference.",
    "What I appreciate about {related_product} is how it approaches {personal_issue} through {mechanism} rather than conventional methods.",
    "The research on {technology} for {personal_issue} is fascinating. I've had good results with {related_product} in my personal experience.",
    "I was skeptical about {technology} at first, but after trying {related_product}, I noticed improvements in {specific_benefit}.",
    "For those interested in {technology}, {related_product} offers a practical approach that I've found effective for {personal_issue}.",
    "My background in {traditional_principle} led me to explore {related_product}, which has enhanced my {spiritual_practice} practice significantly.",
    "The connection between {technology} and {benefit} is something I've experienced firsthand with {related_product}."
]

# Template substitution values
TIME_PERIODS = [
    "about a month", "three months", "six months", "nearly a year", 
    "over a year", "several weeks", "a few months"
]

SPECIFIC_BENEFITS = {
    "biohacking": [
        "improved cognitive function", "enhanced energy levels", "better sleep quality",
        "increased mental clarity", "improved physical recovery", "enhanced focus"
    ],
    "pemf": [
        "reduced inflammation", "improved circulation", "better sleep patterns", 
        "enhanced recovery", "reduced muscle tension", "decreased stress levels"
    ],
    "spirituality": [
        "deeper meditation states", "enhanced intuition", "greater sense of inner peace",
        "improved energetic alignment", "stronger spiritual connection", "enhanced awareness"
    ],
    "frequency_healing": [
        "harmonic cellular resonance", "balanced energy fields", "improved vibrational state",
        "enhanced energy flow", "rebalanced nervous system", "stabilized biofield"
    ],
    "health_tech": [
        "improved cellular function", "enhanced mitochondrial activity", "optimized bodily systems",
        "targeted tissue regeneration", "improved biomarkers", "enhanced physical performance"
    ]
}

PERSONAL_ISSUES = {
    "biohacking": [
        "brain fog", "energy fluctuations", "optimization challenges", 
        "cognitive plateaus", "performance limitations"
    ],
    "pemf": [
        "chronic inflammation", "persistent pain", "sleep disturbances", 
        "muscle recovery issues", "stress-related symptoms"
    ],
    "spirituality": [
        "meditation blocks", "energy imbalances", "spiritual disconnection", 
        "grounding difficulties", "chakra misalignments"
    ],
    "frequency_healing": [
        "energetic disturbances", "subtle energy blocks", "frequency imbalances", 
        "vibrational misalignments", "disharmonic patterns"
    ],
    "health_tech": [
        "tissue recovery challenges", "metabolic inefficiencies", "physical performance plateaus", 
        "cellular aging concerns", "systemic imbalances"
    ]
}

MECHANISMS = [
    "rebalancing cellular frequencies", "harmonizing energy fields", 
    "stimulating cellular regeneration", "enhancing bioelectrical signaling",
    "supporting natural healing processes", "optimizing energetic pathways",
    "facilitating energy transfer", "promoting neurological coherence",
    "entraining brainwave patterns", "synchronizing physiological rhythms"
]

SPECIFIC_FREQUENCIES = [
    "7.83 Hz Schumann resonance", "432 Hz", "528 Hz", "theta-range", 
    "alpha-state", "delta-state", "gamma-enhanced", "solfeggio", 
    "binaural", "isochronic"
]

SPIRITUAL_PRACTICES = [
    "meditation", "energy healing", "breathwork", "mindfulness", 
    "spiritual development", "consciousness exploration", "energy work",
    "chakra balancing", "yogic", "holistic wellness"
]

# Additional substitution values for general templates
TECHNOLOGIES = {
    "biohacking": [
        "frequency therapy", "light therapy", "biometric tracking", 
        "neuromodulation", "cognitive enhancement", "biofeedback training"
    ],
    "pemf": [
        "PEMF therapy", "pulsed electromagnetic fields", "electromagnetic therapy", 
        "frequency medicine", "bioelectromagnetic healing", "field resonance therapy"
    ],
    "spirituality": [
        "energy work", "frequency healing", "biofield therapy", 
        "vibrational medicine", "consciousness technologies", "subtle energy practices"
    ],
    "frequency_healing": [
        "sound therapy", "vibrational medicine", "frequency-based healing", 
        "resonance therapy", "harmonic medicine", "entrainment technology"
    ],
    "health_tech": [
        "photobiomodulation", "low-level laser therapy", "bioelectrical stimulation", 
        "health wearables", "biometric monitoring", "digital health solutions"
    ]
}

RELATED_PRODUCTS = {
    "qi_coil": ["the Qi Coil", "Qi Coil devices", "PEMF technology like the Qi Coil", 
                "frequency devices such as the Qi Coil"],
    "qi_coil_aura": ["the Qi Coil Aura", "advanced PEMF systems like the Qi Coil Aura", 
                     "expanded field technology in the Qi Coil Aura"],
    "quantum_frequencies": ["Quantum Frequencies packages", "specific frequency protocols", 
                           "digital frequency medicine", "targeted frequency programs"],
    "qi_resonance_sound_bed": ["the Qi Resonance Sound Bed", "full-body sound therapy systems", 
                              "resonance therapy platforms", "immersive frequency experiences"],
    "qi_red_light_therapy": ["Qi Red Light Therapy", "red and near-infrared light devices", 
                            "photobiomodulation technology", "targeted light therapy systems"],
    "qi_wand": ["the Qi Wand", "precision energy tools", "targeted acupressure devices", 
               "cold laser therapy instruments"]
}

PERSONAL_STORIES = [
    "my health transformation", "my wellness journey", "my recovery process",
    "my exploration of alternative approaches", "my search for effective solutions",
    "my struggles with conventional treatments", "my biohacking experiments",
    "my quest for natural remedies", "my personal healing journey"
]

TRADITIONAL_PRINCIPLES = [
    "Eastern medicine", "energy medicine", "Traditional Chinese Medicine",
    "Ayurvedic wisdom", "holistic health approaches", "ancient healing traditions",
    "energy-based healing systems", "biofield science", "mind-body medicine"
]

GENERAL_BENEFITS = [
    "wellbeing", "quality of life", "overall health", "vitality",
    "resilience", "energy levels", "mind-body balance", "holistic wellness",
    "physiological harmony", "optimal functioning"
] 