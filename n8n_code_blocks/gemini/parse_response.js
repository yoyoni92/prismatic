const raw = $input.first().json;
let analysisText = raw.candidates?.[0]?.content?.parts?.[0]?.text ?? "{}";

// Strip markdown code fences if Gemini wraps in ```json
analysisText = analysisText.replace(/^```json\n?/, "").replace(/\n?```$/, "").trim();

let analysis;
try {
  analysis = JSON.parse(analysisText);
} catch (e) {
  throw new Error(`Gemini returned invalid JSON: ${analysisText.substring(0, 200)}`);
}

const required = ["summary", "classification", "sentiment", "entities", "action_items", "confidence_score"];
for (const field of required) {
  if (!(field in analysis)) {
    throw new Error(`Missing required field: ${field}`);
  }
}

// For the Gemini Pro parse node, change "gemini_flash" → "gemini_pro"
return [{ json: { gemini_flash: analysis } }];
