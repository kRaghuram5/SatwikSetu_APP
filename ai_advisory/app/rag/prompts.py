"""RAG prompt templates for the AI Advisory chain."""

ADVISORY_SYSTEM_PROMPT = """You are an expert agricultural scientist and crop disease advisor.
Your role is to provide actionable, farmer-friendly treatment advice based on the detected disease and relevant knowledge base documents.

Be specific, practical, and include dosages where applicable.
Consider the farmer's location for region-specific recommendations.
Always include both chemical and organic treatment options.
"""

ADVISORY_USER_PROMPT = """
A crop disease has been detected with the following details:
- **Crop:** {crop}
- **Disease:** {disease}
- **Confidence:** {confidence}%
- **Location:** {location}

Here is relevant information from our agricultural knowledge base:

{context}

---

Please provide a comprehensive advisory with:
1. **Treatment** — Primary chemical/conventional treatment with dosages
2. **Organic Alternative** — Organic/biological control options
3. **Prevention** — Steps to prevent recurrence (as a list)
4. **Fertilizer Recommendation** — Suitable fertilizer for recovery

Format your response as JSON with these exact keys:
{{
  "treatment": "...",
  "organic_alternative": "...",
  "prevention": ["step1", "step2", ...],
  "fertilizer": "..."
}}
"""

MOCK_ADVISORY_RESPONSES = {
    "Late_blight": {
        "treatment": "Apply copper-based fungicide (Bordeaux mixture 1%) or Mancozeb 75WP at 2.5g/L water. Spray at 7-day intervals. Remove and destroy all infected plant parts immediately.",
        "organic_alternative": "Spray neem oil solution (5ml/L water) every 7 days. Apply Trichoderma viride at 5g/L as soil drench. Use copper hydroxide 53.8WP for organic control.",
        "prevention": ["Practice 3-year crop rotation with non-solanaceous crops", "Use certified disease-resistant varieties", "Avoid overhead irrigation — use drip instead", "Maintain proper plant spacing for air circulation", "Remove all crop debris after harvest"],
        "fertilizer": "NPK 10-26-26 for improved disease resistance. Add calcium nitrate at 25kg/ha to strengthen cell walls. Avoid excess nitrogen."
    },
    "Early_blight": {
        "treatment": "Apply Chlorothalonil 75WP at 2g/L or Azoxystrobin 23SC at 1ml/L water. Begin spraying at first sign of symptoms. Repeat every 10-14 days.",
        "organic_alternative": "Spray baking soda solution (1 tbsp per gallon + few drops liquid soap). Apply compost tea biweekly. Mulch heavily around plant base to prevent soil splash.",
        "prevention": ["Apply thick organic mulch around base", "3-year crop rotation mandatory", "Water at soil level only", "Adequate plant spacing of 60-75cm", "Remove lower infected leaves promptly"],
        "fertilizer": "Balanced NPK 15-15-15 at 200kg/ha. Extra potassium (MOP) at 40kg/ha for leaf health."
    },
    "Brown_spot": {
        "treatment": "Apply Propiconazole 25EC at 1ml/L water as foliar spray. Seed treatment with Thiram at 2g/kg seed before sowing. Supplement with potash fertilizer.",
        "organic_alternative": "Seed treatment with Pseudomonas fluorescens at 10g/L. Apply neem cake at 150kg/ha. Foliar spray of 5% neem kernel extract at weekly intervals.",
        "prevention": ["Ensure balanced fertilization, especially potassium and phosphorus", "Use only certified disease-free seeds", "Remove all crop residue after harvest", "Maintain proper water management in paddies"],
        "fertilizer": "Apply Potash (MOP) at 60kg/ha urgently. Supplement with zinc sulphate at 25kg/ha. Ensure adequate phosphorus."
    },
    "default": {
        "treatment": "Consult your local agricultural extension officer for specific treatment. Apply broad-spectrum fungicide as interim measure. Remove all visibly infected plant material.",
        "organic_alternative": "Apply neem oil solution (5ml/L) as general antifungal. Use Trichoderma-enriched compost around plant base. Spray dilute cow urine (1:10) as traditional remedy.",
        "prevention": ["Practice crop rotation", "Use disease-resistant varieties", "Maintain field hygiene", "Balanced nutrition", "Regular scouting"],
        "fertilizer": "Apply balanced NPK fertilizer according to soil test recommendations. Avoid excess nitrogen."
    }
}
